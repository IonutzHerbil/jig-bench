import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def refund_order(charge: ChargeId, customer: Customer, lines: list[Line]) -> Money:  # on failure: raise StoreFailure(StoreError.<reason>)
    """Add refunds: refund the full order total of the given lines against an existing charge through the payments library, and return the refunded amount as Money."""
    ...


def test_examples():
    assert refund_order(ChargeId("ch_anna_2000"), Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("apple"), quantity=1)]) == Money(136)
    with pytest.raises(StoreFailure) as failure:
        refund_order(ChargeId("bogus"), Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("bread"), quantity=1)])
    assert failure.value.error == StoreError.REFUND_FAILED
