import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inspect Data")

st.header("🔍 Inspect Raw Data")

if 'net' not in st.session_state:
    st.warning("Please load a network on the Home page first.")
else:
    net = st.session_state.net

    # Show basic bus table
    st.subheader("Buses")
    st.dataframe(pd.DataFrame(net.bus))

    # Show line table
    st.subheader("Lines")
    st.dataframe(pd.DataFrame(net.line))

    # Profiles (time series) if available
    if hasattr(net, 'profiles') and 'LoadProfile' in net.profiles:
        st.subheader("Load Profiles (first 24h)")
        st.line_chart(net.profiles['LoadProfile'].iloc[:24])
