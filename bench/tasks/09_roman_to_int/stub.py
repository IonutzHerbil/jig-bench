import pytest

def roman_to_int(s: str) -> int:
    """Convert a Roman numeral written with I V X L C D M in standard subtractive notation (IV, IX, XL, XC, CD, CM) to an integer."""
    ...


def test_examples():
    assert roman_to_int("XL") == 40
    with pytest.raises(ValueError):
        roman_to_int("IIZ")
