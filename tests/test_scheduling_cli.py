import io
import unittest
from scheduling_core_fixtures import MemoryApi, ScriptModel
from guarded_scheduling.models import Interpretation
from guarded_scheduling.core import SchedulingSession

class CliTest(unittest.TestCase):
    def test_private_commands_current_confirmation_and_disclosure(self):
        from guarded_scheduling.__main__ import run
        api=MemoryApi(); session=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
        # A choice and ordinary yes must leave the API unchanged.
        output=io.StringIO()
        run(session,io.StringIO('Book primary care downtown\nphone 555-0101\ndob 1985-04-12\n1\nyes\nquit\n'),output)
        self.assertFalse(api.bookings)
        self.assertIn('AI',output.getvalue());self.assertIn('synthetic',output.getvalue())
        self.assertIn('confirm ',output.getvalue())
        self.assertNotIn('555-0101',output.getvalue());self.assertNotIn('1985-04-12',output.getvalue())
        proposal=session.view.proposal_id
        run(session,io.StringIO('confirm '+proposal+'\nquit\n'),io.StringIO())
        self.assertEqual(len(api.bookings),1)
    def test_pending_acknowledgement_precedes_model_work(self):
        from guarded_scheduling.__main__ import run
        output=io.StringIO()
        class Model:
            def interpret(self,text,context):
                assert 'Working' in output.getvalue()
                return Interpretation('provider_lookup','primary_care','downtown')
        run(SchedulingSession(MemoryApi(),Model()),io.StringIO('Find primary care downtown\nquit\n'),output)
        self.assertIn('Dr. Example',output.getvalue())
    def test_unexpected_errors_do_not_dump_identity_or_traceback(self):
        from guarded_scheduling.__main__ import run
        class Broken:
            def message(self,text):raise RuntimeError('555-0101 secret')
        output=io.StringIO();run(Broken(),io.StringIO('public\nquit\n'),output)
        self.assertNotIn('secret',output.getvalue());self.assertNotIn('Traceback',output.getvalue())
        self.assertIn('RuntimeError',output.getvalue())
