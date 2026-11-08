import pytest

def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    """Given closed integer intervals [start, end], merge every pair that overlaps or shares an endpoint and return the result sorted by start."""
    ...


def test_examples():
    assert merge_intervals([[1, 2], [2, 3]]) == [[1, 3]]
    with pytest.raises(ValueError):
        merge_intervals([[5, 1]])
