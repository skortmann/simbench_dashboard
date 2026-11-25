"""Network-level summary statistics computed from a pandapower network.

All functions are defensive against missing or empty element tables so they
work for any SimBench grid level (LV feeders up to complete HV systems).
"""

from __future__ import annotations

import pandas as pd

from .i18n import tr

#: pandapower element tables shown throughout the app (attribute -> label).
ELEMENTS = {
    "bus": "Buses",
    "line": "Lines",
    "trafo": "Transformers (2-winding)",
    "trafo3w": "Transformers (3-winding)",
    "load": "Loads",
    "sgen": "Static generators",
    "gen": "Generators (voltage-controlled)",
    "storage": "Storage units",
    "switch": "Switches",
    "ext_grid": "External grids",
    "shunt": "Shunts",
    "measurement": "Measurements",
}


def element_label(attr: str) -> str:
    """Translated display label of an element table (see :data:`ELEMENTS`)."""
    return {
        "bus": tr("Buses"),
        "line": tr("Lines"),
        "trafo": tr("Transformers (2-winding)"),
        "trafo3w": tr("Transformers (3-winding)"),
        "load": tr("Loads"),
        "sgen": tr("Static generators"),
        "gen": tr("Generators (voltage-controlled)"),
        "storage": tr("Storage units"),
        "switch": tr("Switches"),
        "ext_grid": tr("External grids"),
        "shunt": tr("Shunts"),
        "measurement": tr("Measurements"),
    }.get(attr, ELEMENTS.get(attr, attr))


def _table(net, attr: str) -> pd.DataFrame | None:
    df = net.get(attr) if hasattr(net, "get") else getattr(net, attr, None)
    return df if isinstance(df, pd.DataFrame) else None


def element_counts(net) -> pd.DataFrame:
    """Count of every element type, total and in service."""
    rows = []
    for attr in ELEMENTS:
        df = _table(net, attr)
        if df is None:
            continue
        n = len(df)
        if "in_service" in df.columns and n:
            in_service = int(df["in_service"].sum())
        else:
            in_service = n
        rows.append({"Element": element_label(attr), "Table": attr, "Count": n,
                     "In service": in_service})
    return pd.DataFrame(rows).set_index("Element")


def buses_per_voltage_level(net) -> pd.DataFrame:
    """Bus count per nominal voltage level, descending by voltage."""
    if net.bus.empty:
        return pd.DataFrame()
    out = (net.bus["vn_kv"].value_counts().sort_index(ascending=False)
           .rename_axis("Nominal voltage [kV]").reset_index(name="Buses"))
    return out


def capacity_summary(net) -> pd.DataFrame:
    """Installed demand, generation and storage capacities."""
    rows: list[dict] = []

    def add(quantity: str, value: float, unit: str) -> None:
        rows.append({"Quantity": quantity, "Value": round(float(value), 3),
                     "Unit": unit})

    if len(net.load):
        add(tr("Total active load demand"), net.load["p_mw"].sum(), "MW")
        add(tr("Total reactive load demand"), net.load["q_mvar"].sum(), "Mvar")
    if len(net.sgen):
        add(tr("Installed static generation (sgen)"), net.sgen["p_mw"].sum(), "MW")
    if len(net.gen):
        add(tr("Installed controllable generation (gen)"), net.gen["p_mw"].sum(), "MW")
    if len(net.storage):
        add(tr("Storage rated power"), net.storage["p_mw"].sum(), "MW")
        if "max_e_mwh" in net.storage.columns:
            add(tr("Storage energy capacity"), net.storage["max_e_mwh"].sum(), "MWh")
    return pd.DataFrame(rows)


def sgen_by_type(net) -> pd.DataFrame:
    """Installed sgen capacity grouped by technology type (PV, wind, …)."""
    if net.sgen.empty or "type" not in net.sgen.columns:
        return pd.DataFrame()
    out = (net.sgen.groupby(net.sgen["type"].fillna(tr("unspecified")))
           .agg(Units=("p_mw", "size"), Installed_MW=("p_mw", "sum"))
           .rename_axis("Technology").sort_values("Installed_MW", ascending=False))
    return out.round(3)


def line_stats(net) -> pd.DataFrame:
    """Length statistics and cable/overhead split of the line table."""
    if net.line.empty:
        return pd.DataFrame()
    length = net.line["length_km"]
    rows = [
        (tr("Number of lines"), len(net.line), "–"),
        (tr("Total route length"), round(length.sum(), 3), "km"),
        (tr("Mean line length"), round(length.mean(), 3), "km"),
        (tr("Median line length"), round(length.median(), 3), "km"),
        (tr("Longest line"), round(length.max(), 3), "km"),
        (tr("Distinct standard types"), net.line["std_type"].nunique(), "–"),
    ]
    if "type" in net.line.columns:
        n_cable = int((net.line["type"] == "cs").sum())
        rows.append((tr("Cables (type 'cs')"), n_cable, "–"))
        rows.append((tr("Overhead lines (type 'ol')"),
                     int((net.line["type"] == "ol").sum()), "–"))
    return pd.DataFrame(rows, columns=["Quantity", "Value", "Unit"])


def trafo_stats(net) -> pd.DataFrame:
    """Rating statistics and voltage-level pairs of the 2-winding transformers."""
    if net.trafo.empty:
        return pd.DataFrame()
    sn = net.trafo["sn_mva"]
    rows = [
        (tr("Number of transformers"), len(net.trafo), "–"),
        (tr("Total rated power"), round(sn.sum(), 3), "MVA"),
        (tr("Smallest unit"), round(sn.min(), 3), "MVA"),
        (tr("Largest unit"), round(sn.max(), 3), "MVA"),
    ]
    pairs = (net.trafo.groupby(["vn_hv_kv", "vn_lv_kv"]).size())
    for (hv, lv), n in pairs.items():
        rows.append((tr("Units {hv:g} kV → {lv:g} kV", hv=hv, lv=lv),
                     int(n), "–"))
    return pd.DataFrame(rows, columns=["Quantity", "Value", "Unit"])


def missing_data_overview(net) -> pd.DataFrame:
    """Columns with missing values per element table.

    Many optional pandapower columns are legitimately unset; this table makes
    that explicit rather than letting NaN values surprise users later.
    """
    rows = []
    for attr in ELEMENTS:
        df = _table(net, attr)
        if df is None or df.empty:
            continue
        na = df.isna().sum()
        for col, n in na[na > 0].items():
            rows.append({"Table": attr, "Column": col, "Missing values": int(n),
                         "Share": f"{n / len(df):.0%}"})
    return pd.DataFrame(rows)


def consistency_checks(net) -> list[tuple[bool, str]]:
    """Basic structural sanity checks, returned as (passed, description)."""
    checks: list[tuple[bool, str]] = []

    has_slack = len(net.ext_grid) > 0 or (
        len(net.gen) > 0 and "slack" in net.gen.columns and net.gen["slack"].any()
    )
    checks.append((has_slack,
                   tr("A slack source (external grid or slack generator) exists")))

    if len(net.line):
        checks.append((bool((net.line["length_km"] > 0).all()),
                       tr("All lines have a positive length")))
        bus_ids = set(net.bus.index)
        ok = (net.line["from_bus"].isin(bus_ids).all()
              and net.line["to_bus"].isin(bus_ids).all())
        checks.append((bool(ok), tr("All line endpoints reference existing buses")))

    if len(net.load):
        oos_buses = set(net.bus.index[~net.bus["in_service"]])
        n_bad = int(net.load["bus"].isin(oos_buses).sum())
        checks.append((n_bad == 0,
                       tr("No loads are connected to out-of-service buses "
                          "({n_bad} affected)", n_bad=n_bad) if n_bad
                       else tr("No loads are connected to out-of-service "
                               "buses")))

    if len(net.bus):
        n_dup = int(net.bus["name"].duplicated().sum())
        checks.append((n_dup == 0,
                       tr("Bus names are unique ({n_dup} duplicates)",
                          n_dup=n_dup) if n_dup else tr("Bus names are unique")))
    return checks
