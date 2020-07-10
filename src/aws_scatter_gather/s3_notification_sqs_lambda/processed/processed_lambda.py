import asyncio

from aws_scatter_gather.s3_notification_sqs_lambda.resources import work_bucket, gather_queue
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import json
from aws_scatter_gather.util import logger
from aws_scatter_gather.util import sqs_event, s3_event
from aws_scatter_gather.util.async_util import async_to_sync

logger.configure(name=__name__)


def __extract_batch_id(object_key: str):
    return object_key[0:object_key.find("/")]


def __get_s3_objects_from(event) -> list:
    records = sqs_event.get_bodies(event)
    records = [s3_event.get_single_s3_object(record) for record in records if not s3_event.is_s3_test_event(record)]
    return records


async def __check_if_complete(batch_id, s3_resource, sqs_client):
    if not await work_bucket.exists_pending_chunk(batch_id, s3_resource):
        await gather_queue.send_batch_complete_message(batch_id, sqs_client)


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    s3_objects = __get_s3_objects_from(event)
    batch_ids = set([__extract_batch_id(key[1]) for key in s3_objects])

    async with aioaws.client("sqs") as sqs_client, \
        aioaws.resource("s3") as s3_resource:
        await asyncio.gather(*[__check_if_complete(batch_id, s3_resource, sqs_client) for batch_id in batch_ids])
