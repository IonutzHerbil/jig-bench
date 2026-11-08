import pytest

def shortest_path(edges: list[str], start: str, goal: str) -> int:
    """Find the total weight of the shortest path between two nodes of an undirected weighted graph."""
    ...


def test_examples():
    assert shortest_path(["p-q:3"], "p", "q") == 3
    with pytest.raises(ValueError):
        shortest_path(["p-q:3"], "p", "r")
