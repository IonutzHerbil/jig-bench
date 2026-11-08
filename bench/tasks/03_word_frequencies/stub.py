import pytest

def word_frequencies(text: str, top: int) -> list[tuple[str, int]]:
    """Count the words in a text, case-insensitively."""
    ...


def test_examples():
    assert word_frequencies("a b a", 1) == [("a", 2)]
    assert word_frequencies("Dog dog cat", 2) == [("dog", 2), ("cat", 1)]
