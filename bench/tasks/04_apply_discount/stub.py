import pytest

def apply_discount(total_cents: int, code: str, day: int) -> int:
    """Apply a discount code to a cart total in cents on a given day number."""
    ...


def test_examples():
    assert apply_discount(5000, "HALF", 3) == 2500
    with pytest.raises(ValueError):
        apply_discount(100, "NOPE", 1)
