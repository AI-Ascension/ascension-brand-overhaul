import copy
import unittest

from publisher.errors import PublisherError
from publisher.events import aggregate_events, validate_event
from tests.test_measurement import event_fixture


class MeasurementReviewRepairs(unittest.TestCase):
    def test_conflicting_retry_rejected_in_both_orders_and_across_environments(self):
        first = event_fixture()[0]
        second = copy.deepcopy(first)
        second['environment'] = 'production'
        for events in ([first, second], [second, first]):
            with self.assertRaisesRegex(PublisherError, 'conflicting duplicate'):
                aggregate_events(events)
        self.assertEqual(aggregate_events([first, copy.deepcopy(first)], include_synthetic=True)['event_count'], 1)

    def test_failed_completion_never_counts_as_success(self):
        for name, surface, properties in (
            ('quickstart_success', 'build', {'workflow': 'quickstart'}),
            ('subscribe_confirmed', 'subscription', {}),
            ('unsubscribe_completed', 'subscription', {}),
        ):
            event = event_fixture()[0]
            event.update(event_name=name, surface=surface, consent_state='granted', server_observation='confirmed')
            event['properties'] = dict(properties, status='failed')
            with self.assertRaisesRegex(PublisherError, 'status=completed'):
                validate_event(event)
            event['properties']['status'] = 'completed'
            validate_event(event)

    def test_anonymous_bucket_requires_consent(self):
        for consent in ('not_collected', 'denied'):
            event = event_fixture()[0]
            event.update(consent_state=consent, coarse_cohort={'kind': 'anonymous', 'value': 'bucket-a'})
            with self.assertRaisesRegex(PublisherError, 'requires granted consent'):
                validate_event(event)
