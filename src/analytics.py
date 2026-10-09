"""
analytics.py
------------
Business KPI calculations and insight generation.
All metrics are computed dynamically from the cleaned dataset.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH   = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"


# ──────────────────────────────────────────────────────
# Data loader
# ──────────────────────────────────────────────────────
def load_data(path: Path = CLEAN_PATH) -> pd.DataFrame:
    """Load cleaned CSV; parse dates and ensure derived columns exist."""
    df = pd.read_csv(path, parse_dates=["Order_Date"])

    if "Month" not in df.columns:
        df["Month"]       = df["Order_Date"].dt.to_period("M").astype(str)
    if "Month_Num" not in df.columns:
        df["Month_Num"]   = df["Order_Date"].dt.month
    if "Year" not in df.columns:
        df["Year"]        = df["Order_Date"].dt.year
    if "Profit_Margin" not in df.columns:
        df["Profit_Margin"] = ((df["Profit"] / df["Sales"].replace(0, np.nan)) * 100).round(2)
    if "Age_Group" not in df.columns:
        df["Age_Group"] = pd.cut(
            df["Age"],
            bins=[17, 25, 35, 45, 55, 100],
            labels=["18-25", "26-35", "36-45", "46-55", "55+"],
        )

    return df


# ──────────────────────────────────────────────────────
# KPI calculations
# ──────────────────────────────────────────────────────
def calculate_kpis(df: pd.DataFrame) -> dict:
    """Return a dictionary of all key business KPIs."""
    delivered     = df[df["Order_Status"] == "Delivered"]
    total_revenue = df["Sales"].sum()
    total_profit  = df["Profit"].sum()
    total_orders  = df["Order_ID"].nunique()
    total_cust    = df["Customer_ID"].nunique()
    avg_order_val = df.groupby("Order_ID")["Sales"].sum().mean()
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
    avg_discount  = df["Discount"].mean() * 100

    # Repeat customers
    order_counts   = df.groupby("Customer_ID")["Order_ID"].nunique()
    repeat_cust    = (order_counts > 1).sum()
    repeat_rate    = repeat_cust / total_cust * 100 if total_cust > 0 else 0

    # Top product / category / state
    top_product  = df.groupby("Product_Name")["Sales"].sum().idxmax()
    top_category = df.groupby("Category")["Sales"].sum().idxmax()
    top_state    = df.groupby("State")["Sales"].sum().idxmax()

    return {
        "Total Revenue":        round(total_revenue, 2),
        "Total Profit":         round(total_profit, 2),
        "Total Orders":         total_orders,
        "Total Customers":      total_cust,
        "Average Order Value":  round(avg_order_val, 2),
        "Profit Margin (%)":    round(profit_margin, 2),
        "Avg Discount (%)":     round(avg_discount, 2),
        "Repeat Customer Rate": round(repeat_rate, 2),
        "Top Product":          top_product,
        "Top Category":         top_category,
        "Top State":            top_state,
    }


# ──────────────────────────────────────────────────────
# Monthly aggregations
# ──────────────────────────────────────────────────────
def monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Month")
          .agg(Revenue=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order_ID", "nunique"))
          .reset_index()
          .sort_values("Month")
    )


def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Category")
          .agg(
              Revenue        = ("Sales",   "sum"),
              Profit         = ("Profit",  "sum"),
              Orders         = ("Order_ID","nunique"),
              Quantity_Sold  = ("Quantity","sum"),
          )
          .reset_index()
          .sort_values("Revenue", ascending=False)
    )


def subcategory_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["Category", "Sub_Category"])
          .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"))
          .reset_index()
          .sort_values("Revenue", ascending=False)
    )


def state_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("State")
          .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","nunique"))
          .reset_index()
          .sort_values("Revenue", ascending=False)
    )


def city_performance(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["State","City"])
          .agg(Revenue=("Sales","sum"), Orders=("Order_ID","nunique"))
          .reset_index()
          .sort_values("Revenue", ascending=False)
    )


def top_products(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Product_Name")
          .agg(Revenue=("Sales","sum"), Profit=("Profit","sum"), Quantity_Sold=("Quantity","sum"))
          .reset_index()
          .sort_values("Revenue", ascending=False)
          .head(n)
    )


# ──────────────────────────────────────────────────────
# Customer analytics
# ──────────────────────────────────────────────────────
def customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    cust = (
        df.groupby(["Customer_ID","Customer_Name","Gender","Age","City","State"])
          .agg(
              Total_Revenue = ("Sales",    "sum"),
              Total_Orders  = ("Order_ID", "nunique"),
              Total_Profit  = ("Profit",   "sum"),
          )
          .reset_index()
    )
    cust["Avg_Order_Value"] = (cust["Total_Revenue"] / cust["Total_Orders"]).round(2)
    return cust.sort_values("Total_Revenue", ascending=False)


def age_group_analysis(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Age_Group", observed=True)
          .agg(Revenue=("Sales","sum"), Orders=("Order_ID","nunique"), Customers=("Customer_ID","nunique"))
          .reset_index()
    )


def gender_analysis(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Gender")
          .agg(Revenue=("Sales","sum"), Orders=("Order_ID","nunique"), Customers=("Customer_ID","nunique"))
          .reset_index()
    )


def payment_mode_analysis(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Payment_Mode")
          .agg(Orders=("Order_ID","nunique"), Revenue=("Sales","sum"))
          .reset_index()
          .sort_values("Orders", ascending=False)
    )


def order_status_analysis(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("Order_Status")
          .agg(Orders=("Order_ID","nunique"), Revenue=("Sales","sum"))
          .reset_index()
          .sort_values("Orders", ascending=False)
    )


# ──────────────────────────────────────────────────────
# Business insight generation (dynamic)
# ──────────────────────────────────────────────────────
def generate_insights(df: pd.DataFrame) -> list:
    insights = []

    # 1. Top revenue category
    cat_rev = df.groupby("Category")["Sales"].sum()
    top_cat = cat_rev.idxmax()
    top_cat_pct = cat_rev.max() / cat_rev.sum() * 100
    insights.append(
        f"{top_cat} is the highest-revenue category, contributing "
        f"{top_cat_pct:.1f}% of total revenue."
    )

    # 2. Top state
    state_rev = df.groupby("State")["Sales"].sum()
    top_state = state_rev.idxmax()
    top_state_pct = state_rev.max() / state_rev.sum() * 100
    insights.append(
        f"{top_state} leads all states with {top_state_pct:.1f}% of total sales."
    )

    # 3. Festival season lift
    df2 = df.copy()
    df2["Month_Num"] = df2["Order_Date"].dt.month
    festival_rev = df2[df2["Month_Num"].isin([10, 11])]["Sales"].sum()
    annual_rev   = df2["Sales"].sum()
    festival_pct = festival_rev / annual_rev * 100 if annual_rev > 0 else 0
    insights.append(
        f"Festival months (Oct–Nov) generated {festival_pct:.1f}% of annual revenue, "
        f"reflecting significant Diwali season demand."
    )

    # 4. Discount vs. profit margin
    high_disc   = df[df["Discount"] >= 0.30]["Profit_Margin"].mean()
    normal_disc = df[df["Discount"] <  0.30]["Profit_Margin"].mean()
    if pd.notna(high_disc) and pd.notna(normal_disc):
        insights.append(
            f"Orders with discounts >= 30% have an average profit margin of "
            f"{high_disc:.1f}% vs {normal_disc:.1f}% for lower discounts — "
            f"deep discounts erode margins by {normal_disc - high_disc:.1f} percentage points."
        )

    # 5. Repeat customer revenue share
    order_counts    = df.groupby("Customer_ID")["Order_ID"].nunique()
    repeat_ids      = order_counts[order_counts > 1].index
    repeat_rev      = df[df["Customer_ID"].isin(repeat_ids)]["Sales"].sum()
    repeat_pct      = repeat_rev / df["Sales"].sum() * 100 if df["Sales"].sum() > 0 else 0
    insights.append(
        f"Repeat customers account for {repeat_pct:.1f}% of total revenue — "
        f"retention programmes would have high ROI."
    )

    # 6. Most profitable product
    top_prod = df.groupby("Product_Name")["Profit"].sum().idxmax()
    top_prod_profit = df.groupby("Product_Name")["Profit"].sum().max()
    insights.append(
        f"'{top_prod}' is the most profitable individual product with "
        f"total profit of Rs.{top_prod_profit:,.0f}."
    )

    # 7. UPI adoption
    pay_share = df["Payment_Mode"].value_counts(normalize=True) * 100
    if "UPI" in pay_share.index:
        insights.append(
            f"UPI is the preferred payment mode for {pay_share['UPI']:.1f}% of orders, "
            f"reflecting India's digital payment adoption."
        )

    # 8. Cancelled orders impact
    cancelled = df[df["Order_Status"] == "Cancelled"]
    cancelled_pct = len(cancelled) / len(df) * 100
    lost_rev      = cancelled["Sales"].sum()
    insights.append(
        f"Cancellations represent {cancelled_pct:.1f}% of orders "
        f"(Rs.{lost_rev:,.0f} in lost revenue) — logistics optimisation could recover this."
    )

    # 9. Top city
    top_city = df.groupby("City")["Sales"].sum().idxmax()
    top_city_rev = df.groupby("City")["Sales"].sum().max()
    insights.append(
        f"{top_city} is the highest-revenue city with Rs.{top_city_rev:,.0f} in sales."
    )

    # 10. Youngest age group
    ag = df.groupby("Age_Group", observed=True)["Sales"].sum()
    if len(ag) > 0:
        top_age = ag.idxmax()
        insights.append(
            f"The {top_age} age group contributes the most to sales revenue "
            f"— marketing should target this demographic."
        )

    return insights


if __name__ == "__main__":
    import sys, io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    df = load_data()
    kpis = calculate_kpis(df)
    print("\n=== KEY PERFORMANCE INDICATORS ===")
    for k, v in kpis.items():
        print(f"  {k:<30} {v}")

    print("\n=== BUSINESS INSIGHTS ===")
    for i, insight in enumerate(generate_insights(df), 1):
        print(f"  {i}. {insight}")
