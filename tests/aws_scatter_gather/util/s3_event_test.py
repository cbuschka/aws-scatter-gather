import unittest

from aws_scatter_gather.util import s3_event


class S3EventTest(unittest.TestCase):
    def test_single_s3_object_of_no_records_is_none(self):
        event = {}
        self.assertIsNone(s3_event.get_single_s3_object(event))

    def test_s3_objects_of_no_records_is_empty_list(self):
        event = {}
        self.assertEqual([], s3_event.get_s3_objects(event))

    def test_single_s3_object_of_single_record_event(self):
        event = {"Records": [{"s3": {"bucket": {"name": "bucket0"}, "object": {"key": "key0"}}}]}
        self.assertEqual(("bucket0", "key0"), s3_event.get_single_s3_object(event))

    def test_s3_objects_of_multi_records_event(self):
        event = {"Records": [{"s3": {"bucket": {"name": "bucket0"}, "object": {"key": "key0"}}},
                             {"s3": {"bucket": {"name": "bucket1"}, "object": {"key": "key1"}}}
                             ]}
        self.assertEqual([("bucket0", "key0"), ("bucket1", "key1")], s3_event.get_s3_objects(event))

    def test_single_s3_object_of_multi_records_event(self):
        event = {"Records": [{"s3": {"bucket": {"name": "bucket0"}, "object": {"key": "key0"}}},
                             {"s3": {"bucket": {"name": "bucket1"}, "object": {"key": "key1"}}}
                             ]}
        with self.assertRaises(ValueError):
            s3_event.get_single_s3_object(event)
