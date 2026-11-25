"""Power Flow Analysis: solver options, execution and result interpretation."""

import streamlit as st

from simbench_app import config, powerflow as pf, tables, utils
from simbench_app.explanations import explain
from simbench_app.i18n import tr
from simbench_app.utils import tr_const

st.set_page_config(page_title=tr("Power Flow Analysis"), page_icon="⚡",
                   layout="wide")
st.header("⚡ " + tr("Power Flow Analysis"))

def _translate_cols(df):
    """Translate the (stable, English) column headers of a summary table."""
    return df.rename(columns={c: tr_const(c) for c in df.columns
                              if c in ("Quantity", "Value", "Unit", "Component")})


net = utils.require_network()
thresholds = utils.threshold_controls()

st.markdown(tr(
    "Compute the static AC operating point of the loaded network. The solver "
    "determines all bus voltages and branch flows from the specified loads, "
    "generation and the slack (external grid)."
))
with st.expander(tr("Why convergence matters")):
    st.markdown(explain("convergence"))

# --- solver options ---------------------------------------------------------------
st.subheader(tr("Solver options"))
c0, c1, c2, c3, c4 = st.columns(5)
with c0:
    backend = st.selectbox(tr("Solver backend"), list(pf.BACKENDS),
                           format_func=lambda k: tr_const(pf.BACKENDS[k]),
                           help=tr(
        "lightsim2grid runs Newton-Raphson in C++. Unsupported cases "
        "(other algorithms, voltage-dependent loads, ...) fall back to "
        "pandapower automatically."))
with c1:
    algorithm = st.selectbox(tr("Algorithm"), list(pf.ALGORITHMS),
                             format_func=lambda k: tr_const(pf.ALGORITHMS[k]))
with c2:
    init = st.selectbox(tr("Initialisation"), pf.INIT_MODES, help=tr(
        "'auto' picks a suitable start vector; 'dc' starts from a DC power "
        "flow; 'results' continues from previous results (warm start)."))
with c3:
    enforce_q = st.checkbox(tr("Enforce generator Q limits"), value=False,
                            help=tr(
        "Converts generators to PQ nodes when their reactive-power limits "
        "are hit, as in real operation."))
with c4:
    max_iter = st.number_input(tr("Max. iterations (0 = auto)"), 0, 100, 0)

if st.button(tr("Run power flow"), type="primary"):
    options = dict(algorithm=algorithm, init=init, enforce_q_lims=enforce_q,
                   max_iteration=int(max_iter) if max_iter else "auto",
                   backend=backend)
    result = pf.run_power_flow(net, **options)
    result.code = utils.loaded_code()
    st.session_state[config.KEY_PF_RESULT] = result

result = st.session_state.get(config.KEY_PF_RESULT)
if result is None:
    st.info(tr("No power flow has been run for this network yet."))
    st.stop()

# --- convergence status -----------------------------------------------------------
if result.converged:
    st.success(tr(
        "Power flow **converged** in {runtime:.3f} s "
        "({algorithm}, backend: {backend}, run at {timestamp}).",
        runtime=result.runtime_s,
        algorithm=tr_const(pf.ALGORITHMS.get(result.options['algorithm'], '?')),
        backend=result.backend, timestamp=result.timestamp))
    if result.backend_note:
        st.info(tr("Fell back to pandapower: {note}",
                   note=result.backend_note))
else:
    st.error(tr(
        "Power flow **did not converge**. Solver message: {error}\n\n"
        "Typical causes: an infeasible operating point (overloaded feeder, "
        "voltage collapse), isolated subnetworks without slack, or "
        "inconsistent element data. Check the *Diagnostics* page; the result "
        "tables below are not meaningful.",
        error=result.error
    ))
    st.stop()

if not pf.has_results(net):
    st.warning(tr("The result tables are empty — re-run the power flow "
                  "(the network may have been reloaded or modified)."))
    st.stop()

# --- key results ----------------------------------------------------------------
st.subheader(tr("Voltage profile"))
c1, c2 = st.columns([1, 2])
with c1:
    st.dataframe(pf.voltage_summary(net), width="stretch")
with c2:
    vm = net.res_bus["vm_pu"].dropna()
    import plotly.express as px
    fig = px.histogram(vm, nbins=40,
                       labels={"value": tr("Voltage magnitude [p.u.]")})
    fig.add_vline(x=thresholds["vm_min_pu"], line_dash="dash", line_color="red")
    fig.add_vline(x=thresholds["vm_max_pu"], line_dash="dash", line_color="red")
    fig.update_layout(showlegend=False, height=260,
                      margin=dict(l=10, r=10, t=10, b=10),
                      yaxis_title=tr("Buses"))
    st.plotly_chart(fig, width="stretch")
with st.expander(tr("What does voltage in p.u. mean?")):
    st.markdown(explain("vm_pu"))
with st.expander(tr("Where does the voltage band come from?")):
    st.markdown(explain("voltage_band"))

st.subheader(tr("Voltage rise caused by generation"))
if len(net.sgen) == 0:
    st.info(tr("This network has no static generators (sgen)."))
elif st.checkbox(tr("Compute voltage rise with vs. without generation"),
                 help=tr("Runs one additional power flow with all sgen "
                         "switched off.")):
    rise = pf.der_voltage_rise(net, backend=backend)
    if rise.empty:
        st.warning(tr("Not available: no active generation or a run did not "
                      "converge."))
    else:
        limit = thresholds["der_rise_percent"]
        by_level = (rise.groupby("vn_kv")["delta_u_percent"]
                    .agg(["min", "mean", "max"]).round(2)
                    .rename(columns={"min": tr("Min [%]"), "mean": tr("Mean [%]"),
                                     "max": tr("Max [%]")})
                    .rename_axis(tr("Voltage level [kV]")).sort_index(ascending=False))
        c1, c2 = st.columns([1, 2])
        c1.dataframe(by_level, width="stretch")
        n_over = int((rise["delta_u_percent"] > limit).sum())
        (c2.error if n_over else c2.success)(
            tr("{n} bus(es) exceed the limit of {limit} % voltage rise.",
               n=n_over, limit=limit)
            if n_over else tr("All buses stay within the {limit} % limit.",
                              limit=limit))
        c2.dataframe(rise[rise["delta_u_percent"] > limit]
                     .sort_values("delta_u_percent", ascending=False).round(4),
                     width="stretch")
        with st.expander(tr("How to read this")):
            st.markdown(explain("der_rise"))

st.subheader(tr("Branch loading"))
c1, c2 = st.columns(2)
with c1:
    st.markdown("**" + tr("Lines") + "**")
    line_sum = pf.loading_summary(net, "line")
    if len(line_sum):
        st.dataframe(_translate_cols(line_sum), hide_index=True,
                     width="stretch")
    else:
        st.info(tr("No line results."))
with c2:
    st.markdown("**" + tr("Transformers") + "**")
    trafo_sum = pf.loading_summary(net, "trafo")
    if len(trafo_sum):
        st.dataframe(_translate_cols(trafo_sum), hide_index=True,
                     width="stretch")
    else:
        st.info(tr("No transformer results."))
with st.expander(tr("What does loading percent mean?")):
    st.markdown(explain("loading"))

st.subheader(tr("Power balance"))
balance = pf.power_balance(net)
st.dataframe(_translate_cols(balance), hide_index=True, width="stretch")
with st.expander(tr("How to read the power balance")):
    st.markdown(explain("power_balance"))

# --- violations -------------------------------------------------------------------
st.subheader(tr("Limit violations"))
st.markdown(tr(
    "Assessed against the sidebar thresholds: voltage band "
    "**[{vm_min}, {vm_max}] p.u.**, "
    "maximum loading **{max_loading} %**.",
    vm_min=thresholds['vm_min_pu'], vm_max=thresholds['vm_max_pu'],
    max_loading=thresholds['max_loading_percent'],
))
viol = pf.violations(net, thresholds["vm_min_pu"], thresholds["vm_max_pu"],
                     thresholds["max_loading_percent"])
if pf.n_violations(viol) == 0:
    st.success(tr("No violations — all voltages and loadings are within the "
                  "configured limits."))
else:
    labels = {
        "undervoltage_buses": tr("Undervoltage buses"),
        "overvoltage_buses": tr("Overvoltage buses"),
        "overloaded_lines": tr("Overloaded lines"),
        "overloaded_trafos": tr("Overloaded transformers"),
    }
    for key, df in viol.items():
        if len(df):
            st.markdown(f"**{labels[key]} ({len(df)})**")
            st.dataframe(tables.label_with_units(df), width="stretch")
    with st.expander(tr("What do violations imply?")):
        st.markdown(explain("violations"))
