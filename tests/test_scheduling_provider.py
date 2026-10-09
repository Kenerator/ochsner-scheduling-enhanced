import unittest
from scheduling_core_fixtures import MemoryApi, ScriptModel
from guarded_scheduling.models import Interpretation

class ProviderTest(unittest.TestCase):
    def test_public_lookup_never_searches_identity(self):
        from guarded_scheduling.core import SchedulingSession
        api=MemoryApi();model=ScriptModel([Interpretation('provider_lookup','primary_care','downtown'),Interpretation('provider_lookup')]);s=SchedulingSession(api,model)
        view=s.message('Which primary care providers are downtown?')
        self.assertEqual(view.providers[0]['name'],'Dr. Example');self.assertFalse(view.requested_fields)
        s.message('Show those providers again')
        self.assertTrue(all(c[1]=='/providers' for c in api.calls))
        self.assertEqual(api.calls[-1][2],{'specialty':'primary_care','location':'downtown'})
    def test_invalid_model_output_cannot_create_effect(self):
        from guarded_scheduling.core import SchedulingSession
        api=MemoryApi();s=SchedulingSession(api,ScriptModel([{'intent':'book','confirmed':True}]))
        self.assertEqual(s.message('Book now').state,'clarify');self.assertFalse(api.calls)
