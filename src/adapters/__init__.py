"""ERP Adapter layer.

The single boundary between ERP-specific exports and the canonical warehouse.
ALL ERP-specific concerns — file discovery, header detection, column naming,
type coercion, footer-row stripping, and stable-ID detection — live here. The
warehouse, analytics, and dashboards depend only on the canonical contract
defined by `ERPAdapter`, so swapping or upgrading the ERP changes only this layer.
"""
from src.adapters.base import CanonicalFrame, ERPAdapter
from src.adapters.marg import MargAdapter, get_adapter

__all__ = ["ERPAdapter", "CanonicalFrame", "MargAdapter", "get_adapter"]
