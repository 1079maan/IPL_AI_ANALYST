"""
charts.py — Automatic Plotly chart generation for IPL Nexus Chat.
Matches the Neon Stadium design system from style.py.
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from typing import Optional

# ── Design tokens (mirror style.py) ──────────────────────────────────────────
ORANGE   = "#FF4D00"
ORANGE2  = "#FF7A30"
CYAN     = "#00F0FF"
CYAN2    = "#00B8CC"
VOID     = "#06060A"
VOID2    = "#0C0C14"
VOID3    = "#12121E"
TEXT     = "#E8ECF4"
MUTED    = "#5A6080"
MUTED2   = "#8892AA"

# Neon colour palette for multi-series
PALETTE = [ORANGE, CYAN, "#FFD700", "#00E676", "#7B61FF",
           "#FF4081", "#00BCD4", "#FF6D00", "#69F0AE", "#40C4FF"]

LAYOUT_BASE = dict(
    paper_bgcolor=VOID2,
    plot_bgcolor=VOID3,
    font=dict(family="Barlow Condensed, sans-serif", color=TEXT, size=13),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(
        bgcolor=VOID3,
        bordercolor=ORANGE,
        font=dict(family="Barlow Condensed, sans-serif", color=TEXT),
    ),
    xaxis=dict(
        showgrid=False,
        linecolor=MUTED,
        tickcolor=MUTED,
        tickfont=dict(size=11),
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.04)",
        linecolor=MUTED,
        tickfont=dict(size=11),
        zeroline=False,
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor=MUTED,
        borderwidth=0,
        font=dict(size=11),
    ),
)


def _apply_base(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**LAYOUT_BASE, title=dict(
        text=title,
        font=dict(family="Orbitron, sans-serif", color=TEXT, size=14),
        x=0,
    ))
    return fig


# ── Individual chart builders ─────────────────────────────────────────────────

def make_bar(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y],
        marker=dict(
            color=df[y],
            colorscale=[[0, ORANGE], [1, CYAN]],
            showscale=False,
            line=dict(width=0),
        ),
        hovertemplate=f"<b>%{{x}}</b><br>{y}: %{{y:,}}<extra></extra>",
    ))
    fig.update_xaxes(tickangle=-35)
    return _apply_base(fig, title or f"{y} by {x}")


def make_horizontal_bar(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    """Better for long category names (player names etc.)."""
    df_sorted = df.sort_values(y)
    fig = go.Figure(go.Bar(
        x=df_sorted[y], y=df_sorted[x],
        orientation="h",
        marker=dict(
            color=df_sorted[y],
            colorscale=[[0, ORANGE2], [1, CYAN]],
            showscale=False,
        ),
        hovertemplate=f"<b>%{{y}}</b><br>{y}: %{{x:,}}<extra></extra>",
    ))
    fig.update_layout(height=max(300, len(df) * 35))
    return _apply_base(fig, title or f"{y} by {x}")


def make_line(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df[x], y=df[y],
        mode="lines+markers",
        line=dict(color=ORANGE, width=2.5),
        marker=dict(color=CYAN, size=7, line=dict(color=ORANGE, width=1.5)),
        fill="tozeroy",
        fillcolor="rgba(255,77,0,0.07)",
        hovertemplate=f"<b>%{{x}}</b><br>{y}: %{{y:,}}<extra></extra>",
    ))
    return _apply_base(fig, title or f"{y} over {x}")


def make_pie(df: pd.DataFrame, names: str, values: str, title: str = "") -> go.Figure:
    fig = go.Figure(go.Pie(
        labels=df[names], values=df[values],
        hole=0.42,
        marker=dict(
            colors=PALETTE[:len(df)],
            line=dict(color=VOID2, width=2),
        ),
        textfont=dict(family="Barlow Condensed, sans-serif", color=TEXT),
        hovertemplate="<b>%{label}</b><br>%{value:,} (%{percent})<extra></extra>",
    ))
    fig.update_layout(**LAYOUT_BASE, title=dict(
        text=title or f"{values} distribution",
        font=dict(family="Orbitron, sans-serif", color=TEXT, size=14), x=0,
    ), showlegend=True)
    return fig


def make_scatter(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df[x], y=df[y],
        mode="markers",
        marker=dict(
            color=df[y] if pd.api.types.is_numeric_dtype(df[y]) else ORANGE,
            colorscale=[[0, ORANGE], [1, CYAN]],
            size=9, opacity=0.8,
            line=dict(color=VOID2, width=1),
        ),
        hovertemplate=f"{x}: %{{x}}<br>{y}: %{{y:,}}<extra></extra>",
    ))
    return _apply_base(fig, title or f"{y} vs {x}")


# ── Auto-dispatcher ────────────────────────────────────────────────────────────

def auto_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_col: Optional[str],
    y_col: Optional[str],
    title: str = "",
) -> Optional[go.Figure]:
    """
    Generate the best chart automatically.
    Returns None when no chart is appropriate.
    """
    if df is None or df.empty or chart_type == "none":
        return None
    if len(df) < 2:
        return None  # single-row result: show table only

    # Resolve columns
    cols = list(df.columns)

    def _pick(hint: Optional[str], prefer_numeric: bool = False) -> Optional[str]:
        if hint and hint in cols:
            return hint
        # Guess: first numeric col for y, first text col for x
        if prefer_numeric:
            num = [c for c in cols if pd.api.types.is_numeric_dtype(df[c])]
            return num[0] if num else (cols[-1] if cols else None)
        else:
            text = [c for c in cols if not pd.api.types.is_numeric_dtype(df[c])]
            return text[0] if text else (cols[0] if cols else None)

    x = _pick(x_col, prefer_numeric=False)
    y = _pick(y_col, prefer_numeric=True)

    if not x or not y or x == y:
        return None

    ct = (chart_type or "bar").lower()

    # For bar charts, use horizontal when names are long
    if ct == "bar":
        max_name_len = df[x].astype(str).str.len().max() if x in df else 0
        if max_name_len > 12 or len(df) >= 8:
            return make_horizontal_bar(df, x, y, title)
        return make_bar(df, x, y, title)
    elif ct == "line":
        return make_line(df, x, y, title)
    elif ct == "pie":
        return make_pie(df, x, y, title)
    elif ct == "scatter":
        return make_scatter(df, x, y, title)
    else:
        return make_bar(df, x, y, title)
