"""Element Inspector: filterable element tables with units and downloads."""

import streamlit as st

from simbench_app import network_analysis as na
from simbench_app import tables, utils
from simbench_app.explanations import explain
from simbench_app.i18n import tr

st.set_page_config(page_title=tr("Element Inspector"), page_icon="🔍", layout="wide")
st.header("🔍 " + tr("Element Inspector"))

net = utils.require_network()

st.markdown(tr(
    "Inspect the raw pandapower element tables of the loaded network. Filters "
    "narrow the rows; the column preset keeps tables readable. Every filtered "
    "view can be downloaded as CSV."
))

# Only offer tables that actually contain elements.
available = {attr: na.element_label(attr) for attr in na.ELEMENTS
             if len(net.get(attr, ()))}
if not available:
    st.info(tr("The network contains no element tables."))
    st.stop()

choice = st.selectbox(
    tr("Element table"), list(available),
    format_func=lambda a: tr("{label} ({n})", label=available[a],
                             n=len(net[a])))

if explain(choice):
    st.info(explain(choice))

df = net[choice].copy()

# --- filtering --------------------------------------------------------------
st.subheader(tr("Filters"))
filtered = tables.filter_dataframe(df, choice)
st.caption(tr("{n} of {total} rows match the current filters.",
               n=len(filtered), total=len(df)))

# --- column preset -----------------------------------------------------------
preset_cols = [c for c in tables.PRESETS.get(choice, []) if c in filtered.columns]
view_mode = st.radio(
    tr("Columns"), ["Essential", "All"], horizontal=True,
    format_func={"Essential": tr("Essential"), "All": tr("All")}.get,
    help=tr("The essential preset hides rarely needed parameter columns."))
shown = filtered[preset_cols] if (view_mode == "Essential" and preset_cols) \
    else filtered

st.dataframe(tables.label_with_units(shown), width="stretch")

st.download_button(
    tr("Download filtered table (CSV)"),
    data=utils.df_to_csv_bytes(filtered),
    file_name=f"{utils.loaded_code()}_{choice}_filtered.csv",
    mime="text/csv",
)

# --- corresponding results ----------------------------------------------------
res = net.get(f"res_{choice}")
if res is not None and len(res) and res.notna().any().any():
    with st.expander(tr("Power-flow results for this table (res_{choice})",
                          choice=choice)):
        res_view = res.loc[res.index.intersection(filtered.index)]
        st.dataframe(tables.label_with_units(res_view), width="stretch")
        st.download_button(
            tr("Download result table (CSV)"),
            data=utils.df_to_csv_bytes(res_view),
            file_name=f"{utils.loaded_code()}_res_{choice}.csv",
            mime="text/csv",
        )
