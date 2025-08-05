import streamlit as st
import pandapower as pp
from pandapower.plotting.plotly import vlevel_plotly, pf_res_plotly

st.set_page_config(page_title="Visualize Network", layout="wide")
st.header("🗺️ Network Visualization")

if 'net' not in st.session_state:
    st.warning("Load a network on the Home page first.")
else:
    net = st.session_state.net

    # Run a simple power flow
    pp.runpp(net)

    # Voltage-level colored network plot (disable HTML export)
    st.subheader("Network by Voltage Level")
    fig_vlevel = vlevel_plotly(
        net,
        respect_switches=True,
        filename=None,         # Do not write to an HTML file
        auto_open=False        # Disable auto browser opening
    )
    st.plotly_chart(fig_vlevel, use_container_width=True)

    # Power flow result visualization (disable HTML export)
    st.subheader("Power Flow Results")
    fig_pf = pf_res_plotly(
        net,
        cmap="Jet",
        use_line_geo=None,
        on_map=False,
        projection=None,
        map_style="basic",
        figsize=1,
        aspectratio='auto',
        line_width=2,
        bus_size=10,
        climits_volt=(0.9, 1.1),
        climits_load=(0, 100),
        cpos_volt=1.0,
        cpos_load=1.1,
        filename=None,         # Do not write to an HTML file
        auto_open=False        # Disable auto browser opening
    )
    st.plotly_chart(fig_pf, use_container_width=True)