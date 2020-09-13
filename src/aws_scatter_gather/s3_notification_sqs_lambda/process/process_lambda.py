import asyncio

from aws_scatter_gather.s3_notification_sqs_lambda.resources import work_bucket, items_table
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import json
from aws_scatter_gather.util import logger
from aws_scatter_gather.util import sqs_event, s3_event
from aws_scatter_gather.util.aioaws import enable_xray
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.jsontime import now_epoch_millis
from aws_scatter_gather.util.trace import trace
from aws_scatter_gather.util.aioxray import xray_profile

logger.configure(name=__name__)


def __get_s3_objects_from(event) -> list:
    records = sqs_event.get_bodies(event)
    records = [s3_event.get_single_s3_object(record) for record in records if not s3_event.is_s3_test_event(record)]
    return records


@async_to_sync
@xray_profile
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    enable_xray()

    s3_objects = __get_s3_objects_from(event)

    async with aioaws.resource("s3") as s3_resource, \
        aioaws.resource("dynamodb") as dynamodb_resource, \
        await items_table.new_batch_writer(dynamodb_resource) as batch_writer:
        await asyncio.gather(*[__process(s3_object, s3_resource, batch_writer) for s3_object in s3_objects])


async def __process(s3_object, s3_resource, batch_writer):
    async with trace("Processing {}", json.dumps(s3_object)):
        chunk = await work_bucket.read_pending_chunk(s3_object[0], s3_object[1], s3_resource)
        batch_id = chunk["batchId"]
        index = chunk["index"]
        for record in chunk["records"]:
            request = record["request"]
            item_no = request["itemNo"]
            record["response"] = {"success": True,
                                  "message": "Ok"}
        await items_table.put_item({"itemNo": str(item_no),
                                    "updateTimestamp": now_epoch_millis()},
                                   batch_writer)
        await work_bucket.write_chunk_result(batch_id, index, chunk, s3_resource)
        await work_bucket.delete_pending_chunk(batch_id, index, s3_resource)
