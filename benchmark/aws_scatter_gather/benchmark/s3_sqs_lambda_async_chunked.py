import asyncio
import logging

from botocore.exceptions import ClientError

from aws_scatter_gather.s3_sqs_lambda_async_chunked.resources import input_bucket, output_bucket
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util.async_util import async_to_sync

logger = logging.getLogger(__name__)

ROUNDS = 1000
SLEEP_SECS = 3


def name():
    return "s3-sqs-lambda-async-chunked"


@async_to_sync
async def run(batch_id, batch):
    async with aioaws.resource("s3") as s3_resource:
        await input_bucket.write_batch_input(batch_id, batch, s3_resource)
        await __wait_for_output_json_available_in_s3(batch_id, s3_resource)


async def __sleep(message):
    logger.info(message)
    await asyncio.sleep(SLEEP_SECS)


async def __wait_for_output_json_available_in_s3(batch_id, s3_resource):
    for _ in range(0, ROUNDS):
        await __sleep("Waiting for output available for batchId={}..." \
                      .format(batch_id))
        try:
            data = await output_bucket.read_batch_output(batch_id, s3_resource)
            logger.info(
                "Good, output is available.")
            return data
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                continue
            else:
                raise

    raise ValueError("Output not available.")
