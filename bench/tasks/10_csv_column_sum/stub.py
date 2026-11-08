import pytest

def csv_column_sum(csv: str, column: str) -> int:
    """Sum one integer column of a simple CSV text: the first line is the header, fields are separated by commas with no quoting, and blank lines are ignored."""
    ...


def test_examples():
    assert csv_column_sum("a,b\n1,2\n3,4", "a") == 4
    with pytest.raises(ValueError):
        csv_column_sum("a\n1", "b")
