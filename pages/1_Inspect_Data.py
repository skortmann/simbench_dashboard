import streamlit as st
import pandas as pd

st.set_page_config(page_title="Inspect Data")

st.header("🔍 Inspect Raw Data")

if 'net' not in st.session_state:
    st.warning("Please load a network on the Home page first.")
else:
    net = st.session_state.net

    st.write(net.keys())

    # Define relevant components
    # Be aware that these are only used to give summarized information on which components are not used
    components = {
        "Buses": net.bus,
        "Lines": net.line,
        "Transformers": net.trafo,
        "Loads": net.load,
        "Static Generators": net.sgen,
        "Generators": net.gen,
        "Storage Systems": net.storage,
        "External Grids": net.ext_grid,
        "Switches": net.switch,
    }

    # Identify empty (missing) components
    empty_components = [name for name, df in components.items() if df.empty]

    # Display missing components
    if empty_components:
        st.subheader("Missing Components")
        for name in empty_components:
            st.write(f"❌ {name}")

    ##Display the df of all elements and add analasys and explaination to it
    # Buses
    if not net.bus.empty:
        st.subheader("Buses")

        with st.expander("Show bus data and analysis"):
            # Total number of buses
            st.write(f"**Total buses:** {len(net.bus)}")

            # Voltage levels (unique)
            st.write("**Voltage levels (kV):**", net.bus["vn_kv"].unique())

            # Bus types count
            st.write("**Bus types:**", "b=busbar, m=muff, n=node", net.bus["type"].value_counts())

            # Number of buses per voltage level
            st.write("**Buses per voltage level:**")
            st.dataframe(net.bus["vn_kv"].value_counts().rename_axis("Voltage Level (kV)").reset_index(name="Bus Count"))

        with st.expander("Show explanation of the bus name"):
            st.markdown("""
                SimBench uses structured bus names to identify the location and role of each bus in the network.  
                Here's how to read the naming convention:

                - **Voltage Level Prefix:**
                    - `HV` = High Voltage
                    - `MV` = Medium Voltage
                    - `LV` = Low Voltage

                - **Grid Area Identifier:**
                    - The number following the voltage level (e.g. `HV1`, `MV2`) indicates a specific grid area or region.

                - **Feeder/Subnetwork Code:**
                    - A dot and number (e.g. `.101`) usually indicate a subnetwork or feeder within that area.  
                      Example: `MV2.101` means feeder 101 in MV area 2.

                - **Bus Identifier:**
                    - `"Bus X"` = The X-th bus in that feeder or area
                    - `"busbar1.1"` or similar = Internal busbars at substations (used for detailed modeling)

                #### Examples:
                - `HV1 Bus 19`: Bus number 19 in High Voltage grid area 1  
                - `MV2.101 Bus 116`: Bus number 116 in Medium Voltage feeder 101 of area 2  
                - `MV2.101 busbar1.1`: Internal busbar node (e.g., transformer connection point)
                """)

        # Full bus table
        st.dataframe(net.bus)

    # Lines
    if not net.line.empty:
        st.subheader("Lines")
        st.write(f"Number of lines: {len(net.line)}")
        st.dataframe(net.line)

    # Transformers
    if not net.trafo.empty:
        st.subheader("Transformers")
        st.dataframe(net.trafo)

    # Loads
    if not net.load.empty:
        st.subheader("Loads")
        st.dataframe(net.load)

    # Static Generators
    if not net.sgen.empty:
        st.subheader("Static Generators")
        st.dataframe(net.sgen)

    # Generators
    if not net.gen.empty:
        st.subheader("Generators")
        st.dataframe(net.gen)

    # Storage Systems
    if not net.storage.empty:
        st.subheader("Storage Systems")
        st.dataframe(net.storage)

    # External Grids
    if not net.ext_grid.empty:
        st.subheader("External Grids")
        st.dataframe(net.ext_grid)

    # Switches
    if not net.switch.empty:
        st.subheader("Switches")
        st.dataframe(net.switch)

    # Profiles (time series) if available
    if hasattr(net, 'profiles') and 'LoadProfile' in net.profiles:
        st.subheader("Load Profiles (first 24h)")
        st.line_chart(net.profiles['LoadProfile'].iloc[:24])
