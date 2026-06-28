# Public Live Demo — Deployment Guide

This deploys the Streamlit app as a **public, anonymised** live demo (for LinkedIn
/ recruiters) on **Streamlit Community Cloud** (free). The public instance runs in
`shareable` mode and serves **only** the anonymised warehouse — no real identity is
ever published, and the real data never leaves your machine.

How it stays safe:
- The repo contains **no data** (everything under `data/` is gitignored).
- The **anonymised** warehouse (`erp_warehouse_shareable.db`) is published once as a
  **GitHub Release asset**; the deployed app downloads it on first start.
- `PDI_MODE=shareable` pins the public instance to anonymised data; the role gate
  forces every login to anonymised identities anyway.

---

## One-time setup

### 1. Build the anonymised warehouse (locally)

```bash
venv\Scripts\python run_pipeline.py --mode shareable --currency INR
```

This writes `data/warehouse/erp_warehouse_shareable.db` (anonymous codes; verified
0 real-name leaks).

### 2. Publish it as a Release asset

The download URL is already wired into `config/app_config.yaml` → `demo.db_url`
using the tag **`demo-data-v1`** and filename **`erp_warehouse_shareable.db`**:

```bash
gh release create demo-data-v1 ^
  "data/warehouse/erp_warehouse_shareable.db" ^
  --title "Demo data (anonymised warehouse)" ^
  --notes "Anonymised warehouse for the public live demo. No real identities."
```

To refresh later: `gh release upload demo-data-v1 data/warehouse/erp_warehouse_shareable.db --clobber`.

### 3. Deploy on Streamlit Community Cloud

1. Go to <https://share.streamlit.io> → **New app** → pick this GitHub repo.
2. **Main file path:** `streamlit_app.py`
3. **Python version:** 3.11 (Advanced settings).
4. **Secrets** (Advanced settings → Secrets) — paste:
   ```toml
   [auth]
   salt = "a-long-random-string"
   ```
   (The demo data URL is already in `app_config.yaml`; no secret needed for it.)
5. **Environment variable:** set `PDI_MODE = shareable` (App settings → Environment,
   or add `PDI_MODE="shareable"` under `[env]` if your host supports it). If your
   host can't set env vars, instead change `app.mode: shareable` in
   `config/app_config.yaml` before pushing.
6. **Deploy.** First load downloads the anonymised warehouse (~80 MB, one-time);
   subsequent loads are instant.

### 4. Share

The app **opens with no login** — visitors land straight in the anonymised,
read-only Guest view. Just share the app URL; recruiters click and explore. (Staff
can elevate via the sidebar 🔐 *Staff sign in*, but on the public host only the
anonymised warehouse exists, so they see anonymised data too.)

Put the app URL in your LinkedIn project / README.

---

## Notes

- **Forecasting** uses Prophet; it installs from `requirements.txt` on Cloud (first
  build is slower). If a host can't build Prophet, the engine falls back to SARIMAX.
- **Re-pin the salt** for any real deployment; don't ship the committed default.
- To take the demo down: delete the Streamlit app and the `demo-data-v1` release.
  (Note: anything already public may have been cached/indexed.)
- The internal (real-name) `erp_warehouse.db` must **never** be uploaded anywhere —
  it stays local and gitignored.
