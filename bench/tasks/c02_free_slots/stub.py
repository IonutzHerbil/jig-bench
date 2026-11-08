import pytest

from clinic.types import ClinicError, ClinicFailure, DoctorId, Minute, PatientId, Specialty
from lib.calendar import SlotRef

def free_slots(doctor: DoctorId, length: int) -> list[str]:  # on failure: raise ClinicFailure(ClinicError.<reason>)
    """Add availability: list the start times, written HH:MM, at which a booking of `length` minutes could be made with a doctor: every quarter hour from the doctor's opening time, keeping only starts where the whole booking ends by closing time and does not overlap any existing calendar booking."""
    ...


def test_examples():
    assert free_slots(DoctorId("dr_khan"), 30) == ["10:00", "10:15", "10:30"]
    with pytest.raises(ClinicFailure) as failure:
        free_slots(DoctorId("dr_lee"), 200)
    assert failure.value.error == ClinicError.TOO_LONG
