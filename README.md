# AI Companies SEC Revenue Analysis — Malloy + DuckDB

Analyze revenue trends, biggest climbers, and losers across 13 AI companies
using SEC EDGAR XBRL data, [Malloy](https://www.malloydata.dev/), and DuckDB.

## 🚀 Quick Start (github.dev — no install needed)

1. **Open this repo in your browser**: press `.` on the GitHub repo page  
   (or navigate to `https://github.dev/YOUR_USERNAME/YOUR_REPO`)

2. **Install the Malloy extension**:  
   Click the Extensions icon → search **"Malloy"** → Install

3. **Open a query file** from the `queries/` folder

4. Click **"Run"** above any query block → results appear in the Malloy panel

> The `data/` folder contains sample Parquet files so everything runs immediately.  
> See [Replacing with Real Data](#replacing-with-real-sec-data) below to use live EDGAR data.

---

## 📁 Project Structure

```
ai-sec-malloy/
├── ai_revenue.malloy          # Semantic model (sources, dimensions, measures)
├── queries/
│   ├── climbers_losers.malloy # Main analysis: YoY climbers & losers
│   └── company_deep_dive.malloy # Drill into individual companies
├── data/
│   ├── revenue_facts.parquet  # Revenue records per company/period
│   └── companies.parquet      # Company metadata (ticker, name, tier)
├── fetch_sec_data.py          # Fetches real data from SEC EDGAR API
└── generate_sample_data.py    # Regenerates sample data (offline)
```

---

## 🏢 Companies Covered

| Ticker | Company | Tier |
|--------|---------|------|
| NVDA | NVIDIA | AI Infrastructure |
| AMD | AMD | AI Infrastructure |
| AVGO | Broadcom | AI Infrastructure |
| ARM | Arm Holdings | AI Infrastructure |
| SMCI | Super Micro Computer | AI Infrastructure |
| MSFT | Microsoft | Big Tech |
| GOOGL | Alphabet | Big Tech |
| META | Meta | Big Tech |
| AMZN | Amazon | Big Tech |
| PLTR | Palantir | AI Software |
| AI | C3.ai | AI Software |
| BBAI | BigBear.ai | AI Software |
| SOUN | SoundHound AI | AI Software |

---

## 📊 Key Queries

### Biggest Climbers & Losers (FY2023 → FY2024)
```malloy
// queries/climbers_losers.malloy — Query 1
run: revenue_facts -> {
  where: period_type = 'annual' and fiscal_year = 2024 | 2023
  nest: by_year is {
    group_by: fiscal_year
    aggregate: rev is val_billions.sum()
  }
  group_by: company_name, tier
}
```

### Annual Revenue Leaderboard
```malloy
run: revenue_facts -> {
  where: period_type = 'annual' and fiscal_year = 2024
  group_by: company_name, tier
  aggregate: revenue_2024_b is val_billions.sum()
  order_by: revenue_2024_b desc
}
```

### Multi-Year Growth Arc
```malloy
run: revenue_facts -> {
  where: period_type = 'annual'
  group_by: company_name, tier
  aggregate:
    rev_2021 is val_billions.sum() { where: fiscal_year = 2021 }
    rev_2022 is val_billions.sum() { where: fiscal_year = 2022 }
    rev_2023 is val_billions.sum() { where: fiscal_year = 2023 }
    rev_2024 is val_billions.sum() { where: fiscal_year = 2024 }
}
```

---

## 🔄 Replacing with Real SEC Data

The `data/` folder ships with **approximate sample data** based on public earnings.  
To pull actual XBRL facts from SEC EDGAR (free, no API key):

```bash
# Python 3.10+
pip install requests pandas pyarrow

python fetch_sec_data.py
```

This hits `data.sec.gov` (~13 API calls, ~2s) and overwrites the Parquet files.  
Push the updated files to GitHub → reopen in github.dev → queries reflect real data.

---

## 📐 Data Schema

### `revenue_facts.parquet`

| Column | Type | Description |
|--------|------|-------------|
| ticker | string | Stock ticker (NVDA, MSFT…) |
| form | string | SEC form type (10-K, 10-Q, 20-F) |
| period_type | string | annual / quarterly / semi-annual |
| start | date | Period start date |
| end | date | Period end date |
| val | float | Revenue in USD |
| val_billions | float | Revenue in USD billions |
| fy | int | Fiscal year |
| fp | string | Fiscal period (FY, Q1–Q4) |
| filed | date | Date filed with SEC |
| end_year | int | Calendar year of period end |
| end_quarter | int | Calendar quarter of period end |
| period_days | int | Length of reporting period in days |

### `companies.parquet`

| Column | Type | Description |
|--------|------|-------------|
| ticker | string | Stock ticker |
| cik | string | SEC CIK (unique filer ID) |
| company_name | string | Display name |
| tier | string | AI Infrastructure / Big Tech / AI Software |

---

## 📚 Resources

- [Malloy Documentation](https://docs.malloydata.dev/)
- [Malloy VS Code Extension](https://marketplace.visualstudio.com/items?itemName=malloydata.malloy-vscode)
- [SEC EDGAR XBRL API](https://www.sec.gov/edgar/sec-api-documentation)
- [SEC XBRL Viewer](https://efts.sec.gov/LATEST/search-index?q=%22revenues%22&dateRange=custom&startdt=2024-01-01)
