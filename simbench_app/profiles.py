"""SimBench time-series profile access and a capped time-series power flow."""

from __future__ import annotations

import copy
from dataclasses import dataclass, field

import pandas as pd
import pandapower as pp

from . import config

#: Profile groups stored in ``net.profiles`` (key -> label).
PROFILE_GROUPS = {
    "load": "Load profiles",
    "renewables": "Renewable generation profiles",
    "powerplants": "Power-plant profiles",
    "storage": "Storage profiles",
}


def available_groups(net) -> dict[str, pd.DataFrame]:
    """Non-empty profile groups of the network."""
    profiles = getattr(net, "profiles", None)
    if not isinstance(profiles, dict):
        return {}
    return {k: v for k, v in profiles.items()
            if isinstance(v, pd.DataFrame) and not v.empty
            and len(v.columns.drop("time", errors="ignore"))}


def profile_frame(net, group: str) -> pd.DataFrame:
    """Profile DataFrame of a group with the time column as index."""
    df = net.profiles[group]
    if "time" in df.columns:
        df = df.set_index("time")
    return df


def profile_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Peak, minimum, mean and annualised energy per profile column.

    Energy assumes the SimBench 15-minute resolution and normalised profiles,
    i.e. the result is in 'hours at rated power' (multiply by an element's
    rated MW to obtain MWh).
    """
    stats = pd.DataFrame({
        "Peak": df.max(),
        "Minimum": df.min(),
        "Mean": df.mean(),
        "Energy [h·p.u.]": df.sum() * config.PROFILE_RESOLUTION_H,
    })
    return stats.round(4)


def profile_usage(net) -> pd.DataFrame:
    """How many elements reference each profile name (loads/sgens/storage)."""
    rows = []
    for table in ("load", "sgen", "storage"):
        df = net.get(table)
        if isinstance(df, pd.DataFrame) and "profile" in df.columns and len(df):
            counts = df["profile"].value_counts()
            for name, n in counts.items():
                rows.append({"Element table": table, "Profile": name,
                             "Elements": int(n)})
    return pd.DataFrame(rows)


def run_profile_powerflow(net, n_steps: int, start_step: int = 0,
                          progress_callback=None) -> pd.DataFrame:
    """Demonstrative time-series power flow over a capped number of steps.

    Applies the absolute profile values step by step to a *deep copy* of the
    network (the session network is never modified) and records system-level
    indicators per step. Intentionally a simple loop — transparent and
    sufficient for a demonstration; pandapower's ``timeseries`` module is the
    tool of choice for production studies.
    """
    import simbench as sb

    n_steps = min(n_steps, config.TIMESERIES_MAX_STEPS)
    absolute = sb.get_absolute_values(net, profiles_instead_of_study_cases=True)
    absolute = {k: v for k, v in absolute.items() if isinstance(v, pd.DataFrame)
                and not v.empty}
    if not absolute:
        return pd.DataFrame()

    work = copy.deepcopy(net)
    horizon = len(next(iter(absolute.values())))
    steps = range(start_step, min(start_step + n_steps, horizon))

    records = []
    for pos, t in enumerate(steps):
        for (table, column), values in absolute.items():
            work[table].loc[values.columns, column] = values.loc[t].values
        row: dict = {"step": t}
        try:
            pp.runpp(work, lightsim2grid="auto")
            row.update({
                "converged": True,
                "total_load_mw": float(work.res_load["p_mw"].sum()),
                "total_sgen_mw": float(work.res_sgen["p_mw"].sum())
                if len(work.res_sgen) else 0.0,
                "ext_grid_mw": float(work.res_ext_grid["p_mw"].sum()),
                "min_vm_pu": float(work.res_bus["vm_pu"].min()),
                "max_vm_pu": float(work.res_bus["vm_pu"].max()),
                "max_line_loading": float(work.res_line["loading_percent"].max())
                if len(work.res_line) else float("nan"),
                "losses_mw": float(work.res_line["pl_mw"].sum()
                                   + work.res_trafo["pl_mw"].sum()),
            })
        except Exception:
            row["converged"] = False
        records.append(row)
        if progress_callback is not None:
            progress_callback((pos + 1) / len(steps))
    return pd.DataFrame(records).set_index("step")


# --- annual time series --------------------------------------------------------

@dataclass
class AnnualResult:
    """Aggregated result of a (sub-sampled) full-year time-series power flow."""

    system: pd.DataFrame      # per step (index = timestamp): system KPIs
    buses: pd.DataFrame       # per bus: min/max voltage, hours outside band
    lines: pd.DataFrame       # per line: max loading, hours above limit
    trafos: pd.DataFrame      # per transformer: max loading, hours above limit
    n_failed: int             # steps without a converged power flow
    stride: int               # 1 = 15-min steps, 4 = hourly, ...
    thresholds: dict = field(default_factory=dict)
    backend: str = ""

    @property
    def step_hours(self) -> float:
        """Duration represented by one simulated step [h]."""
        return config.PROFILE_RESOLUTION_H * self.stride


def profile_timestamps(net) -> pd.DatetimeIndex:
    """Timestamps of the SimBench profile rows (reference year 2016)."""
    for key in ("load", "renewables", "powerplants", "storage"):
        df = net.profiles.get(key) if hasattr(net, "profiles") else None
        if df is not None and "time" in df.columns and len(df):
            return pd.DatetimeIndex(pd.to_datetime(
                df["time"], format="%d.%m.%Y %H:%M"))
    return pd.DatetimeIndex([])


def run_annual_timeseries(net, thresholds: dict, *, stride: int = 4,
                          chunk: int = 500, backend: str = "lightsim2grid",
                          progress=None) -> AnnualResult | None:
    """Time-series power flow over the whole SimBench year (sub-sampled).

    Uses pandapower's ``run_timeseries`` with SimBench's constant controllers
    (the standard recipe) on a deep copy; with ``backend="lightsim2grid"`` the
    C++ solver is used, falling back to pandapower for unsupported networks.
    Only every ``stride``-th 15-min step is simulated (``stride=4`` = hourly).
    Results are aggregated per chunk, so memory stays bounded.
    ``progress`` is an optional callable ``progress(fraction)``.

    Returns ``None`` if the network carries no usable profiles.
    """
    import logging

    import numpy as np
    import simbench as sb
    from pandapower.timeseries import OutputWriter, run_timeseries
    from pandapower.timeseries.run_time_series import _call_output_writer

    # pandapower logs every diverged step at ERROR level; we count them instead
    for name in ("pandapower", "pandapower.timeseries.run_time_series"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
    absolute = sb.get_absolute_values(net, profiles_instead_of_study_cases=True)
    absolute = {k: v for k, v in absolute.items()
                if isinstance(v, pd.DataFrame) and not v.empty}
    times = profile_timestamps(net)
    if not absolute or len(times) == 0:
        return None

    prepared = copy.deepcopy(net)
    sb.apply_const_controllers(prepared, absolute)
    horizon = len(next(iter(absolute.values())))
    steps = list(range(0, horizon, stride))

    vmin, vmax = thresholds["vm_min_pu"], thresholds["vm_max_pu"]
    lim = thresholds["max_loading_percent"]
    n_bus, n_line, n_trafo = len(net.bus), len(net.line), len(net.trafo)
    bus_min = np.full(n_bus, np.inf); bus_max = np.full(n_bus, -np.inf)
    bus_under = np.zeros(n_bus); bus_over = np.zeros(n_bus)
    line_max = np.zeros(n_line); line_hours = np.zeros(n_line)
    trafo_max = np.zeros(n_trafo); trafo_hours = np.zeros(n_trafo)
    records, use_ls = [], backend == "lightsim2grid"
    converged_steps: dict[int, bool] = {}

    def _writer(net_, time_step, pf_ok, ctrl_ok, ts_vars):
        # pandapower keeps stale results of the previous step on divergence,
        # so convergence has to be recorded here, not inferred from the output
        converged_steps[time_step] = bool(pf_ok and ctrl_ok)
        _call_output_writer(net_, time_step, pf_ok, ctrl_ok, ts_vars)

    for c0 in range(0, len(steps), chunk):
        part = steps[c0:c0 + chunk]
        work = copy.deepcopy(prepared)
        ow = OutputWriter(work, time_steps=part, output_path=None,
                          log_variables=[])
        for table, col in (("bus", "vm_pu"), ("line", "loading_percent"),
                           ("trafo", "loading_percent"), ("ext_grid", "p_mw"),
                           ("load", "p_mw"), ("sgen", "p_mw")):
            if len(work[table]):
                ow.log_variable(f"res_{table}", col)
        try:
            run_timeseries(work, time_steps=part, continue_on_divergence=True,
                           verbose=False, lightsim2grid=use_ls,
                           output_writer_fct=_writer)
        except NotImplementedError:
            use_ls = False
            work = copy.deepcopy(prepared)
            ow = OutputWriter(work, time_steps=part, output_path=None,
                              log_variables=[])
            for table, col in (("bus", "vm_pu"), ("line", "loading_percent"),
                               ("trafo", "loading_percent"),
                               ("ext_grid", "p_mw"), ("load", "p_mw"),
                               ("sgen", "p_mw")):
                if len(work[table]):
                    ow.log_variable(f"res_{table}", col)
            run_timeseries(work, time_steps=part, continue_on_divergence=True,
                           verbose=False, lightsim2grid=False,
                           output_writer_fct=_writer)
        out = ow.output
        vm = out["res_bus.vm_pu"].to_numpy(float)
        ok = np.array([converged_steps.get(t, False) for t in part])
        line = out["res_line.loading_percent"].to_numpy(float) if n_line else np.zeros((len(part), 0))
        trafo = out["res_trafo.loading_percent"].to_numpy(float) if n_trafo else np.zeros((len(part), 0))
        under = (vm < vmin); over = (vm > vmax)
        rec = pd.DataFrame({
            "min_vm_pu": np.nanmin(np.where(ok[:, None], vm, np.nan), axis=1)
            if ok.any() else np.nan,
            "max_vm_pu": np.nanmax(np.where(ok[:, None], vm, np.nan), axis=1)
            if ok.any() else np.nan,
            "max_line_loading": np.nanmax(line, axis=1) if n_line and ok.any() else np.nan,
            "max_trafo_loading": np.nanmax(trafo, axis=1) if n_trafo and ok.any() else np.nan,
            "ext_grid_mw": out["res_ext_grid.p_mw"].sum(axis=1).to_numpy(float),
            "load_mw": out["res_load.p_mw"].sum(axis=1).to_numpy(float),
            "sgen_mw": out["res_sgen.p_mw"].sum(axis=1).to_numpy(float)
            if "res_sgen.p_mw" in out else 0.0,
            "n_violations": under.sum(axis=1) + over.sum(axis=1)
            + (line > lim).sum(axis=1) + (trafo > lim).sum(axis=1),
        }, index=times[part])
        rec.loc[~ok, rec.columns] = np.nan
        records.append(rec)
        if ok.any():
            bus_min = np.fmin(bus_min, np.nanmin(vm, axis=0))
            bus_max = np.fmax(bus_max, np.nanmax(vm, axis=0))
            bus_under += np.nansum(under, axis=0); bus_over += np.nansum(over, axis=0)
            if n_line:
                line_max = np.fmax(line_max, np.nanmax(line, axis=0))
                line_hours += np.nansum(line > lim, axis=0)
            if n_trafo:
                trafo_max = np.fmax(trafo_max, np.nanmax(trafo, axis=0))
                trafo_hours += np.nansum(trafo > lim, axis=0)
        if progress:
            progress(min(1.0, (c0 + len(part)) / len(steps)))

    n_failed = sum(1 for v in converged_steps.values() if not v)
    h = config.PROFILE_RESOLUTION_H * stride
    name = lambda t: net[t]["name"] if "name" in net[t] else pd.Series(index=net[t].index, dtype=object)
    buses = pd.DataFrame({"name": net.bus["name"], "vn_kv": net.bus["vn_kv"],
                          "min_vm_pu": bus_min, "max_vm_pu": bus_max,
                          "hours_undervoltage": bus_under * h,
                          "hours_overvoltage": bus_over * h}, index=net.bus.index)
    lines = pd.DataFrame({"name": name("line"), "max_loading_percent": line_max,
                          "hours_above_limit": line_hours * h}, index=net.line.index)
    trafos = pd.DataFrame({"name": name("trafo"), "max_loading_percent": trafo_max,
                           "hours_above_limit": trafo_hours * h}, index=net.trafo.index)
    return AnnualResult(system=pd.concat(records), buses=buses, lines=lines,
                        trafos=trafos, n_failed=n_failed, stride=stride,
                        thresholds=dict(thresholds),
                        backend="lightsim2grid" if use_ls else "pandapower")
