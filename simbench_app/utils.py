"""Shared helpers: session-state access, environment info, export byte streams."""

from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone

import pandas as pd
import streamlit as st

from . import config
from .i18n import tr

#: Alias of ``tr`` for texts held in module-level constants (translated on
#: display; the constants themselves are covered by tests/translation_check.py).
tr_const = tr


# --- session state -----------------------------------------------------------

def get_net():
    """Return the loaded pandapower network or ``None``."""
    return st.session_state.get(config.KEY_NET)


def require_network():
    """Return the loaded network, or stop the page with a friendly hint."""
    net = get_net()
    if net is None:
        st.warning(tr(
            "No network loaded yet. Please select and load a SimBench network "
            "on the **Home** page first."
        ))
        st.stop()
    return net


def loaded_code() -> str:
    """SimBench code of the currently loaded network."""
    return st.session_state.get(config.KEY_CODE, "unknown")


def get_thresholds() -> dict:
    """Current assessment thresholds, initialised from the defaults."""
    return st.session_state.setdefault(
        config.KEY_THRESHOLDS, dict(config.DEFAULT_THRESHOLDS)
    )


def _apply_preset() -> None:
    """Copy the selected voltage-band preset into the widget state."""
    lo, hi, _ = config.VOLTAGE_BAND_PRESETS[st.session_state["th_preset"]]
    if lo is not None:
        st.session_state["th_vm_min"] = lo
        st.session_state["th_vm_max"] = hi


def threshold_controls() -> dict:
    """Render sidebar inputs for the assessment thresholds and persist them.

    Shared by the power-flow and diagnostics pages so both always operate on
    the same limits. A preset (EN 50160, planning band, custom) fills the
    voltage band; editing the numbers switches the preset to "Custom".
    """
    th = get_thresholds()
    ss = st.session_state
    # widget state is dropped on pages that do not render it -> restore from th
    ss.setdefault("th_vm_min", float(th["vm_min_pu"]))
    ss.setdefault("th_vm_max", float(th["vm_max_pu"]))
    ss.setdefault("th_preset", th.get("preset", config.DEFAULT_PRESET))
    ss.setdefault("th_max_loading", float(th["max_loading_percent"]))
    ss.setdefault("th_der_rise", float(th.get(
        "der_rise_percent", config.DER_VOLTAGE_RISE_LIMIT_PERCENT)))

    def _to_custom() -> None:
        ss["th_preset"] = "Custom"

    st.sidebar.subheader(tr("Assessment thresholds"))
    preset = st.sidebar.selectbox(
        tr("Voltage band preset"), list(config.VOLTAGE_BAND_PRESETS),
        key="th_preset", on_change=_apply_preset, format_func=tr_const,
        help=tr("Normative or planning-based voltage band. Pick *Custom* to "
                "set your own limits."))
    st.sidebar.caption(tr_const(config.VOLTAGE_BAND_PRESETS[preset][2]))
    th["preset"] = preset
    th["vm_min_pu"] = st.sidebar.number_input(
        tr("Minimum voltage [p.u.]"), min_value=0.50, max_value=1.00, step=0.01,
        key="th_vm_min", on_change=_to_custom,
        help=tr("Buses below this magnitude are flagged as undervoltage."),
    )
    th["vm_max_pu"] = st.sidebar.number_input(
        tr("Maximum voltage [p.u.]"), min_value=1.00, max_value=1.50, step=0.01,
        key="th_vm_max", on_change=_to_custom,
        help=tr("Buses above this magnitude are flagged as overvoltage."),
    )
    th["max_loading_percent"] = st.sidebar.number_input(
        tr("Maximum loading [%]"), min_value=10.0, max_value=200.0, step=5.0,
        key="th_max_loading",
        help=tr("Lines/transformers above this loading are flagged as "
                "overloaded."),
    )
    th["der_rise_percent"] = st.sidebar.number_input(
        tr("Max. voltage rise by generation [%]"), min_value=0.5,
        max_value=10.0, step=0.5, key="th_der_rise",
        help=tr("Limit for the voltage rise caused by all generators compared "
                "with the same case without generation (orientation: 3 % in LV, "
                "VDE-AR-N 4105)."),
    )
    return th


def log_modification(text: str) -> None:
    """Append a user modification to the session modification log."""
    st.session_state.setdefault(config.KEY_MODLOG, []).append(
        f"{now_iso()} — {text}"
    )


# --- environment & formatting -------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def environment_info() -> dict[str, str]:
    """Versions of the packages that determine the numerical results."""
    import sys

    import numpy
    import pandapower
    import plotly
    import simbench

    return {
        "python": sys.version.split()[0],
        "streamlit": st.__version__,
        "pandapower": pandapower.__version__,
        "simbench": simbench.__version__,
        "pandas": pd.__version__,
        "numpy": numpy.__version__,
        "plotly": plotly.__version__,
    }


# --- exports -------------------------------------------------------------------

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    """Encode a DataFrame as UTF-8 CSV for ``st.download_button``."""
    return df.to_csv(index=True).encode("utf-8")


def net_to_bytes(net, fmt: str) -> bytes:
    """Serialise a pandapower network to bytes (``json``, ``pickle`` or ``excel``).

    JSON is the recommended, version-stable pandapower format. Pickle and Excel
    are written through a temporary file because pandapower's writers expect a
    file path.
    """
    import pandapower as pp

    if fmt == "json":
        return pp.to_json(net).encode("utf-8")
    suffix = {"pickle": "p", "excel": "xlsx"}[fmt]
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"network.{suffix}")
        if fmt == "pickle":
            pp.to_pickle(net, path)
        else:
            pp.to_excel(net, path)
        with open(path, "rb") as fh:
            return fh.read()
