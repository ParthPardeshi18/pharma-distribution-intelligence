# Sample Dataset (anonymised)

A small, **fully anonymised** slice of the platform's outputs, so the project can
be explored without the real ERP data. All identities are anonymous codes
(`Customer_0001`, `Supplier_0001`); figures are genuine aggregates; town names are
public places. Passes the project's PII audit.

## Contents

```
samples/
  data/   star-schema CSV slices (Power BI / pandas ready)
    dim_customer_sample.csv   dim_product_sample.csv   dim_supplier_sample.csv
    dim_date_sample.csv       fact_sales_sample.csv
  geo/    canonical GeoJSON layers (Leaflet / Mapbox / Power BI Shape Map / deck.gl)
    districts · talukas · villages · territories · routes · customers · warehouses
```

## Use it
- **pandas:** `pd.read_csv('samples/data/fact_sales_sample.csv')`.
- **Leaflet/Mapbox/deck.gl:** load any `samples/geo/*.geojson` directly.
- **Power BI:** import the CSVs (star schema) and add the GeoJSON via Shape Map;
  see `dashboards/specs/powerbi_data_model.md` and `powerbi_template.md`.

## Regenerate (full, local only)
```
python run_pipeline.py --mode shareable --currency INR
# anonymised exports -> data/warehouse/exports/shareable/  (+ geo/)
```

These samples are a **subset** for demonstration; the full anonymised export is
produced by the pipeline in `--mode shareable`.
