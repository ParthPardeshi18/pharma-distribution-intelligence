"""Warehouse builder — canonical adapter frames -> SQLite star schema.

Per build run (one import batch):
  1. resolve entity keys (customer/supplier/product via EntityResolver; company/
     salesman/area by exact normalized name)
  2. build conformed dimensions (anon vs real *_code per mode; keys identical)
  3. build facts at their true grain, attaching dimension keys
  4. stamp EVERY row with lineage (source report/year/file) + audit (batch,
     timestamp) + record-quality status
  5. reconcile fact totals against the raw ERP export
  6. write all tables + meta_import_batch

Money is stored in INR (the source of truth). Keys are identical across modes, so
analytics are identical; only the displayed *_code differs.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field

import pandas as pd

from src.adapters import get_adapter
from src.anonymise import load_code_map, normalize as anon_normalize
from src.entity_resolution import EntityResolver, stable_key
from src.utils import LOGS_DIR
from src.warehouse.db import create_all, make_engine

_ENTITY_NAME_COL = {"customer": "customer_name", "supplier": "supplier_name",
                    "product": "product_name", "company": "company_name",
                    "salesman": "salesman_name", "area": "area_name"}
_CODE_PREFIX = {"customer": "Customer", "supplier": "Supplier", "salesman": "Salesman"}
_PII = {"customer", "supplier", "salesman"}
_FUZZY = {"customer", "supplier", "product"}


def _simple_norm(name: str) -> str:
    s = re.sub(r"[^A-Z0-9 ]", " ", str(name).upper())
    return re.sub(r"\s+", " ", s).strip()


def _fy(d) -> str:
    if pd.isna(d):
        return ""
    start = d.year if d.month >= 4 else d.year - 1
    return f"{str(start)[-2:]}-{str(start + 1)[-2:]}"


def _date_key(d):
    return None if pd.isna(d) else int(pd.Timestamp(d).strftime("%Y%m%d"))


@dataclass
class BuildResult:
    batch_id: int
    mode: str
    reporting_currency: str
    started_at: str
    finished_at: str = ""
    table_rows: dict = field(default_factory=dict)
    reconciliation: list = field(default_factory=list)
    minted_codes: int = 0
    resolution_summary: dict = field(default_factory=dict)

    @property
    def total_rows(self):
        return sum(self.table_rows.values())


class WarehouseBuilder:
    def __init__(self, mode="internal", reporting_currency="INR"):
        assert mode in ("internal", "shareable")
        self.mode = mode
        self.reporting_currency = reporting_currency
        self.a = get_adapter()
        self.now = dt.datetime.now(dt.timezone.utc)
        self.batch_id = int(self.now.strftime("%Y%m%d%H%M%S"))
        self.res = BuildResult(self.batch_id, mode, reporting_currency, self.now.isoformat())
        self._resolvers = {e: EntityResolver(e) for e in _FUZZY}
        self._code_maps = {e: load_code_map(e) for e in _PII}
        self.keymap: dict[str, dict[str, int]] = {}   # entity -> norm -> key
        self.dims: dict[str, pd.DataFrame] = {}
        self.facts: dict[str, pd.DataFrame] = {}      # built fact frames (for reconcile)
        self._all_cache: dict[str, pd.DataFrame] = {}  # report_key -> all-years frame

    def _load_all(self, report_key: str) -> pd.DataFrame:
        """Cached all-years load (read-only; builders create new frames)."""
        if report_key not in self._all_cache:
            self._all_cache[report_key] = self.a.load_all_years(report_key).data
        return self._all_cache[report_key]

    # ----------------------- normalization & keys --------------------- #
    def norm(self, entity, name):
        if entity in self._resolvers:
            return self._resolvers[entity].normalize_match(str(name))
        return _simple_norm(str(name))

    def key_of(self, entity, name):
        # Returns the dimension key, or None when the name can't be resolved
        # (null/blank, or — for master-only dims — not in the master). A None key
        # is recorded as an unmatched_entity null, never an orphan minted key.
        if name is None or (isinstance(name, float) and pd.isna(name)):
            return None
        n = self.norm(entity, name)
        if not n:
            return None
        return self.keymap.get(entity, {}).get(n)

    def _code(self, entity, real_name, key):
        if self.mode == "internal" or entity not in _PII:
            return real_name
        code = self._code_maps[entity].get(anon_normalize(real_name))
        if code is None:
            self.res.minted_codes += 1
            code = f"{_CODE_PREFIX[entity]}_U{key % 100000:05d}"
        return code

    # ----------------------- standard metadata ------------------------ #
    def _stamp(self, df, report_key, quality="ok"):
        df = df.copy()
        df["src_report"] = report_key
        if "financial_year" in df.columns:
            df["src_year"] = df["financial_year"]
        else:
            df["src_year"] = None
        df["src_file"] = report_key
        df["import_batch_id"] = self.batch_id
        df["processed_at"] = self.now.isoformat()
        if "record_quality" not in df.columns:
            df["record_quality"] = quality
        df["quality_flags"] = df.get("quality_flags", pd.Series([None] * len(df)))
        return df

    # ----------------------- collect names ---------------------------- #
    def _collect_names(self, name_col):
        names: set[str] = set()
        for rk in self.a.list_reports():
            try:
                d = self._load_all(rk)
            except Exception:
                continue
            if name_col in d.columns:
                names.update(d[name_col].dropna().astype(str))
        return sorted(names)

    # ===================== DIMENSIONS ================================= #
    def build_dim_date(self):
        dates = []
        for rk in ["Sales/Sales", "Purchases/Purchase_Report", "Profit/Profit_AllBills",
                   "Outstanding/Outstanding_BillWise", "Outstanding/Payables_Ageing_BillWise"]:
            try:
                d = self._load_all(rk)
            except Exception:
                continue
            for c in [c for c in d.columns if c.endswith("_date") or c == "txn_date"]:
                dates.append(pd.to_datetime(d[c], errors="coerce").dropna())
        alld = pd.concat(dates) if dates else pd.Series([pd.Timestamp("2022-04-01")])
        lo, hi = alld.min().normalize(), alld.max().normalize()
        rng = pd.date_range(lo, hi, freq="D")
        df = pd.DataFrame({"date": rng})
        df["date_key"] = df["date"].dt.strftime("%Y%m%d").astype(int)
        df["financial_year"] = df["date"].map(_fy)
        df["year"] = df["date"].dt.year
        df["month"] = df["date"].dt.month
        df["month_name"] = df["date"].dt.strftime("%b")
        df["quarter"] = df["date"].dt.quarter
        df["fy_month_no"] = ((df["month"] - 4) % 12) + 1
        df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
        self.dims["dim_date"] = df
        return df

    def _entity_dimension(self, entity, master_report, master_attr=None,
                          master_only=False, extra_keymap_cols=None):
        """Build a dimension + the source-name->key map for facts.

        master_only=True (company/salesman/area): dim rows come ONLY from the
        master; transaction names that don't match a master are NOT added as new
        identities (their facts get a null key, reported as unmatched). This keeps
        reference dimensions clean. For customer/supplier/product, unresolved
        transaction identities DO become their own stable surrogate rows.
        """
        name_col = _ENTITY_NAME_COL[entity]
        master = self.a.load(master_report).data
        master_names = master[name_col].dropna().astype(str).tolist()
        source_names = [] if master_only else self._collect_names(name_col)

        # representative real spelling per normalized master identity
        master_real = {}
        for nm in master_names:
            master_real.setdefault(self.norm(entity, nm), nm)
        # master attributes per norm (first occurrence)
        master_attr_by_norm = {}
        if master_attr:
            for _, r in master.iterrows():
                mn = self.norm(entity, r.get(name_col))
                if mn and mn not in master_attr_by_norm:
                    master_attr_by_norm[mn] = master_attr(r)

        keymap: dict[str, int] = {}
        identities: dict[str, dict] = {}

        def add_identity(canon, real, tier, conf, is_master):
            if not canon or canon in identities:
                return
            identities[canon] = dict(key=stable_key(entity, canon), real=real,
                                     tier=tier, confidence=conf, is_master=is_master)

        for mn, real in master_real.items():
            add_identity(mn, real, "master_exact", 1.0, True)

        if entity in self._resolvers:
            resolutions = self._resolvers[entity].resolve(source_names, master_names)
            self.res.resolution_summary[entity] = EntityResolver.summarize(resolutions)
            self._resolvers[entity].flush_review_queue()
            for src_norm, r in resolutions.items():
                canon = r.matched_master if r.matched_master else r.source_norm
                if not r.matched_master:
                    add_identity(canon, src_norm, r.tier, r.confidence, False)
                keymap[src_norm] = stable_key(entity, canon)
        else:
            for nm in source_names:
                sn = self.norm(entity, nm)
                if sn not in master_real:
                    add_identity(sn, nm, "unresolved", 0.0, False)
                keymap[sn] = stable_key(entity, sn)
        for mn in master_real:
            keymap.setdefault(mn, stable_key(entity, mn))
        # extra alias columns also resolve to the master key (e.g. company
        # short-name, so product abbreviations like 'CIPLA' map to the company).
        if extra_keymap_cols:
            for _, r in master.iterrows():
                pn = self.norm(entity, r.get(name_col))
                if not pn:
                    continue
                for ec in extra_keymap_cols:
                    en = self.norm(entity, r.get(ec))
                    if en:
                        keymap.setdefault(en, stable_key(entity, pn))
        self.keymap[entity] = keymap

        rows = []
        for canon, info in identities.items():
            row = {f"{entity}_key": info["key"],
                   f"{entity}_code": self._code(entity, info["real"], info["key"])}
            row.update(master_attr_by_norm.get(canon, {}))
            if entity == "customer":
                row["match_tier"] = info["tier"]
                row["match_confidence"] = round(info["confidence"], 3)
            rows.append(row)
        return pd.DataFrame(rows)

    def build_dim_customer(self):
        def attr(r):
            return {"trade_type": r.get("trade_type"),
                    "discount_pct": pd.to_numeric(r.get("discount_pct"), errors="coerce"),
                    "source_id": r.get("ie_code")}
        df = self._entity_dimension("customer", "Masters/Customer_Master", attr)
        # area_key left null here (master has no clean area join); territory dim exists
        self.dims["dim_customer"] = df
        return df

    def build_dim_supplier(self):
        def attr(r):
            return {"discount_pct": pd.to_numeric(r.get("discount_pct"), errors="coerce")}
        df = self._entity_dimension("supplier", "Masters/Supplier_Master", attr)
        self.dims["dim_supplier"] = df
        return df

    def build_dim_company(self):
        # master-only; also key by short_name so product/stock abbreviations match
        df = self._entity_dimension("company", "Masters/Company_Master",
                                    lambda r: {"short_name": r.get("short_name")},
                                    master_only=True, extra_keymap_cols=["short_name"])
        self.dims["dim_company"] = df
        return df

    def build_dim_product(self):
        def attr(r):
            return {"unit": r.get("unit"),
                    "tax_pct": pd.to_numeric(r.get("tax_pct"), errors="coerce"),
                    "reorder_level": pd.to_numeric(r.get("reorder_level"), errors="coerce"),
                    "company_name": r.get("company_name")}
        df = self._entity_dimension("product", "Masters/Product_Master", attr)
        # map company_name -> company_key
        cmap = self.keymap.get("company", {})
        df["company_key"] = df.pop("company_name").map(
            lambda v: cmap.get(self.norm("company", v)) if pd.notna(v) else None)
        self.dims["dim_product"] = df
        return df

    def build_dim_salesman(self):
        # NOTE: Salesman_Master export is misaligned (salesman_name mostly null;
        # names spill into the address column). Flagged in data_validation.md.
        # No fact references salesman yet, so this is a reference dim only.
        df = self._entity_dimension("salesman", "Masters/Salesman_Master", master_only=True)
        self.dims["dim_salesman"] = df
        return df

    def build_dim_territory(self):
        area = self.a.load("Masters/Area_List").data
        rows = []
        seen = set()
        for _, r in area.iterrows():
            an = self.norm("area", r.get("area_name"))
            if not an or an in seen:
                continue
            seen.add(an)
            key = stable_key("area", an)
            rows.append({"area_key": key, "area_name": r.get("area_name"),
                         "zone_name": r.get("zone_name")})
            self.keymap.setdefault("area", {})[an] = key
        df = pd.DataFrame(rows)
        self.dims["dim_territory"] = df
        return df

    # ===================== FACTS ====================================== #
    def _add_date_key(self, df, src_col, dest="date_key"):
        df[dest] = pd.to_datetime(df[src_col], errors="coerce").map(_date_key)
        return df

    def build_fact_sales(self):
        sales = self._load_all("Sales/Sales")
        profit = self._load_all("Profit/Profit_AllBills")
        p = profit[["voucher_no", "financial_year", "sale_billed_amount",
                    "cost_amount", "profit_amount", "profit_pct"]]
        df = sales.merge(p, on=["voucher_no", "financial_year"], how="left")
        df["date_key"] = pd.to_datetime(df["txn_date"], errors="coerce").map(_date_key)
        df["customer_key"] = df["customer_name"].map(lambda v: self.key_of("customer", v))
        out = pd.DataFrame({
            "date_key": df["date_key"], "customer_key": df["customer_key"],
            "voucher_no": df["voucher_no"], "financial_year": df["financial_year"],
            "net_amount_inr": pd.to_numeric(df["net_amount"], errors="coerce"),
            "billed_amount_inr": pd.to_numeric(df["sale_billed_amount"], errors="coerce"),
            "cost_amount_inr": pd.to_numeric(df["cost_amount"], errors="coerce"),
            "profit_amount_inr": pd.to_numeric(df["profit_amount"], errors="coerce"),
            "profit_pct": pd.to_numeric(df["profit_pct"], errors="coerce"),
        })
        q = out["customer_key"].isna().map(lambda x: "unmatched_entity" if x else "ok")
        out["record_quality"] = q
        return out

    def build_fact_purchases(self):
        d = self._load_all("Purchases/Purchase_Report")
        out = pd.DataFrame({
            "date_key": pd.to_datetime(d["txn_date"], errors="coerce").map(_date_key),
            "supplier_key": d["supplier_name"].map(lambda v: self.key_of("supplier", v)),
            "voucher_no": d["voucher_no"], "bill_no": d.get("bill_no"),
            "financial_year": d["financial_year"],
            "net_amount_inr": pd.to_numeric(d["net_amount"], errors="coerce"),
        })
        return out

    def _product_fact(self, report, measure_map):
        d = self._load_all(report)
        out = pd.DataFrame({"product_key": d["product_name"].map(lambda v: self.key_of("product", v)),
                            "financial_year": d["financial_year"]})
        for dest, src in measure_map.items():
            out[dest] = pd.to_numeric(d[src], errors="coerce") if src in d.columns else None
        return out

    def build_fact_sales_product(self):
        return self._product_fact("Sales/Sales_ProductWise", {
            "quantity": "quantity", "scheme_qty": "scheme_qty",
            "sale_amount_inr": "sale_amount", "scheme_value_inr": "scheme_value"})

    def build_fact_purchase_product(self):
        return self._product_fact("Purchases/Purchase_ProductDetails", {
            "quantity": "quantity", "scheme_qty": "scheme_qty",
            "purchase_amount_inr": "purchase_amount", "purchase_rate_inr": "purchase_rate",
            "sale_rate_inr": "sale_rate", "mrp_inr": "mrp"})

    def build_fact_product_profit(self):
        return self._product_fact("Profit/Profit_ProductWise", {
            "quantity": "quantity", "billed_amount_inr": "sale_billed_amount",
            "cost_amount_inr": "cost_amount", "profit_amount_inr": "profit_amount",
            "profit_pct": "profit_pct"})

    def build_fact_stock_snapshot(self):
        return self._product_fact("Stock/Stock_ProductWise", {
            "quantity": "quantity", "rate_inr": "rate", "value_inr": "value"})

    def build_fact_stock_movement(self):
        d = self._load_all("Stock/Stock_InOutSummary")
        return pd.DataFrame({
            "company_key": d["company_name"].map(lambda v: self.key_of("company", v)),
            "financial_year": d["financial_year"],
            "opening_value_inr": pd.to_numeric(d["opening_value"], errors="coerce"),
            "stock_in_value_inr": pd.to_numeric(d["stock_in_value"], errors="coerce"),
            "stock_out_value_inr": pd.to_numeric(d["stock_out_value"], errors="coerce"),
            "closing_value_inr": pd.to_numeric(d["closing_value"], errors="coerce"),
        })

    def build_fact_ar_outstanding(self):
        d = self._load_all("Outstanding/Outstanding_BillWise")
        return pd.DataFrame({
            "customer_key": d["customer_name"].map(lambda v: self.key_of("customer", v)),
            "bill_date_key": pd.to_datetime(d["txn_date"], errors="coerce").map(_date_key),
            "bill_no": d.get("bill_no"), "financial_year": d["financial_year"],
            "bill_amount_inr": pd.to_numeric(d["bill_amount"], errors="coerce"),
            "balance_amount_inr": pd.to_numeric(d["balance_amount"], errors="coerce"),
            "overdue_days": pd.to_numeric(d.get("overdue_days"), errors="coerce"),
        })

    def build_fact_ap_outstanding(self):
        d = self._load_all("Outstanding/Payables_Ageing_BillWise")
        g = lambda c: pd.to_numeric(d[c], errors="coerce") if c in d.columns else None
        return pd.DataFrame({
            "supplier_key": d["supplier_name"].map(lambda v: self.key_of("supplier", v)),
            "bill_date_key": pd.to_datetime(d["txn_date"], errors="coerce").map(_date_key),
            "bill_no": d.get("bill_no"), "financial_year": d["financial_year"],
            "bill_amount_inr": g("bill_amount"), "balance_amount_inr": g("balance_amount"),
            "overdue_days": g("overdue_days"),
            "ageing_0_30_inr": g("ageing_0_30"), "ageing_31_60_inr": g("ageing_31_60"),
            "ageing_61_90_inr": g("ageing_61_90"), "ageing_91_120_inr": g("ageing_91_120"),
            "ageing_120_plus_inr": g("ageing_120_plus"),
        })

    def build_fact_price_change(self):
        d = self._load_all("Purchases/PTR_Changed_Purchase")
        return pd.DataFrame({
            "product_key": d["product_name"].map(lambda v: self.key_of("product", v)),
            "date_key": pd.to_datetime(d["txn_date"], errors="coerce").map(_date_key),
            "voucher_no": d.get("voucher_no"), "financial_year": d["financial_year"],
            "prev_ptr_inr": pd.to_numeric(d.get("prev_ptr"), errors="coerce"),
            "new_ptr_inr": pd.to_numeric(d.get("new_ptr"), errors="coerce"),
            "prev_mrp_inr": pd.to_numeric(d.get("prev_mrp"), errors="coerce"),
            "new_mrp_inr": pd.to_numeric(d.get("new_mrp"), errors="coerce"),
        })

    # ===================== ORCHESTRATION ============================== #
    _DIM_BUILDERS = ["build_dim_date", "build_dim_company", "build_dim_customer",
                     "build_dim_supplier", "build_dim_product", "build_dim_salesman",
                     "build_dim_territory"]
    _FACT_BUILDERS = {
        "fact_sales": "build_fact_sales", "fact_purchases": "build_fact_purchases",
        "fact_sales_product": "build_fact_sales_product",
        "fact_purchase_product": "build_fact_purchase_product",
        "fact_product_profit": "build_fact_product_profit",
        "fact_stock_snapshot": "build_fact_stock_snapshot",
        "fact_stock_movement": "build_fact_stock_movement",
        "fact_ar_outstanding": "build_fact_ar_outstanding",
        "fact_ap_outstanding": "build_fact_ap_outstanding",
        "fact_price_change": "build_fact_price_change",
    }
    _DIM_TABLE = {"build_dim_date": "dim_date", "build_dim_company": "dim_company",
                  "build_dim_customer": "dim_customer", "build_dim_supplier": "dim_supplier",
                  "build_dim_product": "dim_product", "build_dim_salesman": "dim_salesman",
                  "build_dim_territory": "dim_territory"}

    def run(self):
        from sqlalchemy import text
        engine = make_engine()
        create_all(engine, drop_first=True)
        LOGS_DIR.mkdir(parents=True, exist_ok=True)

        # dimensions (company before product so company_key resolves)
        for b in self._DIM_BUILDERS:
            df = getattr(self, b)()
            tname = self._DIM_TABLE[b]
            self._write(engine, tname, self._stamp(df, tname))

        # facts (retain built frames for reconciliation — no rebuild)
        for tname, b in self._FACT_BUILDERS.items():
            df = getattr(self, b)()
            self.facts[tname] = df
            self._write(engine, tname, self._stamp(df, tname))

        # reconciliation + batch row
        self._reconcile()
        self.res.finished_at = dt.datetime.now(dt.timezone.utc).isoformat()
        self._write_batch(engine)
        self._write_summary()
        return self.res

    def _write_summary(self):
        """Dump a build summary so report generators can run standalone."""
        import json
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        summary = {
            "batch_id": self.batch_id, "mode": self.mode,
            "reporting_currency": self.reporting_currency,
            "started_at": self.res.started_at, "finished_at": self.res.finished_at,
            "table_rows": self.res.table_rows, "total_rows": self.res.total_rows,
            "reconciliation": self.res.reconciliation,
            "resolution_summary": self.res.resolution_summary,
            "minted_codes": self.res.minted_codes,
        }
        (LOGS_DIR / "last_build.json").write_text(
            json.dumps(summary, indent=2, default=str), encoding="utf-8")

    def _write(self, engine, tname, df):
        # keep only columns that exist in the physical table
        from src.warehouse.schema import get_table
        cols = [c.name for c in get_table(tname).all_columns()]
        df = df[[c for c in cols if c in df.columns]]
        df.to_sql(tname, engine, if_exists="append", index=False)
        self.res.table_rows[tname] = len(df)

    def _reconcile(self):
        checks = [
            ("fact_sales", "net_amount_inr", "Sales/Sales", "net_amount"),
            ("fact_purchases", "net_amount_inr", "Purchases/Purchase_Report", "net_amount"),
            ("fact_product_profit", "profit_amount_inr", "Profit/Profit_ProductWise", "profit_amount"),
            ("fact_sales_product", "sale_amount_inr", "Sales/Sales_ProductWise", "sale_amount"),
        ]
        for tname, col, rk, raw_col in checks:
            raw_total = float(pd.to_numeric(
                self._load_all(rk)[raw_col], errors="coerce").sum())
            wh_total = float(pd.to_numeric(self.facts[tname][col], errors="coerce").sum())
            diff = round(wh_total - raw_total, 2)
            self.res.reconciliation.append({
                "table": tname, "measure": col, "raw_total": round(raw_total, 2),
                "warehouse_total": round(wh_total, 2), "difference": diff,
                "status": "PASS" if abs(diff) < 1.0 else "FAIL"})

    def _write_batch(self, engine):
        row = pd.DataFrame([{
            "import_batch_id": self.batch_id, "started_at": self.res.started_at,
            "finished_at": self.res.finished_at, "mode": self.mode,
            "reporting_currency": self.reporting_currency, "status": "success",
            "n_tables": len(self.res.table_rows), "n_rows": self.res.total_rows,
            "git_commit": None, "notes": f"minted_codes={self.res.minted_codes}"}])
        row.to_sql("meta_import_batch", engine, if_exists="append", index=False)


def build_warehouse(mode="internal", reporting_currency="INR") -> BuildResult:
    return WarehouseBuilder(mode, reporting_currency).run()
