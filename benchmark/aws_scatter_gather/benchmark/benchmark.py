import json
import logging
import unittest
from uuid import uuid4

from botocore.exceptions import ClientError
from time import sleep

from aws_scatter_gather.s3_sqs_lambda_sync.resources import input_bucket, output_bucket

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROUNDS = 1000
SLEEP_SECS = 3
RECORD_COUNT = 10


class DummyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.batch_id = str(uuid4())
        self.batch = {"records": [{"index": i, "info": "request#{}".format(i)} for i in range(RECORD_COUNT)]}

    def test_it(self):
        self.__upload_input_json_to_s3()
        output = self.__wait_for_output_json_available_in_s3()
        logger.info("output: {}".format(json.dumps(output, indent=2)))

    def __upload_input_json_to_s3(self):
        input_bucket.write_batch_input(self.batch_id, self.batch)
        logger.info("Input uploaded...")

    def __wait_for_output_json_available_in_s3(self) -> dict:
        for _ in range(0, ROUNDS):
            self.__sleep("Waiting for output available for batchId={}..." \
                         .format(self.batch_id))
            try:
                data = output_bucket.read_batch_output(self.batch_id)
                logger.info(
                    "Good, output is available.")
                return data
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    continue
                else:
                    raise

        raise ValueError("Output not available.")

    def __sleep(self, message):
        logger.info(message)
        sleep(SLEEP_SECS)


if __name__ == "__main__":
    unittest.main()
