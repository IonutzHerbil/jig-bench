import pytest

def parse_duration(text: str) -> int:
    """Parse a duration such as '1h30m', '45s' or '2h5s' into a number of seconds."""
    ...


def test_examples():
    assert parse_duration("2m30s") == 150
    with pytest.raises(ValueError):
        parse_duration("3x")
