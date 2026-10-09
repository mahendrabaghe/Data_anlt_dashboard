"""
database.py
-----------
MySQL database integration for the e-commerce analytics project.
Creates the database schema, loads cleaned data, and provides
helper functions to run SQL queries from Python.

Configuration is read from environment variables (see .env.example).
"""

import os
import pandas as pd
from pathlib import Path
from typing import Optional

# Optional MySQL dependency – the dashboard works without it
try:
    import mysql.connector
    from mysql.connector import Error as MySQLError
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    MySQLError = Exception  # type: ignore

from dotenv import load_dotenv

# ─── load .env if present ──────────────────────────────────
load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH   = PROJECT_ROOT / "data" / "processed" / "cleaned_sales.csv"


# ─────────────────────────────────────────────────────────────
# Connection helpers
# ─────────────────────────────────────────────────────────────
def get_connection(database: Optional[str] = None):
    """Return a MySQL connection using environment variables."""
    if not MYSQL_AVAILABLE:
        raise RuntimeError(
            "mysql-connector-python is not installed. "
            "Run: pip install mysql-connector-python"
        )
    params = {
        "host":     os.getenv("MYSQL_HOST",     "localhost"),
        "port":     int(os.getenv("MYSQL_PORT", "3306")),
        "user":     os.getenv("MYSQL_USER",     "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
    }
    if database:
        params["database"] = database

    return mysql.connector.connect(**params)


def test_connection() -> bool:
    """Return True if the MySQL server is reachable."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────
# Schema setup
# ─────────────────────────────────────────────────────────────
CREATE_DB_SQL = "CREATE DATABASE IF NOT EXISTS ecommerce_analytics CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS orders (
    order_id        VARCHAR(20)    NOT NULL,
    order_date      DATE           NOT NULL,
    customer_id     VARCHAR(20)    NOT NULL,
    customer_name   VARCHAR(100),
    gender          VARCHAR(10),
    age             TINYINT UNSIGNED,
    city            VARCHAR(100),
    state           VARCHAR(100),
    product_id      VARCHAR(20)    NOT NULL,
    product_name    VARCHAR(200),
    category        VARCHAR(100),
    sub_category    VARCHAR(100),
    quantity        SMALLINT UNSIGNED,
    unit_price      DECIMAL(12,2),
    discount        DECIMAL(5,4),
    sales           DECIMAL(12,2),
    cost            DECIMAL(12,2),
    profit          DECIMAL(12,2),
    payment_mode    VARCHAR(50),
    order_status    VARCHAR(50),
    month           VARCHAR(10),
    year            SMALLINT,
    profit_margin   DECIMAL(8,2),
    PRIMARY KEY (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""

INDEXES_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_order_date    ON orders (order_date);",
    "CREATE INDEX IF NOT EXISTS idx_customer_id   ON orders (customer_id);",
    "CREATE INDEX IF NOT EXISTS idx_category      ON orders (category);",
    "CREATE INDEX IF NOT EXISTS idx_state         ON orders (state);",
    "CREATE INDEX IF NOT EXISTS idx_order_status  ON orders (order_status);",
]


def setup_database() -> None:
    """Create the database and orders table if they don't exist."""
    # Create DB
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(CREATE_DB_SQL)
    conn.commit()
    conn.close()
    print("Database 'ecommerce_analytics' ready.")

    # Create table + indexes
    conn = get_connection(database="ecommerce_analytics")
    cur  = conn.cursor()
    cur.execute(CREATE_TABLE_SQL)

    for idx_sql in INDEXES_SQL:
        try:
            cur.execute(idx_sql)
        except MySQLError:
            pass   # index already exists

    conn.commit()
    conn.close()
    print("Table 'orders' ready.")


# ─────────────────────────────────────────────────────────────
# Data loading
# ─────────────────────────────────────────────────────────────
COLUMN_MAP = {
    "Order_ID":      "order_id",
    "Order_Date":    "order_date",
    "Customer_ID":   "customer_id",
    "Customer_Name": "customer_name",
    "Gender":        "gender",
    "Age":           "age",
    "City":          "city",
    "State":         "state",
    "Product_ID":    "product_id",
    "Product_Name":  "product_name",
    "Category":      "category",
    "Sub_Category":  "sub_category",
    "Quantity":      "quantity",
    "Unit_Price":    "unit_price",
    "Discount":      "discount",
    "Sales":         "sales",
    "Cost":          "cost",
    "Profit":        "profit",
    "Payment_Mode":  "payment_mode",
    "Order_Status":  "order_status",
    "Month":         "month",
    "Year":          "year",
    "Profit_Margin": "profit_margin",
}

INSERT_SQL = """
INSERT IGNORE INTO orders
    (order_id, order_date, customer_id, customer_name, gender, age,
     city, state, product_id, product_name, category, sub_category,
     quantity, unit_price, discount, sales, cost, profit,
     payment_mode, order_status, month, year, profit_margin)
VALUES
    (%s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s, %s,
     %s, %s, %s, %s, %s)
"""


def load_data_to_mysql(csv_path: Path = CLEAN_PATH, batch_size: int = 500) -> None:
    """Bulk-insert cleaned CSV into MySQL in batches."""
    df = pd.read_csv(csv_path, parse_dates=["Order_Date"])
    df = df.rename(columns=COLUMN_MAP)

    # Keep only columns that have a mapping
    cols = list(COLUMN_MAP.values())
    df   = df[[c for c in cols if c in df.columns]]

    conn = get_connection(database="ecommerce_analytics")
    cur  = conn.cursor()

    rows  = [tuple(r) for r in df.itertuples(index=False, name=None)]
    total = len(rows)
    inserted = 0

    for i in range(0, total, batch_size):
        batch = rows[i : i + batch_size]
        cur.executemany(INSERT_SQL, batch)
        conn.commit()
        inserted += len(batch)
        print(f"  Inserted {inserted:,} / {total:,} rows …", end="\r")

    conn.close()
    print(f"\nLoaded {total:,} rows into ecommerce_analytics.orders")


# ─────────────────────────────────────────────────────────────
# Query helper
# ─────────────────────────────────────────────────────────────
def run_query(sql: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """Execute a SELECT query and return a DataFrame."""
    conn = get_connection(database="ecommerce_analytics")
    df   = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df


# ─────────────────────────────────────────────────────────────
# Standalone setup
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if not test_connection():
        print("ERROR: Cannot connect to MySQL. Check .env credentials.")
    else:
        setup_database()
        load_data_to_mysql()
        print("MySQL setup complete.")
