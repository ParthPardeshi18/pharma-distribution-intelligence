# Dashboard Spec — Procurement

**Audience:** owner/purchaser. **Answers:** *"Where does our spend go, how
dependent are we on a few suppliers, and where can we negotiate?"* **Cadence:**
monthly + before negotiations.

## Layout

**Row 1 — Spend**
- Cards: Total Purchases, Active Suppliers, Top-5 Supplier Dependency %.
- Purchases trend (monthly) with the 6-month purchase forecast (CI band).

**Row 2 — Concentration & negotiation**
- Supplier ABC table (A/B/C share of spend).
- Top-10 suppliers by spend (bar) → negotiation targets; 1%-of-spend value label.
- Purchases by manufacturer/company.

**Row 3 — Price & terms**
- **PTR/MRP change events** (`fact_price_change`): products with recent
  price/scheme changes — input to repricing.
- AP ageing & creditor days (how long we take to pay) — leverage in negotiations.

## Key measures
`[Purchases INR]`, supplier count, `Top 5 Supplier Share %` (TOPN pattern),
`[Creditor Days]`, `[AP Balance INR]`.

## Slicers
Reporting currency, FY, manufacturer, supplier ABC class.

## Decisions it supports
Annual rate/scheme negotiations with top suppliers, secondary-sourcing for
concentrated categories, and timing of payments.

## Limitation
Supplier lead times and on-time delivery need GRN/PO-date data not in the current
exports; dependency, spend, and price-change analysis are fully supported.
