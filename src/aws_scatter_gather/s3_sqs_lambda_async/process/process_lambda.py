import asyncio
import json

from aws_scatter_gather.common.validation import validate_pending_task, validate_processed_task
from aws_scatter_gather.s3_sqs_lambda_async.resources import work_bucket, gather_queue, items_table
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.jsontime import now_epoch_millis
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    async with aioaws.client("sqs") as sqs_client, \
        aioaws.resource("s3") as s3_resource, \
        aioaws.resource("dynamodb") as dynamodb_resource, \
        await items_table.new_batch_writer(dynamodb_resource) as batch_writer:
        records = [json.loads(record["body"]) for record in event["Records"]]
        await asyncio.gather(*[__process(record, s3_resource, batch_writer) for record in records])

        batch_ids = {record["batchId"] for record in records}
        await asyncio.gather(*[__check_if_complete(batch_id, s3_resource, sqs_client) for batch_id in batch_ids])


async def __process(record, s3_resource, batch_writer):
    async with trace("Processing {}", json.dumps(record)):
        validate_pending_task(record)
        index = record["index"]
        batch_id = record["batchId"]
        request = record["request"]
        item_no = request["itemNo"]
        await items_table.put_item({"itemNo": str(item_no),
                                    "updateTimestamp": now_epoch_millis()},
                                   batch_writer)
        processed_task = {"batchId": batch_id,
                          "index": index,
                          "request": request,
                          "response": {"success": True, "message": "Ok"}}
        validate_processed_task(processed_task)
        await work_bucket.write_task_result(batch_id, index, processed_task, s3_resource)
        await work_bucket.delete_pending_task(batch_id, index, s3_resource)


async def __check_if_complete(batch_id, s3_resource, sqs_client):
    if not await work_bucket.exists_pending_task(batch_id, s3_resource):
        await gather_queue.send_batch_complete_message(batch_id, sqs_client)
