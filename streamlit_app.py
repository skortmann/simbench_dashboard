import streamlit as st
import simbench as sb

st.set_page_config(page_title="SimBench Dashboard", layout="wide")
st.title("🚀 SimBench Dashboard")

# Cache SimBench codes
@st.cache_data
def load_codes():
    return sb.collect_all_simbench_codes()

codes = load_codes()

# Split codes into their components
parts = [c.split("-") for c in codes]

# Helper to get unique sorted list for a given index and optional filters
def get_options(idx, filters):
    vals = [p[idx] for p in parts if all(p[i] == v for i, v in filters.items())]
    return sorted(set(vals))

# 3) Page layout with cascading selectboxes
col1, col2, col3 = st.columns(3)
with col1:
    versions = get_options(0, {})
    version = st.selectbox("Version", versions)
with col2:
    voltages = get_options(1, {0: version})
    voltage = st.selectbox("Voltage levels", voltages)
with col3:
    urbans = get_options(2, {0: version, 1: voltage})
    urban = st.selectbox("Urbanisation", urbans)

col4, col5, col6 = st.columns(3)
with col4:
    lv_subnets = get_options(3, {0: version, 1: voltage, 2: urban})
    lv_subnet = st.selectbox("LV subnet", lv_subnets)
with col5:
    scenarios = get_options(4, {0: version, 1: voltage, 2: urban, 3: lv_subnet})
    scenario = st.selectbox("Scenario", scenarios)
with col6:
    # Determine if switch flag present for current selection
    sw_choices = get_options(5, {0: version, 1: voltage, 2: urban, 3: lv_subnet, 4: scenario})
    include_sw = False
    if sw_choices:
        include_sw = st.checkbox("Include switches", value=True)

# Reconstruct code
sw_part = "sw" if include_sw and "sw" in sw_choices else ""
code_str = "-".join([version, voltage, urban, lv_subnet, scenario] + ([sw_part] if sw_part else []))

st.markdown(f"**Selected code:** `{code_str}`")

if st.button("Load network"):
    st.session_state.net = sb.get_simbench_net(code_str)
    st.success(f"✅ Loaded network: `{code_str}`")
