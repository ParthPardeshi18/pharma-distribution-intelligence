# Dashboard Spec — Operations

**Audience:** owner + delivery/route operations. **Answers:** *"How much are we
moving, how efficiently, and where are the route/territory gaps?"* **Cadence:**
weekly.

## Layout

**Row 1 — Throughput**
- Cards: Bills (sales + purchase), Avg Bill Value, Lines processed (product-fact
  rows), Active Customers served.
- Bills per month trend; bills by transaction type (cash CA vs credit CR/CC).

**Row 2 — Territory / route coverage**
- Sales by area (`Area_Sales`): revenue, # customers, # bills per area.
- Top-5 territory concentration %; underperforming areas table.
- Customers-per-area and bills-per-customer (coverage intensity proxies).

**Row 3 — Service signals**
- Churn/at-risk customers by area (route-coverage signal from `src/di/churn.py`).
- Seasonality strip (peak Sep / trough Apr) to plan delivery capacity.

## Key measures
`[Bills]`, `[Avg Bill Value]`, bills by tran type, area revenue / customers / bills,
churn count by area.

## Slicers
FY, territory/area, transaction type, reporting currency.

## Decisions it supports
Route planning and capacity for the Jul-Sep peak, spotting under-served areas, and
turning churn signals into delivery-route action.

## Limitation
True fulfilment/fill-rate and delivery-time KPIs require dispatch/GRN timestamps
not in the current ERP exports. This page uses bill throughput, territory
coverage, and churn as operational proxies.
