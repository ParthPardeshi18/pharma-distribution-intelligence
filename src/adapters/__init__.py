"""ERP Adapter layer.

The single boundary between ERP-specific exports and the canonical warehouse.
ALL ERP-specific concerns — file discovery, header detection, column naming,
type coercion, footer-row stripping, and stable-ID detection — live here. The
warehouse, analytics, and dashboards depend only on the canonical contract
defined by `ERPAdapter`, so swapping or upgrading the ERP changes only this layer.

The firm's current ERP is MediVision Platinum; `MediVisionAdapter` implements it.
"""
from src.adapters.base import CanonicalFrame, ERPAdapter
from src.adapters.medivision import MediVisionAdapter, get_adapter

__all__ = ["ERPAdapter", "CanonicalFrame", "MediVisionAdapter", "get_adapter"]
