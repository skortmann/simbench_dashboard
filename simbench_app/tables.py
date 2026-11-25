"""Element-table presentation: units, column presets and interactive filtering."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from .i18n import tr

#: Physical units of common pandapower columns (column name -> unit).
UNITS = {
    "vn_kv": "kV", "vn_hv_kv": "kV", "vn_lv_kv": "kV",
    "p_mw": "MW", "q_mvar": "Mvar", "sn_mva": "MVA",
    "min_p_mw": "MW", "max_p_mw": "MW", "min_q_mvar": "Mvar", "max_q_mvar": "Mvar",
    "length_km": "km", "max_i_ka": "kA",
    "r_ohm_per_km": "Ω/km", "x_ohm_per_km": "Ω/km", "c_nf_per_km": "nF/km",
    "vm_pu": "p.u.", "min_vm_pu": "p.u.", "max_vm_pu": "p.u.",
    "va_degree": "°", "vk_percent": "%", "vkr_percent": "%",
    "pfe_kw": "kW", "i0_percent": "%", "loading_percent": "%",
    "max_e_mwh": "MWh", "min_e_mwh": "MWh", "soc_percent": "%",
    "scaling": "–", "pl_mw": "MW", "ql_mvar": "Mvar",
    "i_from_ka": "kA", "i_to_ka": "kA", "i_ka": "kA",
}

#: Compact column presets per element table ("essential" view).
PRESETS = {
    "bus": ["name", "vn_kv", "type", "zone", "in_service"],
    "line": ["name", "from_bus", "to_bus", "length_km", "std_type", "max_i_ka",
             "in_service"],
    "trafo": ["name", "hv_bus", "lv_bus", "sn_mva", "vn_hv_kv", "vn_lv_kv",
              "vk_percent", "in_service"],
    "load": ["name", "bus", "p_mw", "q_mvar", "in_service"],
    "sgen": ["name", "bus", "p_mw", "q_mvar", "type", "in_service"],
    "gen": ["name", "bus", "p_mw", "vm_pu", "in_service"],
    "storage": ["name", "bus", "p_mw", "max_e_mwh", "in_service"],
    "switch": ["name", "bus", "element", "et", "type", "closed"],
    "ext_grid": ["name", "bus", "vm_pu", "va_degree", "in_service"],
    "measurement": ["name", "measurement_type", "element_type", "element", "value"],
}


def label_with_units(df: pd.DataFrame) -> pd.DataFrame:
    """Copy of ``df`` with units appended to known column names."""
    return df.rename(columns={c: f"{c} [{UNITS[c]}]" for c in df.columns
                              if c in UNITS})


def filter_dataframe(df: pd.DataFrame, table: str) -> pd.DataFrame:
    """Render filter widgets for an element table and return the filtered frame.

    Filters offered (when the corresponding column exists): name search,
    in-service state, SimBench voltage level, and one numeric range.
    """
    out = df
    c1, c2, c3 = st.columns(3)

    with c1:
        if "name" in out.columns:
            query = st.text_input(tr("Name contains"), key=f"{table}_name")
            if query:
                out = out[out["name"].astype(str)
                          .str.contains(query, case=False, na=False)]

    with c2:
        if "in_service" in out.columns:
            state_labels = {"All": tr("All"), "Yes": tr("Yes"), "No": tr("No")}
            state = st.selectbox(tr("In service"), ["All", "Yes", "No"],
                                 format_func=state_labels.get,
                                 key=f"{table}_insrv")
            if state != "All":
                out = out[out["in_service"] == (state == "Yes")]

    with c3:
        if "voltLvl" in out.columns and out["voltLvl"].notna().any():
            levels = sorted(out["voltLvl"].dropna().unique())
            chosen = st.multiselect(tr("Voltage level (SimBench voltLvl)"), levels,
                                    key=f"{table}_lvl")
            if chosen:
                out = out[out["voltLvl"].isin(chosen)]

    numeric_cols = [c for c in out.columns
                    if pd.api.types.is_numeric_dtype(out[c])
                    and c not in ("in_service",) and out[c].notna().any()]
    if numeric_cols:
        with st.expander(tr("Numeric range filter")):
            col = st.selectbox(tr("Column"), numeric_cols, key=f"{table}_numcol")
            lo, hi = float(out[col].min()), float(out[col].max())
            if lo < hi:
                sel = st.slider(tr("{col} range", col=col), lo, hi, (lo, hi),
                                key=f"{table}_numrange")
                out = out[out[col].between(*sel) | out[col].isna()]
    return out
