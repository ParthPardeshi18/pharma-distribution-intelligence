# Dashboard Spec — Working Capital

**Audience:** owner/finance. **Answers:** *"How much cash is tied up in the
operating cycle, and which lever frees it?"* **Cadence:** monthly.

## Layout

**Row 1 — The cash cycle**
- Cards: Debtor Days, Inventory Days, Creditor Days, **Cash Conversion Cycle**.
- CCC waterfall: +Debtor Days +Inventory Days −Creditor Days = CCC, with YoY delta.

**Row 2 — Components over time**
- Debtor / Creditor / Inventory days trend (by FY) — see which is moving.
- AR ageing (receivables) and AP ageing (payables) bucket bars.

**Row 3 — Cash impact**
- Working-capital value: AR + Inventory − AP, by FY.
- "What-if" cards: cash released if Inventory Days → 40, or Debtor Days → 10
  (scenario from the strategic opportunity feed).

## Key measures
`[Debtor Days]`, `[Creditor Days]`, `[Inventory Days]`, `[Cash Conversion Cycle]`,
`[AR Balance INR]`, `[AP Balance INR]`, `[Inventory Value INR]`, working-capital =
`[AR Balance INR] + [Inventory Value INR] - [AP Balance INR]`.

## Slicers
Reporting currency, FY.

## Conditional formatting
Debtor Days ≤15 green / ≥60 red; CCC ≤20 green / ≥75 red; inventory days ≤40 green.

## Decisions it supports
Where to focus cash release (here, inventory dominates the cycle), supplier-credit
strategy, and collections priority — even though this is a low-receivables,
cash-heavy business.
