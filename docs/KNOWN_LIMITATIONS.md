# Known Limitations (v1.0)

Honest constraints of the current release, each with the path to resolution.
Surfacing these is deliberate — silent gaps are worse than stated ones.

## Data / source

| # | Limitation | Impact | Resolution |
|---|---|---|---|
| 1 | **No sales/purchase line items** in the ERP export | customer×product analysis and SKU-level monthly demand are not possible | request a sales/purchase *register with product lines*; `fact_sales_line` is reserved in the schema |
| 2 | **`Salesman_Master` export is misaligned** (name column blank) | `dim_salesman` is sparse | no fact references salesman yet → no measure affected; fix at ERP export |
| 3 | **`Area_Sales` repeats 24-25 == 25-26** in the export | naive route-level YoY would read 0% | analyzer auto-selects the most recent *differing* year and flags it; verify with ERP |
| 4 | Some master records carry footer/summary rows | handled, but indicates ERP export hygiene | strip rules in the adapter; ideally clean at source |

## Geographic

| # | Limitation | Impact | Resolution |
|---|---|---|---|
| 5 | **Boundary polygons are Voronoi approximations** | choropleths are catchment-based, not official admin boundaries | drop official GADM/OSM/Census GeoJSON into `data/geo/` (GIS_ROADMAP P1) |
| 6 | **Coordinates are curated/town-level** | distances are town-to-town, not street-level | swap the geocoding cache for a real geocoding API |
| 7 | Customer locations are **town-level** (no per-customer GPS) | density is by town | per-customer geocoding when addresses are reliable / GPS arrives |

## Analytics / AI

| # | Limitation | Impact | Resolution |
|---|---|---|---|
| 8 | **Forecast CI coverage ~50%** vs nominal 80% on 48 monthly points | intervals run narrow | more history, model tuning, or quantile/MCMC intervals (reported transparently today) |
| 9 | Pricing elasticity is a **proxy** (no controlled experiments) | pricing analysis is directional | A/B price tests; demand model in v2.0 |
| 10 | AI layer is **roadmap** (forecasting prototyped) | risk/pricing/optimisation not yet live | see `docs/AI_ROADMAP.md` |

## Platform

| # | Limitation | Impact | Resolution |
|---|---|---|---|
| 11 | **Single-firm, local, file-based** (by design) | not multi-tenant | `docs/SAAS_VISION.md` migration path (Postgres, APIs, RBAC) |
| 12 | Interactive map needs internet for OSM basemap tiles | offline shows vectors only | bundle an offline tile pack or a vector basemap |
| 13 | No real **`.pbit`** shipped (built in Power BI) | template is a documented blueprint | author the `.pbit` in Power BI from `dashboards/specs/` |

None of these block the v1.0 value: a reconciled, explainable decision-support
platform. They define the v2.0/v3.0 backlog.
