"""Queue claims require an actual valid effect result; payloads stay minimized."""
import unittest
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation
from guarded_scheduling.ports import Response,UnknownOutcome
from scheduling_core_fixtures import MemoryApi,ScriptModel

class HandoffApi(MemoryApi):
    def __init__(self,result):super().__init__();self.result=result
    def request(self,method,path,params=None,body=None):
        if path=='/handoffs':
            self.calls.append((method,path,params,body))
            if isinstance(self.result,Exception):raise self.result
            return self.result
        return super().request(method,path,params,body)

class HandoffTests(unittest.TestCase):
    def test_invalid_rejected_or_unknown_handoff_never_claims_queue_or_retries(self):
        for result in [Response(201,{}),Response(201,{'handoffId':7,'status':'queued'}),Response(201,{'handoffId':' ','status':'queued'}),Response(201,{'handoffId':'h','status':'failed'}),Response(400,{'message':'private-secret'}),UnknownOutcome('private-secret URL')]:
            with self.subTest(result=type(result).__name__):
                api=HandoffApi(result);session=SchedulingSession(api,ScriptModel([Interpretation('human_help'),Interpretation('human_help')]))
                view=session.message('I need human help');self.assertNotIn('queued',view.message.lower());self.assertNotIn('private-secret',view.message)
                session.message('I need human help');self.assertEqual(sum(c[1]=='/handoffs' for c in api.calls),1)
    def test_valid_queue_uses_normalized_reason_without_identity_or_transcript(self):
        api=HandoffApi(Response(201,{'handoffId':'h1','status':'queued'}));session=SchedulingSession(api,ScriptModel([Interpretation('medical_advice')]))
        session.set_identity(phone='555-0101',dob='1985-04-12',zip_code='70112')
        view=session.message('I have chest pain, should I wait?')
        self.assertIn('queued',view.message);self.assertIn('mock',view.message)
        body=next(c[3] for c in api.calls if c[1]=='/handoffs');self.assertEqual(set(body),{'reason','summary'});self.assertEqual(body['reason'],'medical_advice')
        for forbidden in ['555-0101','1985-04-12','70112','chest pain','patient1']:self.assertNotIn(forbidden,str(body))
