# Dashboard Spec — Sales

**Audience:** owner + route salesmen. **Answers:** *"How are sales tracking, who's
growing, who's slipping, and which retailers to call?"* **Cadence:** weekly.

## Layout

**Row 1 — Performance**
- Cards: Revenue, Revenue YoY %, Bills, Avg Bill Value, Active Customers.
- Revenue vs same-period-last-year (combo) + 6-month forecast with CI band.

**Row 2 — Customers**
- **RFM segment** treemap (Champions / Loyal / Can't-Lose-Them / At Risk / …) sized
  by value; click to filter.
- ABC customer table (Class A/B/C share).
- Top-10 customers by revenue (bar) and Top-10 concentration % card.

**Row 3 — Churn / win-back (route action)**
- **Churn & at-risk call list**: established retailers silent beyond their cadence
  — customer, last order, days since, prior-year billings. (From `src/di/churn.py`.)
- High-growth customers (biggest YoY gainers) to deepen.
- Sales by territory/area (from Area_Sales) — map or bar.

## Key measures
`[Revenue INR]`, `[Revenue YoY %]`, `[Bills]`, `[Avg Bill Value]`,
`[Top 10 Customer Share %]`, churn status (imported from DI feed), RFM segment
(`dim_customer` attribute or DI feed).

## Slicers
Reporting currency, FY, territory/area, RFM segment, customer ABC class.

## Drill-through
Customer → customer detail (order history, recency, segment, balance).

## Decisions it supports
Daily route call lists, win-back targeting, where to defend concentration, and
which growing accounts to invest in.
