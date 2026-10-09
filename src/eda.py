"""
eda.py
------
Exploratory Data Analysis module.
Generates and saves all EDA plots to reports/figures/.
Can be run standalone or imported by the dashboard.
"""

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

warnings.filterwarnings("ignore")

# ── Style ─────────────────────────────────────────────────
sns.set_theme(style="darkgrid", palette="husl")
plt.rcParams.update({"figure.dpi": 120, "font.family": "DejaVu Sans"})

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIGURES_DIR  = PROJECT_ROOT / "reports" / "figures"
CLEAN_PATH   = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"


def _save(fig: plt.Figure, name: str) -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    path = FIGURES_DIR / f"{name}.png"
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


# ──────────────────────────────────────────────────────────
# Individual EDA plots
# ──────────────────────────────────────────────────────────
def plot_monthly_sales(df: pd.DataFrame) -> Path:
    monthly = df.groupby("Month")[["Sales","Profit"]].sum().reset_index()
    monthly = monthly.sort_values("Month")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(monthly["Month"], monthly["Sales"],  marker="o", label="Revenue", linewidth=2)
    ax.plot(monthly["Month"], monthly["Profit"], marker="s", label="Profit",  linewidth=2, linestyle="--")
    ax.set_title("Monthly Revenue & Profit Trend", fontsize=15, fontweight="bold")
    ax.set_xlabel("Month"); ax.set_ylabel("Amount (₹)")
    ax.tick_params(axis="x", rotation=45)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    ax.legend(); fig.tight_layout()
    return _save(fig, "monthly_sales")


def plot_category_sales(df: pd.DataFrame) -> Path:
    cat = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=cat.values, y=cat.index, ax=ax, palette="Blues_r")
    ax.set_title("Revenue by Category", fontsize=15, fontweight="bold")
    ax.set_xlabel("Revenue (₹)"); ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    for bar, val in zip(ax.patches, cat.values):
        ax.text(bar.get_width() + cat.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"₹{val/1e6:.1f}M", va="center", fontsize=9)
    fig.tight_layout()
    return _save(fig, "category_sales")


def plot_state_sales(df: pd.DataFrame) -> Path:
    state = df.groupby("State")["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(11, 5))
    sns.barplot(x=state.values, y=state.index, ax=ax, palette="Greens_r")
    ax.set_title("Revenue by State", fontsize=15, fontweight="bold")
    ax.set_xlabel("Revenue (₹)"); ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    fig.tight_layout()
    return _save(fig, "state_sales")


def plot_profit_margin_by_category(df: pd.DataFrame) -> Path:
    pm = df.groupby("Category").apply(
        lambda x: x["Profit"].sum() / x["Sales"].sum() * 100
    ).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(pm.index, pm.values, color=sns.color_palette("RdYlGn", len(pm)))
    ax.set_title("Profit Margin by Category (%)", fontsize=15, fontweight="bold")
    ax.set_xlabel("Profit Margin (%)")
    for bar, val in zip(ax.patches, pm.values):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", va="center", fontsize=9)
    fig.tight_layout()
    return _save(fig, "profit_margin_category")


def plot_gender_distribution(df: pd.DataFrame) -> Path:
    gender = df.groupby("Gender")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(gender.values, labels=gender.index, autopct="%1.1f%%",
           colors=["#6C63FF","#FF6584"], startangle=140, textprops={"fontsize": 12})
    ax.set_title("Revenue Split by Gender", fontsize=14, fontweight="bold")
    return _save(fig, "gender_distribution")


def plot_age_group(df: pd.DataFrame) -> Path:
    ag = df.groupby("Age_Group", observed=True)["Sales"].sum()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=ag.index.astype(str), y=ag.values, ax=ax, palette="viridis")
    ax.set_title("Revenue by Age Group", fontsize=15, fontweight="bold")
    ax.set_xlabel("Age Group"); ax.set_ylabel("Revenue (₹)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    fig.tight_layout()
    return _save(fig, "age_group_sales")


def plot_payment_modes(df: pd.DataFrame) -> Path:
    pay = df["Payment_Mode"].value_counts()
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=pay.values, y=pay.index, ax=ax, palette="Set2")
    ax.set_title("Orders by Payment Mode", fontsize=15, fontweight="bold")
    ax.set_xlabel("Number of Orders"); ax.set_ylabel("")
    fig.tight_layout()
    return _save(fig, "payment_modes")


def plot_order_status(df: pd.DataFrame) -> Path:
    status = df["Order_Status"].value_counts()
    colors = {"Delivered":"#27ae60","Cancelled":"#e74c3c",
              "Pending":"#f39c12","Returned":"#8e44ad"}
    clrs = [colors.get(s, "#3498db") for s in status.index]
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(status.index, status.values, color=clrs)
    ax.set_title("Order Status Distribution", fontsize=15, fontweight="bold")
    ax.set_xlabel("Status"); ax.set_ylabel("Count")
    for i, (s, v) in enumerate(zip(status.index, status.values)):
        ax.text(i, v + 20, str(v), ha="center", fontsize=10)
    fig.tight_layout()
    return _save(fig, "order_status")


def plot_top_products(df: pd.DataFrame, n: int = 10) -> Path:
    tp = df.groupby("Product_Name")["Sales"].sum().nlargest(n)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=tp.values, y=tp.index, ax=ax, palette="magma_r")
    ax.set_title(f"Top {n} Products by Revenue", fontsize=15, fontweight="bold")
    ax.set_xlabel("Revenue (₹)"); ax.set_ylabel("")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x/1e6:.1f}M"))
    fig.tight_layout()
    return _save(fig, "top_products")


def plot_discount_vs_profit(df: pd.DataFrame) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(df["Discount"] * 100, df["Profit_Margin"],
               alpha=0.3, s=10, c=df["Profit_Margin"],
               cmap="RdYlGn", vmin=-50, vmax=60)
    ax.set_title("Discount vs Profit Margin", fontsize=15, fontweight="bold")
    ax.set_xlabel("Discount (%)"); ax.set_ylabel("Profit Margin (%)")
    ax.axhline(0, color="red", linestyle="--", linewidth=1)
    fig.tight_layout()
    return _save(fig, "discount_vs_profit")


def plot_correlation_heatmap(df: pd.DataFrame) -> Path:
    cols = ["Sales","Cost","Profit","Quantity","Unit_Price","Discount","Profit_Margin"]
    corr = df[cols].corr()
    fig, ax = plt.subplots(figsize=(9, 7))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                linewidths=0.5, ax=ax, annot_kws={"size": 9})
    ax.set_title("Correlation Heatmap – Numeric Features", fontsize=14, fontweight="bold")
    fig.tight_layout()
    return _save(fig, "correlation_heatmap")


# ──────────────────────────────────────────────────────────
# Run all EDA plots
# ──────────────────────────────────────────────────────────
def run_full_eda(df: pd.DataFrame) -> dict:
    """Generate all EDA plots and return a dict of name → file path."""
    plots = {}
    funcs = [
        ("monthly_sales",           plot_monthly_sales),
        ("category_sales",          plot_category_sales),
        ("state_sales",             plot_state_sales),
        ("profit_margin_category",  plot_profit_margin_by_category),
        ("gender_distribution",     plot_gender_distribution),
        ("age_group_sales",         plot_age_group),
        ("payment_modes",           plot_payment_modes),
        ("order_status",            plot_order_status),
        ("top_products",            plot_top_products),
        ("discount_vs_profit",      plot_discount_vs_profit),
        ("correlation_heatmap",     plot_correlation_heatmap),
    ]
    for name, fn in funcs:
        try:
            path = fn(df)
            plots[name] = path
            print(f"  ✓  {name}")
        except Exception as exc:
            print(f"  ✗  {name} – {exc}")

    return plots


if __name__ == "__main__":
    print("Loading cleaned data …")
    df = pd.read_csv(CLEAN_PATH, parse_dates=["Order_Date"])
    if "Age_Group" not in df.columns:
        df["Age_Group"] = pd.cut(df["Age"], bins=[17,25,35,45,55,100],
                                  labels=["18-25","26-35","36-45","46-55","55+"])
    if "Profit_Margin" not in df.columns:
        df["Profit_Margin"] = (df["Profit"] / df["Sales"].replace(0, float("nan")) * 100).round(2)
    if "Month" not in df.columns:
        df["Month"] = df["Order_Date"].dt.to_period("M").astype(str)

    print("Generating EDA plots …")
    plots = run_full_eda(df)
    print(f"\nAll plots saved to {FIGURES_DIR}")
