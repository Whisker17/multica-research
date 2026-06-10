#!/usr/bin/env python3
"""Generate Slide 3 charts: TVL, DAU, Median Fees — line + pie charts."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_DIR = Path(__file__).parent

CHAIN_COLORS = {
    "Base": "#0052FF",
    "base": "#0052FF",
    "Arbitrum": "#28A0F0",
    "arbitrum": "#28A0F0",
    "OP Mainnet": "#FF0420",
    "optimism": "#FF0420",
    "Mantle": "#00D395",
    "mantle": "#00D395",
    "zkSync Era": "#8C8DFC",
    "zksync": "#8C8DFC",
    "X Layer": "#F0B90B",
    "xlayer": "#F0B90B",
}

CHAIN_DISPLAY = {
    "base": "Base",
    "arbitrum": "Arbitrum",
    "optimism": "OP Mainnet",
    "mantle": "Mantle",
    "zksync": "zkSync Era",
    "xlayer": "X Layer",
    "Base": "Base",
    "Arbitrum": "Arbitrum",
    "OP Mainnet": "OP Mainnet",
    "Mantle": "Mantle",
    "zkSync Era": "zkSync Era",
    "X Layer": "X Layer",
}

CHAIN_ORDER = ["Base", "Arbitrum", "OP Mainnet", "Mantle", "zkSync Era", "X Layer"]

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


def emphasize_mantle(ax, chain_name):
    """Make Mantle lines thicker and more prominent."""
    return 3.0 if "Mantle" in chain_name or "mantle" in chain_name else 1.5


def fmt_billions(x, _):
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


# ── TVL Charts ──────────────────────────────────────────────────────────

def plot_tvl_line():
    df = pd.read_csv(DATA_DIR / "slide3-tvl-daily.csv", parse_dates=["date"])
    df["display"] = df["blockchain"].map(CHAIN_DISPLAY)

    fig, ax = plt.subplots(figsize=(14, 7))
    for chain in CHAIN_ORDER:
        sub = df[df["display"] == chain].sort_values("date")
        if sub.empty:
            continue
        lw = emphasize_mantle(ax, chain)
        zorder = 10 if "Mantle" in chain else 5
        ax.plot(sub["date"], sub["tvl_usd"], label=chain,
                color=CHAIN_COLORS.get(chain, "#888"),
                linewidth=lw, zorder=zorder, alpha=0.95 if "Mantle" in chain else 0.8)

    ax.set_title("L2 TVL Trend (Past 12 Months)", fontweight="bold", pad=15)
    ax.set_ylabel("Total Value Locked (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_billions))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_xlim(df["date"].min(), df["date"].max())
    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide3-tvl-line.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide3-tvl-line.png")


def plot_tvl_pie():
    df = pd.read_csv(DATA_DIR / "slide3-tvl-daily.csv", parse_dates=["date"])
    idx = df.groupby("blockchain")["date"].idxmax()
    latest = df.loc[idx].copy()
    latest["display"] = latest["blockchain"].map(CHAIN_DISPLAY)

    totals = latest.set_index("display")["tvl_usd"].reindex(CHAIN_ORDER).fillna(0)
    colors = [CHAIN_COLORS.get(c, "#888") for c in CHAIN_ORDER]

    explode = [0.05 if c == "Mantle" else 0 for c in CHAIN_ORDER]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        totals, labels=CHAIN_ORDER, colors=colors, autopct="%1.1f%%",
        startangle=90, explode=explode,
        textprops={"color": "#FFFFFF", "fontsize": 11},
        pctdistance=0.75, labeldistance=1.1
    )
    for i, chain in enumerate(CHAIN_ORDER):
        if chain == "Mantle":
            autotexts[i].set_fontweight("bold")
            autotexts[i].set_fontsize(13)
            texts[i].set_fontweight("bold")
            texts[i].set_fontsize(13)

    ax.set_title("L2 TVL Market Share (Latest Snapshot)", fontweight="bold", pad=15)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide3-tvl-pie.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide3-tvl-pie.png")


# ── DAU Charts ──────────────────────────────────────────────────────────

def plot_dau_line():
    df = pd.read_csv(DATA_DIR / "slide3-dau-daily.csv", parse_dates=["date"])
    df["display"] = df["blockchain"].map(CHAIN_DISPLAY)

    # 7-day rolling average for smoother lines
    fig, ax = plt.subplots(figsize=(14, 7))
    for chain in CHAIN_ORDER:
        sub = df[df["display"] == chain].sort_values("date").copy()
        if sub.empty:
            continue
        sub["dau_smooth"] = sub["dau"].rolling(7, min_periods=1).mean()
        lw = emphasize_mantle(ax, chain)
        zorder = 10 if "Mantle" in chain else 5
        ax.plot(sub["date"], sub["dau_smooth"], label=chain,
                color=CHAIN_COLORS.get(chain, "#888"),
                linewidth=lw, zorder=zorder, alpha=0.95 if "Mantle" in chain else 0.8)

    ax.set_title("L2 Daily Active Users — 7d Moving Average (Past 12 Months)", fontweight="bold", pad=15)
    ax.set_ylabel("Daily Active Users")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_thousands))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_xlim(df["date"].min(), df["date"].max())
    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide3-dau-line.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide3-dau-line.png")


def plot_dau_pie():
    df = pd.read_csv(DATA_DIR / "slide3-dau-daily.csv", parse_dates=["date"])
    # Use May 2026 average
    may = df[df["date"] >= "2026-05-01"]
    avg_dau = may.groupby("blockchain")["dau"].mean()
    avg_dau.index = avg_dau.index.map(CHAIN_DISPLAY)
    avg_dau = avg_dau.reindex([c for c in CHAIN_ORDER if c in avg_dau.index]).fillna(0)

    colors = [CHAIN_COLORS.get(c, "#888") for c in avg_dau.index]
    explode = [0.05 if c == "Mantle" else 0 for c in avg_dau.index]

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        avg_dau, labels=avg_dau.index, colors=colors, autopct="%1.1f%%",
        startangle=90, explode=explode,
        textprops={"color": "#FFFFFF", "fontsize": 11},
        pctdistance=0.75, labeldistance=1.1
    )
    for i, chain in enumerate(avg_dau.index):
        if chain == "Mantle":
            autotexts[i].set_fontweight("bold")
            autotexts[i].set_fontsize(13)
            texts[i].set_fontweight("bold")
            texts[i].set_fontsize(13)

    ax.set_title("L2 DAU Market Share (May 2026 Avg)\nX Layer: data unavailable",
                 fontweight="bold", pad=15)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide3-dau-pie.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide3-dau-pie.png")


# ── Fees Charts ─────────────────────────────────────────────────────────

def plot_fees_line():
    df = pd.read_csv(DATA_DIR / "slide3-median-fees-daily.csv", parse_dates=["date"])
    df["display"] = df["blockchain"].map(CHAIN_DISPLAY)

    fig, ax = plt.subplots(figsize=(14, 7))
    for chain in CHAIN_ORDER:
        sub = df[df["display"] == chain].sort_values("date").copy()
        if sub.empty:
            continue
        # 7-day rolling to smooth spikes
        sub["fee_smooth"] = sub["median_fee_usd"].rolling(7, min_periods=1).mean()
        lw = emphasize_mantle(ax, chain)
        zorder = 10 if "Mantle" in chain else 5
        ax.plot(sub["date"], sub["fee_smooth"], label=chain,
                color=CHAIN_COLORS.get(chain, "#888"),
                linewidth=lw, zorder=zorder, alpha=0.95 if "Mantle" in chain else 0.8)

    ax.set_title("L2 Median Transaction Fee — 7d Moving Average (Past 12 Months)",
                 fontweight="bold", pad=15)
    ax.set_ylabel("Median Fee (USD)")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"${x:.4f}" if x < 0.01 else f"${x:.3f}" if x < 1 else f"${x:.2f}"
    ))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.9)
    ax.set_xlim(df["date"].min(), df["date"].max())
    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide3-fees-line.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide3-fees-line.png")


def plot_fees_bar():
    """Bar chart of latest month median fees for comparison."""
    df = pd.read_csv(DATA_DIR / "slide3-median-fees-daily.csv", parse_dates=["date"])
    df["display"] = df["blockchain"].map(CHAIN_DISPLAY)
    may = df[df["date"] >= "2026-05-01"]
    avg_fee = may.groupby("display")["median_fee_usd"].mean()
    avg_fee = avg_fee.reindex(CHAIN_ORDER).fillna(0)

    colors = [CHAIN_COLORS.get(c, "#888") for c in CHAIN_ORDER]
    edge_colors = ["#FFFFFF" if c == "Mantle" else "none" for c in CHAIN_ORDER]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(CHAIN_ORDER, avg_fee, color=colors, edgecolor=edge_colors, linewidth=2)

    for bar, chain in zip(bars, CHAIN_ORDER):
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h * 1.1,
                f"${h:.5f}" if h < 0.001 else f"${h:.4f}" if h < 0.01 else f"${h:.3f}",
                ha="center", va="bottom", fontsize=10, color="#FFFFFF",
                fontweight="bold" if chain == "Mantle" else "normal")

    ax.set_title("L2 Median Transaction Fee Comparison (May 2026 Avg)",
                 fontweight="bold", pad=15)
    ax.set_ylabel("Median Fee (USD)")
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(
        lambda x, _: f"${x:.5f}" if x < 0.001 else f"${x:.4f}" if x < 0.01 else f"${x:.3f}"
    ))
    ax.grid(True, axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide3-fees-bar.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide3-fees-bar.png")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating Slide 3 charts...")
    plot_tvl_line()
    plot_tvl_pie()
    plot_dau_line()
    plot_dau_pie()
    plot_fees_line()
    plot_fees_bar()
    print("Done — all charts saved to", OUT_DIR)
