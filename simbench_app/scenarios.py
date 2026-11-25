"""SimBench planning cases (hL / hW / lW) and development-scenario comparison.

Planning cases are shipped with every SimBench net (``net.loadcases``) and
describe extreme operating points: high load without generation (``hL``),
high load with very high wind (``hW``) and low load with very high wind
(``lW``). Development scenarios (code position 5: 0, 1, 2) are separate
networks of the same grid with increasing generation / new consumers.
"""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import simbench as sb

from . import powerflow as pf

#: Planning cases offered in the UI (key -> plain-language description).
PLANNING_CASES = {
    "hL": "High load, no generation (load 1.0, wind/PV/other 0)",
    "hW": "High load, very high wind (load 1.0, wind 1.0, PV 0.8, other 1.0)",
    "lW": "Low load, very high wind (load 0.25 HV / 0.10 MV, LV, wind 1.0, PV 0.8)",
}


def has_planning_cases(net) -> bool:
    """True if the net carries study-case data (not available for EHV nets)."""
    lc = getattr(net, "loadcases", None)
    return isinstance(lc, pd.DataFrame) and len(lc) > 0


def apply_planning_case(net, case: str) -> None:
    """Write the absolute values of a planning case into ``net`` (in place).

    Sets load p/q, sgen p and the ext_grid voltage setpoint. Storage and
    controllable generators keep their stored values (the cases do not scale
    them). Raises ``ValueError`` if the net has no planning cases.
    """
    if not has_planning_cases(net):
        raise ValueError("This network has no planning cases (e.g. EHV grids).")
    av = sb.get_absolute_values(net, False)
    for (table, col), values in av.items():
        if case not in values.index or table not in ("load", "sgen", "ext_grid"):
            continue
        net[table][col] = values.loc[case].reindex(net[table].index) \
            .fillna(net[table][col])


def case_kpis(net, thresholds: dict, *, backend: str = "lightsim2grid") -> dict:
    """Run a power flow on ``net`` and condense it into scalar KPIs."""
    r = pf.run_power_flow(net, backend=backend)
    out = {"converged": r.converged}
    if not r.converged:
        return out
    vm = net.res_bus["vm_pu"].dropna()
    viol = pf.violations(net, thresholds["vm_min_pu"], thresholds["vm_max_pu"],
                         thresholds["max_loading_percent"])
    out.update({
        "load_mw": float(net.res_load["p_mw"].sum()),
        # res_sgen.p_mw is positive for infeed (generator convention)
        "generation_mw": float(net.res_sgen["p_mw"].sum()) if len(net.res_sgen) else 0.0,
        "grid_exchange_mw": float(net.res_ext_grid["p_mw"].sum()),
        "min_vm_pu": float(vm.min()),
        "max_vm_pu": float(vm.max()),
        "max_line_loading_percent": _max(net, "line"),
        "max_trafo_loading_percent": _max(net, "trafo"),
        "n_violations": pf.n_violations(viol),
    })
    return out


def _max(net, table: str) -> float:
    res = getattr(net, f"res_{table}")
    if res.empty or "loading_percent" not in res:
        return np.nan
    return float(res["loading_percent"].max())


def compare_planning_cases(net, thresholds: dict, *, backend: str = "lightsim2grid",
                           cases=tuple(PLANNING_CASES)) -> pd.DataFrame:
    """KPIs of the same net under each planning case (rows = cases).

    The passed net is not modified.
    """
    rows = {}
    for case in cases:
        work = copy.deepcopy(net)
        apply_planning_case(work, case)
        rows[case] = case_kpis(work, thresholds, backend=backend)
    return pd.DataFrame(rows).T


def sibling_codes(code: str, all_codes: list[str]) -> dict[str, str]:
    """Codes of the same grid for scenarios 0/1/2 (those that exist)."""
    p = code.split("-")
    if len(p) < 5:
        return {}
    out = {}
    for sc in ("0", "1", "2"):
        cand = "-".join(p[:4] + [sc] + p[5:])
        if cand in all_codes:
            out[sc] = cand
    return out


def inventory(net) -> dict:
    """Installed capacity / counts used to compare development scenarios."""
    return {
        "loads": len(net.load),
        "peak_load_mw": float(net.load["p_mw"].sum()),
        "sgen": len(net.sgen),
        "installed_sgen_mw": float(net.sgen["p_mw"].sum()),
        "storage": len(net.storage),
        "storage_mw": float(net.storage["p_mw"].abs().sum()) if len(net.storage) else 0.0,
        "lines": len(net.line),
        "transformers": len(net.trafo),
    }
