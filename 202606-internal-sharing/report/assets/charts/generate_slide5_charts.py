#!/usr/bin/env python3
"""Generate Slide 5 charts: Mantle TVL+DAU combined, Protocol breakdown."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_DIR = Path(__file__).parent

MANTLE_GREEN = "#00D395"
RED = "#FF4444"
BLUE = "#4DA6FF"
ORANGE = "#FFA500"
PURPLE = "#8C8DFC"
YELLOW = "#F0B90B"

plt.rcParams.update({
    "figure.facecolor": "#0A0A0A",
    "axes.facecolor": "#0A0A0A",
    "axes.edgecolor": "#333333",
    "axes.labelcolor": "#CCCCCC",
    "text.color": "#FFFFFF",
    "xtick.color": "#999999",
    "ytick.color": "#999999",
    "grid.color": "#1A1A1A",
    "grid.alpha": 0.8,
    "legend.facecolor": "#111111",
    "legend.edgecolor": "#333333",
    "legend.labelcolor": "#CCCCCC",
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
})


def fmt_millions(x, _):
    if x >= 1e9:
        return f"${x/1e9:.1f}B"
    if x >= 1e6:
        return f"${x/1e6:.0f}M"
    return f"${x:,.0f}"


def fmt_thousands(x, _):
    if x >= 1e6:
        return f"{x/1e6:.1f}M"
    if x >= 1e3:
        return f"{x/1e3:.0f}K"
    return f"{x:.0f}"


# ── Chart 1: Mantle TVL + DAU Combined Dual-Axis ─────────────────────

def plot_tvl_dau_combined():
    """TVL (green, left) and DAU (red, right) on same chart — divergence visible."""
    tvl = pd.read_csv(DATA_DIR / "slide3-tvl-daily.csv", parse_dates=["date"])
    m_tvl = tvl[tvl["blockchain"] == "Mantle"].sort_values("date").copy()

    dau = pd.read_csv(DATA_DIR / "slide3-dau-daily.csv", parse_dates=["date"])
    m_dau = dau[dau["blockchain"] == "mantle"].sort_values("date").copy()
    m_dau["dau_smooth"] = m_dau["dau"].rolling(7, min_periods=1).mean()

    fig, ax1 = plt.subplots(figsize=(14, 7))

    # TVL — left axis (green)
    ax1.fill_between(m_tvl["date"], 0, m_tvl["tvl_usd"], color=MANTLE_GREEN, alpha=0.1)
    ax1.plot(m_tvl["date"], m_tvl["tvl_usd"], color=MANTLE_GREEN, linewidth=2.5,
             label="TVL", alpha=0.9, zorder=5)
    ax1.set_ylabel("TVL (USD)", color=MANTLE_GREEN, fontsize=12)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax1.tick_params(axis="y", labelcolor=MANTLE_GREEN)
    ax1.set_ylim(0, m_tvl["tvl_usd"].max() * 1.15)

    # DAU — right axis (red)
    ax2 = ax1.twinx()
    ax2.plot(m_dau["date"], m_dau["dau_smooth"], color=RED, linewidth=2.5,
             label="DAU (7d avg)", alpha=0.9, zorder=5)
    ax2.set_ylabel("Daily Active Users (7d MA)", color=RED, fontsize=12)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_thousands))
    ax2.tick_params(axis="y", labelcolor=RED)
    ax2.set_ylim(0, m_dau["dau_smooth"].max() * 1.15)

    ax1.set_title("Mantle: TVL vs DAU — TVL Recovers but Users Keep Leaving",
                   fontweight="bold", pad=20)

    # Aave V3 launch annotation
    aave_launch = pd.Timestamp("2026-02-19")
    ax1.axvline(x=aave_launch, color="#FFFFFF", linewidth=1, linestyle="--", alpha=0.5, zorder=3)
    ax1.annotate(
        "Aave V3\nLaunch",
        xy=(aave_launch, m_tvl["tvl_usd"].max() * 0.95),
        fontsize=11, color="#FFFFFF", fontweight="bold",
        ha="center", va="top",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1A1A1A", edgecolor=BLUE, alpha=0.9)
    )

    # TVL annotation
    tvl_start = m_tvl.iloc[0]["tvl_usd"]
    tvl_end = m_tvl.iloc[-1]["tvl_usd"]
    tvl_peak = m_tvl["tvl_usd"].max()
    ax1.annotate(
        f"TVL: ${tvl_start/1e6:.0f}M → peak ${tvl_peak/1e6:.0f}M → ${tvl_end/1e6:.0f}M\nYoY: {(tvl_end/tvl_start-1)*100:+.1f}%",
        xy=(0.02, 0.18), xycoords="axes fraction",
        fontsize=11, color=MANTLE_GREEN, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A1A", edgecolor=MANTLE_GREEN, alpha=0.9)
    )

    # DAU annotation
    dau_start = m_dau.iloc[0]["dau"]
    dau_end = m_dau.iloc[-1]["dau"]
    ax2.annotate(
        f"DAU: {dau_start:,.0f} → {dau_end:,.0f}\nYoY: {(dau_end/dau_start-1)*100:.0f}%",
        xy=(0.98, 0.18), xycoords="axes fraction",
        fontsize=11, color=RED, fontweight="bold", ha="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A1A", edgecolor=RED, alpha=0.9)
    )

    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax1.grid(True, axis="y", linestyle="--", alpha=0.15)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", framealpha=0.9)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide5-tvl-dau-combined.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide5-tvl-dau-combined.png")


# ── Chart 2: Mantle Protocol TVL Stacked Area ────────────────────────

def plot_protocol_breakdown():
    """Stacked area showing native DeFi decline + Aave V3 spike."""
    df = pd.read_csv(DATA_DIR / "slide5-mantle-protocols-tvl.csv", parse_dates=["date"])

    # Exclude Bybit (CEX custodial, not DeFi TVL)
    df = df[df["protocol"] != "Bybit"].copy()

    proto_colors = {
        "Merchant Moe": "#E85D04",
        "Agni Finance": "#DC2F02",
        "Aave V3": BLUE,
        "CIAN Yield Layer": ORANGE,
        "MI4 (Mantle Index Four)": MANTLE_GREEN,
        "Ondo USDY": PURPLE,
    }

    # Stack order: native DEXes at bottom (decline visible), Aave on top (spike visible)
    proto_order = [
        "Merchant Moe", "Agni Finance",
        "CIAN Yield Layer", "MI4 (Mantle Index Four)", "Ondo USDY",
        "Aave V3",
    ]

    # Pivot to wide format
    pivot = df.pivot_table(index="date", columns="protocol", values="tvl_usd", aggfunc="first")
    pivot = pivot.sort_index().fillna(0)

    for p in proto_order:
        if p not in pivot.columns:
            pivot[p] = 0

    pivot = pivot[proto_order]

    # 3-day smooth
    pivot = pivot.rolling(3, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(14, 7))

    colors = [proto_colors.get(p, "#888888") for p in proto_order]
    ax.stackplot(
        pivot.index,
        *[pivot[p].values for p in proto_order],
        labels=proto_order,
        colors=colors,
        alpha=0.8,
    )

    # Aave V3 launch line
    aave_launch = pd.Timestamp("2026-02-19")
    ax.axvline(x=aave_launch, color="#FFFFFF", linewidth=1, linestyle="--", alpha=0.5)
    ax.annotate(
        "Aave V3 Launch\n2026-02-19",
        xy=(aave_launch, pivot.sum(axis=1).max() * 0.92),
        fontsize=10, color="#FFFFFF", fontweight="bold",
        ha="left",
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1A1A1A", edgecolor=BLUE, alpha=0.9)
    )

    # Peak annotation
    total = pivot.sum(axis=1)
    peak_date = total.idxmax()
    peak_val = total.max()
    ax.annotate(
        f"Peak: ${peak_val/1e6:.0f}M",
        xy=(peak_date, peak_val),
        xytext=(20, 10), textcoords="offset points",
        fontsize=11, color="#FFFFFF", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#FFFFFF", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1A1A1A", edgecolor="#FFFFFF")
    )

    # Aave V3 share annotation at peak
    aave_at_peak = pivot.loc[peak_date, "Aave V3"]
    aave_share = aave_at_peak / peak_val * 100
    ax.annotate(
        f"Aave V3 = {aave_share:.0f}% of total at peak",
        xy=(0.98, 0.12), xycoords="axes fraction",
        fontsize=11, color=BLUE, fontweight="bold", ha="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A1A", edgecolor=BLUE, alpha=0.9)
    )

    # Native DEX decline annotation
    moe_start = pivot["Merchant Moe"].iloc[:30].mean()
    moe_end = pivot["Merchant Moe"].iloc[-30:].mean()
    agni_start = pivot["Agni Finance"].iloc[:30].mean()
    agni_end = pivot["Agni Finance"].iloc[-30:].mean()
    ax.annotate(
        f"Native DEX decline:\n"
        f"Merchant Moe ${moe_start/1e6:.0f}M → ${moe_end/1e6:.0f}M ({(moe_end/moe_start-1)*100:+.0f}%)\n"
        f"Agni Finance ${agni_start/1e6:.0f}M → ${agni_end/1e6:.0f}M ({(agni_end/agni_start-1)*100:+.0f}%)",
        xy=(0.02, 0.05), xycoords="axes fraction",
        fontsize=10, color=RED, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A1A", edgecolor=RED, alpha=0.9)
    )

    ax.set_title("Mantle DeFi Protocol TVL — Native DEXes Shrinking, Aave V3 Spike Fading",
                 fontweight="bold", pad=15)
    ax.set_ylabel("Protocol TVL on Mantle (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_millions))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.2)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
    ax.set_xlim(pivot.index.min(), pivot.index.max())

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide5-protocol-breakdown.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide5-protocol-breakdown.png")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating Slide 5 charts...")
    plot_tvl_dau_combined()
    plot_protocol_breakdown()
    print("Done — all charts saved to", OUT_DIR)
