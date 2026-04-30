# AI Companies SEC Revenue Analysis — Malloy + DuckDB

Analyze revenue trends, biggest climbers, and losers across 13 AI companies
using SEC EDGAR XBRL data, [Malloy](https://www.malloydata.dev/), and DuckDB.

## 🚀 Quick Start (github.dev — no install needed)

1. **Open this repo in your browser**: press `.` on the GitHub repo page

2. **Install the Malloy extension**:  
   Click the Extensions icon → search **"Malloy"** → Install → Reload

3. **Open a query file**: `climbers_losers.malloy` or `company_deep_dive.malloy`

4. Click **"Run"** above any query block → results appear in the panel on the right

---

## 📁 File Structure

```
/
├── ai_revenue.malloy          # Semantic model (sources, dimensions, measures)
├── climbers_losers.malloy     # YoY revenue analysis — biggest gainers & losers
├── company_deep_dive.malloy   # Drill into individual companies & tiers
├── data/
│   ├── revenue_facts.parquet  # Revenue records (annual + quarterly, FY2021–2024)
│   └── companies.parquet      # Company metadata (ticker, name, tier)
├── fetch_sec_data.py          # Replaces sample data with real SEC EDGAR data
└── generate_sample_data.py    # Regenerates the sample data from scratch
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

## 🔄 Replacing with Real SEC Data

The `data/` folder ships with **approximate sample data** based on public earnings.  
To pull actual XBRL facts from SEC EDGAR (free, no API key needed):

```bash
pip install requests pandas pyarrow
python fetch_sec_data.py
```

Then push the updated `data/` folder to GitHub and reopen in github.dev.

---

## 📚 Resources

- [Malloy Documentation](https://docs.malloydata.dev/)
- [Malloy VS Code Extension](https://marketplace.visualstudio.com/items?itemName=malloydata.malloy-vscode)
- [SEC EDGAR XBRL API](https://www.sec.gov/edgar/sec-api-documentation)
