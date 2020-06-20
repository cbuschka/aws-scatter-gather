import unittest
from io import StringIO

from aws_scatter_gather.util.jsonstream import JsonStream


class JsonWriterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.out = StringIO()
        self.wr = JsonStream(self.out)

    def test_single_string(self):
        self.wr.write_value("value")

        self.assertEqual("\"value\"", str(self.out.getvalue()))

    def test_single_true(self):
        self.wr.write_value(True)

        self.assertEqual("true", str(self.out.getvalue()))

    def test_single_false(self):
        self.wr.write_value(False)

        self.assertEqual("false", str(self.out.getvalue()))

    def test_single_none(self):
        self.wr.write_value(None)

        self.assertEqual("null", str(self.out.getvalue()))

    def test_empty_object(self):
        self.wr.start_object()
        self.wr.end_object()

        self.assertEqual("{}", str(self.out.getvalue()))

    def test_single_prop_object(self):
        self.wr.start_object()
        self.wr.write_property("key", "value")
        self.wr.end_object()

        self.assertEqual("{\"key\": \"value\"}", str(self.out.getvalue()))

    def test_multi_prop_object(self):
        self.wr.start_object()
        self.wr.write_property("key", "value")
        self.wr.write_property("key2", "value2")
        self.wr.end_object()

        self.assertEqual("{\"key\": \"value\", \"key2\": \"value2\"}", str(self.out.getvalue()))

    def test_single_object_prop_object(self):
        self.wr.start_object()
        self.wr.start_property("key")
        self.wr.start_object()
        self.wr.end_object()
        self.wr.end_object()

        self.assertEqual("{\"key\": {}}", str(self.out.getvalue()))

    def test_single_object_item_array(self):
        self.wr.start_array()
        self.wr.start_object()
        self.wr.end_object()
        self.wr.end_array()

        self.assertEqual("[{}]", str(self.out.getvalue()))

    def test_multi_object_item_array(self):
        self.wr.start_array()
        self.wr.start_object()
        self.wr.end_object()
        self.wr.start_object()
        self.wr.end_object()
        self.wr.end_array()

        self.assertEqual("[{}, {}]", str(self.out.getvalue()))

    def test_single_array_prop_object(self):
        self.wr.start_object()
        self.wr.start_property("key")
        self.wr.start_array()
        self.wr.end_array()
        self.wr.end_object()

        self.assertEqual("{\"key\": []}", str(self.out.getvalue()))

    def test_empty_array(self):
        self.wr.start_array()
        self.wr.end_array()

        self.assertEqual("[]", str(self.out.getvalue()))

    def test_single_item_array(self):
        self.wr.start_array()
        self.wr.write_value("value")
        self.wr.end_array()

        self.assertEqual("[\"value\"]", str(self.out.getvalue()))

    def test_multi_item_array(self):
        self.wr.start_array()
        self.wr.write_value("value")
        self.wr.write_value("value2")
        self.wr.end_array()

        self.assertEqual("[\"value\", \"value2\"]", str(self.out.getvalue()))

    def test_dup_root_value(self):
        self.wr.write_value("value")
        with self.assertRaises(ValueError) as ctx:
            self.wr.write_value("value2")
        self.assertEqual("Invalid state for value: _State.DONE", str(ctx.exception))

    def test_dup_root_object(self):
        self.wr.write_value("value")
        with self.assertRaises(ValueError) as ctx:
            self.wr.start_object()
        self.assertEqual("Invalid state for start object: _State.DONE", str(ctx.exception))

    def test_complex(self):
        self.wr.start_object()
        self.wr.write_property("key1", "value1")
        self.wr.write_property("key2", "value2")
        self.wr.start_property("records")
        self.wr.start_array()
        for record in [{"request": {}, "response": {}}, {"request": {}, "response": {}}]:
            self.wr.write_value(record)
        self.wr.end_array()
        self.wr.end_object()
        self.assertEqual(
            '{"key1": "value1", "key2": "value2", "records": [{"request": {}, "response": {}}, {"request": {}, "response": {}}]}',
            str(self.out.getvalue()))
