import pytest

from clinic.types import ClinicError, ClinicFailure, DoctorId, Minute, PatientId, Specialty
from lib.calendar import SlotRef

def first_free(specialty: Specialty, length: int) -> str:  # on failure: raise ClinicFailure(ClinicError.<reason>)
    """Add matching: find the earliest time any doctor of a specialty can take a booking of `length` minutes (quarter-hour starts from opening time, ending by closing time, not overlapping existing calendar bookings)."""
    ...


def test_examples():
    with pytest.raises(ClinicFailure) as failure:
        first_free(Specialty.DENTAL, 30)
    assert failure.value.error == ClinicError.NOT_FOUND
    with pytest.raises(ClinicFailure) as failure:
        first_free(Specialty.GENERAL, 200)
    assert failure.value.error == ClinicError.TOO_LONG
