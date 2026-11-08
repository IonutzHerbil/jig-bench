import pytest

def bank_ledger(ops: list[str]) -> dict[str, int]:
    """Process bank ledger operations in order and return the final balance of every opened account."""
    ...


def test_examples():
    assert bank_ledger(["open x", "deposit x 10"]) == {"x": 10}
    with pytest.raises(ValueError):
        bank_ledger(["withdraw x 1"])
