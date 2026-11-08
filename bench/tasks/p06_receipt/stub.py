import pytest

from lib.payments import ChargeId
from store.types import Customer, CustomerId, Line, Money, Region, Sku, StoreError, StoreFailure, Tier

def receipt(customer: Customer, lines: list[Line]) -> list[str]:  # on failure: raise StoreFailure(StoreError.<reason>)
    """Add receipts: one text line per cart line, '<product name> x<quantity> <line total>', followed by 'TOTAL <order total>'."""
    ...


def test_examples():
    assert receipt(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("cheese"), quantity=1)]) == ["Cheese x1 12.99", "TOTAL 14.82"]
    with pytest.raises(StoreFailure) as failure:
        receipt(Customer(id=CustomerId("anna"), tier=Tier.GOLD, region=Region.EU), [Line(sku=Sku("caviar"), quantity=1)])
    assert failure.value.error == StoreError.UNKNOWN_SKU
