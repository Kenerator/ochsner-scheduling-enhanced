import unittest
from scheduling_core_fixtures import MemoryApi, ScriptModel, ready
from guarded_scheduling.models import Interpretation

class ConsentTest(unittest.TestCase):
    def setUp(self):
        from guarded_scheduling.core import SchedulingSession
        self.api=MemoryApi();self.model=ScriptModel([Interpretation('book','primary_care','downtown')]);self.s=SchedulingSession(self.api,self.model)
    def test_only_current_separate_confirmation_books_once(self):
        ready(self.s);v=self.s.choose(1)
        self.assertFalse(self.api.bookings)
        self.s.message('yes');self.assertFalse(self.api.bookings)
        self.s.confirm(v.proposal_id);self.assertEqual(len(self.api.bookings),1)
        self.s.confirm(v.proposal_id);self.assertEqual(len(self.api.bookings),1)
        self.assertEqual(self.s.view.state,'booked')
    def test_preference_correction_invalidates_old_consent_even_when_invalid(self):
        ready(self.s);old=self.s.choose(1).proposal_id
        self.s.set_preferences(location='uptown');self.s.confirm(old)
        self.assertFalse(self.api.bookings)
        self.assertNotEqual(self.s.view.state,'booked')
    def test_changed_identity_requires_fresh_verification(self):
        ready(self.s);old=self.s.choose(1).proposal_id
        self.api.matches=[];self.s.set_identity(phone='555-9999');self.s.confirm(old)
        self.assertFalse(self.api.bookings);self.assertIsNone(self.s.view.proposal_id)
    def test_forged_choice_and_confirmation_cannot_write(self):
        ready(self.s);self.s.choose(99);self.s.confirm('invented')
        self.assertFalse(self.api.bookings)
    def test_uncertain_write_locks_reset_and_second_confirmation(self):
        ready(self.s);proposal=self.s.choose(1).proposal_id;self.api.unknown=True
        self.s.confirm(proposal);self.assertEqual(self.s.view.state,'unresolved')
        self.s.reset();self.s.confirm(proposal)
        posts=[c for c in self.api.calls if c[:2]==('POST','/appointments')]
        self.assertEqual(len(posts),1);self.assertEqual(self.s.view.state,'unresolved')
    def test_conflict_requires_fresh_read_choice_and_confirmation(self):
        ready(self.s);old=self.s.choose(1).proposal_id;self.api.booking_status=409
        self.s.confirm(old);self.assertEqual(self.s.view.state,'conflict')
        self.s.confirm(old);self.assertFalse(self.api.bookings)
        self.api.booking_status=201;self.s.refresh();new=self.s.choose(2).proposal_id
        self.assertNotEqual(old,new);self.s.confirm(new);self.assertEqual(len(self.api.bookings),1)
    def test_mixed_private_correction_invalidates_old_proposal_without_model_call(self):
        ready(self.s);old=self.s.choose(1).proposal_id;calls=len(self.model.inputs)
        self.s.message('Actually phone 555-9999, yes book that')
        self.s.confirm(old)
        self.assertFalse(self.api.bookings)
        self.assertEqual(len(self.model.inputs),calls)
