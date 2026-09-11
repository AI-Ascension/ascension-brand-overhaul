import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from publisher.errors import PublisherError
from publisher.events import CONTRACT_PATH, aggregate_events, load_event_contract
from tests.measurement_scope_helper import scope_fixture, trusted_scope
from tests.test_measurement_scope import event


class MeasurementSemanticsTests(unittest.TestCase):
    def test_contract_duplicate_keys_fail_before_semantic_validation(self):
        raw = CONTRACT_PATH.read_text().replace('"surface": "watch"', '"surface": "build", "surface": "watch"', 1)
        self.assertNotEqual(raw, CONTRACT_PATH.read_text())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'contract.json'
            path.write_text(raw)
            with patch('publisher.events.CONTRACT_PATH', path), self.assertRaisesRegex(PublisherError, 'duplicate object key'):
                load_event_contract()

    def test_enrolled_receipt_is_invalidated_by_changed_metric_definitions(self):
        events = [event('page-event')]
        receipt = scope_fixture(events)
        contract = load_event_contract()
        contract['metrics'][0]['numerator'] = 'different metric semantics'
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'contract.json'
            path.write_text(json.dumps(contract))
            with trusted_scope(receipt), patch('publisher.events.CONTRACT_PATH', path), self.assertRaisesRegex(PublisherError, 'semantics revision is stale'):
                aggregate_events(events, scope_receipt=receipt)

    def test_old_data_requires_historical_mode_and_is_labelled(self):
        events = [event('old-event', when='2020-09-07T12:00:00Z')]
        receipt = scope_fixture(events)
        receipt.update(week_start='2020-09-07T00:00:00Z', month_start='2020-09-01T00:00:00Z', observed_through='2020-09-14T00:00:00Z')
        with trusted_scope(receipt), self.assertRaisesRegex(PublisherError, 'current measurement receipt is stale'):
            aggregate_events(events, scope_receipt=receipt)
        receipt['reporting_mode'] = 'historical'
        with trusted_scope(receipt):
            result = aggregate_events(events, scope_receipt=receipt)
        self.assertEqual(result['scope']['reporting_mode'], 'historical')
        self.assertTrue(result['scope']['week_complete'])
        self.assertEqual(result['metrics']['audience-engagement-rate']['state'], 'historical_observation')
        self.assertIn('reviewed_at', result['scope'])

    def test_future_cutoff_or_review_never_passes_either_reporting_mode(self):
        events = [event('page-event')]
        for mode in ('current', 'historical'):
            for change in ({'observed_through': '2099-09-08T00:00:00Z'}, {'reviewed_at': '2099-09-08T00:00:00Z'}):
                receipt = scope_fixture(events)
                receipt.update(reporting_mode=mode, **change)
                with self.subTest(mode=mode, change=change), trusted_scope(receipt), self.assertRaisesRegex(PublisherError, 'dated in the future'):
                    aggregate_events(events, scope_receipt=receipt)

    def test_current_receipt_expires_and_naive_evaluation_clock_fails(self):
        events = [event('page-event')]
        receipt = scope_fixture(events)
        with trusted_scope(receipt):
            with self.assertRaisesRegex(PublisherError, 'stale'):
                aggregate_events(events, scope_receipt=receipt, now=datetime(2026, 9, 10, tzinfo=timezone.utc))
            with self.assertRaisesRegex(PublisherError, 'requires timezone'):
                aggregate_events(events, scope_receipt=receipt, now=datetime(2026, 9, 8))
