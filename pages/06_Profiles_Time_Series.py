"""Profiles & Time Series: SimBench profile inspection and a capped TS power flow."""

import streamlit as st

from simbench_app import config, profiles as prof, utils
from simbench_app.explanations import explain
from simbench_app.i18n import tr
from simbench_app.i18n import tr as trc  # tr() of catalogued constants

st.set_page_config(page_title=tr("Profiles & Time Series"), page_icon="📈",
                   layout="wide")
st.header("📈 " + tr("Profiles & Time Series"))

net = utils.require_network()

st.markdown(explain("profiles"))

groups = prof.available_groups(net)
if not groups:
    st.info(tr(
        "This network carries no time-series profiles. SimBench networks "
        "normally ship a full year of 15-minute profiles; if you loaded a "
        "modified or exported network, the profile data may have been "
        "stripped. Load an original SimBench code on the Home page to "
        "explore time series."
    ))
    st.stop()

# --- profile inspection ------------------------------------------------------
st.subheader(tr("Inspect profiles"))

group = st.selectbox(tr("Profile group"), list(groups),
                     format_func=lambda g: trc(prof.PROFILE_GROUPS[g])
                     if g in prof.PROFILE_GROUPS else g)
df = prof.profile_frame(net, group)

cols = list(df.columns)
default_cols = [c for c in cols if str(c).endswith("_pload")][:3] or cols[:3]
selected = st.multiselect(tr("Profiles"), cols, default=default_cols)

c1, c2 = st.columns(2)
with c1:
    start_day = st.slider(tr("Start day of year"), 1, max(1, len(df) // 96), 1)
with c2:
    n_days = st.slider(tr("Days to display"), 1, 28, 7)

if selected:
    window = df[selected].iloc[(start_day - 1) * 96:(start_day - 1 + n_days) * 96]
    st.line_chart(window)
    st.caption(tr(
        "Normalised profile values (1.0 = rated power of the referencing "
        "element). 96 steps per day at 15-minute resolution."
    ))
    st.markdown(tr("**Statistics over the full year**"))
    st.dataframe(prof.profile_statistics(df[selected]).rename(columns={
        "Peak": tr("Peak"), "Minimum": tr("Minimum"), "Mean": tr("Mean"),
        "Energy [h·p.u.]": tr("Energy [h·p.u.]")}), width="stretch")
else:
    st.info(tr("Select at least one profile to plot."))

usage = prof.profile_usage(net)
if len(usage):
    with st.expander(tr("Which elements use which profile?")):
        st.dataframe(usage.rename(columns={
            "Element table": tr("Element table"), "Profile": tr("Profile"),
            "Elements": tr("Elements")}), hide_index=True, width="stretch")

# --- annual analysis ------------------------------------------------------------
st.subheader(tr("Annual analysis (full SimBench year)"))
st.markdown(tr(
    "Runs a power flow for every simulated time step of the SimBench year "
    "(reference year 2016) and answers: **when does it get tight, how often, "
    "and where?** — duration curves, a day × hour heat map, the critical "
    "days and the elements that violate limits most often."
))
with st.expander(tr("How to read an annual analysis")):
    st.markdown(explain("annual"))

thresholds = utils.threshold_controls()
# display names of result columns that other code indexes by (rename on display only)
COLUMN_LABELS = {
    "max_line_loading": "Max. line loading [%]",
    "max_trafo_loading": "Max. transformer loading [%]",
    "max_loading_percent": "Max. loading [%]",
    "max_vm_pu": "Max. voltage [p.u.]",
    "min_vm_pu": "Min. voltage [p.u.]",
    "peak_import_mw": "Peak import [MW]",
    "peak_export_mw": "Peak export [MW]",
    "violation_hours": "Violation hours [h]",
    "hours_above_limit": "Hours above limit [h]",
    "hours_outside": "Hours outside band [h]",
    "name": "Name",
    "vn_kv": "Nominal voltage [kV]",
    "total_load_mw": "Load [MW]",
    "total_sgen_mw": "Generation [MW]",
    "ext_grid_mw": "Grid exchange [MW] (>0 import)",
    "max_line_loading_percent": "Max. line loading [%]",
}


def _cols(df):
    """Rename result columns to the active language for display."""
    return df.rename(columns={c: trc(COLUMN_LABELS[c]) for c in df.columns
                              if c in COLUMN_LABELS})


horizon_steps = len(prof.profile_timestamps(net))
RESOLUTIONS = {1: "15 min (full resolution)", 2: "30 min", 4: "1 h (recommended)",
               8: "2 h", 16: "4 h"}
if len(net.bus) > config.ANNUAL_MAX_BUSES:
    st.warning(tr(
        "The loaded network has {n} buses; the annual analysis is "
        "limited to networks up to {max_n} buses on shared "
        "hosting. Use pandapower's `timeseries` module locally instead.",
        n=len(net.bus), max_n=config.ANNUAL_MAX_BUSES
    ))
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        stride = st.selectbox(tr("Time resolution"), list(RESOLUTIONS), index=2,
                              format_func=lambda k: trc(RESOLUTIONS[k]))
    n_sim = -(-horizon_steps // stride)
    with c2:
        st.metric(tr("Power flows to compute"), f"{n_sim:,}")
    with c3:
        st.metric(tr("Estimated runtime"),
                  tr("~{m:.1f} min", m=n_sim * 0.01 / 60),
                  help=tr("Roughly 10 ms per step for a small MV network."))
    too_many = n_sim > config.ANNUAL_MAX_STEPS
    if too_many:
        st.warning(tr("More than {n:,} steps are not "
                      "offered here — choose a coarser resolution.",
                      n=config.ANNUAL_MAX_STEPS))
    if st.button(tr("Run annual analysis"), type="primary", disabled=too_many):
        bar = st.progress(0.0, text=tr("Running annual time series …"))
        res = prof.run_annual_timeseries(
            net, thresholds, stride=int(stride),
            progress=lambda f: bar.progress(f))
        bar.empty()
        st.session_state["annual_result"] = (utils.loaded_code(), res)

    saved = st.session_state.get("annual_result")
    if saved and saved[0] == utils.loaded_code() and saved[1] is not None:
        import plotly.express as px

        res = saved[1]
        sysdf, h = res.system, res.step_hours
        ok = sysdf.dropna(subset=["min_vm_pu"])
        if res.n_failed:
            st.warning(tr("{failed} of {total} steps did not converge "
                          "and are excluded.",
                          failed=res.n_failed, total=len(sysdf)))
        th = res.thresholds
        hours_viol = float((ok["n_violations"] > 0).sum() * h)
        imp = float(ok["ext_grid_mw"].clip(lower=0).sum() * h)
        exp = float(-ok["ext_grid_mw"].clip(upper=0).sum() * h)
        k = st.columns(5)
        k[0].metric(tr("Hours with violations"), f"{hours_viol:,.0f} h",
                    tr("{p:.1f} % of the year",
                       p=hours_viol / (len(sysdf) * h) * 100),
                    delta_color="off")
        k[1].metric(tr("Peak line loading"), f"{ok['max_line_loading'].max():.0f} %")
        k[2].metric(tr("Voltage range"), f"{ok['min_vm_pu'].min():.3f} – "
                    f"{ok['max_vm_pu'].max():.3f} p.u.")
        k[3].metric(tr("Grid import"), f"{imp:,.0f} MWh")
        k[4].metric(tr("Grid export (feed-back)"), f"{exp:,.0f} MWh")

        METRICS = {
            "max_line_loading": ("Max. line loading [%]", th["max_loading_percent"]),
            "max_trafo_loading": ("Max. transformer loading [%]", th["max_loading_percent"]),
            "max_vm_pu": ("Max. voltage [p.u.]", th["vm_max_pu"]),
            "min_vm_pu": ("Min. voltage [p.u.]", th["vm_min_pu"]),
            "ext_grid_mw": ("Grid exchange [MW] (>0 import)", None),
        }
        metric = st.selectbox(tr("Quantity"), list(METRICS),
                              format_func=lambda m: trc(METRICS[m][0]))
        label, limit = trc(METRICS[metric][0]), METRICS[metric][1]
        t1, t2, t3 = st.tabs([tr("Duration curve"), tr("Heat map (day × hour)"),
                              tr("Critical days")])
        with t1:
            # highest values first; for min. voltage the lowest values first
            curve = ok[metric].sort_values(ascending=(metric == "min_vm_pu")) \
                .reset_index(drop=True)
            dur = (curve.index.to_series() * h)
            fig = px.line(x=dur, y=curve.values,
                          labels={"x": tr("Hours per year"), "y": label})
            if limit is not None:
                fig.add_hline(y=limit, line_dash="dash", line_color="red")
            fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, width="stretch")
            st.caption(tr("Values sorted from highest (left) to lowest; the "
                          "x-axis shows for how many hours per year a value is "
                          "reached or exceeded (for min. voltage: the lowest "
                          "values come first). Dashed line = configured limit."))
        with t2:
            grid = ok[metric].groupby([ok.index.dayofyear, ok.index.hour]).max() \
                .unstack()
            fig = px.imshow(grid.T, aspect="auto", origin="lower",
                            labels={"x": tr("Day of year"), "y": tr("Hour of day"),
                                    "color": label},
                            color_continuous_scale="RdBu_r"
                            if metric == "ext_grid_mw" else "Viridis")
            fig.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig, width="stretch")
            st.caption(tr("Seasonal and daily patterns: PV peaks around noon in "
                          "summer, load peaks in the evening in winter."))
        with t3:
            daily = ok.groupby(ok.index.date).agg(
                max_line_loading=("max_line_loading", "max"),
                max_vm_pu=("max_vm_pu", "max"), min_vm_pu=("min_vm_pu", "min"),
                peak_import_mw=("ext_grid_mw", "max"),
                peak_export_mw=("ext_grid_mw", "min"),
                violation_hours=("n_violations", lambda v: float((v > 0).sum() * h)))
            c1, c2, c3 = st.columns(3)
            c1.markdown(tr("**Highest line loading**"))
            c1.dataframe(_cols(daily.nlargest(5, "max_line_loading")[["max_line_loading"]].round(1)))
            c2.markdown(tr("**Highest import**"))
            c2.dataframe(_cols(daily.nlargest(5, "peak_import_mw")[["peak_import_mw"]].round(2)))
            c3.markdown(tr("**Highest feed-back (export)**"))
            c3.dataframe(_cols(daily.nsmallest(5, "peak_export_mw")[["peak_export_mw"]].round(2)))
            st.markdown(tr("**Days with the most violation hours**"))
            st.dataframe(_cols(daily.nlargest(5, "violation_hours")[["violation_hours"]]))

        st.markdown(tr("**Critical elements**"))
        e1, e2, e3 = st.columns(3)
        e1.markdown(tr("Lines"))
        e1.dataframe(_cols(res.lines.sort_values(
            ["hours_above_limit", "max_loading_percent"],
            ascending=False).head(10).round(1)))
        e2.markdown(tr("Transformers"))
        e2.dataframe(_cols(res.trafos.sort_values(
            ["hours_above_limit", "max_loading_percent"],
            ascending=False).head(10).round(1)))
        e3.markdown(tr("Buses (hours outside voltage band)"))
        bus_hours = res.buses.assign(
            hours_outside=res.buses["hours_undervoltage"] + res.buses["hours_overvoltage"])
        e3.dataframe(_cols(bus_hours.sort_values("hours_outside", ascending=False)
                           .head(10)[["name", "vn_kv", "hours_outside"]].round(1)))
        st.download_button(tr("Download annual results (CSV)"),
                           utils.df_to_csv_bytes(sysdf.reset_index()),
                           file_name=f"{utils.loaded_code()}_annual.csv",
                           mime="text/csv")
        st.caption(tr("Solver backend: {backend}; every {h:g} h "
                      "simulated; limits as set in the sidebar when the run started.",
                      backend=res.backend, h=res.step_hours))

# --- demonstrative time-series power flow ----------------------------------------
st.subheader(tr("Demonstrative time-series power flow"))
st.markdown(tr(
    "Runs one AC power flow per time step on a **copy** of the network, with "
    "loads and generation set to their absolute profile values. This "
    "demonstrates how voltages and loadings evolve over the day — the "
    "static snapshot rarely shows the binding stress hours."
))

if len(net.bus) > config.TIMESERIES_MAX_BUSES:
    st.warning(tr(
        "The loaded network has {n} buses; the demonstration is "
        "limited to networks below {max_n} buses to "
        "stay responsive on shared hosting. Use pandapower's `timeseries` "
        "module locally for full studies.",
        n=len(net.bus), max_n=config.TIMESERIES_MAX_BUSES
    ))
    st.stop()

c1, c2 = st.columns(2)
with c1:
    ts_day = st.number_input(tr("Day of year"), 1, max(1, len(prof.profile_frame(
        net, list(groups)[0])) // 96), 1)
with c2:
    ts_steps = st.slider(tr("Time steps (15 min each)"), 4, config.TIMESERIES_MAX_STEPS,
                         24, step=4)

if st.button(tr("Run time-series power flow"), type="primary"):
    bar = st.progress(0.0, text=tr("Running power flows …"))
    ts = prof.run_profile_powerflow(
        net, n_steps=int(ts_steps), start_step=(int(ts_day) - 1) * 96,
        progress_callback=lambda frac: bar.progress(frac))
    bar.empty()
    st.session_state["ts_result"] = ts

ts = st.session_state.get("ts_result")
if ts is not None and len(ts):
    n_failed = int((~ts["converged"]).sum())
    if n_failed:
        st.warning(tr("{failed} of {total} steps did not converge and are "
                      "omitted from the plots.", failed=n_failed, total=len(ts)))
    ok = ts[ts["converged"]]
    if len(ok):
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(tr("**System power [MW]**"))
            st.line_chart(_cols(ok[["total_load_mw", "total_sgen_mw", "ext_grid_mw"]]))
            st.caption(tr("Negative external-grid power means the network feeds "
                          "back into the upstream grid."))
        with c2:
            st.markdown(tr("**Voltage envelope [p.u.] / max. line loading [%]**"))
            st.line_chart(_cols(ok[["min_vm_pu", "max_vm_pu"]]))
            st.line_chart(_cols(ok[["max_line_loading"]]))
        st.dataframe(_cols(ok.describe().loc[["min", "mean", "max"]].round(4))
                     .rename(index={"min": tr("Minimum"), "mean": tr("Mean"),
                                    "max": tr("Maximum")}),
                     width="stretch")
        st.download_button(
            tr("Download step results (CSV)"), data=utils.df_to_csv_bytes(ts),
            file_name=f"{utils.loaded_code()}_timeseries.csv", mime="text/csv")
