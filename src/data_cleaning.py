"""
data_cleaning.py
----------------
Data cleaning pipeline for the e-commerce sales dataset.
Produces a clean CSV in data/processed/cleaned_sales.csv and
prints a before/after quality report.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path


# ─────────────────────────────────────────────────────
# Paths  (always relative to project root)
# ─────────────────────────────────────────────────────
PROJECT_ROOT  = Path(__file__).resolve().parent.parent
RAW_PATH      = PROJECT_ROOT / "data" / "raw"  / "ecommerce_sales.csv"
CLEAN_PATH    = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"

# Canonical category names (title-case)
VALID_CATEGORIES = {
    "Electronics", "Clothing", "Home & Kitchen",
    "Books", "Sports & Fitness", "Beauty & Personal Care",
}


# ─────────────────────────────────────────────────────
# Helper
# ─────────────────────────────────────────────────────
def _section(title: str) -> None:
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")


# ─────────────────────────────────────────────────────
# Individual cleaning steps
# ─────────────────────────────────────────────────────
def remove_duplicates(df: pd.DataFrame) -> tuple:
    before = len(df)
    df = df.drop_duplicates(subset=["Order_ID"], keep="first")
    removed = before - len(df)
    return df, removed


def fix_data_types(df: pd.DataFrame) -> pd.DataFrame:
    # Date
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    # Numeric
    for col in ["Quantity", "Unit_Price", "Discount", "Sales", "Cost", "Profit", "Age"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def handle_missing_values(df: pd.DataFrame) -> tuple:
    before_na = df.isnull().sum().sum()

    # Drop rows where critical identifiers are missing
    df = df.dropna(subset=["Order_ID", "Customer_ID", "Product_ID", "Order_Date"])

    # Fill missing Customer_Name with "Unknown"
    df["Customer_Name"] = df["Customer_Name"].fillna("Unknown")

    # Fill missing City/State using Customer_ID mode (most frequent city for that customer)
    for col in ["City", "State"]:
        mode_map = df.groupby("Customer_ID")[col].agg(
            lambda x: x.mode()[0] if not x.mode().empty else np.nan
        )
        mask = df[col].isnull()
        df.loc[mask, col] = df.loc[mask, "Customer_ID"].map(mode_map)
        # Remaining nulls – fill with overall mode
        df[col] = df[col].fillna(df[col].mode()[0])

    # Discount: fill with category median
    df["Discount"] = df.groupby("Category")["Discount"].transform(
        lambda x: x.fillna(x.median())
    )
    df["Discount"] = df["Discount"].fillna(df["Discount"].median())

    # Payment_Mode: fill with mode
    df["Payment_Mode"] = df["Payment_Mode"].fillna(df["Payment_Mode"].mode()[0])

    after_na = df.isnull().sum().sum()
    handled  = int(before_na - after_na)
    return df, handled


def remove_invalid_records(df: pd.DataFrame) -> tuple:
    before = len(df)

    # Invalid dates
    df = df.dropna(subset=["Order_Date"])
    df = df[df["Order_Date"].dt.year.between(2020, 2025)]

    # Invalid quantity / price
    df = df[df["Quantity"]   > 0]
    df = df[df["Unit_Price"] > 0]
    df = df[df["Sales"]      >= 0]

    # Discount must be in [0, 1]
    df = df[(df["Discount"] >= 0) & (df["Discount"] <= 1)]

    # Age sanity check
    df = df[(df["Age"] >= 18) & (df["Age"] <= 100)]

    removed = before - len(df)
    return df, removed


def fix_category_names(df: pd.DataFrame) -> pd.DataFrame:
    """Standardise category strings that were uppercased as noise."""
    mapping = {c.upper(): c for c in VALID_CATEGORIES}
    mapping.update({c: c for c in VALID_CATEGORIES})   # keep already-correct ones

    df["Category"] = df["Category"].apply(
        lambda x: mapping.get(str(x).strip(), str(x).strip().title())
        if pd.notna(x) else x
    )
    return df


def remove_outliers(df: pd.DataFrame) -> tuple:
    """Remove extreme profit outliers using IQR on Profit column."""
    before = len(df)
    q1 = df["Profit"].quantile(0.01)
    q3 = df["Profit"].quantile(0.99)
    df = df[df["Profit"].between(q1, q3)]
    removed = before - len(df)
    return df, removed


def recalculate_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure Sales / Profit consistency after cleaning."""
    df["Sales"]  = (df["Unit_Price"] * df["Quantity"] * (1 - df["Discount"])).round(2)
    df["Profit"] = (df["Sales"] - df["Cost"]).round(2)
    return df


def add_feature_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived columns useful for analysis."""
    df["Month"]       = df["Order_Date"].dt.to_period("M").astype(str)
    df["Month_Num"]   = df["Order_Date"].dt.month
    df["Year"]        = df["Order_Date"].dt.year
    df["Day_of_Week"] = df["Order_Date"].dt.day_name()
    df["Age_Group"]   = pd.cut(
        df["Age"],
        bins=[17, 25, 35, 45, 55, 100],
        labels=["18-25", "26-35", "36-45", "46-55", "55+"],
    )
    df["Profit_Margin"] = ((df["Profit"] / df["Sales"].replace(0, np.nan)) * 100).round(2)
    df["Discount_Pct"]  = (df["Discount"] * 100).round(1)
    return df


# ─────────────────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────────────────
def clean_data(raw_path: Path = RAW_PATH, clean_path: Path = CLEAN_PATH) -> pd.DataFrame:
    _section("LOADING RAW DATA")
    df = pd.read_csv(raw_path)
    rows_before = len(df)
    print(f"  Raw records loaded : {rows_before:,}")

    _section("STEP 1 – TYPE CONVERSION")
    df = fix_data_types(df)
    print("  Data types corrected.")

    _section("STEP 2 – REMOVE DUPLICATES")
    df, dup_removed = remove_duplicates(df)
    print(f"  Duplicate rows removed : {dup_removed:,}")

    _section("STEP 3 – HANDLE MISSING VALUES")
    df, mv_handled = handle_missing_values(df)
    print(f"  Missing values handled : {mv_handled:,}")

    _section("STEP 4 – REMOVE INVALID RECORDS")
    df, inv_removed = remove_invalid_records(df)
    print(f"  Invalid records removed : {inv_removed:,}")

    _section("STEP 5 – STANDARDISE CATEGORIES")
    df = fix_category_names(df)
    print("  Category names standardised.")

    _section("STEP 6 – REMOVE OUTLIERS")
    df, out_removed = remove_outliers(df)
    print(f"  Outlier rows removed : {out_removed:,}")

    _section("STEP 7 – RECALCULATE DERIVED COLUMNS")
    df = recalculate_derived_columns(df)
    print("  Sales / Profit recalculated.")

    _section("STEP 8 – ADD FEATURE COLUMNS")
    df = add_feature_columns(df)
    print("  Feature columns added.")

    # ── final sort ──
    df = df.sort_values("Order_Date").reset_index(drop=True)

    # ── save ──
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)

    rows_after = len(df)
    _section("DATA QUALITY REPORT")
    print(f"  Rows before cleaning         : {rows_before:,}")
    print(f"  Duplicate rows removed       : {dup_removed:,}")
    print(f"  Missing values handled       : {mv_handled:,}")
    print(f"  Invalid records removed      : {inv_removed:,}")
    print(f"  Outlier rows removed         : {out_removed:,}")
    print(f"  Rows after cleaning          : {rows_after:,}")
    print(f"  Cleaned file saved to        : {clean_path}")

    return df


if __name__ == "__main__":
    clean_data()
