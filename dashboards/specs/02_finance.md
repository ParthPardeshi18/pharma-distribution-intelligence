# Dashboard Spec — Finance

**Audience:** owner/accountant in a finance hat. **Answers:** *"How profitable are
we, where is margin moving, and is cash healthy?"* **Cadence:** weekly + month-end.

## Layout (single page)

**Row 1 — P&L headline**
- Cards: Billed Sales, COGS, Gross Profit, Gross Margin %, Net Purchases.
- P&L bridge / waterfall: Billed → −COGS → Gross Profit (current FY).

**Row 2 — Margin analysis**
- Gross Margin % trend (48 months) with the 6% target line.
- Margin by product Class (ABC) and by manufacturer (`dim_company`) — bar.
- Margin-drag table: high-revenue, low-margin products (from profitability ranking).

**Row 3 — Working capital & cash**
- Cards: Debtor Days, Creditor Days, Inventory Days, **Cash Conversion Cycle**.
- AR vs AP balance trend; AP ageing buckets (0-30 … 120+).
- Operating-cash proxy (Gross Profit − ΔWorking Capital) by FY.

## Key measures
`[Billed INR]`, `[COGS INR]`, `[Gross Profit INR]`, `[Gross Margin %]`,
`[Purchases INR]`, `[Debtor Days]`, `[Creditor Days]`, `[Inventory Days]`,
`[Cash Conversion Cycle]`, `[AR Balance INR]`, `[AP Balance INR]`.

P&L statement view: load the parsed `fin_pl_statement` (Trading & P&L) for the
formal account-line view alongside the warehouse measures.

## Slicers
Reporting currency, FY, manufacturer, product ABC class.

## Conditional formatting
Margin % vs 6%/3% bands; CCC vs 20/75 days; Debtor Days vs 15/60.

## Decisions it supports
Pricing/discount policy, which SKUs erode margin, whether the cash cycle is
lengthening, and supplier credit strategy.
