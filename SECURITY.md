# Security & PII Protection

This repository contains code for a Business Intelligence system built on **real
ERP data** from a pharmaceutical distribution firm. The raw data contains
sensitive personal and commercial information and is **never committed**.

## What data is sensitive

| Category | Examples | Where it appears |
|---|---|---|
| Personal contact | mobile numbers, telephone, email | Customer/Supplier/Salesman masters, Purchase reports |
| Identities | customer, supplier, salesman names | every transactional report |
| Commercial | bill numbers, discounts, prices, financial totals | Sales, Purchases, Profit, Outstanding |
| Firm identity | firm name, address, contact block | banner of every export |

## How it is protected

1. **Raw data is immutable and gitignored.** Raw exports are copied to
   `data/raw/` (set read-only). `data/raw/`, `data/processed/`, `data/warehouse/`,
   `data/secure/`, `data/reference/`, the root export folders, and `*.csv/*.xlsx/*.db`
   are all in `.gitignore`. **Verify with `git status` before every commit.**

2. **Anonymisation layer (`src/anonymise.py`).** Builds an append-only secure
   lookup mapping real identities → stable codes (`Customer_0001`,
   `Supplier_0001`, `Salesman_0001`). Stored at `data/secure/pii_lookup.csv`
   — **gitignored; the only bridge between real identities and codes.**

3. **Masking helpers (`src/utils.py`).** No full PII is ever printed to console,
   logs, or reports: mobile → `98XXXXXX99`, names → codes, email → `a***@x.com`,
   IDs → last-4.

4. **PII audit (`src/pii_audit.py`).** Scans any output for mobile/email patterns
   and known real identities; exits non-zero if anything leaks. Run before sharing:
   `python -m src.pii_audit --shareable`.

## Dual-output model

- **Internal** (`reports/internal/`, `dashboards/internal/`) — real data, local
  only, **never committed**.
- **Shareable** (`reports/shareable/`, `dashboards/shareable/`) — anonymised
  codes only, firm name replaced with a placeholder, safe to commit/post.

The public repository contains **no real PII** and all shared outputs use
anonymous codes only.

## Safety checklist before sharing anything

- [ ] `git status` shows zero data files staged
- [ ] All shared outputs use anonymous codes (`Customer_0001`, …)
- [ ] `python -m src.pii_audit --shareable` passed
- [ ] Real firm name replaced with placeholder in the shareable version
- [ ] `data/secure/pii_lookup.csv` exists only on the local machine
- [ ] This `SECURITY.md` is present in the repo
