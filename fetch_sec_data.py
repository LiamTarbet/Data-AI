"""
fetch_sec_data.py
Pulls revenue (Revenues / RevenueFromContractWithCustomerExcludingAssessedTax)
from SEC EDGAR XBRL API for a curated list of AI companies.
Saves two Parquet files:
  data/revenue_facts.parquet  — all quarterly/annual revenue facts
  data/companies.parquet      — company metadata (ticker, name, CIK, SIC)
"""

import requests
import pandas as pd
import time
import json
from pathlib import Path

HEADERS = {"User-Agent": "ai-sec-malloy-project research@example.com"}

# Curated AI company universe: (ticker, CIK, display_name, tier)
COMPANIES = [
    # Pure-play AI / Infrastructure
    ("NVDA",  "0001045810", "NVIDIA",              "AI Infrastructure"),
    ("AMD",   "0000002488", "AMD",                 "AI Infrastructure"),
    ("AVGO",  "0001730168", "Broadcom",            "AI Infrastructure"),
    ("ARM",   "0001973239", "Arm Holdings",        "AI Infrastructure"),
    ("SMCI",  "0000946486", "Super Micro Computer","AI Infrastructure"),
    # Big Tech AI
    ("MSFT",  "0000789019", "Microsoft",           "Big Tech"),
    ("GOOGL", "0001652044", "Alphabet",            "Big Tech"),
    ("META",  "0001326801", "Meta",                "Big Tech"),
    ("AMZN",  "0001018724", "Amazon",              "Big Tech"),
    # Pure-play AI Software
    ("PLTR",  "0001321655", "Palantir",            "AI Software"),
    ("AI",    "0001577552", "C3.ai",               "AI Software"),
    ("BBAI",  "0001836935", "BigBear.ai",          "AI Software"),
    ("SOUN",  "0001840292", "SoundHound AI",       "AI Software"),
]

# Revenue XBRL tags to try in order (companies use different ones)
REVENUE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "SalesRevenueNet",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
]

def get_company_facts(cik: str) -> dict:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/{cik}.json"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.json()

def extract_revenue(facts: dict, ticker: str) -> list[dict]:
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    rows = []
    for tag in REVENUE_TAGS:
        if tag not in us_gaap:
            continue
        units = us_gaap[tag].get("units", {})
        usd_facts = units.get("USD", [])
        for f in usd_facts:
            # Only keep 10-K (annual) and 10-Q (quarterly) filings
            form = f.get("form", "")
            if form not in ("10-K", "10-Q", "20-F"):
                continue
            # Skip amended forms for simplicity (10-K/A etc handled separately)
            rows.append({
                "ticker":     ticker,
                "tag":        tag,
                "form":       form,
                "start":      f.get("start"),
                "end":        f.get("end"),
                "val":        f.get("val"),
                "accn":       f.get("accn"),
                "fy":         f.get("fy"),
                "fp":         f.get("fp"),
                "filed":      f.get("filed"),
            })
        if rows:
            break  # found revenue for this ticker, stop trying tags
    return rows

def main():
    Path("data").mkdir(exist_ok=True)
    all_revenue = []
    company_rows = []

    for ticker, cik, name, tier in COMPANIES:
        print(f"  Fetching {ticker} ({name})...")
        try:
            facts = get_company_facts(cik)
            rev_rows = extract_revenue(facts, ticker)
            all_revenue.extend(rev_rows)
            company_rows.append({
                "ticker":       ticker,
                "cik":          cik,
                "company_name": name,
                "tier":         tier,
            })
            print(f"    → {len(rev_rows)} revenue records")
        except Exception as e:
            print(f"    ✗ {ticker}: {e}")
        time.sleep(0.15)  # SEC rate limit: max 10 req/s

    # ── Revenue facts ──────────────────────────────────────────────
    df = pd.DataFrame(all_revenue)
    df["start"] = pd.to_datetime(df["start"], errors="coerce")
    df["end"]   = pd.to_datetime(df["end"],   errors="coerce")
    df["filed"] = pd.to_datetime(df["filed"], errors="coerce")
    df["val"]   = pd.to_numeric(df["val"],    errors="coerce")

    # Derive period length in days to distinguish annual vs quarterly
    df["period_days"] = (df["end"] - df["start"]).dt.days

    # Flag: annual = ~365 days, quarterly = ~90 days
    df["period_type"] = df["period_days"].apply(
        lambda d: "annual" if d > 300 else ("quarterly" if d < 110 else "semi-annual")
    )

    # Drop duplicates — keep latest filing per (ticker, start, end, form)
    df = df.sort_values("filed").drop_duplicates(
        subset=["ticker", "start", "end", "form"], keep="last"
    )

    df["end_year"]    = df["end"].dt.year
    df["end_quarter"] = df["end"].dt.quarter
    df["val_billions"] = df["val"] / 1e9

    df.to_parquet("data/revenue_facts.parquet", index=False)
    print(f"\n✓ Saved data/revenue_facts.parquet  ({len(df)} rows)")

    # ── Company metadata ───────────────────────────────────────────
    companies_df = pd.DataFrame(company_rows)
    companies_df.to_parquet("data/companies.parquet", index=False)
    print(f"✓ Saved data/companies.parquet  ({len(companies_df)} rows)")

if __name__ == "__main__":
    main()
