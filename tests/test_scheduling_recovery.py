import unittest
from scheduling_core_fixtures import MemoryApi, ScriptModel, ready
from guarded_scheduling.models import Interpretation

class RecoveryTest(unittest.TestCase):
    def test_medical_request_uses_truthful_minimized_handoff(self):
        from guarded_scheduling.core import SchedulingSession
        api=MemoryApi();s=SchedulingSession(api,ScriptModel([Interpretation('medical_advice')]))
        v=s.message('I have chest pain, should I wait?')
        self.assertIn('medical advice',v.message.lower());self.assertEqual(api.handoffs[0]['reason'],'medical_advice')
        self.assertNotIn('chest',str(api.handoffs));self.assertNotIn('patientId',api.handoffs[0])
    def test_outage_does_not_fabricate_queued_handoff(self):
        from guarded_scheduling.core import SchedulingSession
        api=MemoryApi();api.outage=True;s=SchedulingSession(api,ScriptModel([Interpretation('provider_lookup')]))
        v=s.message('Find a provider');self.assertIn('unavailable',v.message.lower());self.assertNotIn('queued',v.message.lower())
        self.assertTrue(any(c[1]=='/handoffs' for c in api.calls))
