"""Domain analyzers. Each exposes analyze() -> DomainReport."""
from src.di.domains import (
    cash_flow, customers, inventory, products, profitability, sales,
    suppliers, territory, working_capital,
)

# Order matters for the report narrative (revenue → profit → drivers → finance).
ALL = [sales, profitability, customers, products, suppliers, inventory,
       working_capital, territory, cash_flow]

__all__ = ["ALL"]
