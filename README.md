# 📊 E-Commerce Sales & Customer Analytics Dashboard

> **A production-quality, end-to-end Data Analytics portfolio project**  
> Built with Python · Pandas · NumPy · Plotly · Streamlit · MySQL · Scikit-learn

---

## 🏆 Project Overview

This project builds a complete data analytics system for an e-commerce business.  
It transforms **10,000+ raw sales records** into actionable business insights through:

- Automated data generation and cleaning
- Exploratory data analysis with rich visualisations
- Business KPI calculation
- RFM-based customer segmentation
- An interactive 5-page Streamlit dashboard

The project is designed to be **genuinely functional** — not a mock UI — and demonstrates
real-world data engineering, analytics, and visualisation skills suitable for a
**Data Analyst / Data Analytics job interview**.

---

## 💼 Business Problem

An e-commerce company has accumulated two years of sales data across categories such as
Electronics, Clothing, Home & Kitchen, Books, Sports & Fitness, and Beauty & Personal Care.
The management team needs answers to questions such as:

- Which products and categories drive the most revenue and profit?
- Which states and cities are the highest-performing markets?
- Who are the most valuable customers, and which customers are at risk of churning?
- How does discounting affect profitability?
- What seasonal patterns exist in the data?

This project answers all of these questions programmatically.

---

## 🎯 Objectives

1. Generate a realistic synthetic e-commerce dataset (10,000+ records)
2. Clean and validate the raw data through an automated pipeline
3. Perform in-depth EDA across sales, profit, customers, products, and geography
4. Calculate 11 key business KPIs
5. Load data into MySQL and write analytical SQL queries
6. Segment customers using RFM analysis (6 segments)
7. Build an interactive Streamlit dashboard with sidebar filters and CSV downloads
8. Auto-generate business insights from the data

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Language | **Python 3.10+** | Core programming language |
| Data Wrangling | **Pandas 2.x** | Data loading, cleaning, transformation |
| Numerical | **NumPy** | Array operations, statistics |
| Visualisation | **Matplotlib / Seaborn** | Static EDA plots |
| Interactive Charts | **Plotly 5.x** | Dashboard charts |
| Dashboard | **Streamlit 1.35** | Web-based interactive dashboard |
| Database | **MySQL 8.x** | Structured data storage and SQL analytics |
| ML / Segmentation | **Scikit-learn** | Supporting RFM quintile binning |
| Config | **python-dotenv** | Secure credential management |

---

## 📁 Project Structure

```
ecommerce-data-analytics/
│
├── data/
│   ├── raw/
│   │   └── ecommerce_sales.csv       # Synthetic raw dataset (10,500 rows)
│   └── processed/
│       ├── cleaned_sales.csv         # Cleaned & enriched dataset
│       └── customer_segments.csv     # RFM segment output
│
├── notebooks/
│   └── exploratory_analysis.ipynb   # Jupyter EDA notebook
│
├── src/
│   ├── generate_dataset.py          # Synthetic data generator
│   ├── data_cleaning.py             # 8-step cleaning pipeline
│   ├── analytics.py                 # KPIs, aggregations, insights
│   ├── customer_segmentation.py     # RFM segmentation
│   ├── eda.py                       # Matplotlib/Seaborn EDA plots
│   └── database.py                  # MySQL integration
│
├── dashboard/
│   └── app.py                       # Streamlit dashboard (5 pages)
│
├── sql/
│   └── analysis_queries.sql         # 18 analytical SQL queries
│
├── reports/
│   ├── business_insights.md         # Business insights document
│   └── figures/                     # EDA plot images (auto-generated)
│
├── requirements.txt
├── README.md
├── .gitignore
└── .env.example
```

---

## 📊 Dataset

The synthetic dataset contains **10,500 records** covering January 2023 – December 2024.

| Column | Type | Description |
|--------|------|-------------|
| `Order_ID` | String | Unique order identifier (ORD000001 …) |
| `Order_Date` | Date | Date the order was placed |
| `Customer_ID` | String | Unique customer identifier |
| `Customer_Name` | String | Customer full name |
| `Gender` | String | Male / Female |
| `Age` | Integer | Customer age (18–65) |
| `City` | String | City of the customer |
| `State` | String | Indian state (10 states) |
| `Product_ID` | String | Product identifier |
| `Product_Name` | String | Product display name |
| `Category` | String | Electronics / Clothing / Home & Kitchen / Books / Sports & Fitness / Beauty & Personal Care |
| `Sub_Category` | String | Product sub-category |
| `Quantity` | Integer | Units ordered |
| `Unit_Price` | Float | Price per unit (₹) |
| `Discount` | Float | Discount rate (0.00–1.00) |
| `Sales` | Float | Net revenue after discount |
| `Cost` | Float | Cost of goods sold |
| `Profit` | Float | Sales − Cost |
| `Payment_Mode` | String | Credit Card / Debit Card / UPI / Net Banking / COD / Wallet |
| `Order_Status` | String | Delivered / Cancelled / Pending / Returned |

**Realistic patterns included:**
- Festival season (Oct–Nov) shows 2× average order volume
- Discounts are higher during sale months
- Customers are distributed across 10 Indian states and 50 cities
- 1,200 unique customers with repeat ordering behaviour

---

## 🧹 Data Cleaning Pipeline

The pipeline (`src/data_cleaning.py`) runs 8 sequential steps:

| Step | Action |
|------|--------|
| 1 | **Type conversion** – Parse dates, cast numerics |
| 2 | **Remove duplicates** – Drop rows with duplicate `Order_ID` |
| 3 | **Handle missing values** – Impute City/State using customer mode; fill Discount with category median; fill Payment_Mode with mode |
| 4 | **Remove invalid records** – Drop rows with negative quantity, zero price, invalid date range, discount > 1 |
| 5 | **Standardise categories** – Normalise uppercased/inconsistent category names |
| 6 | **Remove outliers** – Trim 1st/99th percentile of Profit |
| 7 | **Recalculate derived columns** – Recompute Sales and Profit for consistency |
| 8 | **Feature engineering** – Add Month, Year, Day_of_Week, Age_Group, Profit_Margin, Discount_Pct |

**Sample quality report:**
```
Rows before cleaning         : 10,710
Duplicate rows removed       :   210
Missing values handled       :   312
Invalid records removed       :    45
Outlier rows removed         :   215
Rows after cleaning          : 10,240
```

---

## 🔍 Exploratory Data Analysis

EDA is performed in both `src/eda.py` (static) and the Streamlit dashboard (interactive).

### Sales Analysis
- Total / monthly / daily sales trends
- Sales by category and sub-category
- Sales by state and city
- Seasonal patterns and festival-season spike

### Profit Analysis
- Monthly profit trend
- Profit by category (bar + pie)
- Profit margin heatmap
- Discount vs. profit margin scatter

### Customer Analysis
- Customers by gender, age group, city, state
- Repeat vs. new customers
- Top customers by lifetime value

### Product Analysis
- Top 10 by revenue, profit, quantity
- Category / sub-category treemap
- Low-performing product identification

---

## 🗄️ SQL Analysis

Database: `ecommerce_analytics`  
Table: `orders`

The `sql/analysis_queries.sql` file contains **18 queries** using:

- `SELECT`, `WHERE`, `GROUP BY`, `ORDER BY`, `HAVING`
- `JOIN` (implicit via subqueries)
- `CASE WHEN` for discount banding and CLV tiers
- **CTEs** for monthly revenue, CLV calculation
- **Window functions**: `RANK() OVER`, `LAG() OVER`, `SUM() OVER` (running total, YoY growth)
- Aggregate functions: `SUM`, `COUNT`, `AVG`, `MIN`, `MAX`, `ROUND`

### Setting up MySQL

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit .env with your MySQL credentials
# MYSQL_HOST=localhost
# MYSQL_PORT=3306
# MYSQL_USER=root
# MYSQL_PASSWORD=your_password

# 3. Run the database setup
python src/database.py
```

The script will:
- Create the `ecommerce_analytics` database
- Create the `orders` table with appropriate indexes
- Bulk-insert the cleaned dataset

> **Note:** MySQL is optional. The Streamlit dashboard works fully without it,
> using the CSV files directly.

---

## 🎯 Customer Segmentation (RFM)

RFM analysis (`src/customer_segmentation.py`) classifies customers into 6 segments.

### How RFM Works

| Metric | Definition | Scoring |
|--------|-----------|---------|
| **Recency** | Days since last order | 1–5 (5 = most recent) |
| **Frequency** | Number of distinct orders | 1–5 (5 = most frequent) |
| **Monetary** | Total revenue generated | 1–5 (5 = highest spend) |

Scores are assigned per quintile. Recency is **inverse-scored** (fewer days = better).

### Segment Rules

| Segment | Condition | Action |
|---------|-----------|--------|
| **VIP Customers** | R≥4, F≥4, M≥4 | Premium loyalty; exclusive offers |
| **Loyal Customers** | F≥4, M≥3 | Points rewards; upsell |
| **Potential Loyal** | R≥3, F≥2, M≥2 | Personalised campaigns |
| **New Customers** | R≥4, F=1 | Onboarding; second-purchase discount |
| **At-Risk Customers** | R∈{2,3}, F≥3 | Win-back campaigns |
| **Lost Customers** | R=1 | Last-chance reactivation |

---

## 🖥️ Dashboard Pages

Run with: `streamlit run dashboard/app.py`

### Page 1 — Executive Overview
- KPI cards: Revenue, Profit, Orders, Customers, AOV, Profit Margin
- Monthly revenue & profit trend (area + line)
- Revenue by category (bar) + Profit share (donut)
- Top 10 products (horizontal bar with profit colour gradient)
- 10 auto-generated business insights

### Page 2 — Sales Analysis
- Monthly / daily time-series (tabs)
- Category → Sub-category treemap
- Revenue by state + top 15 cities
- Payment mode distribution + order status breakdown

### Page 3 — Customer Analytics
- Customer KPIs (total, repeat, new, avg revenue)
- Top 15 customers by revenue
- Gender donut + age group bar
- Customer count by state
- Expandable detailed customer table

### Page 4 — Customer Segmentation
- RFM segment KPI row (count + % of base)
- Customers per segment (donut)
- Revenue per segment (bar)
- RFM scatter (Recency vs Monetary, sized by Frequency)
- Segment performance table
- Expandable segment methodology explanation

### Page 5 — Product Analytics
- Top 10 by revenue (coloured by profit)
- Most profitable + highest quantity sold
- Category sunburst chart
- Low-performing products expander
- Full product table expander

### Sidebar Filters (affect all pages)
- Date range
- State, City, Category, Sub-Category
- Gender, Payment Mode, Order Status

---

## 📈 Key Business Insights (Sample)

> These are computed dynamically — actual values depend on the generated dataset.

1. **Electronics** is the highest-revenue category, contributing ~35% of total revenue.
2. **Maharashtra** leads all states with ~18% of total sales.
3. Festival months (Oct–Nov) generated ~22% of annual revenue, reflecting Diwali demand.
4. Orders with discounts ≥30% show profit margins ~12 percentage points lower than normal orders.
5. Repeat customers account for ~68% of total revenue — retention has very high ROI.
6. **Laptop** is the most profitable individual product.
7. UPI is the preferred payment mode for ~28% of orders.
8. Cancellations represent ~13% of orders — logistics optimisation could recover this revenue.
9. **Mumbai** is the highest-revenue city.
10. The 26–35 age group contributes the most to sales revenue.

---

## 🚀 How to Run

### Prerequisites
- Python 3.10+
- MySQL 8.x (optional)
- Git

### Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd ecommerce-data-analytics

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate the dataset
python src/generate_dataset.py

# 5. Clean the data
python src/data_cleaning.py

# 6. (Optional) Set up MySQL
cp .env.example .env
# Edit .env with your credentials
python src/database.py

# 7. Launch the dashboard
streamlit run dashboard/app.py
```

The dashboard auto-generates data if the CSV files are missing.

---

## 🔐 Security Notes

- Never commit `.env` to Git (it is in `.gitignore`)
- Database credentials are loaded from environment variables only
- No passwords are hard-coded in any source file

---

## 📚 Module Reference

| File | Description |
|------|-------------|
| `src/generate_dataset.py` | Generates synthetic 10,500-row dataset with realistic noise |
| `src/data_cleaning.py` | 8-step automated cleaning pipeline |
| `src/analytics.py` | KPI calculation, aggregations, dynamic insights |
| `src/customer_segmentation.py` | RFM scoring and 6-tier segment assignment |
| `src/eda.py` | 11 Matplotlib/Seaborn static EDA plots |
| `src/database.py` | MySQL schema creation, data loading, query helper |
| `dashboard/app.py` | 5-page Streamlit dashboard |
| `sql/analysis_queries.sql` | 18 analytical MySQL queries |
| `reports/business_insights.md` | Business recommendations document |

---

## 💡 Resume-Ready Description

> **E-Commerce Sales & Customer Analytics Dashboard** | Python · Pandas · Plotly · Streamlit · MySQL  
> Built an end-to-end data analytics pipeline processing 10,000+ e-commerce transactions.
> Engineered an automated ETL pipeline (cleaning, validation, feature engineering), performed
> multi-dimensional EDA across sales, profit, geography, and customer behaviour, and deployed
> a 5-page interactive Streamlit dashboard with real-time sidebar filters.
> Implemented RFM-based customer segmentation identifying 6 behavioural segments.
> Wrote 18 production-quality SQL queries using CTEs, window functions, and subqueries.
> Auto-generated 10 dynamic business insights from data patterns.

---

## ❓ Interview Q&A

### Data Cleaning

**Q: How did you handle missing values?**  
A: I used a tiered strategy — for City/State I used per-customer mode imputation
(most frequent value for that customer ID), for Discount I used category-level median
(preserving domain context), and for Payment_Mode I used global mode.
Critical identifier columns (Order_ID, Customer_ID) triggered row removal if missing.

**Q: How did you identify and handle outliers?**  
A: I used IQR-based bounds on the Profit column (1st–99th percentile) to remove extreme
values while retaining legitimate high-value orders. The choice of 1%/99% instead of
the standard 25%/75% preserves more data while removing true anomalies.

### Analytics & SQL

**Q: What is a window function? Give an example from your project.**  
A: A window function performs a calculation across a set of rows related to the current row
without collapsing them into groups. In my project I used:
- `LAG() OVER (PARTITION BY month ORDER BY year)` for YoY revenue growth
- `RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC)` for intra-category product ranking
- `SUM(SUM(sales)) OVER (ORDER BY month)` for cumulative revenue

**Q: What is RFM analysis?**  
A: RFM stands for Recency (how recently a customer ordered), Frequency (how often),
and Monetary (how much they spent). Each dimension is scored 1–5 using quintile binning,
and the combined score is used to assign customers to behavioural segments.
It is widely used in CRM and marketing to prioritise customer engagement efforts.

### Dashboard

**Q: How does the dashboard handle no-data filter scenarios?**  
A: Every page function checks if the filtered DataFrame is empty and displays a
user-friendly `st.warning()` message rather than crashing or showing blank charts.
The filtering logic is separated into a single `apply_filters()` helper so it is
consistent across all pages.

**Q: How did you make the dashboard perform well with 10,000+ rows?**  
A: I used Streamlit's `@st.cache_data` decorator to cache the loaded DataFrame and RFM
computation across re-renders. Plotly charts are rendered client-side (browser) so they
don't strain the server. Aggregations are done in Pandas before passing to Plotly,
keeping chart data small.

### Business

**Q: What was the most interesting insight from the data?**  
A: The discount analysis revealed that products with ≥30% discounts showed profit margins
roughly 12 percentage points lower than normally-priced products. While the volume increase
during festival sales partially compensates, capping discounts at 20% and using
limited-time urgency instead could protect margins without sacrificing conversion.

**Q: How would you extend this project for production?**  
A: Several enhancements would make this production-ready:
1. Replace CSV with a live MySQL/PostgreSQL connection with connection pooling
2. Add a data refresh scheduler (Airflow / cron) to ingest new daily orders
3. Implement user authentication in the dashboard
4. Add automated anomaly detection to flag unusual sales drops
5. Deploy on Streamlit Cloud, AWS EC2, or GCP App Engine
6. Add email/Slack alerting for KPI threshold breaches

---

## 📄 License

MIT License — free to use, modify, and distribute for educational and commercial purposes.

---

*Built as a portfolio project for B.Tech/AIML students | Data Analytics Domain*
