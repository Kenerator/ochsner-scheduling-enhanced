import unittest
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation
from guarded_scheduling.http_adapter import HttpAdapter
from test_scheduling_helpers import ReferenceServer,ScriptedModel
class LookupTest(unittest.TestCase):
    def test_private_verification_and_correction_bind_returned_appointments(self):
        with ReferenceServer() as server:
            model=ScriptedModel(Interpretation('appointment_lookup'));session=SchedulingSession(HttpAdapter(server.base_url),model)
            self.assertEqual(session.message('Show my appointments').state,'needs_identity');self.assertFalse(server.events)
            view=session.set_identity(phone='555-0101',dob='1985-04-12');self.assertEqual(view.state,'appointments');self.assertEqual(view.appointments[0]['specialty'],'primary_care')
            self.assertNotIn('patientId',str(view.appointments));view=session.set_identity(phone='555-0102',dob='1992-06-03');self.assertEqual(view.appointments[0]['specialty'],'dermatology')
        self.assertEqual(sum(e[1]=='/patients/search' for e in server.events),2);self.assertEqual(len(model.calls),1);self.assertNotIn('555-',str(model.calls))
