"""Modify Network: controlled what-if changes to the session working copy."""

import pandapower as pp
import streamlit as st

from simbench_app import config, data_loading as dl, utils
from simbench_app.i18n import tr

st.set_page_config(page_title=tr("Modify Network"), page_icon="⚙️", layout="wide")
st.header("⚙️ " + tr("Modify Network"))

net = utils.require_network()

st.markdown(tr(
    "Apply controlled modifications to the **session working copy** of the "
    "network for what-if studies. The cached original is untouched — reload "
    "the network to discard all changes. Power-flow results are invalidated "
    "by every modification; re-run the power flow afterwards."
))

# --- load scaling -------------------------------------------------------------
st.subheader(tr("Scale loads"))
scale = st.slider(
    tr("Load scale factor"), 0.5, 2.0, 1.0, step=0.05,
    help=tr("Multiplies active and reactive power of every load. Useful to "
            "emulate demand growth or stress-test the feeder."))
if st.button(tr("Apply scaling")):
    net.load["p_mw"] *= scale
    net.load["q_mvar"] *= scale
    st.session_state.pop(config.KEY_PF_RESULT, None)
    utils.log_modification(tr("Scaled all loads by factor {scale}",
                                      scale=scale))
    st.success(tr("Scaled {n} loads by {scale}× (active and reactive power).",
                  n=len(net.load), scale=scale))

# --- add storage -----------------------------------------------------------------
st.subheader(tr("Add a storage unit"))
with st.form("add_storage"):
    name = st.text_input(tr("Name"), "Added_storage_1")
    power = st.number_input(tr("Power [MW] (positive = charging)"), value=1.0,
                            step=0.1)
    capacity = st.number_input(tr("Energy capacity [MWh]"), value=1.0,
                               min_value=0.0, step=0.1)
    bus_sel = st.selectbox(
        tr("Connection bus"), list(net.bus.index),
        format_func=lambda b: f"{b} — {net.bus.at[b, 'name']} "
                              f"({net.bus.at[b, 'vn_kv']:g} kV)")
    submitted = st.form_submit_button(tr("Add storage"))

if submitted:
    try:
        idx = pp.create_storage(net, bus=int(bus_sel), p_mw=float(power),
                                max_e_mwh=float(capacity), name=name)
        st.session_state.pop(config.KEY_PF_RESULT, None)
        utils.log_modification(tr(
            "Added storage '{name}' ({power} MW / {capacity} MWh) "
            "at bus {bus}", name=name, power=power, capacity=capacity,
            bus=bus_sel))
        st.success(tr("Storage '{name}' added with index {idx}.",
                      name=name, idx=idx))
    except Exception as exc:
        st.error(tr("Adding the storage failed: {exc}", exc=exc))

# --- modification log & reset ---------------------------------------------------
st.subheader(tr("Modification log"))
modlog = st.session_state.get(config.KEY_MODLOG, [])
if modlog:
    for entry in modlog:
        st.markdown(f"- {entry}")
    st.caption(tr("Modifications are recorded in the analysis report on the "
                  "*Export & Report* page for reproducibility."))
else:
    st.info(tr("No modifications applied in this session."))

if st.button(tr("Discard modifications and reload original network")):
    code = utils.loaded_code()
    st.session_state[config.KEY_NET] = dl.load_network(code)
    st.session_state[config.KEY_LOADED_AT] = utils.now_iso()
    st.session_state.pop(config.KEY_PF_RESULT, None)
    st.session_state.pop(config.KEY_MODLOG, None)
    st.success(tr("Reloaded original network `{code}`.", code=code))
    st.rerun()
