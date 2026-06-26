"""End-to-end ERP BI pipeline orchestrator.

Runs the whole warehouse build + documentation + quality reporting with one
command, parameterised by mode and reporting currency.

    python run_pipeline.py --mode internal  --currency INR
    python run_pipeline.py --mode shareable --currency GBP

Stages:
  1. Build the star-schema warehouse from the raw ERP exports (reconciled).
  2. Generate the data dictionary + business metadata catalog (from schema).
  3. Generate the validation report (raw vs warehouse).
  4. Generate the warehouse statistics report.
  5. Generate the Data Quality Dashboard (HTML + CSV).

Money is always stored in INR; --currency only affects presentation/exports.
"""
from __future__ import annotations

import argparse
import time


def main() -> int:
    ap = argparse.ArgumentParser(description="ERP BI pipeline")
    ap.add_argument("--mode", choices=["internal", "shareable"], default="internal")
    ap.add_argument("--currency", default="INR",
                    help="reporting currency (INR is the stored source of truth)")
    ap.add_argument("--skip-build", action="store_true",
                    help="reuse the existing warehouse; only regenerate reports/docs")
    args = ap.parse_args()

    print("=" * 64)
    print(f" ERP BI PIPELINE  ·  mode={args.mode}  currency={args.currency}")
    print("=" * 64)
    t0 = time.time()

    # Stage 1 — build
    res = None
    if not args.skip_build:
        from src.warehouse.build import build_warehouse
        print("\n[1/5] Building warehouse ...")
        res = build_warehouse(mode=args.mode, reporting_currency=args.currency)
        print(f"      {res.total_rows:,} rows across {len(res.table_rows)} tables "
              f"(batch {res.batch_id})")
        npass = sum(c["status"] == "PASS" for c in res.reconciliation)
        print(f"      reconciliation: {npass}/{len(res.reconciliation)} PASS")
        if npass != len(res.reconciliation):
            print("      ❌ RECONCILIATION FAILED — stopping. Investigate the adapter.")
            return 1
    else:
        print("\n[1/5] Skipping build (--skip-build).")

    # Stage 2 — catalog/dictionary
    from src.warehouse import catalog, stats, validation
    from src import quality
    print("[2/5] Generating data dictionary + business metadata catalog ...")
    for p in catalog.generate():
        print(f"      {p}")

    # Stage 3 — validation
    print("[3/5] Generating validation report ...")
    recon = res.reconciliation if res else _recon_from_log()
    print(f"      {validation.generate(recon)}")

    # Stage 4 — statistics
    print("[4/5] Generating warehouse statistics ...")
    print(f"      {stats.generate(res)}")

    # Stage 5 — data quality dashboard
    print("[5/6] Generating data quality dashboard ...")
    html, csv = quality.generate()
    print(f"      {html}")
    print(f"      {csv}")

    # Stage 6 — decision intelligence
    print("[6/6] Generating decision intelligence (analysis, insights, BHI) ...")
    from src.di import run as di_run
    di = di_run.generate()
    print(f"      Business Health Index: {di['bhi']}/100 ({di['grade']})")
    print(f"      {di['md']}")

    print("\n" + "=" * 64)
    print(f" DONE in {time.time() - t0:.1f}s")
    print("=" * 64)
    if args.mode == "shareable":
        print("Reminder: run `python -m src.pii_audit --shareable` before sharing.")
    return 0


def _recon_from_log():
    import json
    from src.utils import LOGS_DIR
    p = LOGS_DIR / "last_build.json"
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8")).get("reconciliation", [])
    return []


if __name__ == "__main__":
    raise SystemExit(main())
