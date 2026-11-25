"""Diagnostic checks on the loaded network, with severity levels.

Severities: ``critical`` (results unusable or network unsolvable),
``warning`` (results questionable, needs attention), ``info`` (worth knowing).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
import pandapower.topology as top

from . import network_analysis as na
from . import powerflow as pf
from .i18n import get_lang, tr
from .utils import tr_const

SEVERITY_ORDER = {"critical": 0, "warning": 1, "info": 2}


@dataclass
class Finding:
    severity: str  # "critical" | "warning" | "info"
    title: str
    detail: str


def run_diagnostics(net, thresholds: dict, pf_result=None) -> list[Finding]:
    """Run all structural and (if available) result-based checks."""
    findings: list[Finding] = []
    findings += _structural_checks(net)
    findings += _data_quality_checks(net)
    findings += _result_checks(net, thresholds, pf_result)
    findings.sort(key=lambda f: SEVERITY_ORDER.get(f.severity, 9))
    return findings


# --- structural ---------------------------------------------------------------

def _structural_checks(net) -> list[Finding]:
    findings: list[Finding] = []

    if len(net.ext_grid) == 0 and not (
        len(net.gen) and "slack" in net.gen.columns and net.gen["slack"].any()
    ):
        findings.append(Finding(
            "critical", tr("No slack source"),
            tr("The network has neither an external grid nor a slack generator. "
               "A power flow cannot balance the system without a slack bus."),
        ))

    try:
        unsupplied = top.unsupplied_buses(net)
    except Exception:
        unsupplied = set()
    if unsupplied:
        findings.append(Finding(
            "critical", tr("{n} unsupplied bus(es)", n=len(unsupplied)),
            tr("These buses have no electrical path to a slack source "
               "(considering switch states and in-service flags): "
               "{buses}. "
               "Power flow treats them as isolated.",
               buses=f"{sorted(unsupplied)[:20]}"
                     f"{' …' if len(unsupplied) > 20 else ''}"),
        ))
    else:
        findings.append(Finding(
            "info", tr("All buses are supplied"),
            tr("Every in-service bus is topologically connected to a slack source."),
        ))

    try:
        import networkx as nx
        graph = top.create_nxgraph(net, respect_switches=True)
        n_comp = nx.number_connected_components(graph)
        if n_comp > 1:
            findings.append(Finding(
                "warning", tr("Network splits into {n} islands", n=n_comp),
                tr("With the current switch states the network graph is not a "
                   "single connected component. Islands without their own slack "
                   "source cannot be solved."),
            ))
    except Exception:
        pass

    oos = []
    for attr, label in na.ELEMENTS.items():
        df = net.get(attr)
        if isinstance(df, pd.DataFrame) and "in_service" in df.columns and len(df):
            n = int((~df["in_service"]).sum())
            if n:
                oos.append(f"{n} " + (label.lower() if get_lang() == "en"
                                      else tr_const(label)))
    if oos:
        findings.append(Finding(
            "info", tr("Elements out of service"),
            tr("The following elements are switched off and ignored by "
               "analyses: {elements}.", elements=", ".join(oos)),
        ))
    return findings


# --- data quality ---------------------------------------------------------------

def _data_quality_checks(net) -> list[Finding]:
    findings: list[Finding] = []

    required = {
        "load": ["p_mw"],
        "line": ["length_km", "r_ohm_per_km", "x_ohm_per_km", "max_i_ka"],
        "trafo": ["sn_mva", "vk_percent"],
        "bus": ["vn_kv"],
    }
    for table, cols in required.items():
        df = net.get(table)
        if not isinstance(df, pd.DataFrame) or df.empty:
            continue
        for col in cols:
            if col in df.columns and df[col].isna().any():
                findings.append(Finding(
                    "warning",
                    tr("Missing values in {table}.{col}", table=table, col=col),
                    tr("{n} of {total} entries are NaN. "
                       "This parameter is required for power-flow modelling.",
                       n=int(df[col].isna().sum()), total=len(df)),
                ))

    if len(net.line) and (net.line["length_km"] <= 0).any():
        n = int((net.line["length_km"] <= 0).sum())
        findings.append(Finding(
            "warning", tr("{n} line(s) with non-positive length", n=n),
            tr("Zero or negative lengths usually indicate data errors and "
               "distort impedances."),
        ))

    geo = net.bus.get("geo")
    n_geo = int(geo.notna().sum()) if geo is not None else 0
    if n_geo == 0:
        findings.append(Finding(
            "info", tr("No geographic coordinates"),
            tr("The bus table has no geodata; the topology page falls back to "
               "an automatically computed layout."),
        ))
    elif n_geo < len(net.bus):
        findings.append(Finding(
            "info", tr("Partial geographic coordinates"),
            tr("Only {n} of {total} buses carry geodata.",
               n=n_geo, total=len(net.bus)),
        ))
    return findings


# --- result-based -----------------------------------------------------------------

def _result_checks(net, thresholds: dict, pf_result) -> list[Finding]:
    findings: list[Finding] = []

    if pf_result is not None and not pf_result.converged:
        findings.append(Finding(
            "critical", tr("Last power flow did not converge"),
            tr("Solver message: {error}. All result-based "
               "checks are skipped; the result tables are not meaningful.",
               error=pf_result.error or tr("unknown")),
        ))
        return findings

    if not pf.has_results(net):
        findings.append(Finding(
            "info", tr("No power-flow results yet"),
            tr("Run a power flow on the *Power Flow Analysis* page to enable "
               "voltage and loading checks."),
        ))
        return findings

    viol = pf.violations(net, thresholds["vm_min_pu"], thresholds["vm_max_pu"],
                         thresholds["max_loading_percent"])
    n_under = len(viol.get("undervoltage_buses", ()))
    n_over = len(viol.get("overvoltage_buses", ()))
    if n_under or n_over:
        worst_low = viol["undervoltage_buses"]["vm_pu"].min() if n_under else None
        worst_high = viol["overvoltage_buses"]["vm_pu"].max() if n_over else None
        detail = []
        if n_under:
            detail.append(tr("{n} buses below {limit} p.u. "
                             "(worst: {worst:.4f} p.u.)",
                             n=n_under, limit=thresholds['vm_min_pu'],
                             worst=worst_low))
        if n_over:
            detail.append(tr("{n} buses above {limit} p.u. "
                             "(worst: {worst:.4f} p.u.)",
                             n=n_over, limit=thresholds['vm_max_pu'],
                             worst=worst_high))
        findings.append(Finding(
            "warning" if (n_under + n_over) < 0.05 * len(net.bus) else "critical",
            tr("Voltage-band violations"), "; ".join(detail) + ".",
        ))
    else:
        findings.append(Finding(
            "info", tr("All bus voltages within the configured band"),
            f"[{thresholds['vm_min_pu']}, {thresholds['vm_max_pu']}] p.u.",
        ))

    for table in ("line", "trafo"):
        over = viol.get(f"overloaded_{table}s", pd.DataFrame())
        if len(over):
            worst = float(over["loading_percent"].max())
            findings.append(Finding(
                "critical" if worst > 120 else "warning",
                (tr("{n} overloaded lines", n=len(over)) if table == "line"
                 else tr("{n} overloaded transformers", n=len(over))),
                tr("Loading above {limit} % "
                   "(worst: {worst:.1f} %). Sustained overloading accelerates "
                   "ageing and may trip protection.",
                   limit=thresholds['max_loading_percent'], worst=worst),
            ))
        else:
            findings.append(Finding(
                "info",
                tr("No overloaded lines") if table == "line"
                else tr("No overloaded transformers"),
                (tr("All lines are at or below {limit} % loading.",
                    limit=thresholds['max_loading_percent']) if table == "line"
                 else tr("All transformers are at or below {limit} % loading.",
                         limit=thresholds['max_loading_percent'])),
            ))
    return findings
