import unittest
from scheduling_core_fixtures import MemoryApi, ScriptModel, ready
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation

class SuggestionIntegration(unittest.TestCase):
    def test_vocabulary_suggestion_does_not_select_or_preserve_consent(self):
        api=MemoryApi();s=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        ready(s);old=s.choose(1).proposal_id
        v=s.message('specialty dermatolgy')
        self.assertIn('dermatology',v.message);self.assertIn('explicit',v.message)
        self.assertEqual(s.preferences.specialty,'primary_care')
        s.confirm(old);self.assertFalse(api.bookings)
    def test_provider_suggestion_uses_only_returned_names_without_selection(self):
        api=MemoryApi();s=SchedulingSession(api,ScriptModel())
        v=s.message('provider Dr. Exampel')
        self.assertIn('Dr. Example',v.message)
        self.assertIsNone(s.preferences.provider_id)
        self.assertEqual(api.calls[0][:2],('GET','/providers'))
        self.assertFalse(s.model.inputs)
