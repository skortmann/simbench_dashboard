"""Smoke test for the SimBench analysis platform.

Plain script (no test framework): imports every module, loads the default
network, runs a power flow, exercises the analysis layer, and executes every
Streamlit page via ``streamlit.testing.v1.AppTest`` — each with and without a
loaded network. Exits non-zero on any failure.

Run with:  uv run python tests/smoke_test.py
"""

from __future__ import annotations

import os
import sys
import warnings

warnings.filterwarnings("ignore")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)  # pages import simbench_app; AppTest needs the root

failures: list[str] = []


def check(label: str, ok: bool, detail: str = "") -> None:
    print(f"{'OK   ' if ok else 'FAIL '} {label}" + (f": {detail}" if detail else ""))
    if not ok:
        failures.append(f"{label}: {detail}")


# --- 1) module imports ---------------------------------------------------------
from simbench_app import (config, contingency, data_loading,  # noqa: E402
                          explanations, scenarios,
                          network_analysis as na, powerflow as pf,
                          profiles as prof, report, tables, utils,
                          validation, visualization as viz)

check("module imports", True)

# --- 2) network loading & analysis layer ------------------------------------------
import simbench as sb  # noqa: E402

net = sb.get_simbench_net(config.DEFAULT_CODE)
check("default network loads", len(net.bus) > 0,
      f"{len(net.bus)} buses, {len(net.line)} lines")

check("element counts", len(na.element_counts(net)) > 0)
check("consistency checks all pass",
      all(ok for ok, _ in na.consistency_checks(net)))

result = pf.run_power_flow(net)
check("power flow converges", result.converged, result.error)
check("voltage summary", len(pf.voltage_summary(net)) > 0)
check("power balance", len(pf.power_balance(net)) == 6)

viol = pf.violations(net, 0.95, 1.05, 100.0)
check("violations computed", set(viol) == {
    "undervoltage_buses", "overvoltage_buses",
    "overloaded_lines", "overloaded_trafos"})

findings = validation.run_diagnostics(net, config.DEFAULT_THRESHOLDS, result)
check("diagnostics produce findings", len(findings) > 0)

coords, source = viz.bus_coordinates(net)
check("bus coordinates", coords.notna().all().all(), source)
fig = viz.network_figure(net, coords, bus_color="vm_pu", line_color="loading")
check("network figure", len(fig.data) > 0, f"{len(fig.data)} traces")

groups = prof.available_groups(net)
check("profiles available", "load" in groups, str(list(groups)))
ts = prof.run_profile_powerflow(net, n_steps=4)
check("time-series demo", bool(ts["converged"].all()), f"{len(ts)} steps")

# lightsim2grid backend and fallback
check("backend lightsim2grid used", result.backend == "lightsim2grid", result.backend)
r_bfsw = pf.run_power_flow(net, algorithm="bfsw")
check("non-NR algorithm falls back to pandapower",
      r_bfsw.backend == "pandapower" and bool(r_bfsw.backend_note), r_bfsw.backend_note)

# voltage rise by generation
rise = pf.der_voltage_rise(net)
check("DER voltage rise", len(rise) > 0 and rise["delta_u_percent"].max() > 0)

# N-1
n1 = contingency.n1_analysis(net)
check("N-1 analysis", len(n1) > 0 and set(n1["status"]) <= {
    "ok", "violation", "restored", "restored (violations)", "supply loss",
    "no convergence"}, str(contingency.summarize(n1).to_dict()))
check("N-1 never restores by the failed line itself",
      not any(r.restored_by == f"line {r['index']}" for _, r in n1.iterrows()
              if r["element"] == "line"))

# planning cases and scenarios
mv = sb.get_simbench_net("1-MV-rural--0-sw")
cases = scenarios.compare_planning_cases(mv, config.DEFAULT_THRESHOLDS)
check("planning cases converge", bool(cases["converged"].all()))
check("hL imports, hW/lW export (reverse power flow)",
      cases.loc["hL", "grid_exchange_mw"] > 0 > cases.loc["lW", "grid_exchange_mw"])
check("scenario siblings", set(scenarios.sibling_codes(
    "1-MV-rural--0-sw", data_loading.list_codes())) == {"0", "1", "2"})

# annual time series: daily sub-sampling, divergence must be counted
ann = prof.run_annual_timeseries(mv, config.DEFAULT_THRESHOLDS, stride=96)
check("annual time series", ann is not None and ann.n_failed == 0
      and len(ann.system) == 366, f"{len(ann.system)} steps, {ann.backend}")
bad = sb.get_simbench_net("1-MV-rural--0-sw")
bad.profiles["load"].iloc[:, 1:] *= 40
ann_bad = prof.run_annual_timeseries(bad, config.DEFAULT_THRESHOLDS, stride=96)
check("annual time series counts diverged steps", ann_bad.n_failed == 366,
      f"{ann_bad.n_failed} failed")

md = report.build_markdown_report(net, config.DEFAULT_CODE, result,
                                  config.DEFAULT_THRESHOLDS)
check("markdown report", len(md) > 1000, f"{len(md)} chars")
check("network JSON export", len(utils.net_to_bytes(net, "json")) > 0)

# --- 3) every page executes ----------------------------------------------------
from streamlit.testing.v1 import AppTest  # noqa: E402

PAGES = ["streamlit_app.py"] + sorted(
    os.path.join("pages", f) for f in os.listdir(os.path.join(ROOT, "pages"))
    if f.endswith(".py"))

for lang in ("en", "de"):
    for page in PAGES:
        for with_net in (False, True):
            at = AppTest.from_file(os.path.join(ROOT, page), default_timeout=300)
            at.session_state["_lang"] = lang
            if with_net:
                at.session_state[config.KEY_NET] = net
                at.session_state[config.KEY_CODE] = config.DEFAULT_CODE
                at.session_state[config.KEY_PF_RESULT] = result
            at.run()
            errors = [str(e.value) for e in at.exception]
            check(f"page {page} [{lang}] ({'with' if with_net else 'no'} net)",
                  not errors, "; ".join(errors))

# --- 4) translation coverage -----------------------------------------------------
sys.path.insert(0, os.path.join(ROOT, "tests"))
from translation_check import missing_translations  # noqa: E402

missing = missing_translations()
check("all UI strings have a German translation", not missing,
      f"{len(missing)} missing, first: {missing[:3]}")

# --- summary ----------------------------------------------------------------------
print()
if failures:
    print(f"SMOKE TEST FAILED — {len(failures)} failure(s):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
print("SMOKE TEST PASSED — all checks green.")
