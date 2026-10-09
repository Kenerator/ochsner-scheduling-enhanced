import unittest
from scheduling_core_fixtures import MemoryApi, ScriptModel, PATIENT, ready
from guarded_scheduling.models import Interpretation

class PrivateIdentityTest(unittest.TestCase):
    def make(self):
        from guarded_scheduling.core import SchedulingSession
        api=MemoryApi();model=ScriptModel([Interpretation('book','primary_care','downtown')]);return api,model,SchedulingSession(api,model)
    def test_incremental_identity_and_model_privacy(self):
        api,model,s=self.make();s.message('Book primary care downtown');s.set_identity(phone='555-0101')
        self.assertFalse(any(c[1]=='/availability' for c in api.calls))
        s.set_identity(dob='1985-04-12');self.assertTrue(s.view.slots)
        captured=str(model.inputs)
        for value in ('555-0101','1985-04-12','patient1','70112'):self.assertNotIn(value,captured)
    def test_duplicate_zip_is_private_local_filter(self):
        api,model,s=self.make();api.matches=[dict(PATIENT),dict(PATIENT,patientId='patient2',zipCode='70001')]
        view=ready(s);self.assertEqual(view.state,'needs_zip');self.assertFalse(view.slots)
        for value in ('Synthetic','70112','70001','patient1','patient2'):self.assertNotIn(value,view.message)
        s.set_identity(zip_code='70112');self.assertTrue(s.view.slots)
        searches=[c for c in api.calls if c[1]=='/patients/search'];self.assertEqual(len(searches),1)
        self.assertNotIn('zip',searches[0][2])
    def test_no_match_never_exposes_or_books(self):
        api,model,s=self.make();api.matches=[];view=ready(s)
        self.assertFalse(view.slots);self.assertFalse(api.bookings);self.assertIn('verify',view.message.lower())
    def test_invalid_identity_date_is_local_correction_without_handoff(self):
        from guarded_scheduling.core import SchedulingSession
        api=MemoryApi();s=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        s.message('Book primary care downtown');s.set_identity(phone='555-0101')
        v=s.set_identity(dob='1985-02-30')
        self.assertEqual(v.state,'needs_identity');self.assertFalse(api.calls)
