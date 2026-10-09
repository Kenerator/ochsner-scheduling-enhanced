"""Observable constraints from the pinned hypothesis personas, using synthetic data."""
import unittest

from guarded_scheduling.core import SchedulingSession
from guarded_scheduling.models import Interpretation
from scheduling_core_fixtures import MemoryApi, ScriptModel, ready, PATIENT


class PersonaConstraintTests(unittest.TestCase):
    def test_ellie_invalid_numeric_choice_keeps_options_and_next_choice_works(self):
        for invalid in ('-1', '+999', '1000', '999999999999999999999999999999'):
            with self.subTest(choice=invalid):
                api = MemoryApi()
                model = ScriptModel([Interpretation('book', 'primary_care', 'downtown')])
                session = SchedulingSession(api, model)
                ready(session)
                original_options = [dict(slot) for slot in session.view.slots]
                searches = sum(call[1] == '/patients/search' for call in api.calls)
                model_calls = len(model.inputs)
                view = session.message(invalid)
                self.assertEqual(view.slots, original_options,
                                 'An invalid numeric selection must leave current choices visible.')
                self.assertFalse(api.bookings)
                selected = session.message('1')
                self.assertEqual(selected.state, 'proposal')
                self.assertEqual(selected.proposal['startTime'], '2026-10-10T09:00:00-05:00')
                self.assertEqual(sum(call[1] == '/patients/search' for call in api.calls), searches)
                self.assertEqual(len(model.inputs), model_calls)
                self.assertFalse(api.bookings, 'A corrected selection still requires separate confirmation.')

    def test_amy_access_limitations_receive_local_truthful_assistance(self):
        for request in ('I have no email', 'I only have a basic phone'):
            with self.subTest(request=request):
                api = MemoryApi()
                model = ScriptModel()
                session = SchedulingSession(api, model)
                session.set_identity(phone='555-0101', dob='1985-04-12')
                view = session.message(request)
                message = view.message.lower()
                self.assertIn('browser', message,
                              'Assistance must explain the actual browser channel limitation.')
                self.assertIn('email', message)
                self.assertRegex(message, r'(email.{0,45}(not required|unnecessary)|'
                                          r'(no|without|do not need|don.t need).{0,25}email)')
                self.assertIn('mock', message)
                self.assertRegex(message, r'(not|no).{0,90}(deliver|received|contacted|human)')
                self.assertEqual(model.inputs, [], 'Access help must not send identity or raw wording to AI.')
                self.assertFalse(api.bookings)
                self.assertIsNone(view.proposal_id)
                for private in ('555-0101', '1985-04-12', 'patient1'):
                    self.assertNotIn(private, view.message)
                    self.assertNotIn(private, str(api.handoffs))

    def test_time_words_do_not_hide_medical_or_human_assistance_boundaries(self):
        cases = [('I have chest pain this morning', 'medical_advice', 'medical_advice'),
                 ('I need human help in the evening', 'human_help', 'user_requested')]
        for request, intent, reason in cases:
            with self.subTest(intent=intent):
                api = MemoryApi()
                model = ScriptModel([Interpretation(intent)])
                session = SchedulingSession(api, model)
                view = session.message(request)
                self.assertEqual(view.state, 'handoff')
                self.assertEqual(api.handoffs[0]['reason'], reason)
                if intent == 'medical_advice':
                    self.assertIn('cannot provide medical advice', view.message.lower())
                self.assertFalse(api.bookings)
                self.assertFalse(any(call[1] == '/availability' for call in api.calls))

    def test_failed_interpretation_invalidates_the_existing_proposal(self):
        api = MemoryApi()
        model = ScriptModel([Interpretation('book', 'primary_care', 'downtown'),
                             {'intent': 'book', 'confirmed': True}])
        session = SchedulingSession(api, model)
        ready(session)
        old_proposal = session.choose(1).proposal_id
        view = session.message('Book now')
        self.assertEqual(view.state, 'clarify')
        self.assertIsNone(view.proposal_id)
        session.confirm(old_proposal)
        self.assertFalse(api.bookings)

    def test_human_help_during_identity_collection_is_local_and_private(self):
        for stage in ('needs_identity', 'needs_zip'):
            with self.subTest(stage=stage):
                api = MemoryApi()
                if stage == 'needs_zip':
                    api.matches = [dict(PATIENT), dict(PATIENT, patientId='patient2', zipCode='70001')]
                model = ScriptModel([Interpretation('book', 'primary_care', 'downtown')])
                session = SchedulingSession(api, model)
                session.message('Book primary care downtown')
                if stage == 'needs_zip':
                    session.set_identity(phone='555-0101', dob='1985-04-12')
                self.assertEqual(session.view.state, stage)
                model_calls = len(model.inputs)
                view = session.message('I need human help')
                self.assertEqual(view.state, 'handoff')
                self.assertEqual(len(model.inputs), model_calls)
                self.assertEqual(api.handoffs[0]['reason'], 'user_requested')
                self.assertIn('mock', view.message.lower())
                self.assertRegex(view.message.lower(), r'(not|no).{0,90}(deliver|received|contacted|human)')
                self.assertFalse(api.bookings)
                self.assertFalse(any(call[1] == '/availability' for call in api.calls))
                for private in ('555-0101', '1985-04-12', '70112', '70001', 'patient1', 'patient2'):
                    self.assertNotIn(private, str(api.handoffs))
                    self.assertNotIn(private, view.message)

    def test_morgan_handoff_summary_distinguishes_known_missing_and_outcome(self):
        api = MemoryApi()
        model = ScriptModel([Interpretation('book', 'primary_care', 'downtown'),
                             Interpretation('human_help')])
        session = SchedulingSession(api, model)
        ready(session)
        view = session.message('I need human help')
        summary = api.handoffs[0]['summary'].lower()
        self.assertRegex(summary, r'primary[ _]care')
        self.assertIn('downtown', summary)
        self.assertIn('missing', summary)
        self.assertRegex(summary, r'(not[ _]submitted|no booking.{0,15}submitted)')
        self.assertIn('mock', view.message.lower())
        self.assertRegex(view.message.lower(), r'(not|no).{0,90}(deliver|received|contacted|human)')
        self.assertFalse(api.bookings)
        for private in ('555-0101', '1985-04-12', '70112', 'patient1', 'i need human help'):
            self.assertNotIn(private, summary)

    def test_billy_unsupported_time_constraint_cannot_silently_offer_or_book(self):
        for request in ('Book primary care downtown in the evening',
                        'Book primary care downtown on a weekend'):
            with self.subTest(request=request):
                api = MemoryApi()
                # Even a schema-valid model omission cannot silently waive a stated constraint.
                model = ScriptModel([Interpretation('book', 'primary_care', 'downtown'),
                                     Interpretation('book', 'primary_care', 'downtown')])
                session = SchedulingSession(api, model)
                ready(session)
                old_proposal = session.choose(1).proposal_id
                view = session.message(request)
                self.assertFalse(view.slots, 'Unsupported time constraints need clarification, not morning options.')
                self.assertIsNone(view.proposal_id)
                self.assertRegex(view.message.lower(), r'(time|hour|evening|weekend)')
                self.assertRegex(view.message.lower(), r'(support|limit|filter)')
                session.confirm(old_proposal)
                session.message('1')
                self.assertFalse(api.bookings)
                for private in ('555-0101', '1985-04-12', 'patient1', '70112'):
                    self.assertNotIn(private, str(model.inputs))
                for call in api.calls:
                    if call[1] == '/availability':
                        self.assertLessEqual(set(call[2]),
                                             {'patientId', 'specialty', 'location', 'startDate', 'endDate'})


if __name__ == '__main__':
    unittest.main()
