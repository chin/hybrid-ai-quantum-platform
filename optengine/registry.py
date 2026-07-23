"""Compatibility imports for the pre-Catalog API."""

from optengine.catalog import Catalog

StrategyRegistry = Catalog

__all__ = [
    "Catalog",
    "StrategyRegistry",
]
