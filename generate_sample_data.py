"""
generate_sample_data.py
Creates sample Parquet files with realistic revenue data for AI companies.
These approximate actual reported figures from SEC filings (2022-2025).
Run fetch_sec_data.py to replace with real EDGAR data.
"""
import pandas as pd
import numpy as np
from pathlib import Path

Path("data").mkdir(exist_ok=True)

COMPANIES = [
    ("NVDA",  "0001045810", "NVIDIA",               "AI Infrastructure"),
    ("AMD",   "0000002488", "AMD",                  "AI Infrastructure"),
    ("AVGO",  "0001730168", "Broadcom",             "AI Infrastructure"),
    ("ARM",   "0001973239", "Arm Holdings",         "AI Infrastructure"),
    ("SMCI",  "0000946486", "Super Micro Computer", "AI Infrastructure"),
    ("MSFT",  "0000789019", "Microsoft",            "Big Tech"),
    ("GOOGL", "0001652044", "Alphabet",             "Big Tech"),
    ("META",  "0001326801", "Meta",                 "Big Tech"),
    ("AMZN",  "0001018724", "Amazon",               "Big Tech"),
    ("PLTR",  "0001321655", "Palantir",             "AI Software"),
    ("AI",    "0001577552", "C3.ai",                "AI Software"),
    ("BBAI",  "0001836935", "BigBear.ai",           "AI Software"),
    ("SOUN",  "0001840292", "SoundHound AI",        "AI Software"),
]

# Annual revenue (USD billions) per company: FY2021, FY2022, FY2023, FY2024
# Sources: public earnings releases / 10-K filings (approximate)
ANNUAL_REVENUE = {
    "NVDA":  [16.68,  26.97,  44.87,  130.50],
    "AMD":   [16.43,  23.60,  22.68,   25.79],
    "AVGO":  [27.45,  33.20,  35.82,   51.57],
    "ARM":   [ 2.70,   2.70,   2.68,    3.23],
    "SMCI":  [ 3.56,   5.20,   7.12,   14.94],
    "MSFT":  [168.09, 198.27, 211.92,  245.12],
    "GOOGL": [257.64, 282.84, 307.39,  350.02],
    "META":  [117.93, 116.61, 134.90,  164.50],
    "AMZN":  [469.82, 513.98, 574.79,  637.96],
    "PLTR":  [  1.54,   1.91,   2.23,    2.87],
    "AI":    [  0.183,  0.253,  0.267,   0.311],
    "BBAI":  [  0.145,  0.155,  0.155,   0.158],
    "SOUN":  [  0.047,  0.057,  0.066,   0.108],
}

FISCAL_YEARS = [2021, 2022, 2023, 2024]

rows = []
for ticker, cik, name, tier in COMPANIES:
    annual_revs = ANNUAL_REVENUE[ticker]
    for i, (fy, annual) in enumerate(zip(FISCAL_YEARS, annual_revs)):
        # Add annual record
        rows.append({
            "ticker":       ticker,
            "form":         "10-K",
            "period_type":  "annual",
            "start":        pd.Timestamp(f"{fy-1}-02-01"),
            "end":          pd.Timestamp(f"{fy}-01-31") if ticker in ("NVDA", "MSFT") else pd.Timestamp(f"{fy}-12-31"),
            "val":          annual * 1e9,
            "val_billions": annual,
            "fy":           fy,
            "fp":           "FY",
            "filed":        pd.Timestamp(f"{fy+1}-02-15"),
            "end_year":     fy,
            "end_quarter":  4,
            "period_days":  365,
        })

        # Synthesize 4 quarters (roughly proportioned with some growth curve)
        # Q1 slightly lighter, Q4 heavier for most tech companies
        weights = np.array([0.22, 0.24, 0.25, 0.29])
        for q, w in enumerate(weights, 1):
            q_rev = annual * w
            q_end_month = q * 3
            q_end = pd.Timestamp(f"{fy}-{q_end_month:02d}-{28 if q_end_month in [2,4,6,9,11] else 30}")
            q_start = q_end - pd.DateOffset(months=3) + pd.DateOffset(days=1)
            rows.append({
                "ticker":       ticker,
                "form":         "10-Q",
                "period_type":  "quarterly",
                "start":        q_start,
                "end":          q_end,
                "val":          q_rev * 1e9,
                "val_billions": q_rev,
                "fy":           fy,
                "fp":           f"Q{q}",
                "filed":        q_end + pd.DateOffset(days=45),
                "end_year":     fy,
                "end_quarter":  q,
                "period_days":  90,
            })

df = pd.DataFrame(rows)
df.to_parquet("data/revenue_facts.parquet", index=False)
print(f"✓ revenue_facts.parquet  ({len(df)} rows)")

companies_df = pd.DataFrame([
    {"ticker": t, "cik": c, "company_name": n, "tier": tier}
    for t, c, n, tier in COMPANIES
])
companies_df.to_parquet("data/companies.parquet", index=False)
print(f"✓ companies.parquet  ({len(companies_df)} rows)")
