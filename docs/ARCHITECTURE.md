# Platform Architecture

> **Pharmaceutical Distribution Intelligence Platform** — v1.0.
> This document is the canonical description of the product architecture: the
> layers, how data flows through them, and how each layer is isolated so it can
> evolve independently.

## 1. Architectural principles

1. **Layered & loosely coupled.** Each layer depends only on the contract of the
   layer below. The ERP can change, the warehouse can move to Postgres, the BI
   tool can change — without rewriting analytics.
2. **One ERP boundary.** All ERP-specific knowledge lives in the *Adapter Layer*.
   Everything above it sees only canonical, ERP-agnostic data.
3. **Config over code.** Column maps, report specs, KPI thresholds, currency
   rates, health-index weights, churn rules, and geocoding all live in `config/`.
4. **Schema-as-data.** The warehouse schema, KPI registry, and (future) AI feature
   registry are declarative — documentation and physical artifacts are generated
   from them, so they never drift.
5. **INR is the source of truth.** Money is stored once in INR; currency is a
   presentation concern.
6. **GeoJSON is the canonical spatial format.** Lat/lon is only a geocoding cache.
7. **PII-first.** Anonymisation and audit gate every shareable output.
8. **Reproducible.** One command (`run_pipeline.py`) rebuilds everything;
   raw data is immutable and reconciled to the rupee at every step.

## 2. The layer stack

```mermaid
flowchart TB
    subgraph SRC["Source systems"]
      ERP["ERP exports (MediVision today;<br/>Marg / Busy / Tally / SAP / Oracle / CSV tomorrow)"]
      GEO["Geo reference (geocoding cache)"]
      FX["Exchange rates"]
    end

    subgraph ADP["1 · ERP Adapter Layer  (src/adapters)"]
      A1["File discovery · header detection"]
      A2["Canonical column mapping"]
      A3["Footer/total stripping · type coercion"]
      A4["Stable-ID detection (future-proof keys)"]
    end

    subgraph ING["2 · Data Ingestion  (src/cleaning, entity_resolution)"]
      I1["Cleaning · de-dup · reconciliation"]
      I2["Entity resolution (fuzzy + review queue)"]
      I3["Surrogate keys (float64-safe)"]
    end

    subgraph WH["3 · Data Warehouse  (src/warehouse — SQLite star schema)"]
      W1["Conformed dims + facts at true grain"]
      W2["Lineage / audit / quality on every row"]
      W3["dim_geo_feature (GeoJSON geometry)"]
    end

    subgraph BI["4 · Business Intelligence  (src/di/warehouse_api, src/quality)"]
      B1["KPI registry · analytics API"]
      B2["Validation · statistics · DQ dashboard"]
    end

    subgraph DI["5 · Decision Intelligence  (src/di)"]
      D1["Insight · root-cause · risk · opportunity"]
      D2["Recommendation · scorecards"]
      D3["Business Health Index (weight profiles)"]
    end

    subgraph SA["6 · Strategic Analytics  (src/strategic)"]
      S1["ABC/Pareto · RFM · lifecycle · seasonality"]
      S2["Forecasting (CI + quality + assumptions)"]
    end

    subgraph GIS["7 · Geographic Intelligence  (src/geo, src/geo/gis)"]
      G1["Geocoding · territory · concentration"]
      G2["Canonical GeoJSON layers"]
      G3["Interactive maps (Leaflet)"]
    end

    subgraph AI["8 · AI Layer  (future — src/ai)"]
      AI1["Demand / sales / cash forecasting"]
      AI2["Risk scoring · pricing · optimisation"]
      AI3["Executive Copilot / NL assistant"]
    end

    subgraph OUT["9 · Presentation & Delivery"]
      P1["Power BI (star-schema CSV + GeoJSON)"]
      P2["Business Health Report (.docx)"]
      P3["REST APIs (future)"]
      P4["Web dashboards (future)"]
    end

    AUTO["10 · Automation & Orchestration<br/>(run_pipeline.py → cron/CI → cloud)"]

    SRC --> ADP --> ING --> WH --> BI --> DI --> SA
    WH --> GIS
    BI --> AI
    DI --> OUT
    SA --> OUT
    GIS --> OUT
    AI --> OUT
    AUTO -.orchestrates.-> ADP
    AUTO -.orchestrates.-> OUT
```

## 3. Layer responsibilities

| # | Layer | Today (v1.0) | Module(s) |
|---|---|---|---|
| 1 | **ERP Adapter** | MediVision Platinum exports → canonical frames | `src/adapters/` |
| 2 | **Data Ingestion** | clean, reconcile, resolve entities, mint keys | `src/cleaning*`, `src/entity_resolution.py` |
| 3 | **Data Warehouse** | SQLite star schema, lineage/audit/quality, spatial table | `src/warehouse/` |
| 4 | **Business Intelligence** | KPI registry, validation, statistics, DQ dashboard | `src/di/kpis.py`, `src/quality.py`, `src/warehouse/{validation,stats}.py` |
| 5 | **Decision Intelligence** | insights, risks, opportunities, recommendations, BHI | `src/di/` |
| 6 | **Strategic Analytics** | ABC/RFM/lifecycle/seasonality/forecasting | `src/strategic/` |
| 7 | **Geographic Intelligence** | geocoding, territory, **canonical GeoJSON**, maps | `src/geo/`, `src/geo/gis/` |
| 8 | **AI Layer** | *(roadmap)* forecasting, risk, pricing, copilot | `src/ai/` (future) |
| 9 | **Presentation** | Power BI exports, .docx reports, *(future)* APIs/web | `src/powerbi/`, `src/report/` |
| 10 | **Automation** | one-command pipeline → cron/CI → cloud | `run_pipeline.py` |

## 4. Data flow (end to end)

```mermaid
flowchart LR
    raw["data/raw/*.xlsx<br/>(immutable)"] -->|adapter| canon["canonical frames"]
    canon -->|clean + resolve| keyed["keyed, reconciled data"]
    keyed -->|load| db[("erp_warehouse.db<br/>star schema")]
    db --> kpis["KPIs / metrics"]
    kpis --> di["Decision Intelligence<br/>+ Business Health Index"]
    kpis --> strat["Strategic + forecasts"]
    db --> gis["GeoJSON layers<br/>+ dim_geo_feature"]
    di --> docx["Health Report .docx"]
    strat --> stratmd["Strategic report"]
    gis --> maps["Interactive maps"]
    db --> pbi["Power BI CSV + GeoJSON exports"]
    di --> pbi
    gis --> pbi
```

Every money figure reconciles to the ERP's own report totals to the rupee at the
warehouse boundary; nothing downstream can silently diverge.

## 5. Cross-cutting concerns

- **Security / PII** — `src/anonymise.py` + `src/pii_audit.py`; internal vs
  shareable modes; `SECURITY.md`.
- **Multi-currency** — `src/currency.py`, `config/currency_config.yaml`.
- **Quality & lineage** — every warehouse row carries source report/year/file,
  import batch, timestamp, and a record-quality status.
- **Configuration** — `config/*.yaml` (+ `config/geo_reference.csv`).

## 6. Why this architecture lasts 10 years

The contracts between layers are stable; the implementations behind them are
swappable. A new ERP touches only Layer 1. A move to Postgres or a cloud warehouse
touches only Layer 3. New AI modules read the same warehouse and KPI registry.
The spatial layer already speaks GeoJSON, so GPS/telematics and routing add new
*tables and modules*, never a redesign. See `AI_ROADMAP.md`, `GIS_ROADMAP.md`,
`ERP_EXPANSION.md`, and `SAAS_VISION.md`.
