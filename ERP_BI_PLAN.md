# ERP Business Intelligence & Decision-Support System
## Master Prompt for Claude Code (Plan Mode)

> **How to use:** Save this file as `PLAN.md` in your project root. Then in Claude Code, paste the message at the very bottom under "STARTING MESSAGE" to begin. Work phase by phase.

---

```
I am building a complete Business Intelligence and decision-support 
system for my own firm using data exported from our ERP system.

This is REAL company data — not a portfolio project. Accuracy, data 
integrity, protecting raw files, and securing sensitive personal 
information are the highest priorities.

The system serves TWO purposes from ONE codebase: running my actual 
firm (internal, real data) AND demonstrating my skills for job 
applications (shareable, anonymised data).

═══════════════════════════════════════════════════════════
CRITICAL RULES — FOLLOW THROUGHOUT THE ENTIRE PROJECT
═══════════════════════════════════════════════════════════

DATA INTEGRITY:
- NEVER modify, overwrite, or delete the raw ERP export files
- Copy all raw files into data/raw/ and treat that folder as READ-ONLY
- All cleaning produces NEW files — raw stays untouched
- After every cleaning step, print a reconciliation check:
  "Raw total: X, Processed total: Y, Difference: Z" — flag mismatches
- Never silently drop rows — log every row removed with the reason
- Validate every financial total against the ERP source before proceeding

ACCURACY:
- After loading each report, print row count, column list, date range, 
  and key totals so I can verify against the ERP
- If any number looks wrong, STOP and ask me before continuing
- Currency: all amounts in INR (₹) unless the data says otherwise
- Print a "SO WHAT" business insight after every analysis — not just numbers

SCALABILITY:
- Design so future ERP exports can be dropped into data/raw/ and the 
  whole pipeline re-runs with one command
- Use config files for column mappings, not hardcoded names
- Build a single run_pipeline.py that executes everything end to end

GIT:
- Set git config user.name "ParthPardeshi18" before first commit
- All data folders go in .gitignore — only code and anonymised 
  shareable outputs are committed
- Commit after each phase

═══════════════════════════════════════════════════════════
DATA SECURITY & PII PROTECTION — MANDATORY, NON-NEGOTIABLE
═══════════════════════════════════════════════════════════

The raw ERP data contains sensitive personal and commercial information: 
mobile numbers, customer names and contact details, supplier names and 
details, salesman names, firm details, and financial records. This data 
must be protected at every step.

ABSOLUTE RULES:
1. NEVER commit raw, processed, or warehouse data to git. data/raw/, 
   data/processed/, data/warehouse/, and data/secure/ all go in 
   .gitignore. Verify BEFORE the first commit by running git status — 
   confirm no .csv, .xlsx, or .db files are staged.

2. NEVER print full PII to the console or logs. When showing samples, 
   MASK sensitive fields:
   - Mobile: 98XXXXXX21 (first 2 + last 2 only)
   - Customer/supplier/salesman names: "Cust_0001", "Supp_0001", 
     "Sales_001" in any output, chart, or report
   - Email: a***@domain.com
   - Any ID/PAN/GST number: last 4 chars only

3. Build a PII anonymisation layer as the FIRST processing step.
   Create src/anonymise.py that:
   - Reads raw data
   - Creates a SECURE LOOKUP TABLE mapping real names/numbers to 
     anonymous codes (Customer_001, Supplier_001, Salesman_001)
   - Saves the lookup to data/secure/pii_lookup.csv (gitignored, 
     restricted access)
   - Outputs an anonymised dataset where analysis runs on codes
   - All shareable dashboards, charts, reports use ONLY anonymous codes

4. Create data/secure/ folder that is:
   - Listed in .gitignore (never version controlled)
   - Home of the PII lookup table
   - Documented as "RESTRICTED — the only mapping between real 
     identities and anonymous codes"

5. Run a PII audit before any output is shared.
   Create src/pii_audit.py that scans any output file (docx, csv, 
   png filenames, xlsx) for phone-number/email patterns or known 
   customer names, and flags them BEFORE anything is shared.

6. .gitignore MUST include:
   data/raw/
   data/processed/
   data/warehouse/
   data/secure/
   reports/internal/
   dashboards/internal/
   *.csv
   *.xlsx
   *.db
   *.pbix
   venv/
   __pycache__/
   .env
   .claude/

7. Add SECURITY.md to the repo documenting:
   - What data is sensitive
   - How it is protected (anonymisation, gitignore, secure folder)
   - That the public repo contains NO real PII
   - That all shared outputs use anonymous codes only

8. Before the FIRST git commit and before ANY phase that produces 
   shareable output, STOP and confirm with me that PII protection 
   works: show me a masked sample and the git status.

═══════════════════════════════════════════════════════════
DUAL-OUTPUT REQUIREMENT — INTERNAL vs SHAREABLE
═══════════════════════════════════════════════════════════

This project serves two purposes from the SAME codebase:

PURPOSE 1 — INTERNAL (for running my actual firm):
- REAL customer names, supplier names, mobile numbers, figures
- A genuine decision-support tool to run the business
- Lives only on my local machine
- NEVER committed to git, never shared, never anonymised
- Output: reports/internal/ and dashboards/internal/
- Shows "Sharma Traders owes ₹4.2L at 90 days"

PURPOSE 2 — SHAREABLE (for job search portfolio / LinkedIn):
- ANONYMOUS codes only (Customer_017, Supplier_003, etc.)
- Same analytical skill, zero real PII
- Safe to commit to GitHub and post on LinkedIn
- Output: reports/shareable/ and dashboards/shareable/
- Shows "Customer_017, top-decile risk, ₹4.2L at 90+ days"
- Real firm name replaced with "a mid-size [industry] distribution firm"

IMPLEMENTATION:
- Build the analysis ONCE, parameterised by a MODE flag
- run_pipeline.py --mode internal   → real data, internal/ outputs
- run_pipeline.py --mode shareable  → anonymised data, shareable/ outputs
- Analytical logic, charts, KPIs, forecasts are IDENTICAL in both modes — 
  only the identities differ
- Internal outputs gitignored; shareable outputs may be committed
- Both modes always stay in sync — never maintain two codebases

═══════════════════════════════════════════════════════════
PHASE 0 — DISCOVERY, SETUP & PII PROTECTION
═══════════════════════════════════════════════════════════

1. List every file in the project folder and subfolders
2. For EACH ERP export file, print:
   - File name and size
   - All sheet names (if Excel)
   - Column headers of each sheet
   - Row count
   - First 3 rows as a sample — WITH PII ALREADY MASKED
3. Create folder structure:
   data/raw/  data/processed/  data/warehouse/  data/secure/
   src/  config/  analysis/
   dashboards/internal/  dashboards/shareable/
   reports/internal/  reports/shareable/
   outputs/charts/  docs/
4. requirements.txt: pandas, numpy, openpyxl, sqlalchemy, matplotlib, 
   seaborn, plotly, scikit-learn, statsmodels, prophet, xlsxwriter, 
   python-docx, pyyaml
5. Set up venv, install requirements
6. Create .gitignore per the security rules above
7. Produce docs/discovery_report.md documenting every file, sheet, 
   and column (with PII masked)

Then BUILD src/anonymise.py (the very first code written):
- Test the anonymisation layer
- Show me a masked sample
- Confirm data/secure/pii_lookup.csv is created and gitignored
- Run git status and confirm NO data files are staged

STOP. Show me the discovery report, a masked data sample, and git 
status. Wait for my approval before Phase 1.

═══════════════════════════════════════════════════════════
PHASE 1 — DATA MODEL & RELATIONSHIP MAPPING
═══════════════════════════════════════════════════════════

After I approve Phase 0:

1. Map relationships between ALL reports (Sales, Purchases, Stock, 
   Outstanding, Profit, Masters):
   - Key linking Sales to Customers?
   - Key linking Sales to Products?
   - Key linking Purchases to Suppliers?
   - Key linking Stock to Products?
   - Key linking Outstanding to Customers?
2. Produce an ERD (mermaid) at docs/data_model.md
3. Design a STAR SCHEMA warehouse:
   FACT: fact_sales, fact_purchases, fact_stock_movement, 
         fact_outstanding
   DIM: dim_customer, dim_product, dim_supplier, dim_territory, 
        dim_date, dim_salesman
   Document at docs/warehouse_schema.md

STOP. Show me the data model and schema for approval before building.

═══════════════════════════════════════════════════════════
PHASE 2 — CLEANING, VALIDATION & WAREHOUSE BUILD
═══════════════════════════════════════════════════════════

1. Cleaning function per report:
   - Standardise column names (config/column_mappings.yaml)
   - Parse dates, numbers, currency
   - Handle nulls, duplicates, whitespace, casing
   - Log every transformation and removed row
   - Reconcile totals against raw (print before/after)
2. Build star schema in data/warehouse/erp_warehouse.db
3. Data dictionary at docs/data_dictionary.md
4. Validation report at reports/data_validation.md:
   - Row counts: raw vs warehouse
   - Financial totals: raw vs warehouse (must match exactly)
   - Orphaned keys
   - Date coverage per table
   - Anomalies flagged

STOP. Show me the validation report before proceeding.

═══════════════════════════════════════════════════════════
PHASE 3 — MULTI-DIMENSIONAL ANALYSIS
═══════════════════════════════════════════════════════════

One analysis script per domain in analysis/. Charts to 
outputs/charts/, findings summary per domain. Cover:
- Sales performance (trend, YoY growth, by month/quarter)
- Customer performance (top customers, concentration, churn signals)
- Product performance (top/bottom sellers, lifecycle)
- Supplier performance (spend, dependency, reliability)
- Inventory performance (turnover, ageing, dead stock, buildup)
- Territory/area performance
- Profitability (gross margin by product, customer, territory)
- Working capital (debtor days, creditor days, inventory days, CCC)
- Cash flow (inflow vs outflow trend)

Generate KPIs per domain. Flag problems: slow growth, margin erosion, 
inventory buildup, poor collections, customer concentration risk, 
supplier dependency, pricing issues, working capital inefficiency.
Every finding gets a "SO WHAT" and quantified impact.

═══════════════════════════════════════════════════════════
PHASE 4 — STRATEGIC ANALYSES
═══════════════════════════════════════════════════════════

Implement each separately:
- ABC / Pareto (customers, products, suppliers)
- Customer segmentation (RFM)
- Product lifecycle analysis
- Multi-year trend analysis
- Seasonal analysis
- Inventory turnover & ageing
- Customer / supplier / territory profitability ranking
- Sales / purchase / demand forecasting (Prophet; fall back to 
  statsmodels ARIMA if Prophet fails to install)

Compare MULTIPLE financial years for long-term trends.
Summary at reports/strategic_analysis.md

═══════════════════════════════════════════════════════════
PHASE 5 — EXECUTIVE DASHBOARD SPECIFICATIONS
═══════════════════════════════════════════════════════════

I build dashboards in Power BI. Produce a detailed SPEC per 
stakeholder at dashboards/ (visuals, KPIs, slicers, layout):
- Owner/CEO (revenue, profit, cash, top risks)
- Finance (P&L, margins, working capital, cash flow)
- Sales (performance, targets, by salesman/territory)
- Inventory (turnover, ageing, stockouts, dead stock)
- Procurement (supplier spend, dependency, lead times)
- Operations (fulfilment, efficiency)
- Working capital (debtor/creditor/inventory days, CCC)

Export clean star-schema CSVs to data/warehouse/exports/ for Power BI.
Produce BOTH internal (real) and shareable (anonymised) export sets.

═══════════════════════════════════════════════════════════
PHASE 6 — BUSINESS HEALTH REPORT
═══════════════════════════════════════════════════════════

Generate reports/business_health_report.docx (produce internal and 
shareable versions):
- Executive summary (1 page): overall health verdict
- Findings by domain
- Key risks (ranked by severity)
- Key opportunities (ranked by impact)
- Multi-year trend analysis
- Prioritised recommendations: 2x2 impact vs effort, 
  high-impact/low-effort first
- Each recommendation has a measurable expected business impact

═══════════════════════════════════════════════════════════
PHASE 7 — ROADMAP & AI ENHANCEMENT PLAN
═══════════════════════════════════════════════════════════

Create reports/implementation_roadmap.docx:
- 5-year decision-support vision
- Roadmap: data prep → analytics → dashboards → automation → AI → scale
- Future AI features with rationale: demand prediction, inventory 
  optimisation, customer risk scoring, pricing recommendations, 
  natural-language business assistant
- Per feature: data required, expected benefit, complexity
- Scalability design: how future ERP exports plug in and refresh 
  dashboards automatically

═══════════════════════════════════════════════════════════
EXECUTION INSTRUCTIONS
═══════════════════════════════════════════════════════════

- Work phase by phase. Complete each fully.
- STOP for my review after Phase 0, Phase 1, and Phase 2 — the 
  foundation must be correct before building on it.
- After Phase 2, proceed through Phases 3-7, printing a summary 
  after each.
- The end goal is a DECISION SUPPORT SYSTEM, not a set of reports.
- Always preserve raw data. Always reconcile totals. Always protect 
  PII. Always explain the business "so what".

Start with Phase 0. Show me the discovery report, masked sample, 
and git status. Wait for my approval before proceeding.
```

---

## STARTING MESSAGE (paste this first in Claude Code)

```
Read PLAN.md in this folder. We are building an ERP Business 
Intelligence and decision-support system phase by phase.

This is real company data with sensitive PII — follow the security 
rules exactly. Start with Phase 0 only. Build the anonymisation layer, 
show me the discovery report, a masked data sample, and git status 
confirming no data files are staged. Do not proceed to Phase 1 until 
I approve.
```

---

## Quick reference — what tool does what

| Task | Tool | Mode |
|------|------|------|
| Discovery, cleaning, warehouse, analysis | Claude Code | both |
| PII anonymisation | Claude Code (src/anonymise.py) | n/a |
| Dashboards | Power BI Desktop | internal + shareable |
| Business health report & roadmap | Claude Code (.docx) | both |
| Git & GitHub | Terminal | shareable only |

## Safety checklist before sharing anything

- [ ] `git status` shows zero data files staged
- [ ] All shared outputs use anonymous codes (Customer_001 etc.)
- [ ] `src/pii_audit.py` passed on every file before sharing
- [ ] Real firm name replaced with placeholder in shareable version
- [ ] `data/secure/pii_lookup.csv` exists only on your local machine
- [ ] SECURITY.md present in the repo

---

*Plan version 1.0 — Parth Pardeshi — ERP BI Decision-Support System*
