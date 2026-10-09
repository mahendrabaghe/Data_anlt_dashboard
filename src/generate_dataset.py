"""
generate_dataset.py
-------------------
Generates a realistic synthetic e-commerce dataset with 10,000+ records.
Saves output to data/raw/ecommerce_sales.csv
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
import os

# ─────────────────────────────────────────
# Seed for reproducibility
# ─────────────────────────────────────────
np.random.seed(42)
random.seed(42)

# ─────────────────────────────────────────
# Reference data
# ─────────────────────────────────────────
STATES_CITIES: dict = {
    "Maharashtra":   ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Delhi":         ["New Delhi", "Dwarka", "Rohini", "Saket", "Lajpat Nagar"],
    "Karnataka":     ["Bengaluru", "Mysuru", "Hubli", "Mangaluru", "Belagavi"],
    "Tamil Nadu":    ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem"],
    "Uttar Pradesh": ["Lucknow", "Kanpur", "Agra", "Varanasi", "Meerut"],
    "Gujarat":       ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],
    "West Bengal":   ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
    "Rajasthan":     ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Bikaner"],
    "Telangana":     ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Madhya Pradesh":["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"],
}

CATEGORIES: dict = {
    "Electronics": [
        {"name": "Smartphone",       "sub": "Mobile Phones",   "price_range": (8000,  80000), "cost_pct": 0.65},
        {"name": "Laptop",           "sub": "Computers",       "price_range": (25000, 150000), "cost_pct": 0.70},
        {"name": "Tablet",           "sub": "Computers",       "price_range": (10000, 60000),  "cost_pct": 0.68},
        {"name": "Wireless Earbuds", "sub": "Audio",           "price_range": (1000,  15000),  "cost_pct": 0.55},
        {"name": "Smart Watch",      "sub": "Wearables",       "price_range": (3000,  40000),  "cost_pct": 0.60},
        {"name": "DSLR Camera",      "sub": "Cameras",         "price_range": (20000, 120000), "cost_pct": 0.72},
        {"name": "LED TV 43in",      "sub": "Televisions",     "price_range": (18000, 60000),  "cost_pct": 0.70},
        {"name": "Bluetooth Speaker","sub": "Audio",           "price_range": (500,   8000),   "cost_pct": 0.50},
        {"name": "Gaming Console",   "sub": "Gaming",          "price_range": (15000, 55000),  "cost_pct": 0.75},
        {"name": "Power Bank",       "sub": "Accessories",     "price_range": (800,   5000),   "cost_pct": 0.45},
    ],
    "Clothing": [
        {"name": "Men T-Shirt",      "sub": "Mens Wear",       "price_range": (299,   2000),   "cost_pct": 0.40},
        {"name": "Women Kurti",      "sub": "Womens Wear",     "price_range": (399,   3000),   "cost_pct": 0.38},
        {"name": "Jeans",            "sub": "Mens Wear",       "price_range": (799,   4000),   "cost_pct": 0.45},
        {"name": "Saree",            "sub": "Womens Wear",     "price_range": (500,   15000),  "cost_pct": 0.42},
        {"name": "Sports Shoes",     "sub": "Footwear",        "price_range": (999,   8000),   "cost_pct": 0.50},
        {"name": "Winter Jacket",    "sub": "Mens Wear",       "price_range": (1500,  10000),  "cost_pct": 0.48},
        {"name": "Ethnic Dress",     "sub": "Womens Wear",     "price_range": (600,   5000),   "cost_pct": 0.40},
        {"name": "Formal Shirt",     "sub": "Mens Wear",       "price_range": (699,   3500),   "cost_pct": 0.43},
        {"name": "Leggings",         "sub": "Womens Wear",     "price_range": (199,   1200),   "cost_pct": 0.35},
        {"name": "Sneakers",         "sub": "Footwear",        "price_range": (1200,  7000),   "cost_pct": 0.52},
    ],
    "Home & Kitchen": [
        {"name": "Mixer Grinder",    "sub": "Appliances",      "price_range": (1500,  8000),   "cost_pct": 0.60},
        {"name": "Pressure Cooker",  "sub": "Cookware",        "price_range": (800,   4000),   "cost_pct": 0.55},
        {"name": "Water Purifier",   "sub": "Appliances",      "price_range": (5000,  25000),  "cost_pct": 0.65},
        {"name": "Bed Sheet Set",    "sub": "Bedding",         "price_range": (499,   3000),   "cost_pct": 0.40},
        {"name": "Air Fryer",        "sub": "Appliances",      "price_range": (2500,  12000),  "cost_pct": 0.62},
        {"name": "Non-stick Kadai",  "sub": "Cookware",        "price_range": (500,   3000),   "cost_pct": 0.50},
        {"name": "Coffee Maker",     "sub": "Appliances",      "price_range": (2000,  15000),  "cost_pct": 0.60},
        {"name": "Storage Cabinet",  "sub": "Furniture",       "price_range": (3000,  20000),  "cost_pct": 0.58},
        {"name": "Curtain Set",      "sub": "Home Decor",      "price_range": (400,   5000),   "cost_pct": 0.42},
        {"name": "Dining Table",     "sub": "Furniture",       "price_range": (8000,  50000),  "cost_pct": 0.65},
    ],
    "Books": [
        {"name": "Fiction Novel",    "sub": "Fiction",         "price_range": (150,   600),    "cost_pct": 0.35},
        {"name": "Self-Help Book",   "sub": "Self-Help",       "price_range": (200,   800),    "cost_pct": 0.30},
        {"name": "Programming Book", "sub": "Technology",      "price_range": (300,   1500),   "cost_pct": 0.38},
        {"name": "UPSC Prep Book",   "sub": "Education",       "price_range": (250,   1200),   "cost_pct": 0.32},
        {"name": "Childrens Book",   "sub": "Children",        "price_range": (100,   500),    "cost_pct": 0.28},
    ],
    "Sports & Fitness": [
        {"name": "Yoga Mat",         "sub": "Yoga",            "price_range": (400,   3000),   "cost_pct": 0.45},
        {"name": "Dumbbell Set",     "sub": "Weights",         "price_range": (800,   8000),   "cost_pct": 0.50},
        {"name": "Cricket Bat",      "sub": "Cricket",         "price_range": (500,   5000),   "cost_pct": 0.48},
        {"name": "Badminton Racket", "sub": "Badminton",       "price_range": (300,   4000),   "cost_pct": 0.45},
        {"name": "Cycling Helmet",   "sub": "Cycling",         "price_range": (600,   5000),   "cost_pct": 0.50},
        {"name": "Skipping Rope",    "sub": "Fitness",         "price_range": (100,   800),    "cost_pct": 0.35},
    ],
    "Beauty & Personal Care": [
        {"name": "Face Serum",       "sub": "Skin Care",       "price_range": (300,   3000),   "cost_pct": 0.40},
        {"name": "Shampoo 500ml",    "sub": "Hair Care",       "price_range": (150,   800),    "cost_pct": 0.38},
        {"name": "Perfume",          "sub": "Fragrance",       "price_range": (500,   8000),   "cost_pct": 0.45},
        {"name": "Lipstick",         "sub": "Makeup",          "price_range": (200,   2000),   "cost_pct": 0.35},
        {"name": "Electric Trimmer", "sub": "Grooming",        "price_range": (800,   5000),   "cost_pct": 0.52},
    ],
}

PAYMENT_MODES  = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash on Delivery", "Wallet"]
ORDER_STATUSES = ["Delivered", "Delivered", "Delivered", "Delivered", "Cancelled", "Pending", "Returned"]

FIRST_NAMES_M = ["Rahul","Amit","Vikas","Arjun","Rohit","Sanjay","Deepak","Ajay",
                  "Nitin","Sachin","Karan","Vijay","Suresh","Ramesh","Pradeep",
                  "Manoj","Anil","Rakesh","Harish","Girish"]
FIRST_NAMES_F = ["Priya","Anita","Sunita","Kavita","Pooja","Neha","Deepa","Sneha",
                  "Ritu","Sona","Asha","Meena","Geeta","Seema","Divya",
                  "Nisha","Rekha","Shweta","Komal","Ankita"]
LAST_NAMES    = ["Sharma","Verma","Patel","Singh","Kumar","Gupta","Joshi","Mehta",
                  "Reddy","Nair","Pillai","Rao","Iyer","Mishra","Tiwari",
                  "Agarwal","Malhotra","Kapoor","Jain","Srivastava"]

NUM_RECORDS      = 10500
NUM_CUSTOMERS    = 1200
START_DATE       = datetime(2023, 1, 1)
END_DATE         = datetime(2024, 12, 31)


def _rand_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def _festival_boost(date: datetime) -> float:
    """Return a sales volume multiplier based on festival season."""
    month = date.month
    if month in (10, 11):      # Diwali season
        return 2.0
    if month in (8, 9):        # Onam / Independence Day
        return 1.4
    if month in (12, 1):       # Christmas / New Year
        return 1.5
    if month == 7:             # Mid-year sale
        return 1.3
    return 1.0


def generate_customers(n: int) -> pd.DataFrame:
    rows = []
    for i in range(1, n + 1):
        gender = random.choice(["Male", "Female"])
        fname  = random.choice(FIRST_NAMES_M if gender == "Male" else FIRST_NAMES_F)
        lname  = random.choice(LAST_NAMES)
        state  = random.choice(list(STATES_CITIES.keys()))
        city   = random.choice(STATES_CITIES[state])
        age    = int(np.clip(np.random.normal(32, 10), 18, 65))
        rows.append({
            "Customer_ID":   f"CUST{i:04d}",
            "Customer_Name": f"{fname} {lname}",
            "Gender":        gender,
            "Age":           age,
            "City":          city,
            "State":         state,
        })
    return pd.DataFrame(rows)


def generate_products() -> list:
    products = []
    pid = 1
    for cat, items in CATEGORIES.items():
        for item in items:
            products.append({
                "Product_ID":   f"PROD{pid:03d}",
                "Product_Name": item["name"],
                "Category":     cat,
                "Sub_Category": item["sub"],
                "price_range":  item["price_range"],
                "cost_pct":     item["cost_pct"],
            })
            pid += 1
    return products


def generate_orders(customers_df: pd.DataFrame, products: list, n: int) -> pd.DataFrame:
    records = []
    for oid in range(1, n + 1):
        order_date = _rand_date(START_DATE, END_DATE)
        boost      = _festival_boost(order_date)

        prod       = random.choice(products)
        cust       = customers_df.sample(1).iloc[0]

        qty = max(1, int(np.random.poisson(1.2 * boost)))
        qty = min(qty, 10)

        lo, hi     = prod["price_range"]
        unit_price = round(random.uniform(lo, hi), 2)

        month = order_date.month
        if month in (10, 11, 12, 7):
            discount = round(random.uniform(0.05, 0.35), 2)
        else:
            discount = round(random.uniform(0.00, 0.20), 2)

        sales  = round(unit_price * qty * (1 - discount), 2)
        cost   = round(unit_price * qty * prod["cost_pct"], 2)
        profit = round(sales - cost, 2)

        records.append({
            "Order_ID":      f"ORD{oid:06d}",
            "Order_Date":    order_date.strftime("%Y-%m-%d"),
            "Customer_ID":   cust["Customer_ID"],
            "Customer_Name": cust["Customer_Name"],
            "Gender":        cust["Gender"],
            "Age":           cust["Age"],
            "City":          cust["City"],
            "State":         cust["State"],
            "Product_ID":    prod["Product_ID"],
            "Product_Name":  prod["Product_Name"],
            "Category":      prod["Category"],
            "Sub_Category":  prod["Sub_Category"],
            "Quantity":      qty,
            "Unit_Price":    unit_price,
            "Discount":      discount,
            "Sales":         sales,
            "Cost":          cost,
            "Profit":        profit,
            "Payment_Mode":  random.choice(PAYMENT_MODES),
            "Order_Status":  random.choice(ORDER_STATUSES),
        })

    return pd.DataFrame(records)


def introduce_noise(df: pd.DataFrame, noise_pct: float = 0.02) -> pd.DataFrame:
    """Introduce realistic dirty-data noise for the cleaning pipeline to fix."""
    n   = len(df)
    idx = df.index.tolist()

    # Duplicate rows
    dup_idx = random.sample(idx, int(n * noise_pct))
    df = pd.concat([df, df.loc[dup_idx]], ignore_index=True)

    # Missing values
    for col in ["Customer_Name", "City", "Discount", "Payment_Mode"]:
        miss_idx = random.sample(list(df.index), int(len(df) * noise_pct * 0.5))
        df.loc[miss_idx, col] = np.nan

    # Negative quantities
    neg_idx = random.sample(list(df.index), int(len(df) * noise_pct * 0.3))
    df.loc[neg_idx, "Quantity"] = -1

    # Invalid prices
    inv_idx = random.sample(list(df.index), int(len(df) * noise_pct * 0.3))
    df.loc[inv_idx, "Unit_Price"] = 0

    # Inconsistent category names
    cat_idx = random.sample(list(df.index), int(len(df) * noise_pct * 0.4))
    df.loc[cat_idx, "Category"] = df.loc[cat_idx, "Category"].str.upper()

    return df


def main() -> None:
    out_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ecommerce_sales.csv")

    print("Generating customers ...")
    customers = generate_customers(NUM_CUSTOMERS)

    print("Generating products  ...")
    products  = generate_products()

    print("Generating orders    ...")
    orders    = generate_orders(customers, products, NUM_RECORDS)

    print("Introducing noise    ...")
    orders    = introduce_noise(orders)

    orders.to_csv(out_path, index=False)
    print(f"Dataset saved to {out_path}  ({len(orders):,} rows)")


if __name__ == "__main__":
    main()
