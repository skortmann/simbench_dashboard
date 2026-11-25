"""Plotly figures for network topology and result visualization.

pandapower ≥ 3.0 stores geodata as GeoJSON strings in ``net.bus.geo``. When
coordinates are missing, a generic layout is computed with networkx so every
network remains plottable.
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd
import plotly.graph_objects as go

from . import config
from .i18n import tr

#: Loading bins used when colouring lines by result loading.
LOADING_BINS = [(0, 50, "#2ca02c", "< 50 %"), (50, 80, "#ffbf00", "50–80 %"),
                (80, 100, "#ff7f0e", "80–100 %"), (100, np.inf, "#d62728", "> 100 %")]

_LEVEL_PALETTE = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
                  "#8c564b", "#e377c2", "#7f7f7f"]


def has_geodata(net) -> bool:
    geo = net.bus.get("geo")
    return geo is not None and geo.notna().any()


def bus_coordinates(net) -> tuple[pd.DataFrame, str]:
    """(x, y) per bus and the coordinate source (``geographic``/``generic``).

    Parses GeoJSON points from ``net.bus.geo``; if fewer than 90 % of buses
    have valid coordinates, computes a deterministic spring layout instead.
    """
    coords: dict[int, tuple[float, float]] = {}
    geo = net.bus.get("geo")
    if geo is not None:
        for idx, raw in geo.items():
            obj = raw
            if isinstance(obj, str) and obj.strip():
                try:
                    obj = json.loads(obj)
                except (ValueError, TypeError):
                    continue
            if isinstance(obj, dict) and obj.get("type") == "Point":
                x, y = obj["coordinates"][:2]
                coords[idx] = (float(x), float(y))

    if coords and len(coords) >= 0.9 * len(net.bus):
        df = pd.DataFrame.from_dict(coords, orient="index", columns=["x", "y"])
        return df.reindex(net.bus.index), "geographic"

    import networkx as nx
    import pandapower.topology as top

    graph = top.create_nxgraph(net, respect_switches=False)
    pos = nx.spring_layout(graph, seed=42)
    df = pd.DataFrame.from_dict(pos, orient="index", columns=["x", "y"])
    return df.reindex(net.bus.index), "generic"


def _segments(coords: pd.DataFrame, pairs: pd.DataFrame,
              from_col: str, to_col: str) -> tuple[list, list]:
    """x/y arrays with None separators for a set of two-terminal branches."""
    xs: list = []
    ys: list = []
    for _, row in pairs.iterrows():
        a, b = row[from_col], row[to_col]
        if a in coords.index and b in coords.index:
            xs += [coords.at[a, "x"], coords.at[b, "x"], None]
            ys += [coords.at[a, "y"], coords.at[b, "y"], None]
    return xs, ys


def network_figure(net, coords: pd.DataFrame, *, bus_color: str = "voltage_level",
                   line_color: str = "uniform",
                   show_injections: bool = False) -> go.Figure:
    """Interactive topology figure.

    bus_color: ``voltage_level`` | ``vm_pu`` | ``uniform``
    line_color: ``uniform`` | ``loading`` (requires power-flow results)
    """
    large = len(net.line) > config.LARGE_NET_THRESHOLD
    scatter_cls = go.Scattergl if large else go.Scatter
    fig = go.Figure()

    # --- branches -------------------------------------------------------------
    res_line = getattr(net, "res_line", pd.DataFrame())
    if (line_color == "loading" and len(res_line)
            and "loading_percent" in res_line.columns
            and res_line["loading_percent"].notna().any()):
        loading = res_line["loading_percent"].reindex(net.line.index)
        for lo, hi, colour, label in LOADING_BINS:
            mask = (loading >= lo) & (loading < hi)
            if not mask.any():
                continue
            xs, ys = _segments(coords, net.line[mask], "from_bus", "to_bus")
            fig.add_trace(scatter_cls(
                x=xs, y=ys, mode="lines", name=tr("Lines {label}", label=label),
                line=dict(color=colour, width=2), hoverinfo="skip"))
    else:
        xs, ys = _segments(coords, net.line, "from_bus", "to_bus")
        fig.add_trace(scatter_cls(
            x=xs, y=ys, mode="lines", name=tr("Lines"),
            line=dict(color="#888888", width=1.5), hoverinfo="skip"))

    if len(net.trafo):
        xs, ys = _segments(coords, net.trafo, "hv_bus", "lv_bus")
        fig.add_trace(scatter_cls(
            x=xs, y=ys, mode="lines", name=tr("Transformers"),
            line=dict(color="#444444", width=3, dash="dot"), hoverinfo="skip"))

    # --- line hover midpoints (skipped for very large nets) --------------------
    if not large and len(net.line):
        mid_x, mid_y, texts = [], [], []
        for idx, row in net.line.iterrows():
            a, b = row["from_bus"], row["to_bus"]
            if a in coords.index and b in coords.index:
                mid_x.append((coords.at[a, "x"] + coords.at[b, "x"]) / 2)
                mid_y.append((coords.at[a, "y"] + coords.at[b, "y"]) / 2)
                text = tr("Line {idx}: {name}<br>{length:.3f} km, {std_type}",
                          idx=idx, name=row.get('name', ''),
                          length=row['length_km'],
                          std_type=row.get('std_type', ''))
                if len(res_line) and idx in res_line.index \
                        and pd.notna(res_line.at[idx, "loading_percent"]):
                    text += tr("<br>loading: {value:.1f} %",
                               value=res_line.at[idx, 'loading_percent'])
                texts.append(text)
        fig.add_trace(go.Scatter(
            x=mid_x, y=mid_y, mode="markers", name=tr("Line info"),
            marker=dict(size=4, color="rgba(0,0,0,0)"),
            hoverinfo="text", hovertext=texts, showlegend=False))

    # --- buses -------------------------------------------------------------------
    hover = [
        tr("Bus {idx}: {name}<br>{vn:g} kV", idx=idx, name=row['name'],
           vn=row['vn_kv'])
        + (tr("<br>vm = {value:.4f} p.u.", value=net.res_bus.at[idx, 'vm_pu'])
           if len(getattr(net, 'res_bus', ())) and idx in net.res_bus.index
           and pd.notna(net.res_bus.at[idx, "vm_pu"]) else "")
        for idx, row in net.bus.iterrows()
    ]
    bx, by = coords["x"], coords["y"]

    if bus_color == "voltage_level":
        levels = sorted(net.bus["vn_kv"].unique(), reverse=True)
        for i, level in enumerate(levels):
            mask = net.bus["vn_kv"] == level
            fig.add_trace(scatter_cls(
                x=bx[mask], y=by[mask], mode="markers", name=tr("{level:g} kV buses", level=level),
                marker=dict(size=7, color=_LEVEL_PALETTE[i % len(_LEVEL_PALETTE)]),
                hoverinfo="text",
                hovertext=[h for h, m in zip(hover, mask) if m]))
    elif bus_color == "vm_pu" and len(getattr(net, "res_bus", ())):
        vm = net.res_bus["vm_pu"].reindex(net.bus.index)
        fig.add_trace(scatter_cls(
            x=bx, y=by, mode="markers", name=tr("Buses"),
            marker=dict(size=7, color=vm, colorscale="Jet",
                        cmin=0.9, cmax=1.1,
                        colorbar=dict(title="vm [p.u.]", thickness=12)),
            hoverinfo="text", hovertext=hover))
    else:
        fig.add_trace(scatter_cls(
            x=bx, y=by, mode="markers", name=tr("Buses"),
            marker=dict(size=7, color="#1f77b4"),
            hoverinfo="text", hovertext=hover))

    # --- injections overlay ---------------------------------------------------------
    if show_injections:
        for table, symbol, colour, label, singular in (
                ("load", "triangle-down", "#d62728", tr("Loads"), tr("Load")),
                ("sgen", "triangle-up", "#2ca02c", tr("Static generators"),
                 tr("Static generator")),
                ("storage", "square", "#9467bd", tr("Storage"),
                 tr("Storage unit"))):
            df = net.get(table)
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue
            buses = df["bus"]
            fig.add_trace(go.Scatter(
                x=coords["x"].reindex(buses), y=coords["y"].reindex(buses),
                mode="markers", name=label,
                marker=dict(size=10, symbol=symbol, color=colour,
                            line=dict(width=1, color="white")),
                hoverinfo="text",
                hovertext=[tr("{kind} {i}: {name}<br>p = {p:.3f} MW",
                              kind=singular, i=i, name=r.get('name', ''),
                              p=r['p_mw']) for i, r in df.iterrows()]))

    fig.update_layout(
        showlegend=True, height=650, margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(visible=False), yaxis=dict(visible=False, scaleanchor="x"),
        legend=dict(orientation="h", yanchor="bottom", y=1.01),
        hovermode="closest")
    return fig


def bus_neighborhood(net, bus: int) -> dict[str, pd.DataFrame]:
    """All elements electrically attached to a bus, keyed by element table."""
    out: dict[str, pd.DataFrame] = {}
    if len(net.line):
        mask = (net.line["from_bus"] == bus) | (net.line["to_bus"] == bus)
        out["line"] = net.line[mask]
    if len(net.trafo):
        mask = (net.trafo["hv_bus"] == bus) | (net.trafo["lv_bus"] == bus)
        out["trafo"] = net.trafo[mask]
    for table in ("load", "sgen", "gen", "storage", "ext_grid"):
        df = net.get(table)
        if isinstance(df, pd.DataFrame) and len(df):
            out[table] = df[df["bus"] == bus]
    if len(net.switch):
        out["switch"] = net.switch[net.switch["bus"] == bus]
    return {k: v for k, v in out.items() if len(v)}
