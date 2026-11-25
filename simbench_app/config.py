"""Central configuration: session-state keys, defaults and thresholds.

All pages address ``st.session_state`` exclusively through these keys so the
shared state contract is defined in a single place.
"""

# --- session-state keys -----------------------------------------------------
KEY_NET = "net"                # loaded pandapower network (mutable working copy)
KEY_CODE = "sb_code"           # SimBench code of the loaded network
KEY_LOADED_AT = "loaded_at"    # ISO timestamp of loading
KEY_PF_RESULT = "pf_result"    # simbench_app.powerflow.PowerFlowResult of last run
KEY_THRESHOLDS = "thresholds"  # dict, see DEFAULT_THRESHOLDS
KEY_MODLOG = "modification_log"  # list[str], user modifications applied to the net

# --- defaults ----------------------------------------------------------------
DEFAULT_CODE = "1-LV-rural1--0-sw"  # small example network, loads in seconds

DEFAULT_THRESHOLDS = {
    "vm_min_pu": 0.95,          # lower voltage band (p.u.)
    "vm_max_pu": 1.05,          # upper voltage band (p.u.)
    "max_loading_percent": 100.0,  # thermal loading limit for lines/transformers
}

#: Voltage-band presets (label -> (min p.u., max p.u., explanation)).
#: EN 50160 is the normative supply-voltage tolerance at the customer; the
#: 5 % band is a common, more conservative *planning* band. The split of the
#: 10 % between MV, transformer and LV is DSO-specific - adapt as needed.
VOLTAGE_BAND_PRESETS = {
    "EN 50160 (±10 %)": (
        0.90, 1.10,
        "Normative tolerance of the supply voltage at the connection point "
        "(DIN EN 50160, 10-min mean values, 95 % of a week)."),
    "Planning band (±5 %)": (
        0.95, 1.05,
        "Conservative band leaving headroom for the other network levels - "
        "a typical starting point for planning; use your own DSO's allocation."),
    "Custom": (None, None, "Set the limits manually below."),
}
DEFAULT_PRESET = "Planning band (±5 %)"

#: Default limit for the voltage rise caused by generation [% of Un].
#: Orientation value: VDE-AR-N 4105 allows 3 % for all generators at an LV
#: connection point (MV/HV rules, e.g. VDE-AR-N 4110/4120, are stricter per plant).
DER_VOLTAGE_RISE_LIMIT_PERCENT = 3.0

PROFILE_RESOLUTION_H = 0.25     # SimBench time series are sampled in 15-min steps
TIMESERIES_MAX_STEPS = 96       # cap for the demonstrative time-series power flow
TIMESERIES_MAX_BUSES = 1000     # skip the demo for larger networks
ANNUAL_MAX_BUSES = 1000         # annual time series only for networks up to this size
ANNUAL_MAX_STEPS = 9000         # cap on simulated steps (hourly year = 8784)
LARGE_NET_THRESHOLD = 3000      # above this many lines, switch to WebGL rendering
