import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def split_bill(customer: Customer, lines: list[Line], people: int) -> list[Money]:  # on failure: raise StoreFailure(StoreError.<reason>)
    """Add bill splitting: split the order total between `people` as evenly as possible in whole cents, the first shares taking any extra cents, e.g."""
    ...


def test_examples():
    assert split_bill(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("bread"), quantity=2)], 2) == [Money(399), Money(399)]
    with pytest.raises(StoreFailure) as failure:
        split_bill(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("bread"), quantity=2)], -1)
    assert failure.value.error == StoreError.INVALID_QUANTITY
