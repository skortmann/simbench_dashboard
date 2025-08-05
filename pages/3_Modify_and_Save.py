import streamlit as st
import pandapower as pp
from pandapower import to_pickle, from_pickle, to_json, from_json, to_excel, from_excel

st.set_page_config(page_title="Modify & Save", layout="wide")
st.header("⚙️ Modify & Export Network")

if 'net' not in st.session_state:
    st.warning("Load a network on the Home page first.")
else:
    net = st.session_state.net

    # Example modification: scale all loads
    st.subheader("Modify Loads")
    scale = st.slider("Load scale factor", 0.5, 2.0, 1.0)
    if st.button("Apply scaling"):
        net.load['p_mw'] *= scale
        st.success(f"Scaled loads by {scale}×")

    # Export options
    st.subheader("Save Network")
    fmt = st.selectbox("Export format", ["Pickle (.p)", "JSON (.json)", "Excel (.xlsx)"])
    fname = st.text_input("Filename (with extension)", value=f"network{fmt.split()[1].strip("()")}")

    if st.button("Export"):
        try:
            if fmt.startswith("Pickle"):
                to_pickle(net, fname)
            elif fmt.startswith("JSON"):
                # store_index_names=False by default
                to_json(net, fname)
            else:
                # include_empty_tables=False, include_results=True by default
                to_excel(net, fname)
            st.success(f"Network saved to {fname}")
            with open(fname, "rb") as f:
                st.download_button("Download file", data=f, file_name=fname)
        except Exception as e:
            st.error(f"Error saving network: {e}")