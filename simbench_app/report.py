"""Lightweight Markdown report generation with reproducibility information."""

from __future__ import annotations

import pandas as pd

from . import network_analysis as na
from . import powerflow as pf
from . import utils
from .i18n import tr
from .i18n import tr as trc  # tr() of catalogued constants

#: Violation table keys -> English display titles (translated at build time).
VIOLATION_TITLES = {
    "undervoltage_buses": "Undervoltage buses",
    "overvoltage_buses": "Overvoltage buses",
    "overloaded_lines": "Overloaded lines",
    "overloaded_trafos": "Overloaded trafos",
}


def _df_md(df: pd.DataFrame) -> str:
    """DataFrame as a Markdown table (empty string for empty frames)."""
    return df.to_markdown() if len(df) else tr("_(none)_")


def build_markdown_report(net, code: str, pf_result=None,
                          thresholds: dict | None = None,
                          modifications: list[str] | None = None) -> str:
    """Assemble a self-contained Markdown analysis report for the network."""
    parts: list[str] = []
    env = utils.environment_info()

    parts.append(tr("# SimBench Network Analysis Report") + "\n")
    parts.append(tr("- **SimBench code:** `{code}`", code=code))
    parts.append(tr("- **Generated:** {ts}", ts=utils.now_iso()))
    parts.append(tr("- **Software:** {env}",
                    env=", ".join(f"{k} {v}" for k, v in env.items())))
    if modifications:
        parts.append(tr("- **User modifications applied:**"))
        parts += [f"    - {m}" for m in modifications]
    parts.append("")

    parts.append(tr("## Network structure") + "\n")
    parts.append(_df_md(na.element_counts(net)) + "\n")
    parts.append(tr("### Buses per voltage level") + "\n")
    parts.append(_df_md(na.buses_per_voltage_level(net).set_index(
        "Nominal voltage [kV]")) + "\n")
    parts.append(tr("### Installed capacities") + "\n")
    parts.append(_df_md(na.capacity_summary(net).set_index("Quantity")) + "\n")

    line_df = na.line_stats(net)
    if len(line_df):
        parts.append(tr("### Line statistics") + "\n")
        parts.append(_df_md(line_df.set_index("Quantity")) + "\n")
    trafo_df = na.trafo_stats(net)
    if len(trafo_df):
        parts.append(tr("### Transformer statistics") + "\n")
        parts.append(_df_md(trafo_df.set_index("Quantity")) + "\n")

    parts.append(tr("## Power flow") + "\n")
    if pf_result is None:
        parts.append(tr("_No power flow has been run in this session._") + "\n")
    else:
        parts.append(tr("- **Converged:** {v}", v=pf_result.converged))
        parts.append(tr("- **Run at:** {v}", v=pf_result.timestamp))
        parts.append(tr("- **Runtime:** {v:.3f} s", v=pf_result.runtime_s))
        parts.append(tr("- **Solver backend:** {v}", v=pf_result.backend)
                     + (f" ({pf_result.backend_note})" if pf_result.backend_note else ""))
        parts.append(tr("- **Solver options:** `{v}`", v=pf_result.options) + "\n")
        if pf_result.converged and pf.has_results(net):
            parts.append(tr("### Voltage summary per level") + "\n")
            parts.append(_df_md(pf.voltage_summary(net)) + "\n")
            parts.append(tr("### Power balance") + "\n")
            parts.append(_df_md(pf.power_balance(net).set_index("Component"))
                         + "\n")
            if thresholds:
                viol = pf.violations(net, thresholds["vm_min_pu"],
                                     thresholds["vm_max_pu"],
                                     thresholds["max_loading_percent"])
                parts.append(tr(
                    "### Violations (limits: {vmin}–{vmax} p.u., {load} % loading)",
                    vmin=thresholds['vm_min_pu'], vmax=thresholds['vm_max_pu'],
                    load=thresholds['max_loading_percent']) + "\n")
                for key, df in viol.items():
                    title = trc(VIOLATION_TITLES[key]) if key in VIOLATION_TITLES \
                        else key.replace('_', ' ').title()
                    parts.append(f"**{title}:** {len(df)}\n")
                    if 0 < len(df) <= 25:
                        parts.append(_df_md(df) + "\n")
        elif not pf_result.converged:
            parts.append(tr("- **Solver message:** {v}", v=pf_result.error) + "\n")

    parts.append(tr("## Reproducibility notes") + "\n")
    parts.append(tr(
        "Results stem from a static, balanced AC power flow with pandapower. "
        "Re-running with the listed package versions, SimBench code, solver "
        "options and modifications reproduces them exactly.") + "\n")
    return "\n".join(parts)
