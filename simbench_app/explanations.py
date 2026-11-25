"""Explanation texts for the explainability layer.

Concise academic explanations rendered next to the numbers, so the platform
explains *what the results mean*, not only what they are. Keys are referenced
from the pages via :func:`explain`.
"""

from __future__ import annotations

from .i18n import tr as tr_const  # texts live in the TEXTS constant

TEXTS: dict[str, str] = {
    "platform": (
        "This platform provides transparent, reproducible inspection and "
        "analysis of **SimBench benchmark networks** with "
        "[pandapower](https://www.pandapower.org). SimBench is a public German "
        "benchmark dataset of realistic, fully parameterised distribution and "
        "transmission grids with time series, designed for comparable studies "
        "of grid planning and operation."
    ),
    "code_structure": (
        "SimBench codes follow the pattern "
        "`version-gridlevel-type-subnet-scenario(-sw)`, e.g. "
        "`1-MV-rural--0-sw`: dataset version 1, a rural medium-voltage grid, "
        "scenario 0 (base state), with explicitly modelled switches. Scenarios "
        "1 and 2 are development scenarios labelled 2024 and 2034 with "
        "increasing distributed generation, heat pumps and e-mobility."
    ),
    "bus": (
        "**Buses** are the electrical nodes of the model. Every other element "
        "attaches to one or more buses. Each bus has a nominal voltage "
        "`vn_kv`; the power flow computes its actual voltage magnitude and "
        "angle."
    ),
    "line": (
        "**Lines** (cables `cs` or overhead lines `ol`) connect two buses. "
        "Their impedance per kilometre and length determine losses and "
        "voltage drop; `max_i_ka` is the thermal current limit used to "
        "compute loading in percent."
    ),
    "trafo": (
        "**Transformers** couple voltage levels (e.g. 20 kV → 0.4 kV). The "
        "rated power `sn_mva` and short-circuit voltage `vk_percent` define "
        "their capacity and impedance. Loading above 100 % of `sn_mva` means "
        "operation beyond the nameplate rating."
    ),
    "load": (
        "**Loads** model consumption as fixed active/reactive power (PQ "
        "model). In SimBench each load references a normalised time-series "
        "profile; the static values represent one operating snapshot."
    ),
    "sgen": (
        "**Static generators** model injections without voltage control — in "
        "SimBench mostly photovoltaics, wind and other distributed energy "
        "resources. They are PQ elements: power is specified, voltage is a "
        "result."
    ),
    "ext_grid": (
        "The **external grid** is the slack: it fixes voltage magnitude and "
        "angle at its bus and balances the system's active/reactive power "
        "mismatch, representing the upstream transmission system."
    ),
    "vm_pu": (
        "Voltages are reported **per unit (p.u.)** — the ratio of the actual "
        "to the nominal voltage. 1.0 p.u. equals nominal; typical European "
        "distribution-grid planning limits are ±5 % to ±10 % (EN 50160). "
        "Per-unit values make different voltage levels directly comparable."
    ),
    "loading": (
        "**Loading percent** relates actual current (lines) or apparent power "
        "(transformers) to the element's thermal rating. Values above 100 % "
        "indicate overloading: permissible briefly, but sustained overloads "
        "accelerate ageing and can trigger protection."
    ),
    "convergence": (
        "The AC power flow solves a nonlinear equation system iteratively "
        "(here: Newton-Raphson by default). **Convergence** means a "
        "self-consistent operating point was found. Non-convergence usually "
        "indicates an infeasible operating point (e.g. voltage collapse), "
        "isolated subnetworks, or data errors — the result tables are then "
        "meaningless."
    ),
    "power_balance": (
        "The **power balance** verifies that generation equals demand plus "
        "network losses. The slack (external grid) covers the residual. "
        "Active-power losses arise from current through line and transformer "
        "resistances; reactive behaviour additionally reflects line charging "
        "and transformer magnetising."
    ),
    "violations": (
        "**Violations** compare results against the configured planning "
        "limits: a voltage band in p.u. and a maximum loading in percent. "
        "Violations in a benchmark scenario indicate stress cases that grid "
        "reinforcement or operational measures would need to resolve — they "
        "are analysis findings, not software errors."
    ),
    "voltage_band": (
        "The permissible voltage is a **budget shared across network levels**. "
        "DIN EN 50160 requires the supply voltage at the customer within "
        "**±10 %** of the nominal value. That 10 % is split between the "
        "medium-voltage grid, the MV/LV transformer (incl. tap position) and "
        "the low-voltage grid, and generation connected in a level may only "
        "use a part of it (orientation: 3 % for all generators in LV, "
        "VDE-AR-N 4105; stricter per-plant values in MV/HV, VDE-AR-N 4110/4120). "
        "How the budget is allocated is a DSO-specific planning rule - the "
        "presets here are orientation values, not a replacement for your own "
        "planning principles."
    ),
    "der_rise": (
        "The **voltage rise by generation** is the difference of the bus "
        "voltage with and without the connected generators, for the *same* "
        "load situation. It isolates what the generation does to the "
        "voltage - independent of the voltage level the load flow starts at. "
        "Compare it with the allowed share (default 3 % in LV). Evaluate it "
        "in the SimBench high-generation / low-load case for the "
        "worst-case situation."
    ),
    "scenarios": (
        "**Development scenarios** are separate networks of the same grid. "
        "Scenario 0 is the base state and keeps voltage and equipment limits, "
        "also under n-1. Scenarios 1 and 2 (labelled 2024 and 2034 in the "
        "SimBench documentation) were built by randomly adding renewables "
        "and new consumers until a share of nodes/lines violated limits "
        "(about 15 % for scenario 1, 30 % for scenario 2) - they are "
        "deliberately **stress cases for planning studies, not forecasts**. "
        "LV grids gain PV, PV storage, heat pumps and EVs, MV grids add "
        "biomass, wind and wind storage, HV grids only wind. Storage in "
        "stand-alone MV/HV nets appears as `_eq` equivalents for lumped "
        "lower-level batteries. The EHV scenarios are incomplete."
    ),
    "planning_cases": (
        "**Planning cases** are extreme operating points shipped with each "
        "net: **hL** = high load without generation (typical for "
        "transformer/feeder loading and undervoltage), **hW** = high load "
        "with very high wind, **lW** = low load with very high wind "
        "(typical for reverse power flow and overvoltage). They scale the "
        "active power of loads and generators (reactive load is scaled "
        "separately) and set the slack voltage. They are not available for "
        "EHV grids. Further cases (n1, hPV, lPV) exist in the data."
    ),
    "n1": (
        "**N-1** means: the grid must tolerate the loss of any single "
        "line or transformer without limit violations or (after switching) "
        "loss of supply. Here every in-service line/transformer is failed "
        "once and an AC power flow is computed. If buses lose supply, one "
        "closing action at a normally-open point (open switch or "
        "out-of-service line) is tried to restore them. **Not covered:** "
        "switching sequences and times, remote-control capability, busbar "
        "faults, multiple outages, protection and short-circuit behaviour, "
        "generation curtailment. Treat the result as an orientation for "
        "structural weak points, not as a security certificate. Radial LV "
        "grids typically show supply loss by design."
    ),
    "annual": (
        "A single snapshot (e.g. the planning case *hW*) shows one extreme "
        "point. The **annual analysis** runs a power flow for each time step "
        "of the SimBench year and thereby tells **how often and when** limits "
        "are reached. A *duration curve* sorts all values of the year from "
        "high to low: where it crosses a limit line, you read off the number "
        "of hours per year in violation. The *heat map* arranges the year as "
        "day × hour to reveal seasonal and daily patterns. Note: SimBench "
        "profiles are synthetic and normalised - they describe a plausible "
        "year of the reference year 2016 (a leap year), not a measured one - "
        "and coarser resolutions (e.g. hourly) can miss short 15-minute peaks."
    ),
    "profiles": (
        "SimBench ships **one year of time series at 15-minute resolution** "
        "(35,136 steps) as normalised profiles per consumer/generator type. "
        "Multiplying a profile by an element's rated power yields its "
        "time-dependent injection. The static network represents a single "
        "snapshot; time-series analysis reveals when stress actually occurs."
    ),
    "limitations": (
        "**Model limitations.** Results are from a *static, balanced AC power "
        "flow*: no dynamics, no asymmetry, no protection behaviour, and loads/"
        "generators reduced to PQ set-points. SimBench grids are synthetic "
        "benchmarks — realistic, but not images of specific real networks. "
        "Geodata, where present, is schematic. Conclusions transfer to real "
        "grids only within these assumptions."
    ),
    "bus_naming": (
        "SimBench uses structured bus names encoding location and role:\n\n"
        "- **Voltage-level prefix:** `HV` (high), `MV` (medium), `LV` (low "
        "voltage).\n"
        "- **Grid-area identifier:** the number after the level (e.g. `HV1`, "
        "`MV2`) denotes a grid area.\n"
        "- **Feeder/subnetwork code:** a dot and number (e.g. `.101`) denote "
        "a feeder within that area — `MV2.101` is feeder 101 in MV area 2.\n"
        "- **Bus identifier:** `Bus X` is the X-th bus of that feeder; names "
        "like `busbar1.1` are internal substation busbars.\n\n"
        "Examples: `HV1 Bus 19` — bus 19 in HV area 1; `MV2.101 Bus 116` — "
        "bus 116 in MV feeder 101 of area 2."
    ),
    "diagnostics": (
        "Diagnostics distinguish **critical** findings (the model cannot be "
        "solved or results are unusable), **warnings** (results need "
        "scrutiny) and **info** items (worth knowing). Structural checks are "
        "independent of the power flow; voltage and loading checks require a "
        "converged power flow first."
    ),
}


def explain(key: str) -> str:
    """Markdown explanation for ``key`` in the active language (empty if unknown)."""
    text = TEXTS.get(key, "")
    return tr_const(text) if text else ""
