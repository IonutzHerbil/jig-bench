import pytest

def traffic_light(events: list[str]) -> str:
    """Simulate a traffic light that starts red, given a list of events."""
    ...


def test_examples():
    assert traffic_light(["timer", "timer"]) == "yellow"
    with pytest.raises(ValueError):
        traffic_light(["fly"])
