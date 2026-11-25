"""Export & Report: downloadable tables, network files and a Markdown report."""

import streamlit as st

from simbench_app import config, network_analysis as na, powerflow as pf
from simbench_app import report, utils
from simbench_app.i18n import tr
from simbench_app.i18n import tr as trc  # tr() of catalogued constants

st.set_page_config(page_title=tr("Export & Report"), page_icon="📤", layout="wide")
st.header("📤 " + tr("Export & Report"))

net = utils.require_network()
code = utils.loaded_code()
pf_result = st.session_state.get(config.KEY_PF_RESULT)
thresholds = utils.get_thresholds()
modlog = st.session_state.get(config.KEY_MODLOG, [])

st.markdown(tr(
    "All exports are generated in memory from the current session network — "
    "including any modifications — and carry the SimBench code in the "
    "filename for traceability."
))

# --- summary tables ----------------------------------------------------------
st.subheader(tr("Network summary"))
c1, c2 = st.columns(2)
with c1:
    st.download_button(
        tr("Element counts (CSV)"),
        data=utils.df_to_csv_bytes(na.element_counts(net)),
        file_name=f"{code}_element_counts.csv", mime="text/csv")
    st.download_button(
        tr("Installed capacities (CSV)"),
        data=utils.df_to_csv_bytes(na.capacity_summary(net)),
        file_name=f"{code}_capacities.csv", mime="text/csv")
with c2:
    st.download_button(
        tr("Buses per voltage level (CSV)"),
        data=utils.df_to_csv_bytes(na.buses_per_voltage_level(net)),
        file_name=f"{code}_voltage_levels.csv", mime="text/csv")
    st.download_button(
        tr("Missing-data overview (CSV)"),
        data=utils.df_to_csv_bytes(na.missing_data_overview(net)),
        file_name=f"{code}_missing_data.csv", mime="text/csv")

# --- element & result tables -------------------------------------------------------
st.subheader(tr("Element and result tables"))
available = [attr for attr in na.ELEMENTS if len(net.get(attr, ()))]
table = st.selectbox(tr("Table"), available,
                     format_func=lambda a: f"{trc(na.ELEMENTS[a])} ({len(net[a])})")
c1, c2 = st.columns(2)
with c1:
    st.download_button(
        tr("Download {table} table (CSV)", table=table),
        data=utils.df_to_csv_bytes(net[table]),
        file_name=f"{code}_{table}.csv", mime="text/csv")
with c2:
    res = net.get(f"res_{table}")
    if pf.has_results(net) and res is not None and len(res):
        st.download_button(
            tr("Download res_{table} results (CSV)", table=table),
            data=utils.df_to_csv_bytes(res),
            file_name=f"{code}_res_{table}.csv", mime="text/csv")
    else:
        st.caption(tr("Result table available after a converged power flow."))

# --- whole network -------------------------------------------------------------
st.subheader(tr("Complete network file"))
st.markdown(tr(
    "**JSON** is pandapower's recommended, version-stable exchange format "
    "(`pandapower.from_json`). Pickle is Python-specific; Excel is convenient "
    "for manual inspection but loses some type information."
))
fmt = st.radio(tr("Format"), ["json", "pickle", "excel"], horizontal=True)
ext = {"json": "json", "pickle": "p", "excel": "xlsx"}[fmt]
mime = {"json": "application/json", "pickle": "application/octet-stream",
        "excel": "application/vnd.openxmlformats-officedocument"
                 ".spreadsheetml.sheet"}[fmt]
try:
    payload = utils.net_to_bytes(net, fmt)
    st.download_button(tr("Download network ({fmt})", fmt=fmt), data=payload,
                       file_name=f"{code}.{ext}", mime=mime)
except Exception as exc:
    st.error(tr("Serialising the network as {fmt} failed: {exc}", fmt=fmt, exc=exc))

# --- markdown report ---------------------------------------------------------------
st.subheader(tr("Analysis report (Markdown)"))
st.markdown(tr(
    "A self-contained report with structure statistics, power-flow summary, "
    "violations and full reproducibility information (package versions, "
    "SimBench code, solver settings, applied modifications, timestamp)."
))
md = report.build_markdown_report(net, code, pf_result, thresholds,
                                  modifications=modlog)
st.download_button(tr("Download report (Markdown)"), data=md.encode("utf-8"),
                   file_name=f"{code}_report.md", mime="text/markdown")
with st.expander(tr("Preview report")):
    st.markdown(md)

# --- environment -------------------------------------------------------------------
with st.expander(tr("Software environment (reproducibility)")):
    env = utils.environment_info()
    st.table({tr("Package"): list(env.keys()), tr("Version"): list(env.values())})
