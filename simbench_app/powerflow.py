"""Power-flow execution and result post-processing."""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import pandas as pd
import pandapower as pp

from .i18n import tr

#: Power-flow algorithms exposed in the UI (pandapower key -> label).
ALGORITHMS = {
    "nr": "Newton-Raphson (default, robust)",
    "bfsw": "Backward/forward sweep (radial networks)",
    "gs": "Gauss-Seidel (slow, didactic)",
    "fdbx": "Fast-decoupled (BX)",
    "fdxb": "Fast-decoupled (XB)",
}

INIT_MODES = ["auto", "flat", "dc", "results"]

#: Solver backends (key -> label). lightsim2grid is a C++ Newton-Raphson solver.
BACKENDS = {
    "lightsim2grid": "lightsim2grid (C++, fast; Newton-Raphson only)",
    "pandapower": "pandapower native (all algorithms)",
}

try:  # optional dependency
    import lightsim2grid  # noqa: F401
    LIGHTSIM2GRID_AVAILABLE = True
except ImportError:
    LIGHTSIM2GRID_AVAILABLE = False


@dataclass
class PowerFlowResult:
    """Metadata of the last power-flow run (numerical results live in net.res_*)."""

    converged: bool
    error: str = ""
    options: dict = field(default_factory=dict)
    runtime_s: float = 0.0
    timestamp: str = ""
    code: str = ""
    backend: str = "pandapower"  # backend actually used
    backend_note: str = ""  # why a requested backend was not used


def run_power_flow(net, *, algorithm: str = "nr", init: str = "auto",
                   enforce_q_lims: bool = False,
                   max_iteration: int | str = "auto",
                   backend: str = "lightsim2grid") -> PowerFlowResult:
    """Run an AC power flow and return run metadata.

    Results are written into the ``net.res_*`` tables of the passed network
    (the session working copy), as is pandapower convention.

    ``backend="lightsim2grid"`` is tried first; if it is unavailable or does
    not support the network/options (non-NR algorithm, voltage-dependent
    loads, several ext_grids, ...), the run falls back to pandapower's own
    solver and the reason is stored in ``backend_note``.
    """
    from .utils import now_iso

    options = {
        "algorithm": algorithm,
        "init": init,
        "enforce_q_lims": enforce_q_lims,
        "max_iteration": max_iteration,
    }
    start = time.perf_counter()
    used, note = "pandapower", ""
    try:
        if backend == "lightsim2grid" and LIGHTSIM2GRID_AVAILABLE:
            try:
                pp.runpp(net, lightsim2grid=True, **options)
                used = "lightsim2grid"
            except NotImplementedError as exc:
                note = tr("lightsim2grid not applicable: {exc}", exc=exc)
        elif backend == "lightsim2grid":
            note = tr("lightsim2grid is not installed")
        if used == "pandapower":
            pp.runpp(net, lightsim2grid=False, **options)
        return PowerFlowResult(converged=True, options=options,
                               runtime_s=time.perf_counter() - start,
                               timestamp=now_iso(), backend=used,
                               backend_note=note)
    except Exception as exc:  # LoadflowNotConverged and option errors
        return PowerFlowResult(converged=False, error=str(exc), options=options,
                               runtime_s=time.perf_counter() - start,
                               timestamp=now_iso(), backend=used,
                               backend_note=note)


def has_results(net) -> bool:
    """True if the network carries usable bus power-flow results."""
    res = getattr(net, "res_bus", None)
    return (isinstance(res, pd.DataFrame) and len(res) > 0
            and res["vm_pu"].notna().any())


def voltage_summary(net) -> pd.DataFrame:
    """Min/mean/max voltage magnitude per nominal voltage level."""
    if not has_results(net):
        return pd.DataFrame()
    df = net.res_bus.join(net.bus[["vn_kv"]])
    out = (df.groupby("vn_kv")["vm_pu"].agg(["min", "mean", "max", "count"])
           .rename(columns={"min": tr("Min [p.u.]"), "mean": tr("Mean [p.u.]"),
                            "max": tr("Max [p.u.]"), "count": tr("Buses")})
           .rename_axis(tr("Voltage level [kV]")).sort_index(ascending=False))
    return out.round(4)


def loading_summary(net, table: str) -> pd.DataFrame:
    """Loading statistics for ``line`` or ``trafo`` results."""
    res = getattr(net, f"res_{table}", None)
    if res is None or res.empty or "loading_percent" not in res.columns:
        return pd.DataFrame()
    s = res["loading_percent"].dropna()
    if s.empty:
        return pd.DataFrame()
    return pd.DataFrame({
        "Quantity": [tr("Elements"), tr("Mean loading"), tr("Median loading"),
                     tr("Maximum loading"), tr("Elements above 80 %")],
        "Value": [len(s), round(s.mean(), 1), round(s.median(), 1),
                  round(s.max(), 1), int((s > 80).sum())],
        "Unit": ["–", "%", "%", "%", "–"],
    })


def power_balance(net) -> pd.DataFrame:
    """System-wide active/reactive power balance from the result tables."""
    if not has_results(net):
        return pd.DataFrame()

    def res_sum(table: str, col: str) -> float:
        res = getattr(net, f"res_{table}", None)
        if res is None or res.empty or col not in res.columns:
            return 0.0
        return float(res[col].sum())

    losses_p = res_sum("line", "pl_mw") + res_sum("trafo", "pl_mw") \
        + res_sum("trafo3w", "pl_mw")
    rows = [
        (tr("External grid infeed"), res_sum("ext_grid", "p_mw"),
         res_sum("ext_grid", "q_mvar")),
        (tr("Generation (gen)"), res_sum("gen", "p_mw"), res_sum("gen", "q_mvar")),
        (tr("Static generation (sgen)"), res_sum("sgen", "p_mw"),
         res_sum("sgen", "q_mvar")),
        (tr("Load demand"), res_sum("load", "p_mw"), res_sum("load", "q_mvar")),
        (tr("Storage (positive = charging)"), res_sum("storage", "p_mw"),
         res_sum("storage", "q_mvar")),
        (tr("Network losses (lines + transformers)"), losses_p, float("nan")),
    ]
    df = pd.DataFrame(rows, columns=["Component", "P [MW]", "Q [Mvar]"])
    return df.round(4)


def violations(net, vm_min: float, vm_max: float,
               max_loading: float) -> dict[str, pd.DataFrame]:
    """Threshold violations after a power flow, keyed by violation type.

    Returns DataFrames with element name, bus/terminal info and the violating
    value, ready for display and export.
    """
    out: dict[str, pd.DataFrame] = {}
    if not has_results(net):
        return out

    vb = net.res_bus.join(net.bus[["name", "vn_kv"]])
    under = vb[vb["vm_pu"] < vm_min]
    over = vb[vb["vm_pu"] > vm_max]
    out["undervoltage_buses"] = under[["name", "vn_kv", "vm_pu"]].sort_values("vm_pu")
    out["overvoltage_buses"] = over[["name", "vn_kv", "vm_pu"]] \
        .sort_values("vm_pu", ascending=False)

    for table in ("line", "trafo"):
        res = getattr(net, f"res_{table}", None)
        if res is None or res.empty or "loading_percent" not in res.columns:
            out[f"overloaded_{table}s"] = pd.DataFrame()
            continue
        over = res[res["loading_percent"] > max_loading]
        cols = ["name"] if "name" in net[table].columns else []
        joined = over.join(net[table][cols]) if cols else over.copy()
        keep = cols + ["loading_percent"]
        out[f"overloaded_{table}s"] = joined[keep] \
            .sort_values("loading_percent", ascending=False)
    return out


def n_violations(viol: dict[str, pd.DataFrame]) -> int:
    """Total number of violating elements across all violation tables."""
    return sum(len(df) for df in viol.values())


def der_voltage_rise(net, *, backend: str = "lightsim2grid") -> pd.DataFrame:
    """Voltage rise caused by generation, per bus.

    Runs the power flow twice on the *same* load situation: once as given and
    once with all ``sgen`` switched off. The difference of the voltage
    magnitudes is the voltage change attributable to generation (positive =
    generation raises the voltage), in percent of the nominal voltage.

    The passed network keeps its results of the run *with* generation; the
    comparison runs on a deep copy. Returns an empty frame if there is no
    generation or a run does not converge.
    """
    import copy

    if len(net.sgen) == 0 or not net.sgen["in_service"].any():
        return pd.DataFrame()
    base = copy.deepcopy(net)
    base.sgen["in_service"] = False
    if not run_power_flow(base, backend=backend).converged:
        return pd.DataFrame()
    with_gen = copy.deepcopy(net)
    if not run_power_flow(with_gen, backend=backend).converged:
        return pd.DataFrame()
    out = pd.DataFrame({
        "name": net.bus["name"],
        "vn_kv": net.bus["vn_kv"],
        "vm_without_gen_pu": base.res_bus["vm_pu"],
        "vm_with_gen_pu": with_gen.res_bus["vm_pu"],
    })
    out["delta_u_percent"] = (out["vm_with_gen_pu"] - out["vm_without_gen_pu"]) * 100
    return out.dropna(subset=["delta_u_percent"])
