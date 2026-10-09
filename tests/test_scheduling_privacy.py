import unittest
from guarded_scheduling.privacy import project
class PrivacyTests(unittest.TestCase):
    def test_public_language(self):
        for text in ['Which primary care doctors are downtown?','I want to book dermatology uptown','Can I cancel my appointment?','Should I take medication for chest pain?','I need help from a human','What about cardiology at lakeside?','Any location is fine','Remove my specialty preference','I have chest pain, should I wait?','Show those providers again','Book now']:
            with self.subTest(text=text):self.assertEqual(project(text),text)
    def test_identity_encodings_records_mixed_fail_closed(self):
        for text in ['5045550100','Find doctors; phone 504.555.0100','Find doctors born January fifth nineteen eighty','Find doctors five zero four five five five zero one zero zero','Find doctors DOB 1980-01-05','Book dermatology ZIP 70112','Find doctors ５０４５５５０１００','Patient Jane Example wants dermatology','{"patientId":"p1","name":"Jane"}','Find doctors; email example@example.invalid','Find doctors born 1/5/80','Find doctors\nprivate record p-001']:
            with self.subTest(text=text):self.assertIsNone(project(text))
    def test_private_collisions_identity_stage(self):
        self.assertIsNone(project('Find doctors downtown',private_values=['downtown']));self.assertIsNone(project('Find doctors',expecting_identity=True));self.assertIsNone(project('Find doctors',private_values=['Find doctors']))
    def test_local_and_unknown_input_suppressed(self):
        for text in ['', '   ', '2', '2026-12-01', 'yes','confirm abc123','unrecognized personal detail',None]:
            with self.subTest(text=text):self.assertIsNone(project(text))
