import copy
import hashlib
import unittest

from publisher.canonical import canonical_json
from publisher.errors import PublisherError
from publisher.events import aggregate_events
from tests.measurement_scope_helper import scope_fixture, trusted_scope
from tests.test_measurement import event_fixture


def event(identifier, when='2026-09-07T12:00:00Z', content='eligible-run'):
    result = event_fixture()[0]
    result.update(event_id=identifier, occurred_at=when, content_id=content, environment='production')
    return result


class MeasurementScopeTests(unittest.TestCase):
    def test_relabelled_fixture_and_self_issued_receipt_are_not_authority(self):
        events = [event('page-event')]
        with self.assertRaisesRegex(PublisherError, 'require an enrolled'):
            aggregate_events(events)
        receipt = scope_fixture(events)
        with self.assertRaisesRegex(PublisherError, 'not enrolled'):
            aggregate_events(events, scope_receipt=receipt)
        with trusted_scope(receipt):
            result = aggregate_events(events, scope_receipt=receipt)
            self.assertEqual(result['event_count'], 1)
            self.assertFalse(result['scope']['week_complete'])
            changed = copy.deepcopy(events)
            changed[0]['occurred_at'] = '2026-09-07T12:01:00Z'
            with self.assertRaisesRegex(PublisherError, 'does not match the event stream'):
                aggregate_events(changed, scope_receipt=receipt)

    def test_weekly_dates_eligibility_and_upstream_exclusions(self):
        events = [event('eligible-event'), event('before-week', '2026-09-06T12:00:00Z'), event('after-cutoff', '2026-09-09T12:00:00Z'), event('not-public', content='unlisted-run'), event('bot-event'), event('test-event'), event('infra-event')]
        watch = event('watch-event')
        watch.update(event_name='meaningful_watch_or_read', surface='watch', properties={'media_kind': 'report'})
        events.append(watch)
        receipt = scope_fixture(events)
        receipt['eligible_public_content_ids'] = ['eligible-run']
        receipt['public_content_registry_digest'] = hashlib.sha256(canonical_json(['eligible-run'])).hexdigest()
        receipt['excluded_events'] = [{'event_id': name, 'reason': reason} for name, reason in [('bot-event', 'bot'), ('test-event', 'test_traffic'), ('infra-event', 'infrastructure_failure')]]
        with trusted_scope(receipt):
            result = aggregate_events(events, scope_receipt=receipt)
            reversed_result = aggregate_events(reversed(events), scope_receipt=receipt)
        self.assertEqual(result, reversed_result)
        self.assertEqual(result['event_count'], 2)
        self.assertEqual(result['metrics']['audience-engagement-rate']['value'], 1.0)

    def test_monthly_cohort_window_is_distinct_from_weekly_counts(self):
        events = [event('month-only', '2026-09-03T12:00:00Z'), event('prior-month', '2026-08-31T12:00:00Z')]
        for item in events:
            item.update(consent_state='granted', coarse_cohort={'kind': 'consented_cohort', 'value': item['event_id']})
        receipt = scope_fixture(events)
        with trusted_scope(receipt):
            result = aggregate_events(events, scope_receipt=receipt)
        self.assertIsNone(result['event_count'])
        self.assertIsNone(result['metrics']['audience-engagement-rate']['value'])
        self.assertEqual(result['metrics']['repeat-engagement-proxy']['value'], 1)

    def test_bad_calendar_bounds_and_exclusion_ids_fail(self):
        events = [event('page-event')]
        for changes in ({'week_start': '2026-09-08T00:00:00Z'}, {'month_start': '2026-09-02T00:00:00Z'}, {'excluded_events': [{'event_id': 'missing-event', 'reason': 'bot'}]}):
            receipt = scope_fixture(events)
            receipt.update(changes)
            with trusted_scope(receipt), self.assertRaises(PublisherError):
                aggregate_events(events, scope_receipt=receipt)

    def test_excluding_all_observations_preserves_absence(self):
        events = [event('bot-event')]
        receipt = scope_fixture(events)
        receipt['excluded_events'] = [{'event_id': 'bot-event', 'reason': 'bot'}]
        with trusted_scope(receipt):
            result = aggregate_events(events, scope_receipt=receipt)
        self.assertIsNone(result['event_count'])
        self.assertTrue(all(metric['value'] is None for metric in result['metrics'].values()))
