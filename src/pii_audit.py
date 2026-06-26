"""PII audit — last line of defence before anything is shared.

Scans output files (and optionally the whole repo) for leaked personal data:
- Indian mobile numbers (10-digit starting 6-9)
- email addresses
- any real identity present in the secure lookup (customer/supplier/salesman names)

Exit code is non-zero if anything is found, so it can gate a commit/share.

CLI:
  python -m src.pii_audit <path> [<path> ...]   # scan specific files/dirs
  python -m src.pii_audit --shareable           # scan reports/shareable + dashboards/shareable + data/warehouse/exports
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

from src.utils import PROJECT_ROOT, SECURE_DIR

MOBILE_RE = re.compile(r"(?<!\d)[6-9]\d{9}(?!\d)")
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]{2,}@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

TEXT_SUFFIXES = {".md", ".csv", ".txt", ".json", ".html", ".svg"}
# Binary office docs we also peek into as text
BINARY_SUFFIXES = {".docx", ".xlsx", ".pptx"}

SHAREABLE_DIRS = [
    PROJECT_ROOT / "reports" / "shareable",
    PROJECT_ROOT / "dashboards" / "shareable",
    PROJECT_ROOT / "data" / "warehouse" / "exports",
    PROJECT_ROOT / "outputs",
]


def _load_allowlist() -> set[str]:
    cfg_path = PROJECT_ROOT / "config" / "anonymisation.yaml"
    if not cfg_path.exists():
        return set()
    try:
        import yaml
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
        return {str(x).upper().strip() for x in cfg.get("audit_allowlist", [])}
    except Exception:
        return set()


def _load_real_names() -> list[str]:
    p = SECURE_DIR / "pii_lookup.csv"
    if not p.exists():
        return []
    lk = pd.read_csv(p, dtype=str).fillna("")
    allow = _load_allowlist()
    # Only flag reasonably distinctive names (avoid 1-2 char false positives) and
    # skip the owner's own allowlisted identities.
    return [v for v in lk["real_value"].tolist()
            if len(str(v).strip()) >= 5 and str(v).upper().strip() not in allow]


def _read_text(path: Path) -> str:
    if path.suffix.lower() in BINARY_SUFFIXES:
        try:
            import zipfile
            with zipfile.ZipFile(path) as z:
                return " ".join(
                    z.read(n).decode("utf-8", "ignore")
                    for n in z.namelist() if n.endswith(".xml"))
        except Exception:
            return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def scan_file(path: Path, real_names: list[str]) -> list[str]:
    findings: list[str] = []
    text = _read_text(path)
    if not text:
        return findings
    if MOBILE_RE.search(text):
        findings.append(f"mobile-number pattern ×{len(MOBILE_RE.findall(text))}")
    if EMAIL_RE.search(text):
        findings.append(f"email pattern ×{len(EMAIL_RE.findall(text))}")
    upper = text.upper()
    # Two-stage: fast substring prefilter, then word-boundary confirm so a short
    # identity (e.g. "PARTH") does not match inside a longer token ("PARTHPARDESHI18").
    hits = []
    for n in real_names:
        nu = n.upper()
        if nu in upper and re.search(rf"\b{re.escape(nu)}\b", upper):
            hits.append(n)
    if hits:
        findings.append(f"real identities ×{len(hits)} (e.g. masked)")
    return findings


def gather_paths(targets: list[Path]) -> list[Path]:
    files: list[Path] = []
    for t in targets:
        if t.is_dir():
            files += [p for p in t.rglob("*")
                      if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES | BINARY_SUFFIXES]
        elif t.is_file():
            files.append(t)
    return files


def main() -> int:
    ap = argparse.ArgumentParser(description="PII leak audit")
    ap.add_argument("paths", nargs="*", help="files/dirs to scan")
    ap.add_argument("--shareable", action="store_true",
                    help="scan all shareable output directories")
    args = ap.parse_args()

    targets = [Path(p) for p in args.paths]
    if args.shareable:
        targets += SHAREABLE_DIRS
    targets = [t for t in targets if t.exists()]
    if not targets:
        print("Nothing to scan (no existing paths given).")
        return 0

    real_names = _load_real_names()
    files = gather_paths(targets)
    print(f"PII audit: scanning {len(files)} file(s); "
          f"{len(real_names)} known identities loaded.")

    flagged = 0
    for f in files:
        findings = scan_file(f, real_names)
        if findings:
            flagged += 1
            rel = f.relative_to(PROJECT_ROOT) if PROJECT_ROOT in f.parents else f
            print(f"  ⚠️  {rel}: {', '.join(findings)}")

    if flagged:
        print(f"\n❌ PII AUDIT FAILED — {flagged} file(s) contain potential PII. "
              f"Do NOT share until resolved.")
        return 1
    print("\n✅ PII audit passed — no leaks detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
