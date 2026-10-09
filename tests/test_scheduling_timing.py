"""Controlled blocking verifies feedback ordering and serialized consent, not latency claims."""
import io
import threading
import unittest
from guarded_scheduling.__main__ import run
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation
from scheduling_core_fixtures import MemoryApi,ScriptModel,ready

class TimingTests(unittest.TestCase):
    def test_pending_feedback_is_flushed_while_model_or_api_is_still_blocked(self):
        for boundary in ['model','api']:
            with self.subTest(boundary=boundary):
                entered=threading.Event();release=threading.Event();flushed=threading.Event();errors=[]
                class Output(io.StringIO):
                    def flush(self):
                        if 'Working' in self.getvalue():flushed.set()
                output=Output()
                def block():
                    entered.set()
                    if not release.wait(2):raise RuntimeError('Controlled test release timed out')
                class Model:
                    def interpret(self,text,context):
                        if boundary=='model':block()
                        return Interpretation('provider_lookup','primary_care','downtown')
                class Api(MemoryApi):
                    def request(self,*args,**kwargs):
                        if boundary=='api':block()
                        return super().request(*args,**kwargs)
                def work():
                    try:run(SchedulingSession(Api(),Model()),io.StringIO('Find providers downtown\nquit\n'),output)
                    except Exception as exc:errors.append(type(exc).__name__)
                worker=threading.Thread(target=work,daemon=True);worker.start()
                try:
                    self.assertTrue(entered.wait(1));self.assertTrue(flushed.is_set());self.assertTrue(worker.is_alive());self.assertNotIn('Dr. Example',output.getvalue())
                finally:release.set();worker.join(2)
                self.assertFalse(worker.is_alive());self.assertFalse(errors);self.assertIn('Dr. Example',output.getvalue())
    def test_concurrent_confirmation_consumes_one_current_consent(self):
        entered=threading.Event();release=threading.Event();second_started=threading.Event();errors=[]
        class Api(MemoryApi):
            def request(self,method,path,params=None,body=None):
                if (method,path)==('POST','/appointments'):
                    entered.set()
                    if not release.wait(2):raise RuntimeError('Controlled test release timed out')
                return super().request(method,path,params,body)
        api=Api();session=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        ready(session);proposal=session.choose(1).proposal_id
        def confirm(second=False):
            if second:second_started.set()
            try:session.confirm(proposal)
            except Exception as exc:errors.append(type(exc).__name__)
        first=threading.Thread(target=confirm,daemon=True);second=threading.Thread(target=lambda:confirm(True),daemon=True)
        first.start()
        try:
            self.assertTrue(entered.wait(1));self.assertEqual(session.view.state,'submitting');self.assertFalse(api.bookings)
            second.start();self.assertTrue(second_started.wait(1))
        finally:
            release.set();first.join(2)
            if second.ident is not None:second.join(2)
        self.assertFalse(first.is_alive());self.assertFalse(second.is_alive());self.assertFalse(errors)
        self.assertEqual(sum(c[:2]==('POST','/appointments') for c in api.calls),1);self.assertEqual(len(api.bookings),1);self.assertEqual(session.view.state,'booked')
