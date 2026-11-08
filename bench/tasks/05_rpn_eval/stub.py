import pytest

def rpn_eval(expr: str) -> int:
    """Evaluate an integer expression in Reverse Polish Notation."""
    ...


def test_examples():
    assert rpn_eval("2 3 *") == 6
    with pytest.raises(ValueError):
        rpn_eval("4 0 /")
