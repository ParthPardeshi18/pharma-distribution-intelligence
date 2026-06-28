# Streamlit Application (v1.1) — Primary User Interface

The Streamlit app is the **primary way to use the platform**. It is a thin
presentation layer over the existing engines: every number it shows is computed
in `src/` (warehouse, Decision Intelligence, Strategic Analytics, GIS,
forecasting, KPI registry, Business Health Index) and merely **cached and
rendered** by `app/`. No business logic is duplicated.

> Power BI is retained as an **optional** reporting layer — see
> [`dashboards/specs/`](../dashboards/specs/). The app is the front door.

## Launch

```bash
venv\Scripts\activate                 # Windows (see docs/INSTALLATION.md)
pip install -r requirements.txt        # adds streamlit + pydeck
python run_pipeline.py --mode internal --currency INR   # build the warehouse first
python -m streamlit run streamlit_app.py
```

The app opens at <http://localhost:8501>.

> ⚠️ **Launch Streamlit through the project's Python 3.11 venv.** Use
> `python -m streamlit run …` from the **activated** venv, or
> `venv\Scripts\python -m streamlit run streamlit_app.py` without activating.
> A bare `streamlit run …` may resolve to a global Python install that lacks the
> project dependencies and fails with `ModuleNotFoundError: No module named
> 'sqlalchemy'`.

## Data modes — internal vs public (privacy by design)

The platform serves **two physically separate warehouses** built from the same
pipeline (surrogate keys are identical across both, so all engines work unchanged):

| Mode | Warehouse file | Identities | Use |
|------|----------------|-----------|-----|
| `internal` | `data/warehouse/erp_warehouse.db` | **Real** customer / supplier / salesman names | Your firm's own decision-making |
| `shareable` | `data/warehouse/erp_warehouse_shareable.db` | **Anonymous codes** (`Customer_0001`…) | Public / LinkedIn / portfolio |

The app reads **only** the warehouse for the active mode, so in public mode the
engines never even open the real-name database. The mode also flows into the
Decision Intelligence narratives — because those interpolate the (now anonymous)
codes, the prose is anonymised too, automatically.

**Build both warehouses:**

```bash
python run_pipeline.py --mode internal  --currency INR   # real (your firm)
python run_pipeline.py --mode shareable --currency INR   # anonymised (public)
```

**Two gates decide what a user sees — role first, then app mode:**

1. **Role gate (per user).** `auth.real_data_roles` in `config/app_config.yaml`
   lists the roles allowed to see real identities (default `[admin, analyst]`).
   **Any role not listed — e.g. `viewer` — is forced to the anonymised warehouse**,
   no matter how the app is configured. A viewer can never be shown PII, even on
   your internal deployment. Tighten to `[admin]` if analysts should also be
   anonymised.
2. **App mode (deployment-wide).** For the allowed roles, the base mode comes from
   `PDI_MODE=shareable` (env, recommended for public deployments) → `app.mode` in
   config (default `internal`). An **admin** can flip modes live from the sidebar
   to preview the anonymised view (only if that warehouse is built); switching
   clears all caches.

The active mode is per-session (thread-local), so on a shared server an admin and
a viewer can be signed in at once and each sees only their own data — no
cross-contamination. Every page carries a coloured banner — 🔒 red for internal,
🔓 green for anonymised.

### Publishing publicly — do this

1. Build the shareable warehouse (`--mode shareable`).
2. Deploy with **`PDI_MODE=shareable`** set, and ship **only** the
   `erp_warehouse_shareable.db` file (never the internal `.db`, which is
   gitignored and must stay private).
3. The Reports page in public mode generates **only** the anonymised `.docx`.

> Town / taluka / district names on the Geographic page are public geography
> (like state/city in any case study) and are intentionally shown in both modes.
> Only person/account identities (customers, suppliers, salesmen) are anonymised.
> Aggregate ₹ figures follow the existing "shareable" policy (already published in
> the shareable reports). If you do not want ₹ figures public either, deploy with
> a redacted currency layer or omit the financial pages — ask and I'll wire it.

## Open access + separate staff sign-in

The app **opens with no login wall** — every visitor lands as a **Guest** in the
read-only, **anonymised** view (`auth.guest_role: viewer` in config). This is the
public/LinkedIn default. **Staff sign in separately** from the sidebar
(🔐 *Staff sign in*) to elevate to real data:

| Login | Role | Access |
|-------|------|--------|
| _(none — default)_ | Guest (viewer) | read-only dashboards · **always anonymised** |
| `admin` / `admin123` | admin | all pages incl. Data Quality · real data |
| `analyst` / `analyst123` | analyst | all analytics + reports · real data |

On a public host only the anonymised warehouse exists, so even a staff login sees
anonymised data there. To require a login for everyone (no guest), set
`auth.guest_role: ""`; to disable auth entirely on a trusted single-user host, set
`auth.enabled: false`.

Credentials live in `config/app_users.yaml` (gitignored). Copy
`config/app_users.example.yaml`, replace the SHA-256 hashes, and override the salt
via `.streamlit/secrets.toml` (`[auth] salt = "…"`) or the `AUTH_SALT` env var.

## Pages

| Page | What it shows |
|------|----------------|
| **Overview** | Business Health Index gauge, headline KPIs with YoY, BHI across all weight profiles, firm-wide top risks & opportunities, executive narrative |
| **Decision Intelligence** | Per-domain drill-down: KPI cards, insights, root causes, ranked risks & ₹-opportunities, a prioritised impact-vs-effort recommendation matrix, and a scorecard |
| **Strategic Analytics** | ABC/Pareto, RFM segments, product lifecycle, seasonality, multi-year trends, inventory ageing, profitability rankings |
| **Forecasting** | Sales/purchases projections with confidence-interval bands, model-quality metrics (MAPE, coverage), assumptions, and a plain-language explanation |
| **Geographic** | Interactive **pydeck GeoJSON** maps over the canonical spatial layers; territory productivity and geographic-concentration (HHI, distance bands) analytics |
| **Reports & Downloads** | Generate the executive Business Health Report (.docx), download GeoJSON layers and warehouse CSV datasets |
| **Data Quality** | Row counts, referential integrity (orphan keys), quality-status breakdown, database size (admin-only) |

## Sidebar controls

- **Presentation currency** — INR / USD / EUR / GBP. INR is the source of truth;
  figures convert at display time only.
- **Health Index profile** — balanced / conservative / growth / cash_preservation
  / profit_optimization / custom (default: `cash_preservation`).
- **Fiscal year** — applied where relevant.
- **Refresh data** — clears caches and re-reads the warehouse.

## Optional Claude AI summaries

Executive narratives always come from the local DI engine and need no network.
An **optional** enhancer rewrites them into board-ready prose with Claude
(`claude-opus-4-8`). It is **off by default**. To enable:

1. Set `ai_summary.enabled: true` in `config/app_config.yaml`.
2. Provide an API key via `ANTHROPIC_API_KEY` or
   `.streamlit/secrets.toml` (`[anthropic] api_key = "…"`).
3. `pip install anthropic`.

A "✨ Polish with Claude" button then appears under each narrative. If the key or
SDK is missing, the button is hidden and the engine narrative is shown unchanged.

## Caching

- `@st.cache_data` memoises every warehouse-derived result (1-hour TTL).
- `@st.cache_resource` holds the SQLite engine and currency converter.
- The warehouse is built by a batch pipeline, not live; use **Refresh data**
  after a rebuild.

## Architecture

```
streamlit_app.py        entry point — st.navigation + auth gate + RBAC
app/
  config.py             app_config.yaml + app_users.yaml loaders
  theme.py              palette, CSS, status colours
  auth.py               login + role-based access control (pure + UI)
  data.py               cached accessors over src/ (zero logic duplication)
  components.py         KPI cards, filters, narrative box, downloads
  ai.py                 optional Claude enhancer
  views/                one render(opts) per page
```

## Tests

```bash
pytest tests/test_streamlit_app.py -q          # full (incl. AppTest)
pytest tests/test_streamlit_app.py -m "not slow" -q   # fast unit tests only
```

Covers auth hashing/verification, RBAC, config integrity, currency formatters,
and `streamlit.testing` AppTest checks of the auth gate plus every page rendering
against the real warehouse.
