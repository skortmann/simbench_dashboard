"""N-1 Security: single outage of every line / transformer."""

import streamlit as st

from simbench_app import contingency as cg
from simbench_app import utils
from simbench_app.explanations import explain
from simbench_app.i18n import tr
from simbench_app.i18n import tr as trc  # tr() of catalogued constants

st.set_page_config(page_title=tr("N-1 Security"), page_icon="🛡️", layout="wide")
st.header("🛡️ " + tr("N-1 Security Check"))

net = utils.require_network()
thresholds = utils.threshold_controls()
code = utils.loaded_code()

st.markdown(tr(
    "Each line and transformer is taken out of service once and the power "
    "flow is recomputed. The result shows where a single outage interrupts "
    "supply or violates limits — and whether closing a normally-open point "
    "restores supply."
))
with st.expander(tr("How the check works and what it does not do")):
    st.markdown(explain("n1"))

c1, c2, c3 = st.columns(3)
with c1:
    max_outages = st.number_input(tr("Max. outages to simulate"), 10, 2000, 300,
                                  help=tr("Most heavily loaded elements first."))
with c2:
    restore = st.checkbox(tr("Try restoration by closing open points"), value=True)
with c3:
    backend = st.selectbox(tr("Solver backend"), ["lightsim2grid", "pandapower"])

if st.button(tr("Run N-1 analysis"), type="primary"):
    bar = st.progress(0.0)
    res = cg.n1_analysis(
        net, vm_min=thresholds["vm_min_pu"], vm_max=thresholds["vm_max_pu"],
        max_loading=thresholds["max_loading_percent"],
        max_outages=int(max_outages), restore=restore, backend=backend,
        progress=lambda d, t: bar.progress(d / max(t, 1)))
    bar.empty()
    st.session_state["n1_result"] = (code, res)

saved = st.session_state.get("n1_result")
if not saved or saved[0] != code:
    st.info(tr("No N-1 analysis has been run for this network yet."))
    st.stop()

# status keys of contingency.py are logic keys (English); translated on display
STATUS_LABELS = ["ok", "restored", "restored (violations)", "violation",
                 "supply loss", "no convergence"]
ELEMENT_LABELS = {"line": "Line", "trafo": "Transformer"}
COLUMN_LABELS = {
    "element": "Element type", "index": "Index", "name": "Name",
    "vn_kv": "Nominal voltage [kV]",
    "base_loading_percent": "Base-case loading [%]",
    "restored_by": "Restored by", "unsupplied_buses": "Unsupplied buses",
    "min_vm_pu": "Min. voltage [p.u.]", "max_vm_pu": "Max. voltage [p.u.]",
    "max_line_loading_percent": "Max. line loading [%]",
    "max_trafo_loading_percent": "Max. transformer loading [%]",
    "n_violations": "Limit violations", "status": "Status",
}


def _restored_by(v):
    """'switch 5' / 'line 7' -> translated display text."""
    if isinstance(v, str) and v.startswith("switch "):
        return tr("switch {i}", i=v.split(" ", 1)[1])
    if isinstance(v, str) and v.startswith("line "):
        return tr("line {i}", i=v.split(" ", 1)[1])
    return v


res = saved[1]
if res.empty:
    st.error(tr("The base case does not converge — run the power flow page first "
                "and fix the base case."))
    st.stop()

def _display(df):
    """Translate column names, statuses and element kinds for display only."""
    out = df.copy()
    out["status"] = out["status"].map(lambda v: trc(v) if v in STATUS_LABELS else v)
    out["element"] = out["element"].map(lambda v: trc(ELEMENT_LABELS.get(v, v)))
    out["restored_by"] = out["restored_by"].map(_restored_by)
    return out.rename(columns={c: trc(COLUMN_LABELS[c]) for c in out.columns
                               if c in COLUMN_LABELS})


summary = cg.summarize(res)
cols = st.columns(len(summary))
for col, (status, n) in zip(cols, summary.items()):
    col.metric(trc(status), int(n))

problem = res[res["status"] != "ok"]
st.subheader(tr("Outages with consequences"))
if problem.empty:
    st.success(tr("(n-1) secure: no single outage causes a violation or supply loss."))
else:
    st.dataframe(_display(problem.drop(columns=["bus_a", "bus_b"]).round(3)),
                 hide_index=True, width="stretch")
with st.expander(tr("All simulated outages")):
    st.dataframe(_display(res.round(3)), hide_index=True, width="stretch")
st.download_button(tr("Download results (CSV)"), res.to_csv(index=False).encode(),
                   file_name=f"n1_{code}.csv", mime="text/csv")
