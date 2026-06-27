# Dashboard Spec — Geographic & Route Intelligence

**Audience:** owner + route/logistics planning. **Answers:** *"Where do sales come
from geographically, which routes/days are productive, and where is the coverage
white-space?"* **Cadence:** monthly + route reviews.

## Data
Built on the geocoded route layer (`src/geo/`): Area_Sales routes parsed (day +
town), geocoded to coordinates via `data/reference/geo_reference.csv`, with
distance from the Shirur base. Load `dim_route_geo.csv` (route, town, lat, lon,
district, distance_km, delivery_day, customers, bills, sales) alongside the model.

## Layout

**Row 1 — Footprint**
- Map visual (Power BI **Map** / **Azure Map**): bubbles at route lat/lon, size =
  sales, colour = district or distance band. Base (Shirur) pinned.
- Cards: Routes, % sales within 30 km (local), % outstation, Geographic HHI.

**Row 2 — Territory performance**
- Routes table: town, day, distance, customers, **drops/customer** (visit
  frequency), avg bill, sales, YoY.
- Sales by **district** (Pune / Ahmednagar / …) bar; sales by **distance band**.

**Row 3 — Route schedule & white-space**
- **Sales by delivery day** (Mon–Sat) — capacity planning; Wednesday is the peak
  (Ranjangaon belt).
- **Coverage white-space**: routes with low drop-frequency vs the median — targets
  for added visits / re-engagement.

## Key measures
Sales, customers, bills by route/district/day; `Bills per customer` (drop
frequency); `Revenue per km`; `% within 30 km`; geographic HHI (calculated in the
geo layer, surfaced via the JSON feed or a measure).

## Slicers
FY, district, distance band, delivery day, reporting currency.

## Decisions it supports
Route scheduling and capacity (peak days), where to add coverage (white-space
towns), which outer territories (Shrigonda, Parner) to deepen, and how far to
extend the network economically (62% of sales are within 30 km).

## Notes
Coordinates are from a curated geocoding reference for the firm's towns — refine
with a formal geocoding pass for street-level precision. Area_Sales is a route
snapshot; some export years repeat (flagged in the geo report) — confirm with the
ERP before reading route-level YoY as definitive.
