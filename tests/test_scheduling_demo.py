import contextlib,io,json,socket,unittest
from guarded_scheduling.demo import run,main
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.http_adapter import HttpAdapter
from guarded_scheduling.models import Interpretation
from test_scheduling_helpers import ReferenceServer,ScriptedModel
class DemoTest(unittest.TestCase):
    def test_each_demo_uses_real_reference_and_discloses_scripted_model(self):
        for scenario in ['provider','booking','no-match','guards']:
            with self.subTest(scenario=scenario):
                result=run(scenario);self.assertTrue(result['passed']);self.assertEqual(result['backend'],'supplied_reference');self.assertEqual(result['model'],'scripted');self.assertTrue(result['simulation']);self.assertTrue(result['checks'])
    def test_demo_cli_reports_failure_without_false_success(self):
        out=io.StringIO()
        with contextlib.redirect_stdout(out):code=main(['provider','--python','/missing/private/interpreter'])
        self.assertEqual(code,1);self.assertNotIn('private',out.getvalue());self.assertFalse(json.loads(out.getvalue())['passed'])
    def test_lost_real_write_stays_unknown_without_second_post_or_reset(self):
        def drop(handler):
            original=handler.respond
            def respond(self,status,payload):
                if self.command=='POST' and self.path=='/appointments' and status==201:
                    self.close_connection=True;self.connection.shutdown(socket.SHUT_RDWR);self.connection.close()
                else:original(self,status,payload)
            handler.respond=respond
        with ReferenceServer(drop) as server:
            session=SchedulingSession(HttpAdapter(server.base_url),ScriptedModel(Interpretation('book','primary_care','downtown')))
            session.message('Book primary care downtown');session.set_identity(phone='555-0101',dob='1985-04-12');proposal=session.choose(1)
            self.assertEqual(session.confirm(proposal.proposal_id).state,'unresolved');self.assertEqual(session.confirm(proposal.proposal_id).state,'unresolved');self.assertEqual(session.reset().state,'unresolved')
        self.assertEqual(sum(e[0]=='POST' and e[1]=='/appointments' for e in server.events),1);self.assertEqual(len(server.store.appointments),3)
