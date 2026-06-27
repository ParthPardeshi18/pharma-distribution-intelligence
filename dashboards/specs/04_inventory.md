# Dashboard Spec — Inventory

**Audience:** owner + store/purchase staff. **Answers:** *"Is stock right-sized,
what's slow or near expiry, and where is cash locked up?"* **Cadence:** weekly.

## Layout

**Row 1 — Health**
- Cards: Inventory Value, Inventory Turnover (×), Inventory Days, At-Risk (≤90-day
  expiry) value.
- Turnover trend vs the 9× target.

**Row 2 — Ageing & expiry (pharma-critical)**
- Expiry-bucket bar: Expired / ≤90d / 91-180 / 181-365 / >365, by stock value.
- Near-expiry product table (batch, expiry date, qty, value) — prioritised for
  sell-through or return-to-supplier.

**Row 3 — Movement & lifecycle**
- Stock value by manufacturer (`fact_stock_movement`: opening/in/out/closing).
- **Product lifecycle** stacked bar: New / Growth / Mature / Decline / Dormant
  with revenue share (from `src/strategic/lifecycle.py`).
- Slow-mover / dead-stock list: products with stock but low/no recent sales.

## Key measures
`[Inventory Value INR]`, `[Inventory Turnover]`, `[Inventory Days]`, at-risk value
(from strategic ageing feed), lifecycle stage (from strategic feed).

## Slicers
Reporting currency, FY, manufacturer, expiry bucket, lifecycle stage.

## Decisions it supports
Reorder-level setting by velocity, clearing slow/near-expiry stock before the
April trough, and releasing working capital from over-stocked lines.

## Limitation
Stockouts/fill-rate need order-vs-availability data the ERP does not export; this
page covers value, turnover, ageing, and lifecycle.
