"""Home page: platform introduction and SimBench network selection."""

import streamlit as st

from simbench_app import config, data_loading as dl, utils
from simbench_app.explanations import explain
from simbench_app.i18n import tr

st.set_page_config(page_title=tr("SimBench Analysis Platform"), page_icon="⚡",
                   layout="wide")

st.title(tr("⚡ SimBench Network Analysis Platform"))
st.markdown(explain("platform"))

with st.expander(tr("How SimBench codes are structured")):
    st.markdown(explain("code_structure"))


def _load(code: str) -> None:
    """Load a network into the session, replacing any previous one."""
    try:
        net = dl.load_network(code)
    except Exception as exc:
        st.error(tr(
            "Loading `{code}` failed: {exc}\n\n"
            "Likely causes: an invalid code combination (not every component "
            "combination exists in the dataset), or insufficient memory for "
            "very large grids (e.g. complete HV datasets) on small hosts.",
            code=code, exc=exc))
        return
    st.session_state[config.KEY_NET] = net
    st.session_state[config.KEY_CODE] = code
    st.session_state[config.KEY_LOADED_AT] = utils.now_iso()
    # Results and modification log belong to the previous network.
    st.session_state.pop(config.KEY_PF_RESULT, None)
    st.session_state.pop(config.KEY_MODLOG, None)
    st.success(tr("Loaded network `{code}` — {buses} buses, {lines} lines.",
                  code=code, buses=len(net.bus), lines=len(net.line)))


# --- quick start ----------------------------------------------------------------
st.subheader(tr("Quick start"))
st.markdown(tr(
    "New here? Load the small example network `{code}` "
    "(a rural low-voltage feeder) and explore the pages on the left.",
    code=config.DEFAULT_CODE))
if st.button(tr("Load example network"), type="primary"):
    _load(config.DEFAULT_CODE)

# --- cascading code selection ------------------------------------------------------
st.subheader(tr("Select a SimBench network"))

codes = dl.list_codes()
parts = dl.split_codes(codes)

col1, col2, col3 = st.columns(3)
with col1:
    version = st.selectbox(tr("Version"), dl.options_for(parts, 0, {}))
with col2:
    voltage = st.selectbox(tr("Grid level"),
                           dl.options_for(parts, 1, {0: version}))
with col3:
    urban = st.selectbox(tr("Urbanisation / type"),
                         dl.options_for(parts, 2, {0: version, 1: voltage}))

col4, col5, col6 = st.columns(3)
with col4:
    lv_subnet = st.selectbox(
        tr("LV subnet"), dl.options_for(parts, 3, {0: version, 1: voltage, 2: urban}),
        help=tr("Only meaningful for combined MV/LV grids; empty otherwise."))
with col5:
    scenario = st.selectbox(
        tr("Scenario"), dl.options_for(parts, 4, {0: version, 1: voltage,
                                              2: urban, 3: lv_subnet}),
        help=tr("0 = today, 1 = near future, 2 = far future (more DER)."))
with col6:
    sw_choices = dl.options_for(parts, 5, {0: version, 1: voltage, 2: urban,
                                           3: lv_subnet, 4: scenario})
    include_sw = st.checkbox(tr("Include switches"), value=True) \
        if "sw" in sw_choices else False

sw_part = ["sw"] if include_sw and "sw" in sw_choices else []
code_str = "-".join([version, voltage, urban, lv_subnet, scenario] + sw_part)

meta = dl.describe_code(code_str)
st.markdown(tr("**Selected code:** `{code}`", code=code_str))
labels = dl.code_labels()
st.table({tr("Property"): [labels[k] for k in meta], tr("Value"): list(meta.values())})

if code_str not in codes:
    st.warning(tr("This exact combination does not exist in the SimBench dataset — "
                  "adjust the selection above."))
elif st.button(tr("Load network")):
    _load(code_str)

# --- session status ---------------------------------------------------------------
st.divider()
net = utils.get_net()
if net is None:
    st.info(tr("No network loaded yet."))
else:
    st.markdown(tr(
        "**Currently loaded:** `{code}` "
        "({buses} buses, {lines} lines, "
        "{trafos} transformers) — loaded at {time}.",
        code=utils.loaded_code(), buses=len(net.bus), lines=len(net.line),
        trafos=len(net.trafo),
        time=st.session_state.get(config.KEY_LOADED_AT, "?")))
    st.markdown(tr(
        "Continue with **Network Overview** for summary statistics, "
        "**Topology Visualization** for the network map, or "
        "**Power Flow Analysis** to compute the operating state."
    ))

st.caption(tr("Time series at full year length are part of every SimBench "
              "network; see the *Profiles & Time Series* page."))
