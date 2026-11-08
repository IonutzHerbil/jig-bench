import pytest

from clinic.types import ClinicError, ClinicFailure, DoctorId, Minute, PatientId, Specialty
from lib.calendar import SlotRef

def remind(doctor: DoctorId, patient: PatientId, start: Minute) -> str:  # on failure: raise ClinicFailure(ClinicError.<reason>)
    """Add reminders: text a patient a reminder of an appointment through the SMS service, worded exactly 'Hi <patient name>, your appointment with Dr <doctor name> is at <HH:MM>.', and return the message id."""
    ...


def test_examples():
    assert remind(DoctorId("dr_khan"), PatientId("p_ann"), Minute(660)) == "msg:+441234:Hi Ann, your appointment with Dr Khan is at 11:00."
    with pytest.raises(ClinicFailure) as failure:
        remind(DoctorId("dr_who"), PatientId("p_ann"), Minute(660))
    assert failure.value.error == ClinicError.UNKNOWN_DOCTOR
