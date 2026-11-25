"""Topology Visualization: interactive network map with result overlays."""

import streamlit as st

from simbench_app import config, powerflow as pf, tables, utils
from simbench_app import visualization as viz
from simbench_app.explanations import explain
from simbench_app.i18n import tr

st.set_page_config(page_title=tr("Topology Visualization"), page_icon="🗺️",
                   layout="wide")
st.header("🗺️ " + tr("Topology Visualization"))

net = utils.require_network()
has_pf = pf.has_results(net)

coords, source = viz.bus_coordinates(net)
if source == "geographic":
    st.markdown(tr("Bus positions use the **geographic coordinates** shipped "
                   "with the SimBench dataset (schematic, not surveyed)."))
else:
    st.markdown(tr("This network carries no geodata — bus positions are a "
                   "**computed topological layout** (force-directed, "
                   "deterministic). Distances on screen carry no physical "
                   "meaning."))

# --- display options -----------------------------------------------------------
c1, c2, c3 = st.columns(3)
with c1:
    bus_modes = {"voltage_level": tr("Nominal voltage level"),
                 "uniform": tr("Uniform")}
    if has_pf:
        bus_modes["vm_pu"] = tr("Voltage magnitude (vm, p.u.)")
    bus_color = st.selectbox(tr("Colour buses by"), list(bus_modes),
                             format_func=bus_modes.get)
with c2:
    line_modes = {"uniform": tr("Uniform")}
    if has_pf:
        line_modes["loading"] = tr("Loading (% of thermal limit)")
    line_color = st.selectbox(tr("Colour lines by"), list(line_modes),
                              format_func=line_modes.get)
with c3:
    show_injections = st.checkbox(
        tr("Show loads / generation / storage"), value=False,
        help=tr("Overlays markers at the connection buses of injections."))

if not has_pf:
    st.caption(tr("Result-based colouring (voltage magnitude, line loading) "
                  "becomes available after running a power flow on the "
                  "*Power Flow Analysis* page."))

large = len(net.line) > config.LARGE_NET_THRESHOLD
if large:
    st.info(tr("Large network ({n} lines): rendering switches to "
               "WebGL and per-line hover labels are disabled to stay "
               "responsive.", n=len(net.line)))

fig = viz.network_figure(net, coords, bus_color=bus_color,
                         line_color=line_color,
                         show_injections=show_injections)
st.plotly_chart(fig, width="stretch")

with st.expander(tr("How to read this figure")):
    st.markdown(tr(
        "- **Dots** are buses (electrical nodes); **solid grey or coloured "
        "segments** are lines; **dotted dark segments** are transformers "
        "coupling two voltage levels.\n"
        "- Hover over buses (and, for moderate network sizes, line midpoints) "
        "for names, nominal voltages and — after a power flow — result "
        "values.\n"
        "- Line colours follow the loading bins green < 50 %, yellow 50–80 %, "
        "orange 80–100 %, red > 100 % of the thermal rating."
    ))
    st.markdown(explain("vm_pu"))

# --- neighbourhood inspector ----------------------------------------------------
st.subheader(tr("Bus neighbourhood"))
st.markdown(tr("Select a bus to list every element electrically attached "
                "to it."))

options = list(net.bus.index)
bus_sel = st.selectbox(
    tr("Bus"), options,
    format_func=lambda b: f"{b} — {net.bus.at[b, 'name']} "
                          f"({net.bus.at[b, 'vn_kv']:g} kV)")

neighborhood = viz.bus_neighborhood(net, bus_sel)
if not neighborhood:
    st.info(tr("No elements are attached to this bus."))
else:
    labels = {"line": tr("Lines"), "trafo": tr("Transformers"),
              "load": tr("Loads"), "sgen": tr("Static generators"),
              "gen": tr("Generators"), "storage": tr("Storage"),
              "ext_grid": tr("External grids"), "switch": tr("Switches")}
    for table, df in neighborhood.items():
        st.markdown(tr("**{label} ({n})**",
                    label=labels.get(table, table), n=len(df)))
        preset = [c for c in tables.PRESETS.get(table, []) if c in df.columns]
        st.dataframe(tables.label_with_units(df[preset] if preset else df),
                     width="stretch")
