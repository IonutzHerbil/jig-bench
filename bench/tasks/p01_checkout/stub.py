import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def checkout(customer: Customer, lines: list[Line]) -> ChargeId:  # on failure: raise StoreFailure(StoreError.<reason>)
    """Add checkout: charge the customer for their order total through the payments library, using the customer's id as the payments customer."""
    ...


def test_examples():
    assert checkout(Customer(id=CustomerId("zoe"), tier=Tier.STANDARD, region=Region.US), [Line(sku=Sku("apple"), quantity=2)]) == ChargeId("ch_zoe_256")
    with pytest.raises(StoreFailure) as failure:
        checkout(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("cheese"), quantity=100)])
    assert failure.value.error == StoreError.OUT_OF_STOCK
