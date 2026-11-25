"""Scenario Comparison: planning cases and development scenarios."""

import streamlit as st

from simbench_app import data_loading as dl
from simbench_app import scenarios as sc
from simbench_app import utils
from simbench_app.explanations import explain
from simbench_app.i18n import tr
from simbench_app.i18n import tr as trc  # tr() of catalogued constants

st.set_page_config(page_title=tr("Scenario Comparison"), page_icon="🔀",
                   layout="wide")
st.header("🔀 " + tr("Scenario Comparison"))

net = utils.require_network()
thresholds = utils.threshold_controls()
code = utils.loaded_code()

st.markdown(tr(
    "SimBench describes a grid in two dimensions: the **planning case** "
    "(operating point: high load, high wind, low load) and the "
    "**development scenario** (0/1/2: how much generation and new load the "
    "grid has). This page compares both for the loaded network."
))

backend = st.sidebar.selectbox(tr("Solver backend"), ["lightsim2grid", "pandapower"])

KPI_LABELS = {
    "converged": "Converged", "load_mw": "Load [MW]",
    "generation_mw": "Generation [MW]", "grid_exchange_mw": "Grid exchange [MW]",
    "min_vm_pu": "Min voltage [p.u.]", "max_vm_pu": "Max voltage [p.u.]",
    "max_line_loading_percent": "Max line loading [%]",
    "max_trafo_loading_percent": "Max trafo loading [%]",
    "n_violations": "Limit violations",
}


INVENTORY_LABELS = {
    "loads": "Loads", "peak_load_mw": "Peak load [MW]", "sgen": "Generators",
    "installed_sgen_mw": "Installed generation [MW]", "storage": "Storage units",
    "storage_mw": "Storage power [MW]", "lines": "Lines",
    "transformers": "Transformers",
}


def _kpi_columns(df):
    """Rename KPI columns to the active language for display."""
    return df.rename(columns={c: trc(KPI_LABELS[c]) for c in df.columns
                              if c in KPI_LABELS})


# --- planning cases -----------------------------------------------------------------
st.subheader(tr("Planning cases of the loaded network"))
with st.expander(tr("What are planning cases?")):
    st.markdown(explain("planning_cases"))

if not sc.has_planning_cases(net):
    st.info(tr("This network ships no planning cases (typical for EHV grids)."))
else:
    for k, v in sc.PLANNING_CASES.items():
        st.markdown(f"- **{k}** — {trc(v)}")
    if st.button(tr("Run planning cases"), type="primary"):
        with st.spinner(tr("Running power flows …")):
            res = sc.compare_planning_cases(net, thresholds, backend=backend)
        st.session_state["case_comparison"] = (code, res)
    saved = st.session_state.get("case_comparison")
    if saved and saved[0] == code:
        st.dataframe(_kpi_columns(saved[1]).round(3),
                     width="stretch")
        st.caption(tr("Grid exchange > 0: import from the upstream grid; < 0: "
                      "export (reverse power flow). The loaded network itself "
                      "is not modified."))

# --- development scenarios ----------------------------------------------------------
st.subheader(tr("Development scenarios of the same grid"))
with st.expander(tr("What are development scenarios?")):
    st.markdown(explain("scenarios"))

siblings = sc.sibling_codes(code, dl.list_codes())
if len(siblings) < 2:
    st.info(tr("No other scenarios of this grid found."))
else:
    st.markdown(tr("Available: {items}", items=", ".join(
        f"`{c}` ({trc(dl.SCENARIO_MEANING[s]).split(' — ')[0]})"
        for s, c in siblings.items())))
    case_choices = list(sc.PLANNING_CASES) if sc.has_planning_cases(net) else []
    case = st.selectbox(tr("Planning case for the power flow"), case_choices) \
        if case_choices else None
    if st.button(tr("Compare scenarios")):
        rows, inv = {}, {}
        with st.spinner(tr("Loading scenarios and running power flows …")):
            for s, c in siblings.items():
                n = dl.load_network(c)
                inv[tr("Scenario {s}", s=s)] = sc.inventory(n)
                if case:
                    sc.apply_planning_case(n, case)
                rows[tr("Scenario {s}", s=s)] = sc.case_kpis(n, thresholds, backend=backend)
        import pandas as pd
        st.session_state["scenario_comparison"] = (
            code, case, pd.DataFrame(inv).T, pd.DataFrame(rows).T)
    saved = st.session_state.get("scenario_comparison")
    if saved and saved[0] == code:
        _, case_used, inv_df, kpi_df = saved
        st.markdown(tr("**Installed capacities and element counts**"))
        st.dataframe(inv_df.rename(columns={
            c: trc(INVENTORY_LABELS[c]) for c in inv_df.columns
            if c in INVENTORY_LABELS}).round(3), width="stretch")
        st.markdown(tr("**Operating state** (planning case: {case})",
                       case=case_used or tr("as stored")))
        st.dataframe(_kpi_columns(kpi_df).round(3), width="stretch")
        st.caption(tr("Scenarios 1 and 2 are stress cases built to violate limits "
                      "- rising violation counts are expected."))
