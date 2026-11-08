import pytest

from clinic.types import ClinicError, ClinicFailure, DoctorId, Minute, PatientId, Specialty
from lib.calendar import SlotRef

def book(doctor: DoctorId, patient: PatientId, start: Minute, length: int) -> SlotRef:  # on failure: raise ClinicFailure(ClinicError.<reason>)
    """Add booking: book a patient with a doctor at a start time for a length in minutes, and return the calendar's slot reference."""
    ...


def test_examples():
    assert book(DoctorId("dr_khan"), PatientId("p_ann"), Minute(600), 30) == SlotRef("dr_khan@600")
    with pytest.raises(ClinicFailure) as failure:
        book(DoctorId("dr_lee"), PatientId("p_ann"), Minute(540), 30)
    assert failure.value.error == ClinicError.SLOT_TAKEN
