import unittest

from jsonschema.exceptions import ValidationError

from aws_scatter_gather.common.validation import validate_input, validate_pending_task, validate_processed_task, \
    validate_pending_chunk_of_tasks, validate_processed_chunk_of_tasks


class InputValidationTest(unittest.TestCase):
    def test_missing_records_invalid(self):
        doc = {}
        with self.assertRaises(ValidationError):
            validate_input(doc)

    def test_empty_is_valid(self):
        doc = {"records": []}
        validate_input(doc)

    def test_happy_doc(self):
        doc = {"records": [
            {"itemNo": "1",
             "price": 100}
        ]}
        validate_input(doc)

    def test_missing_price_invalid(self):
        doc = {"records": [
            {"itemNo": "1"}
        ]}
        with self.assertRaises(ValidationError):
            validate_input(doc)

    def test_missing_item_no_invalid(self):
        doc = {"records": [
            {"price": 100}
        ]}
        with self.assertRaises(ValidationError):
            validate_input(doc)


class PendingTaskValidationTest(unittest.TestCase):
    def test_missing_batch_id_invalid(self):
        doc = {"index": 0}
        with self.assertRaises(ValidationError):
            validate_pending_task(doc)

    def test_missing_index_invalid(self):
        doc = {"batch_id": "abcd"}
        with self.assertRaises(ValidationError):
            validate_pending_task(doc)

    def test_empty_is_invalid(self):
        doc = {}
        with self.assertRaises(ValidationError):
            validate_pending_task(doc)

    def test_happy_doc(self):
        doc = {"batch_id": "abc", "index": 0, "request": {"itemNo": "1", "price": 30}}
        validate_pending_task(doc)


class PendingChunkOfTasksValidationTest(unittest.TestCase):
    def test_missing_batch_id_invalid(self):
        doc = {"index": 0}
        with self.assertRaises(ValidationError):
            validate_pending_chunk_of_tasks(doc)

    def test_missing_index_invalid(self):
        doc = {"batchId": "abcd"}
        with self.assertRaises(ValidationError):
            validate_pending_chunk_of_tasks(doc)

    def test_empty_is_invalid(self):
        doc = {}
        with self.assertRaises(ValidationError):
            validate_pending_chunk_of_tasks(doc)

    def test_happy_doc(self):
        doc = {"batchId": "abc", "index": 0, "request": {"itemNo": "1", "price": 30}}
        validate_pending_chunk_of_tasks(doc)


class ProcessedTaskValidationTest(unittest.TestCase):
    def test_missing_batch_id_invalid(self):
        with self.assertRaises(ValidationError):
            doc = {"index": 0}
            validate_processed_task(doc)

    def test_missing_index_invalid(self):
        doc = {"batchId": "abcd"}
        with self.assertRaises(ValidationError):
            validate_processed_task(doc)

    def test_empty_is_invalid(self):
        doc = {}
        with self.assertRaises(ValidationError):
            validate_processed_task(doc)

    def test_happy_doc(self):
        doc = {"batchId": "abc", "index": 0,
               "request": {"itemNo": "1", "price": 30},
               "response": {"success": True, "message": "Ok"}}
        validate_processed_task(doc)


class ProcessedChunkOfTasksValidationTest(unittest.TestCase):
    def test_missing_batch_id_invalid(self):
        with self.assertRaises(ValidationError):
            doc = {"index": 0}
            validate_processed_chunk_of_tasks(doc)

    def test_missing_index_invalid(self):
        doc = {"batchId": "abcd"}
        with self.assertRaises(ValidationError):
            validate_processed_chunk_of_tasks(doc)

    def test_empty_is_invalid(self):
        doc = {}
        with self.assertRaises(ValidationError):
            validate_processed_chunk_of_tasks(doc)

    def test_happy_doc(self):
        doc = {"batchId": "abc", "index": 0,
               "records": [{"index": 0,
                            "request": {"itemNo": "1", "price": 30},
                            "response": {"success": True, "message": "Ok"}}
                           ]
               }
        validate_processed_chunk_of_tasks(doc)


class PendingChunkOfTasksValidationTest(unittest.TestCase):
    def test_missing_batch_id_invalid(self):
        with self.assertRaises(ValidationError):
            doc = {"index": 0}
            validate_pending_chunk_of_tasks(doc)

    def test_missing_index_invalid(self):
        doc = {"batchId": "abcd"}
        with self.assertRaises(ValidationError):
            validate_pending_chunk_of_tasks(doc)

    def test_empty_is_invalid(self):
        doc = {}
        with self.assertRaises(ValidationError):
            validate_pending_chunk_of_tasks(doc)

    def test_happy_doc(self):
        doc = {"batchId": "abc", "index": 0,
               "records": [{"index": 0,
                            "request": {"itemNo": "1", "price": 30}}
                           ]
               }
        validate_pending_chunk_of_tasks(doc)
