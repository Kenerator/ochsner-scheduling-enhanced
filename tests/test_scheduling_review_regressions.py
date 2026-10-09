import unittest
from scheduling_core_fixtures import MemoryApi,ScriptModel,ready,PATIENT
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation
from guarded_scheduling.http_adapter import HttpAdapter
from guarded_scheduling.mock_runner import MockRunner

class ReviewRegression(unittest.TestCase):
    def test_rejected_identity_response_is_never_reused_as_verification(self):
        api=MemoryApi();api.matches=[dict(PATIENT,phone='555-0999')]
        s=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        ready(s);self.assertEqual(s.view.state,'handoff')
        s.refresh();self.assertNotEqual(s.view.state,'options');self.assertIsNone(s._patient)
        self.assertFalse(any(c[1]=='/availability' for c in api.calls))
    def test_decline_cannot_hide_unknown_outcome(self):
        api=MemoryApi();s=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        ready(s);p=s.choose(1);api.unknown=True;s.confirm(p.proposal_id)
        v=s.message('decline');self.assertEqual(v.state,'unresolved')
        self.assertNotIn('No booking was submitted',v.message)
    def test_selected_provider_filters_valid_broad_returned_catalog(self):
        with MockRunner(port=0) as mock:
            api=HttpAdapter(mock.base_url);providers=api.request('GET','/providers',{'specialty':'primary_care'}).data['providers']
            chosen=providers[0]
            s=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care')]))
            s.message('Book primary care');s.select_provider(chosen['name'])
            v=s.set_identity(phone='555-0101',dob='1985-04-12')
            self.assertEqual(v.state,'options');self.assertTrue(v.slots)
            self.assertTrue(all(x['providerId']==chosen['providerId'] for x in v.slots))
