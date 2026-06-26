# Entity Resolution & Surrogate-Key Strategy (Phase 1)

## Why this exists

Current ERP exports identify customers/suppliers/products by **text name**, not a
stable code. The warehouse must still give every entity a **stable key** so facts
join reliably and analysis is reproducible — and it must **automatically adopt
real ERP IDs** the day they appear, with zero downstream change.

Measured reality (all FYs vs masters):

| Entity | Distinct in txns | In master | Exact match (normalized) | Approach |
|---|--:|--:|--:|---|
| **Supplier** | 100 | 231 | **100%** | direct key on normalized name |
| **Product** | 8,742 | 29,034 | **100%** | direct key on normalized name |
| **Customer** | 3,243 | 2,126 | **32%** | **fuzzy resolution** + key |

So entity resolution is, in practice, a **customer-only** problem. Suppliers and
products resolve by exact normalized name today.

## The surrogate key — three-tier precedence

Every dimension row gets one immutable `*_key`. How it is derived, in priority
order (the adapter already surfaces tier 1 via `source_id_columns`):

1. **Tier 1 — ERP source ID (preferred, future-proof).** If a populated stable
   ID column exists (`id_candidates` in `report_specs.yaml`, e.g. `ie_code`,
   `alias`), the key is derived from it: `key = hash(entity, source_id)`. When the
   ERP starts exporting codes on transactions, this tier activates automatically.
2. **Tier 2 — resolved master identity.** Name matched (exact or fuzzy) to a
   master row → key tied to that master entity. Carries master enrichment (area,
   discount, contact).
3. **Tier 3 — unresolved surrogate.** No master match → the entity still gets a
   stable key from its normalized name (`key = hash(entity, norm_name)`) and is
   **quarantined** for review. Analysis is never blocked; the row simply lacks
   master enrichment until mapped.

`norm_name` = upper-cased, punctuation-stripped, whitespace-collapsed
(`src.anonymise.normalize`). Keys are deterministic hashes so re-runs and
incremental loads are stable (append-only, never renumbered).

## Customer fuzzy matching (Tier 2 for the 68% non-exact)

Pipeline, conservative by design (false matches are worse than misses):

1. **Blocking** — group candidates by cheap signals (first token, area/town,
   soundex of first word) to avoid O(n²) comparisons.
2. **Score** within blocks using token-set ratio (rapidfuzz if available; pure-
   Python Jaccard fallback) on `norm_name`, with `address`/`area` as a tiebreaker.
3. **Decide:**
   - score ≥ 0.92 **and** unambiguous → auto-accept (Tier 2).
   - 0.80–0.92 or ambiguous → **review queue** (`data/secure/customer_match_review.csv`).
   - < 0.80 → Tier 3 unresolved surrogate.
4. **Persist** accepted matches in `data/reference/customer_map.csv`
   (`norm_name → customer_key`), append-only and human-editable. Once a mapping
   exists it is reused — matching is incremental, not redone each run.

> Known cause of mismatch to investigate during build: transaction names embed a
> route/zone marker like `VEDANTA (A) MEDICAL`, `BALAJI (G) MED STORE`. A
> normalization rule to strip the `(X)` marker into a separate attribute is
> expected to lift exact-match rate materially before fuzzy matching even runs.

## Quarantine & transparency

- Unresolved entities are listed in `reports/data_validation.md` with counts and
  the **value they represent** (₹ of sales/purchases sitting on unresolved keys),
  so we know the materiality of what's unmatched.
- **No silent drops, no silent guesses.** Auto-accepted matches above threshold
  are logged; everything else is visible in the review queue.

## Auto-adoption of future stable IDs (the forward-compat contract)

- The adapter already detects populated `id_candidates` and exposes them as
  `source_id_columns` on every `CanonicalFrame`.
- The Phase-2 warehouse loader's `resolve_entity_key()` checks Tier 1 **first**.
  The day Sales/Purchase exports include a customer/product code, those rows key
  off the code automatically; name-based keys remain only for historical rows
  lacking codes, and a one-time backfill maps old keys to new IDs.
- **No change to facts, dimensions, analytics, or dashboards is required** — the
  contract is "give me a `customer_key`", and only its derivation changes.

## Build order (Phase 2)

1. Normalize names (incl. `(X)` route-marker rule) → exact match suppliers/products.
2. Build `dim_customer` with Tier 1→3; run customer fuzzy matcher; write review queue.
3. Generate keys; attach to all facts; report unresolved materiality in validation.
