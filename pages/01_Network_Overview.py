"""Network Overview: scientific summary statistics with explanations."""

import streamlit as st

from simbench_app import network_analysis as na
from simbench_app import data_loading as dl, utils
from simbench_app.explanations import explain
from simbench_app.i18n import tr

st.set_page_config(page_title=tr("Network Overview"), page_icon="📊", layout="wide")
st.header("📊 " + tr("Network Overview"))

# Column headers of the analysis tables stay English in ``network_analysis``
# (stable keys for report/export); they are translated for display here.
_QVU = {"Quantity": tr("Quantity"), "Value": tr("Value"), "Unit": tr("Unit")}

net = utils.require_network()
code = utils.loaded_code()

meta = dl.describe_code(code)
st.markdown(tr("Summary of **`{code}`** — {level} grid, {kind}, "
               "scenario {scenario}.", code=code, level=meta['Grid level'],
               kind=meta['Urbanisation / type'], scenario=meta['Scenario']))

with st.expander(tr("What does this network represent?")):
    st.markdown(explain("code_structure"))
    st.markdown(explain("limitations"))

# --- element counts -----------------------------------------------------------
st.subheader(tr("Element inventory"))
counts = na.element_counts(net)
present = counts[counts["Count"] > 0]
absent = counts[counts["Count"] == 0]

c1, c2 = st.columns([2, 1])
with c1:
    st.dataframe(
        present.drop(columns="Table")
        .rename(columns={"Count": tr("Count"), "In service": tr("In service")})
        .rename_axis(tr("Element")), width="stretch")
with c2:
    if len(absent):
        st.markdown(tr("**Not present in this network:**"))
        for label in absent.index:
            st.markdown(f"- {label}")

with st.expander(tr("What do these element types mean?")):
    for key in ("bus", "line", "trafo", "load", "sgen", "ext_grid"):
        st.markdown(explain(key))

# --- voltage levels & capacities ------------------------------------------------
st.subheader(tr("Voltage levels and installed capacities"))
c1, c2 = st.columns(2)
with c1:
    st.markdown(tr("**Buses per voltage level**"))
    st.dataframe(na.buses_per_voltage_level(net).rename(columns={
        "Nominal voltage [kV]": tr("Nominal voltage [kV]"),
        "Buses": tr("Buses")}), hide_index=True, width="stretch")
with c2:
    st.markdown(tr("**Installed capacities**"))
    st.dataframe(na.capacity_summary(net).rename(columns=_QVU),
                 hide_index=True, width="stretch")

sgen_types = na.sgen_by_type(net)
if len(sgen_types):
    st.markdown(tr("**Static generation by technology**"))
    st.dataframe(sgen_types.rename(columns={
        "Units": tr("Units"), "Installed_MW": tr("Installed_MW")})
        .rename_axis(tr("Technology")), width="stretch")

cap = na.capacity_summary(net)
load_row = cap[cap["Quantity"] == tr("Total active load demand")]
gen_rows = cap[cap["Quantity"].isin([
    tr("Installed static generation (sgen)"),
    tr("Installed controllable generation (gen)")])]
if len(load_row) and len(gen_rows):
    p_load = float(load_row["Value"].iloc[0])
    p_gen = float(gen_rows["Value"].sum())
    if p_load > 0:
        ratio = p_gen / p_load
        st.markdown(tr(
            "**Generation-to-demand ratio:** installed generation covers "
            "**{ratio:.0%}** of peak active demand. Values near or above "
            "100 % indicate that reverse power flow towards the upstream grid "
            "can occur at times of high generation and low demand — a typical "
            "driver of voltage-rise problems in distribution grids.",
            ratio=ratio))

# --- branch statistics ---------------------------------------------------------
st.subheader(tr("Lines and transformers"))
c1, c2 = st.columns(2)
with c1:
    line_df = na.line_stats(net)
    if len(line_df):
        st.markdown(tr("**Line statistics**"))
        st.dataframe(line_df.rename(columns=_QVU), hide_index=True, width="stretch")
    else:
        st.info(tr("This network contains no lines."))
with c2:
    trafo_df = na.trafo_stats(net)
    if len(trafo_df):
        st.markdown(tr("**Transformer statistics**"))
        st.dataframe(trafo_df.rename(columns=_QVU), hide_index=True, width="stretch")
    else:
        st.info(tr("This network contains no 2-winding transformers."))

# --- data completeness -----------------------------------------------------------
st.subheader(tr("Data completeness and consistency"))
missing = na.missing_data_overview(net)
if len(missing):
    with st.expander(tr("Columns with missing values ({n})", n=len(missing))):
        st.dataframe(missing.rename(columns={
            "Table": tr("Table"), "Column": tr("Column"),
            "Missing values": tr("Missing values"), "Share": tr("Share")}),
            hide_index=True, width="stretch")
        st.caption(tr(
            "Many pandapower columns are optional and legitimately unset "
            "(e.g. capability limits). Missing values only matter when a "
            "parameter is required by an analysis — see the Diagnostics page."
        ))
else:
    st.success(tr("No missing values in any element table."))

for ok, text in na.consistency_checks(net):
    (st.success if ok else st.error)(("✓ " if ok else "✗ ") + text)

with st.expander(tr("How to read SimBench bus names")):
    st.markdown(explain("bus_naming"))
