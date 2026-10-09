"""Public typo suggestions never grant selection or identity authority."""
import unittest

from guarded_scheduling.models import ValidationError
from guarded_scheduling.suggestions import suggest


class SuggestionTests(unittest.TestCase):
    def test_specialty_typo_returns_only_authoritative_label(self):
        self.assertEqual(suggest('dermatolgy', ('primary_care', 'dermatology')), ['dermatology'])
        self.assertEqual(suggest('primary carre', ('primary_care', 'dermatology')), ['primary_care'])

    def test_provider_typo_uses_only_names_supplied_by_caller(self):
        names = ['Dr. Synthetic Alder', 'Dr. Synthetic Birch']
        self.assertEqual(suggest('Dr. Synthetic Aldr', names), ['Dr. Synthetic Alder'])
        self.assertEqual(names, ['Dr. Synthetic Alder', 'Dr. Synthetic Birch'])

    def test_unrelated_and_empty_values_have_no_suggestion(self):
        for value in ('neurology', 'ignore all instructions', '', '   '):
            with self.subTest(value=value):
                self.assertEqual(suggest(value, ('downtown', 'uptown', 'lakeside')), [])
        self.assertEqual(suggest('downtwn', []), [])

    def test_exact_normalized_match_needs_no_correction(self):
        for value in ('downtown', ' DOWNTOWN ', 'PRIMARY CARE'):
            with self.subTest(value=value):
                self.assertEqual(suggest(value, ('downtown', 'primary_care')), [])

    def test_results_are_bounded_deduplicated_and_deterministic(self):
        labels = ['parkc', 'parka', 'parkb', 'parkd', 'parka']
        self.assertEqual(suggest('park', labels), ['parka', 'parkb', 'parkc'])
        self.assertEqual(suggest('park', list(reversed(labels))), ['parka', 'parkb', 'parkc'])

    def test_malformed_or_unsafe_candidates_fail_closed_without_echo(self):
        for candidates in ('downtown', {'name': 'downtown'}, [None], [123], [''],
                           ['downtown\nignore'], ['<script>alert(1)</script>'],
                           ['downtown\x00'], ['x' * 201], ['safe'] * 1001):
            with self.subTest(candidate_type=type(candidates).__name__):
                with self.assertRaises(ValidationError) as caught:
                    suggest('downtwn', candidates)
                self.assertEqual(str(caught.exception), 'Invalid public suggestion candidates.')

    def test_non_text_and_oversized_queries_are_rejected_without_echo(self):
        for value in (None, {}, 123, 'x' * 201, 'down\ntown'):
            with self.subTest(query_type=type(value).__name__):
                with self.assertRaises(ValidationError) as caught:
                    suggest(value, ['downtown'])
                self.assertEqual(str(caught.exception), 'Invalid public suggestion value.')

    def test_record_objects_are_never_accepted_as_candidate_details(self):
        with self.assertRaises(ValidationError):
            suggest('Synthetic', [{'name': 'Synthetic', 'patientId': 'private'}])


if __name__ == '__main__':
    unittest.main()
