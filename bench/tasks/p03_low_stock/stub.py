import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def low_stock(threshold: int) -> list[Sku]:
    """Add a low-stock report: the SKUs of every catalog product whose stock is below the threshold, in alphabetical order."""
    ...


def test_examples():
    assert low_stock(3) == [Sku("wine")]
    assert low_stock(50) == [Sku("bread"), Sku("cheese"), Sku("wine")]
