# Dashboard Spec — Owner / CEO

**Audience:** the owner. **Question it answers:** *"Is the business healthy, and
what are the 3 things I must act on?"* **Cadence:** daily glance, weekly review.

## Layout (single page, 3 bands)

**Band 1 — Health headline (top)**
- **Business Health Index** card: 0-100 gauge with grade (A-F), profile selector
  (Balanced / Cash Preservation / Growth / …). Source: `src/di/health_index.py`.
- KPI cards (with YoY arrow + sparkline): Revenue, Gross Profit, Gross Margin %,
  Cash Conversion Cycle, Inventory Value, AR Balance.

**Band 2 — Trend & seasonality (middle)**
- Combo chart: monthly Revenue (bars) + Gross Margin % (line), 24 months.
- Sales forecast line with **80% confidence band** (next 6 months) — from
  `reports/strategic_analysis` forecast feed.
- Seasonality strip: monthly index heatmap (peak Sep / trough Apr).

**Band 3 — Act on this (bottom)**
- **Top 3 risks** (from DI risk engine) — name, score, one-line description.
- **Top 3 opportunities** with ₹ impact (win-back, inventory release, pricing).
- **Do-first recommendations** table (ranked by impact × confidence ÷ effort).

## Visuals & measures
| Visual | Measure(s) |
|---|---|
| Health gauge | BHI (imported from DI JSON, or modelled from component measures) |
| Revenue / Profit / Margin cards | `[Revenue INR]`, `[Gross Profit INR]`, `[Gross Margin %]`, `[Revenue YoY %]` |
| CCC card | `[Cash Conversion Cycle]` |
| Revenue+margin combo | `[Revenue INR]`, `[Gross Margin %]` by `dim_date[month]` |
| Forecast band | forecast yhat / lower / upper |

## Slicers
Reporting currency (`dim_rate[currency]`), financial year, time range.

## Drill-through
From any KPI card → the matching stakeholder page (margin → Finance, CCC →
Working Capital, inventory → Inventory).

## Decisions it supports
Where to spend attention this week; whether the recovery is holding; whether cash
and margins are safe while revenue moves.
