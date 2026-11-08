import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def shipping_cost(customer: Customer, lines: list[Line]) -> Money:  # on failure: raise StoreFailure(StoreError.<reason>)
    """Add shipping costs: shipping is free when the order total is at least 5000 cents; otherwise it costs 499 cents in the EU, 599 in the UK and 799 in the US."""
    ...


def test_examples():
    assert shipping_cost(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("apple"), quantity=1)]) == Money(499)
    with pytest.raises(StoreFailure) as failure:
        shipping_cost(Customer(id=CustomerId("zoe"), tier=Tier.STANDARD, region=Region.US), [])
    assert failure.value.error == StoreError.EMPTY_CART
