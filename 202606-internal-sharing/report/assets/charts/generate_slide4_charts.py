#!/usr/bin/env python3
"""Generate Slide 4 charts: DeFi vs RWA narrative comparison."""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.patches import FancyArrowPatch
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_DIR = Path(__file__).parent

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

RED = "#FF4444"
GREEN = "#00D395"
BLUE = "#4DA6FF"
ORANGE = "#FFA500"
PURPLE = "#8C8DFC"
YELLOW = "#F0B90B"


def fmt_billions(x, _):
    if x >= 1e9:
        return f"${x/1e9:.0f}B"
    if x >= 1e6:
        return f"${x/1e6:.0f}M"
    return f"${x:,.0f}"


def fmt_billions_short(x, _):
    if abs(x) >= 1e9:
        return f"${x/1e9:.1f}B"
    if abs(x) >= 1e6:
        return f"${x/1e6:.0f}M"
    return f"${x:,.0f}"


# ── Chart 1: DeFi TVL vs RWA TVL — Dual-Axis Divergence ──────────────

def plot_defi_vs_rwa():
    """Main comparison: DeFi stagnation vs RWA acceleration."""
    defi = pd.read_csv(DATA_DIR / "slide4-defi-tvl-global.csv", parse_dates=["date"])
    rwa = pd.read_csv(
        DATA_DIR / "rwa-token-timeseries-export-1779895846602.csv",
        parse_dates=["Date"]
    )

    rwa["total"] = rwa.drop(columns=["Timestamp", "Date", "Measure"]).sum(axis=1)
    rwa = rwa[rwa["Date"] >= "2025-05-01"].copy()
    rwa = rwa.rename(columns={"Date": "date"})

    defi = defi[defi["date"] >= "2025-05-01"].sort_values("date")
    rwa = rwa.sort_values("date")

    fig, ax1 = plt.subplots(figsize=(14, 7))

    ax1.plot(defi["date"], defi["tvl_usd"], color=RED, linewidth=2.5,
             label="Global DeFi TVL", alpha=0.9, zorder=5)
    ax1.set_ylabel("DeFi TVL (USD)", color=RED)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_billions))
    ax1.tick_params(axis="y", labelcolor=RED)
    ax1.set_ylim(0, defi["tvl_usd"].max() * 1.15)

    ax2 = ax1.twinx()
    ax2.plot(rwa["date"], rwa["total"], color=GREEN, linewidth=2.5,
             label="On-chain RWA (excl. Stablecoins)", alpha=0.9, zorder=5)
    ax2.fill_between(rwa["date"], 0, rwa["total"], color=GREEN, alpha=0.08)
    ax2.set_ylabel("RWA Value (USD)", color=GREEN)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_billions))
    ax2.tick_params(axis="y", labelcolor=GREEN)
    ax2.set_ylim(0, rwa["total"].max() * 1.15)

    ax1.set_title(
        "DeFi TVL vs On-chain RWA: Diverging Trajectories (May 2025 — May 2026)",
        fontweight="bold", pad=20
    )

    # YoY annotation
    defi_start = defi.iloc[0]["tvl_usd"]
    defi_end = defi.iloc[-1]["tvl_usd"]
    rwa_start = rwa.iloc[0]["total"]
    rwa_end = rwa.iloc[-1]["total"]
    defi_yoy = (defi_end / defi_start - 1) * 100
    rwa_yoy = (rwa_end / rwa_start - 1) * 100

    ax1.annotate(
        f"DeFi YoY: {defi_yoy:+.1f}%\n${defi_start/1e9:.0f}B → ${defi_end/1e9:.0f}B",
        xy=(0.02, 0.95), xycoords="axes fraction",
        fontsize=12, color=RED, fontweight="bold",
        va="top", ha="left",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A1A", edgecolor=RED, alpha=0.9)
    )
    ax2.annotate(
        f"RWA YoY: +{rwa_yoy:.0f}%\n${rwa_start/1e9:.1f}B → ${rwa_end/1e9:.1f}B",
        xy=(0.98, 0.95), xycoords="axes fraction",
        fontsize=12, color=GREEN, fontweight="bold",
        va="top", ha="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A1A", edgecolor=GREEN, alpha=0.9)
    )

    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax1.grid(True, axis="y", linestyle="--", alpha=0.2)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper center", framealpha=0.9)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide4-defi-vs-rwa.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide4-defi-vs-rwa.png")


# ── Chart 2: RWA Category Breakdown — Stacked Area ───────────────────

def plot_rwa_breakdown():
    """RWA growth by asset category (rwa.xyz data)."""
    df = pd.read_csv(
        DATA_DIR / "rwa-token-timeseries-export-1779895846602.csv",
        parse_dates=["Date"]
    )
    df = df[df["Date"] >= "2025-05-01"].copy()
    df = df.sort_values("Date")

    cats = [c for c in df.columns if c not in ["Timestamp", "Date", "Measure"]]
    for c in cats:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    latest = df.iloc[-1]
    cat_totals = {c: latest[c] for c in cats if latest[c] > 0}
    sorted_cats = sorted(cat_totals, key=lambda x: cat_totals[x], reverse=True)

    top_cats = sorted_cats[:6]
    other_cats = sorted_cats[6:]

    cat_colors = {
        "US Treasury Debt": "#4DA6FF",
        "Commodities": YELLOW,
        "Asset-Backed Credit": ORANGE,
        "Specialty Finance": PURPLE,
        "Stocks": "#FF6B6B",
        "non-US Government Debt": "#66BB6A",
    }

    fig, ax = plt.subplots(figsize=(14, 7))

    plot_cats = top_cats.copy()
    plot_data = {}
    for c in plot_cats:
        plot_data[c] = df[c].values
    if other_cats:
        plot_data["Others"] = df[other_cats].sum(axis=1).values
        plot_cats.append("Others")

    colors = [cat_colors.get(c, "#888888") for c in plot_cats]
    if "Others" in plot_cats:
        colors[-1] = "#555555"

    ax.stackplot(
        df["Date"],
        *[plot_data[c] for c in plot_cats],
        labels=plot_cats,
        colors=colors,
        alpha=0.85,
    )

    ax.set_title(
        "On-chain RWA by Asset Category (Source: rwa.xyz, excl. Stablecoins)",
        fontweight="bold", pad=15
    )
    ax.set_ylabel("Bridged Token Value (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_billions))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.2)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
    ax.set_xlim(df["Date"].min(), df["Date"].max())

    total_latest = sum(cat_totals.values())
    ax.annotate(
        f"Total: ${total_latest/1e9:.1f}B",
        xy=(0.98, 0.95), xycoords="axes fraction",
        fontsize=14, color=GREEN, fontweight="bold",
        va="top", ha="right",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1A1A1A", edgecolor=GREEN, alpha=0.9)
    )

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide4-rwa-breakdown.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide4-rwa-breakdown.png")


# ── Chart 3: Blast TVL Collapse (DeFi Case Study) ────────────────────

def plot_blast_collapse():
    """Blast TVL decline — incentive-driven DeFi case study."""
    df = pd.read_csv(DATA_DIR / "slide4-blast-tvl.csv", parse_dates=["date"])
    df = df.sort_values("date")

    fig, ax = plt.subplots(figsize=(12, 5))

    ax.fill_between(df["date"], 0, df["tvl_usd"], color=RED, alpha=0.15)
    ax.plot(df["date"], df["tvl_usd"], color=RED, linewidth=2, alpha=0.9)

    peak_idx = df["tvl_usd"].idxmax()
    peak_row = df.loc[peak_idx]
    ax.annotate(
        f"Peak: ${peak_row['tvl_usd']/1e9:.2f}B\n{peak_row['date'].strftime('%Y-%m-%d')}",
        xy=(peak_row["date"], peak_row["tvl_usd"]),
        xytext=(30, 10), textcoords="offset points",
        fontsize=11, color="#FFFFFF", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#FFFFFF", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1A1A1A", edgecolor=RED)
    )

    latest = df.iloc[-1]
    ax.annotate(
        f"Now: ${latest['tvl_usd']/1e6:.0f}M\n({latest['tvl_usd']/peak_row['tvl_usd']*100:.1f}% of peak)",
        xy=(latest["date"], latest["tvl_usd"]),
        xytext=(-120, 60), textcoords="offset points",
        fontsize=11, color="#FFFFFF", fontweight="bold",
        arrowprops=dict(arrowstyle="->", color="#FFFFFF", lw=1.5),
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#1A1A1A", edgecolor=RED)
    )

    decline_pct = (1 - latest["tvl_usd"] / peak_row["tvl_usd"]) * 100
    ax.set_title(
        f"Blast TVL: Incentive-Driven DeFi Collapse (−{decline_pct:.0f}%)",
        fontweight="bold", pad=15, color=RED
    )
    ax.set_ylabel("TVL (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_billions))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.2)
    ax.set_xlim(df["date"].min(), df["date"].max())

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide4-blast-collapse.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide4-blast-collapse.png")


# ── Chart 4: Top RWA Protocols Growth ─────────────────────────────────

def plot_top_rwa_protocols():
    """Top RWA protocols individual growth trajectories."""
    df = pd.read_csv(DATA_DIR / "slide4-top-rwa-protocols.csv", parse_dates=["date"])

    protocol_colors = {
        "BlackRock BUIDL": "#000000",
        "Ondo OUSG/USDY": BLUE,
        "Circle USYC": "#2775CA",
        "Superstate USTB": ORANGE,
        "Spiko": PURPLE,
    }

    fig, ax = plt.subplots(figsize=(14, 7))

    for proto in df["protocol"].unique():
        sub = df[df["protocol"] == proto].sort_values("date")
        sub["tvl_smooth"] = sub["tvl_usd"].rolling(7, min_periods=1).mean()
        color = protocol_colors.get(proto, "#888888")
        edge_color = "#FFFFFF" if proto == "BlackRock BUIDL" else color
        ax.plot(sub["date"], sub["tvl_smooth"], label=proto,
                color=edge_color, linewidth=2.2, alpha=0.9)

    ax.set_title(
        "Top Tokenized Treasury / RWA Protocols — TVL Growth (Past 12 Months)",
        fontweight="bold", pad=15
    )
    ax.set_ylabel("TVL (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(fmt_billions_short))
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
    ax.grid(True, axis="y", linestyle="--", alpha=0.2)
    ax.legend(loc="upper left", framealpha=0.9, fontsize=10)
    ax.set_xlim(df["date"].min(), df["date"].max())

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide4-top-rwa-protocols.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide4-top-rwa-protocols.png")


# ── Chart 5: DeFi vs RWA Growth Rate Comparison Bar ───────────────────

def plot_growth_comparison():
    """YoY growth rate comparison: DeFi metrics vs RWA metrics."""
    defi = pd.read_csv(DATA_DIR / "slide4-defi-tvl-global.csv", parse_dates=["date"])
    rwa = pd.read_csv(
        DATA_DIR / "rwa-token-timeseries-export-1779895846602.csv",
        parse_dates=["Date"]
    )

    rwa_cols = [c for c in rwa.columns if c not in ["Timestamp", "Date", "Measure"]]
    for c in rwa_cols:
        rwa[c] = pd.to_numeric(rwa[c], errors="coerce").fillna(0)
    rwa["total"] = rwa[rwa_cols].sum(axis=1)

    defi_start = defi.iloc[0]["tvl_usd"]
    defi_end = defi.iloc[-1]["tvl_usd"]
    defi_peak = defi["tvl_usd"].max()

    rwa_may25 = rwa[rwa["Date"] >= "2025-05-01"].iloc[0]
    rwa_latest = rwa.iloc[-1]
    rwa_start = rwa_may25["total"]
    rwa_end = rwa_latest["total"]

    rwa_treasury_start = rwa_may25["US Treasury Debt"]
    rwa_treasury_end = rwa_latest["US Treasury Debt"]

    buidl = pd.read_csv(DATA_DIR / "slide4-buidl-tvl.csv", parse_dates=["date"])
    buidl_13m = buidl[buidl["date"] >= "2025-05-01"]
    buidl_start = buidl_13m.iloc[0]["tvl_usd"]
    buidl_end = buidl_13m.iloc[-1]["tvl_usd"]

    aave = pd.read_csv(DATA_DIR / "slide4-aave-tvl.csv", parse_dates=["date"])
    aave_start = aave.iloc[0]["tvl_usd"]
    aave_end = aave.iloc[-1]["tvl_usd"]

    labels = [
        "Global\nDeFi TVL",
        "Aave V3\nTVL",
        "Blast\nTVL",
        "On-chain\nRWA Total",
        "US Treasury\nTokenized",
        "BlackRock\nBUILD",
    ]

    blast = pd.read_csv(DATA_DIR / "slide4-blast-tvl.csv", parse_dates=["date"])
    blast_13m = blast[blast["date"] >= "2025-05-01"]
    blast_start = blast_13m.iloc[0]["tvl_usd"] if len(blast_13m) > 0 else blast.iloc[0]["tvl_usd"]
    blast_end = blast_13m.iloc[-1]["tvl_usd"] if len(blast_13m) > 0 else blast.iloc[-1]["tvl_usd"]

    values = [
        (defi_end / defi_start - 1) * 100,
        (aave_end / aave_start - 1) * 100,
        (blast_end / blast_start - 1) * 100,
        (rwa_end / rwa_start - 1) * 100,
        (rwa_treasury_end / rwa_treasury_start - 1) * 100,
        (buidl_end / buidl_start - 1) * 100,
    ]

    colors = [RED if v < 0 else GREEN for v in values]

    fig, ax = plt.subplots(figsize=(14, 7))
    bars = ax.bar(labels, values, color=colors, edgecolor="none", width=0.6, alpha=0.85)

    for bar, val in zip(bars, values):
        h = bar.get_height()
        offset = 5 if h >= 0 else -5
        va = "bottom" if h >= 0 else "top"
        ax.text(bar.get_x() + bar.get_width() / 2, h + offset,
                f"{val:+.0f}%", ha="center", va=va,
                fontsize=13, fontweight="bold", color="#FFFFFF")

    ax.axhline(y=0, color="#666666", linewidth=0.8)

    ax.axvline(x=2.5, color="#444444", linewidth=1, linestyle="--")
    ax.text(1.0, max(values) * 0.95, "DeFi", fontsize=16, color=RED,
            fontweight="bold", ha="center", alpha=0.6)
    ax.text(4.0, max(values) * 0.95, "RWA", fontsize=16, color=GREEN,
            fontweight="bold", ha="center", alpha=0.6)

    ax.set_title("YoY Growth: DeFi Stagnation vs RWA Acceleration (May 2025 → May 2026)",
                 fontweight="bold", pad=15)
    ax.set_ylabel("Year-over-Year Change (%)")
    ax.grid(True, axis="y", linestyle="--", alpha=0.2)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide4-growth-comparison.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide4-growth-comparison.png")


# ── Chart 6: RWA Category YoY Growth Rates ────────────────────────────

def plot_rwa_category_growth():
    """Individual RWA category YoY growth rates."""
    df = pd.read_csv(
        DATA_DIR / "rwa-token-timeseries-export-1779895846602.csv",
        parse_dates=["Date"]
    )

    cats = [c for c in df.columns if c not in ["Timestamp", "Date", "Measure"]]
    for c in cats:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

    may25 = df[df["Date"] >= "2025-05-01"].iloc[0]
    latest = df.iloc[-1]

    growth_data = []
    for c in cats:
        start = may25[c]
        end = latest[c]
        if start > 1e6 and end > 1e6:
            yoy = (end / start - 1) * 100
            growth_data.append((c, yoy, end))

    growth_data.sort(key=lambda x: x[1], reverse=True)

    cat_short = {
        "US Treasury Debt": "US Treasury",
        "non-US Government Debt": "non-US Gov Debt",
        "Corporate Credit": "Corp Credit",
        "Stocks": "Stocks",
        "Private Equity": "Private Equity",
        "Real Estate": "Real Estate",
        "Commodities": "Commodities",
        "Diversified Credit": "Diversified Credit",
        "Asset-Backed Credit": "Asset-Backed",
        "Active Strategies": "Active Strategies",
        "Specialty Finance": "Specialty Finance",
        "Venture Capital": "Venture Capital",
    }

    fig, ax = plt.subplots(figsize=(12, 7))

    names = [cat_short.get(g[0], g[0]) for g in growth_data]
    values = [g[1] for g in growth_data]
    sizes = [g[2] for g in growth_data]

    colors = [GREEN if v > 100 else BLUE if v > 0 else RED for v in values]

    bars = ax.barh(names[::-1], values[::-1], color=colors[::-1], alpha=0.85, height=0.6)

    for bar, val, sz in zip(bars, values[::-1], sizes[::-1]):
        w = bar.get_width()
        ax.text(w + 15, bar.get_y() + bar.get_height() / 2,
                f"+{val:.0f}% (${sz/1e9:.1f}B)" if val > 0 else f"{val:.0f}%",
                ha="left", va="center", fontsize=10, color="#CCCCCC")

    ax.set_title("RWA Category Growth Rates — YoY (Source: rwa.xyz)",
                 fontweight="bold", pad=15)
    ax.set_xlabel("Year-over-Year Change (%)")
    ax.axvline(x=0, color="#666666", linewidth=0.8)
    ax.grid(True, axis="x", linestyle="--", alpha=0.2)

    fig.tight_layout()
    fig.savefig(OUT_DIR / "slide4-rwa-category-growth.png", dpi=200)
    plt.close(fig)
    print("  ✓ slide4-rwa-category-growth.png")


if __name__ == "__main__":
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print("Generating Slide 4 charts...")
    plot_defi_vs_rwa()
    plot_rwa_breakdown()
    plot_blast_collapse()
    plot_top_rwa_protocols()
    plot_growth_comparison()
    plot_rwa_category_growth()
    print("Done — all charts saved to", OUT_DIR)
