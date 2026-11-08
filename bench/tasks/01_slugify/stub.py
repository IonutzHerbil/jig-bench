import pytest

def slugify(text: str) -> str:
    """Turn a title into a URL slug: lowercase it, replace every run of characters that are not a-z or 0-9 with a single '-', and remove '-' from both ends."""
    ...


def test_examples():
    assert slugify("Rock & Roll 2") == "rock-roll-2"
    assert slugify("  Spaces  ") == "spaces"
