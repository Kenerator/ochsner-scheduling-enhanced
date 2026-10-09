import io,json,unittest
from guarded_scheduling.diagnostics import Diagnostics
class DiagnosticsTest(unittest.TestCase):
    def test_only_normalized_allowlisted_values_serialize(self):
        stream=io.StringIO();sink=Diagnostics(stream)
        sink({'session':'a'*32,'intent':'book','state':'options','route':'/patients/pat_private/appointments','status':200,'duration_ms':1.25,'phone':'555-0101','exception':'secret-url','prompt':'private'})
        row=json.loads(stream.getvalue());self.assertEqual(row['route'],'/patients/{patientId}/appointments');self.assertEqual(row['status'],200);self.assertEqual(row['duration_ms'],1.25)
        for private in ['pat_private','555-0101','secret-url','prompt']:self.assertNotIn(private,stream.getvalue())
        self.assertEqual(sink.events,[row])
    def test_unrecognized_values_do_not_serialize(self):
        sink=Diagnostics();sink({'session':'secret','intent':'secret','state':'secret','route':'/patients/search?phone=secret','reason':'secret','source':'secret','status':'secret','duration_ms':float('nan'),'body':{'secret':True}})
        self.assertEqual(sink.events,[{}])
