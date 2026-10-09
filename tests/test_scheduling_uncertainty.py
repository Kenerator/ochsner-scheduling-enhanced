"""An untrustworthy success response cannot erase possible booking effects."""
import unittest
from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation
from guarded_scheduling.ports import Response
from scheduling_core_fixtures import MemoryApi,ScriptModel,ready

class UncertaintyTests(unittest.TestCase):
    def test_malformed_or_foreign_created_result_locks_booking_without_repeat_post(self):
        for mutation in ['missing_appointment','foreign_patient','different_time','missing_status']:
            with self.subTest(mutation=mutation):
                class Api(MemoryApi):
                    def request(self,method,path,params=None,body=None):
                        result=super().request(method,path,params,body)
                        if (method,path)==('POST','/appointments'):
                            if mutation=='missing_appointment':return Response(201,{})
                            appointment=dict(result.data['appointment'])
                            if mutation=='foreign_patient':appointment['patientId']='different-patient'
                            elif mutation=='different_time':appointment['startTime']='2026-10-12T12:00:00-05:00'
                            else:appointment.pop('status')
                            return Response(201,{'appointment':appointment})
                        return result
                api=Api();session=SchedulingSession(api,ScriptModel([Interpretation('book','primary_care','downtown')]))
                ready(session);proposal=session.choose(1).proposal_id
                self.assertEqual(session.confirm(proposal).state,'unresolved');self.assertEqual(len(api.bookings),1)
                for action in [session.reset,session.refresh,lambda:session.set_identity(phone='555-9999'),lambda:session.set_preferences(location='uptown'),lambda:session.choose(2),lambda:session.confirm(proposal)]:
                    self.assertEqual(action().state,'unresolved')
                self.assertEqual(sum(c[:2]==('POST','/appointments') for c in api.calls),1);self.assertNotIn('different-patient',session.view.message)
