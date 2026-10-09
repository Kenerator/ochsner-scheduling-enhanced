import unittest

class ModelsTest(unittest.TestCase):
    def test_identity_dates_are_calendar_valid(self):
        from guarded_scheduling.models import PrivateIdentity, ValidationError
        self.assertEqual(PrivateIdentity('555-0101', '1985-04-12').phone, '555-0101')
        with self.assertRaises(ValidationError):
            PrivateIdentity('555-0101', '1985-02-30')

    def test_preferences_reject_reversed_bounds(self):
        from guarded_scheduling.models import Preferences, ValidationError
        with self.assertRaises(ValidationError):
            Preferences('primary_care', 'downtown', '2026-10-12', '2026-10-10')

    def test_interpretation_cannot_grant_consent(self):
        from guarded_scheduling.models import Interpretation, ValidationError
        valid = dict(intent='book', specialty='primary_care', location=None, clear_specialty=False, clear_location=False)
        self.assertEqual(Interpretation.from_dict(valid).intent, 'book')
        with self.assertRaises(ValidationError):
            Interpretation.from_dict(dict(valid, confirmed=True))

    def test_slots_reject_foreign_context_duplicate_and_nonboolean_available(self):
        from guarded_scheduling.models import validate_slots, Preferences, ValidationError
        slot = dict(slotId='s1', providerId='p1', specialty='primary_care', location='downtown', startTime='2026-10-10T09:00:00-05:00', available=True)
        prefs = Preferences('primary_care', 'downtown')
        self.assertEqual(validate_slots({'slots':[slot]}, prefs)[0]['startTime'], '2026-10-10T09:00:00-05:00')
        for slots in ([slot,slot], [dict(slot,location='uptown')], [dict(slot,available=1)]):
            with self.assertRaises(ValidationError): validate_slots({'slots':slots}, prefs)

    def test_created_result_must_match_exact_proposal(self):
        from guarded_scheduling.models import validate_appointment, ValidationError
        slot = dict(slotId='s1', providerId='p1', specialty='primary_care', location='downtown', startTime='2026-10-10T09:00:00-05:00', available=True)
        appt = dict(appointmentId='a1',patientId='patient1',providerId='p1',specialty='primary_care',location='downtown',startTime=slot['startTime'],status='scheduled')
        self.assertEqual(validate_appointment({'appointment':appt},'patient1',slot)['appointmentId'],'a1')
        with self.assertRaises(ValidationError): validate_appointment({'appointment':dict(appt,patientId='other')},'patient1',slot)

    def test_interpretation_rejects_untrusted_types_and_actions(self):
        from guarded_scheduling.models import Interpretation, ValidationError
        base = dict(intent='book',specialty=None,location=None,clear_specialty=False,clear_location=False)
        for patch in ({'intent':'execute'},{'clear_location':'yes'},{'specialty':42}):
            with self.assertRaises(ValidationError): Interpretation.from_dict(dict(base,**patch))

    def test_provider_display_requires_typed_authoritative_fields(self):
        from guarded_scheduling.models import validate_providers, ValidationError
        valid = dict(providerId='p1',name='Dr. Test',specialty='primary_care',locations=['downtown'],modalities=['in_person'])
        self.assertEqual(validate_providers({'providers':[valid]})[0]['name'],'Dr. Test')
        for providers in ([dict(valid,locations='downtown')],[valid,valid],[{'name':'invented'}]):
            with self.assertRaises(ValidationError): validate_providers({'providers':providers})
