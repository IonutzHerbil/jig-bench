import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def reserve(lines: list[Line]) -> dict[Sku, int]:  # on failure: raise StoreFailure(StoreError.<reason>)
    """Add stock reservation: check that the catalog can supply all the lines together (lines for the same SKU add up) and return the stock left for each SKU in the cart."""
    ...


def test_examples():
    assert reserve([Line(sku=Sku("apple"), quantity=1)]) == {Sku("apple"): 49}
    with pytest.raises(StoreFailure) as failure:
        reserve([Line(sku=Sku("bread"), quantity=11)])
    assert failure.value.error == StoreError.OUT_OF_STOCK
