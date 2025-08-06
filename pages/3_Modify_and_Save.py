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

    # Add a storage to the system
    st.subheader("Add Storage")

    with st.form("test"):
        titel = st.text_input("Name", "Added_storage_1")
        power = st.number_input("Power (MW)", value= 1.0, min_value=0.0, step=0.1)
        capacity = st.number_input("Capacity (MWh)", value = 1.0, min_value=0.0, step=0.1)
        bus_connection = st.number_input("Connect to Bus (Index)", step=1)

        submitted = st.form_submit_button("Add storage")

        if submitted:
            try:
                pp.create_storage(
                    net=st.session_state.net,
                    bus=int(bus_connection),
                    p_mw=float(power),
                    max_e_mwh=float(capacity),
                    name=titel
                )
                st.success(f"Storage '{titel}' was successfully added to the network.")
            except Exception as e:
                st.error(f"Error while adding the storage '{titel}': {e}")





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