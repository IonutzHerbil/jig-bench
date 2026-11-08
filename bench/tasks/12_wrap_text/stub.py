import pytest

def wrap_text(text: str, width: int) -> list[str]:
    """Greedy word wrap: split the text on whitespace into words and fill lines left to right, joining words with one space and never exceeding `width` characters per line."""
    ...


def test_examples():
    assert wrap_text("one two three", 7) == ["one two", "three"]
    with pytest.raises(ValueError):
        wrap_text("x", -1)
