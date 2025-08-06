import streamlit as st
import pandapower as pp
from pandapower.control.controller.const_control import ConstControl

st.set_page_config(page_title="Power Flow Calculation", layout="wide")
st.header("Power Flow Calculation")

if 'net' not in st.session_state:
    st.warning("Load a network on the Home page first.")
else:
    net = st.session_state.net
    ConstControl