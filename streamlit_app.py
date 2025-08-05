import streamlit as st
import simbench as sb

st.set_page_config(page_title="SimBench Dashboard", layout="wide")
st.title("🚀 SimBench Dashboard")

# 1) Fetch all codes once, using st.cache_data
@st.cache_data
def load_codes():
    return sb.collect_all_simbench_codes()

codes = load_codes()

# 2) Split codes into their 6 parts:
parts = [c.split("-") for c in codes]
versions     = sorted({p[0] for p in parts})
voltages     = sorted({p[1] for p in parts})
urban_types  = sorted({p[2] for p in parts})
lv_subnets   = sorted({p[3] for p in parts})
scenarios    = sorted({p[4] for p in parts})
switch_flags = sorted({p[5] for p in parts})

# 3) Page layout
col1, col2, col3 = st.columns(3)
with col1:
    version = st.selectbox("Version", versions)
with col2:
    voltage = st.selectbox("Voltage levels", voltages)
with col3:
    urban = st.selectbox("Urbanisation", urban_types)

col4, col5, col6 = st.columns(3)
with col4:
    lv_subnet = st.selectbox("LV subnet", lv_subnets)
with col5:
    scenario = st.selectbox("Scenario", scenarios)
with col6:
    # if the only flag is 'sw', checkbox toggles it
    include_sw = st.checkbox("Include switches", value=True)

# 4) Reconstruct and load
sw_part = "sw" if include_sw and switch_flags else "no_sw"
code_str = "-".join([version, voltage, urban, lv_subnet, scenario, sw_part])

st.markdown(f"**Selected code:** `{code_str}`")

if st.button("Load network"):
    st.session_state.net = sb.get_simbench_net(code_str)
    st.success(f"✅ Loaded network: `{code_str}`")
