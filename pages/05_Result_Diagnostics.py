"""Result Diagnostics: severity-ranked structural and result checks."""

import streamlit as st

from simbench_app import config, utils, validation
from simbench_app.explanations import explain
from simbench_app.i18n import tr

st.set_page_config(page_title=tr("Result Diagnostics"), page_icon="🩺",
                   layout="wide")
st.header("🩺 " + tr("Result Diagnostics"))

net = utils.require_network()
thresholds = utils.threshold_controls()
pf_result = st.session_state.get(config.KEY_PF_RESULT)

st.markdown(tr(
    "Automated checks of the loaded network and — once a power flow has been "
    "run — of its results. Each finding carries a severity and a plain-"
    "language explanation."
))
with st.expander(tr("How severities are assigned")):
    st.markdown(explain("diagnostics"))

findings = validation.run_diagnostics(net, thresholds, pf_result)

n_by_sev = {"critical": 0, "warning": 0, "info": 0}
for f in findings:
    n_by_sev[f.severity] = n_by_sev.get(f.severity, 0) + 1

c1, c2, c3 = st.columns(3)
c1.metric(tr("Critical"), n_by_sev["critical"])
c2.metric(tr("Warnings"), n_by_sev["warning"])
c3.metric(tr("Info"), n_by_sev["info"])

icons = {"critical": "🟥", "warning": "🟨", "info": "🟦"}
renderers = {"critical": st.error, "warning": st.warning, "info": st.info}

for f in findings:
    renderers[f.severity](f"{icons[f.severity]} **{f.title}** — {f.detail}")

if pf_result is None:
    st.caption(tr("Run a power flow on the *Power Flow Analysis* page to "
                  "enable voltage-band and loading checks."))

with st.expander(tr("Model limitations to keep in mind")):
    st.markdown(explain("limitations"))
