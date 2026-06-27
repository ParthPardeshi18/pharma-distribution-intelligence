# Dashboard Spec — Geographic & Route Intelligence

**Audience:** owner + route/logistics planning. **Answers:** *"Where do sales come
from geographically, which routes/days are productive, and where is the coverage
white-space?"* **Cadence:** monthly + route reviews.

## Data — canonical GeoJSON (GIS layer)
Geography is now a proper GIS layer (`src/geo/gis/`) with **GeoJSON as the
canonical format** (lat/lon is only a geocoding cache). The pipeline writes
`data/geo/*.geojson` and exports copies to `data/warehouse/exports/{mode}/geo/`:

| Layer | Geometry | Use |
|---|---|---|
| `districts` / `talukas` / `villages` | Polygon | choropleth (sales/customers) |
| `territories` | Polygon | sales-territory heatmap (by route-day) |
| `routes` | LineString | delivery-route visualisation |
| `customers` | Point | customer-density / expansion map |
| `warehouses` | Point | base location |

The warehouse `dim_geo_feature` table stores every feature with its geometry as
GeoJSON (the source of truth) plus metrics — joinable to facts.

### Consuming the GeoJSON
- **Power BI**: Shape Map visual → add the `villages`/`districts` GeoJSON as a
  custom map; bind colour to `sales_inr`. (Also `dim_route_geo.csv` for the basic
  Map visual.)
- **Leaflet / Mapbox / Azure Maps / deck.gl**: load the GeoJSON FeatureCollections
  directly. A ready interactive **Leaflet** map is generated at
  `dashboards/geo/geo_intelligence_map.html` (choropleth, territories, routes,
  customer density, coverage rings, expansion targets — all toggleable).

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
