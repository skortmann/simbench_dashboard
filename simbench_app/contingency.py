"""N-1 security analysis: single outage of every line / transformer.

For each outage the AC power flow is recomputed and the result is classified:

* ``ok``            - supply intact, no limit violated
* ``violation``     - supply intact but a voltage or loading limit is violated
* ``restored``      - buses lost supply but closing one normally-open point
                      (open switch or out-of-service line) restores all of
                      them without violations
* ``restored (violations)`` - supply restored, but with limit violations
* ``supply loss``   - buses remain without supply
* ``no convergence``- the power flow of the outage case did not converge

The restoration step is a simple single-switching search (one closing action
per outage). It is an *orientation* for DSOs, not a switching-sequence
optimiser: no switching order, no remote-control times, no reserve capacity of
the upstream network beyond what the power flow shows.
"""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd

from . import powerflow as pf

OUTAGE_TABLES = ("line", "trafo")

#: Candidate switching actions tried per outage (bounds runtime).
MAX_RESTORE_CANDIDATES = 12


def _evaluate(net, vm_min: float, vm_max: float, max_loading: float) -> dict:
    """Condense the result tables of one power flow into scalar KPIs."""
    vm = net.res_bus["vm_pu"]
    supplied = vm.notna()
    out = {
        "unsupplied_buses": int((~supplied).sum()),
        "min_vm_pu": float(vm.min()) if supplied.any() else np.nan,
        "max_vm_pu": float(vm.max()) if supplied.any() else np.nan,
        "max_line_loading_percent": _max_loading(net, "line"),
        "max_trafo_loading_percent": _max_loading(net, "trafo"),
    }
    n_v = int(((vm < vm_min) | (vm > vm_max)).sum())
    n_l = _n_over(net, "line", max_loading) + _n_over(net, "trafo", max_loading)
    out["n_violations"] = n_v + n_l
    return out


def _max_loading(net, table: str) -> float:
    res = getattr(net, f"res_{table}")
    if res.empty or "loading_percent" not in res:
        return np.nan
    v = res["loading_percent"].max()
    return float(v) if pd.notna(v) else np.nan


def _n_over(net, table: str, limit: float) -> int:
    res = getattr(net, f"res_{table}")
    if res.empty or "loading_percent" not in res:
        return 0
    return int((res["loading_percent"] > limit).sum())


def _restore_candidates(net, lost_buses: set[int],
                        outage: tuple[str, int]) -> list[tuple[str, int]]:
    """Normally-open points that touch the de-energised area.

    Returns ``("switch", idx)`` for open switches and ``("line", idx)`` for
    out-of-service lines, restricted to those adjacent to a lost bus. The
    failed element itself is never a candidate.
    """
    cands: list[tuple[str, int]] = []
    sw = net.switch[~net.switch["closed"]]
    for idx, row in sw.iterrows():
        buses = {int(row["bus"])}
        if row["et"] == "l" and int(row["element"]) in net.line.index:
            ln = net.line.loc[int(row["element"])]
            buses |= {int(ln["from_bus"]), int(ln["to_bus"])}
        elif row["et"] == "b":
            buses.add(int(row["element"]))
        elif row["et"] == "t" and int(row["element"]) in net.trafo.index:
            tr = net.trafo.loc[int(row["element"])]
            buses |= {int(tr["hv_bus"]), int(tr["lv_bus"])}
        if buses & lost_buses:
            cands.append(("switch", int(idx)))
    for idx, ln in net.line[~net.line["in_service"]].iterrows():
        if outage == ("line", int(idx)):
            continue
        if {int(ln["from_bus"]), int(ln["to_bus"])} & lost_buses:
            cands.append(("line", int(idx)))
    return cands[:MAX_RESTORE_CANDIDATES]


def _set_candidate(net, cand: tuple[str, int], on: bool) -> None:
    kind, idx = cand
    if kind == "switch":
        net.switch.at[idx, "closed"] = on
    else:
        net.line.at[idx, "in_service"] = on


def n1_analysis(net, *, vm_min: float = 0.95, vm_max: float = 1.05,
                max_loading: float = 100.0, tables=OUTAGE_TABLES,
                max_outages: int = 300, restore: bool = True,
                backend: str = "lightsim2grid",
                progress=None) -> pd.DataFrame:
    """Run an N-1 analysis and return one row per simulated outage.

    The passed network is not modified (a deep copy is used). Outages are
    ordered by base-case loading, so with ``max_outages`` smaller than the
    number of elements the most heavily loaded ones are analysed first.
    ``progress`` is an optional callable ``progress(done, total)``.

    The base case must converge; otherwise an empty frame is returned.
    """
    work = copy.deepcopy(net)
    base = pf.run_power_flow(work, backend=backend)
    if not base.converged:
        return pd.DataFrame()

    # candidates: in-service elements, most loaded first
    cand: list[tuple[str, int, float]] = []
    for table in tables:
        res = getattr(work, f"res_{table}")
        for idx in work[table].index[work[table]["in_service"]]:
            load = res["loading_percent"].get(idx, np.nan) \
                if "loading_percent" in res else np.nan
            cand.append((table, int(idx), -1.0 if pd.isna(load) else float(load)))
    cand.sort(key=lambda c: -c[2])
    cand = cand[:max_outages]

    rows = []
    for n, (table, idx, base_loading) in enumerate(cand):
        if progress:
            progress(n, len(cand))
        work[table].at[idx, "in_service"] = False
        row = _outage_row(work, table, idx, base_loading, vm_min, vm_max,
                          max_loading, restore, backend)
        work[table].at[idx, "in_service"] = True
        rows.append(row)
    if progress:
        progress(len(cand), len(cand))
    return pd.DataFrame(rows)


def _outage_row(work, table, idx, base_loading, vm_min, vm_max, max_loading,
                restore, backend) -> dict:
    el = work[table].loc[idx]
    if table == "line":
        b1, b2 = int(el["from_bus"]), int(el["to_bus"])
    else:
        b1, b2 = int(el["hv_bus"]), int(el["lv_bus"])
    row = {
        "element": table, "index": idx,
        "name": el.get("name", ""),
        "bus_a": b1, "bus_b": b2,
        "vn_kv": float(work.bus.at[b1, "vn_kv"]),
        "base_loading_percent": None if base_loading < 0 else round(base_loading, 1),
        "restored_by": "",
    }
    r = pf.run_power_flow(work, backend=backend)
    if not r.converged:
        row.update(status="no convergence", unsupplied_buses=np.nan,
                   n_violations=np.nan)
        return row
    kpi = _evaluate(work, vm_min, vm_max, max_loading)
    row.update(kpi)

    if kpi["unsupplied_buses"] > 0 and restore:
        lost = set(work.res_bus.index[work.res_bus["vm_pu"].isna()])
        best = None
        for c in _restore_candidates(work, lost, (table, idx)):
            _set_candidate(work, c, True)
            rr = pf.run_power_flow(work, backend=backend)
            if rr.converged:
                k = _evaluate(work, vm_min, vm_max, max_loading)
                score = (k["unsupplied_buses"], k["n_violations"])
                if best is None or score < best[0]:
                    best = (score, c, k)
            _set_candidate(work, c, False)
        if best is not None and best[0][0] < kpi["unsupplied_buses"]:
            row.update(best[2])
            kind, i = best[1]
            row["restored_by"] = f"{'switch' if kind == 'switch' else 'line'} {i}"

    if row["unsupplied_buses"] > 0:
        row["status"] = "supply loss"
    elif row["restored_by"]:
        row["status"] = ("restored" if row["n_violations"] == 0
                         else "restored (violations)")
    else:
        row["status"] = "ok" if row["n_violations"] == 0 else "violation"
    return row


def summarize(result: pd.DataFrame) -> pd.Series:
    """Count outages per status."""
    if result.empty:
        return pd.Series(dtype=int)
    order = ["ok", "restored", "restored (violations)", "violation",
             "supply loss", "no convergence"]
    counts = result["status"].value_counts()
    return counts.reindex([s for s in order if s in counts.index])
