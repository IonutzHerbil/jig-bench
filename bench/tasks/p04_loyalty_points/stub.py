import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def loyalty_points(customer: Customer, lines: list[Line]) -> int:  # on failure: raise StoreFailure(StoreError.<reason>)
    """Add loyalty points: a customer earns one point per full 100 cents of their order total; PLATINUM customers earn double."""
    ...


def test_examples():
    assert loyalty_points(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("apple"), quantity=3)]) == 4
    with pytest.raises(StoreFailure) as failure:
        loyalty_points(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("bread"), quantity=-1)])
    assert failure.value.error == StoreError.INVALID_QUANTITY
