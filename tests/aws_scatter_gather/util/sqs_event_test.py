import unittest

from aws_scatter_gather.util import sqs_event


class SqsEventTest(unittest.TestCase):
    def test_single_body_of_no_records_is_none(self):
        event = {}
        self.assertIsNone(sqs_event.get_single_body(event))

    def test_bodies_of_no_records_is_empty_list(self):
        event = {}
        self.assertEqual([], sqs_event.get_bodies(event))

    def test_single_body_of_single_record_event(self):
        event = {"Records": [{"body": "\"rec0\""}]}
        self.assertEqual("rec0", sqs_event.get_single_body(event))

    def test_bodies_of_multi_records_event(self):
        event = {"Records": [{"body": "\"rec0\""}, {"body": "\"rec1\""}]}
        self.assertEqual(["rec0", "rec1"], sqs_event.get_bodies(event))

    def test_single_body_of_multi_records_event(self):
        event = {"Records": [{"body": "\"rec0\""}, {"body": "\"rec1\""}]}
        with self.assertRaises(ValueError):
            sqs_event.get_single_body(event)
