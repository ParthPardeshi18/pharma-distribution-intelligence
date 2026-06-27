# Installation Guide

## Prerequisites
- **Python 3.11** (production runtime; see `.python-version`).
- Git. ~1 GB free disk. Windows / macOS / Linux.
- (Optional) Power BI Desktop for dashboards.

## Steps

```bash
# 1. Clone
git clone <repo-url>
cd "Sukhakarta Distributors"

# 2. Create the virtual environment on Python 3.11
py -3.11 -m venv venv            # Windows
# python3.11 -m venv venv        # macOS/Linux
venv\Scripts\activate            # Windows
# source venv/bin/activate       # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) configure
copy .env.example .env           # set REPORTING_CURRENCY, PIPELINE_MODE
```

## Provide data
Place ERP exports under the source folders the adapter reads, then copy to the
immutable raw store:
```
data/raw/<Domain>/<Report>_<FY>.xlsx     # e.g. data/raw/Sales/Sales_25-26.xlsx
```
Raw files are treated as read-only. (For a portfolio run, use the anonymised
`samples/` dataset — see `docs/USER_GUIDE.md`.)

## Verify
```bash
python -m pytest -q               # full test suite (skips DB-backed tests until first build)
python run_pipeline.py --mode internal --currency INR
```
A successful run prints `4/4 reconciliation PASS` and writes the warehouse,
reports, GeoJSON layers, and Power BI exports.

## Troubleshooting
- **shapely/scipy import errors** → ensure Python 3.11 (not 3.12+); reinstall.
- **Prophet install issues** → the pipeline falls back to SARIMAX automatically.
- **`no such table`** → run `run_pipeline.py` once to build the warehouse.
- See `docs/warehouse_maintenance.md` for refresh and config details.
