import logging
from time import sleep

from botocore.exceptions import ClientError

from aws_scatter_gather.s3_sqs_lambda_sync.resources import input_bucket, output_bucket

logger = logging.getLogger(__name__)

ROUNDS = 1000
SLEEP_SECS = 3


def run(batch_id, batch):
    input_bucket.write_batch_input(batch_id, batch)
    __wait_for_output_json_available_in_s3(batch_id)


def __sleep(message):
    logger.info(message)
    sleep(SLEEP_SECS)


def __wait_for_output_json_available_in_s3(batch_id):
    for _ in range(0, ROUNDS):
        __sleep("Waiting for output available for batchId={}..." \
                .format(batch_id))
        try:
            data = output_bucket.read_batch_output(batch_id)
            logger.info(
                "Good, output is available.")
            return data
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                continue
            else:
                raise

    raise ValueError("Output not available.")
