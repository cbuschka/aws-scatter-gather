import asyncio

from aws_scatter_gather.s3_sqs_lambda_dynamodb.resources import gather_queue, items_table, batch_tasks_table
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import json
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.aioaws import enable_xray
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.jsontime import now_epoch_millis
from aws_scatter_gather.util.trace import trace

enable_xray()

logger.configure(name=__name__)


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    async with aioaws.client("sqs") as sqs_client, \
        aioaws.resource("dynamodb") as dynamodb_resource, \
        await items_table.new_batch_writer(dynamodb_resource) as batch_writer:
        chunks = [json.loads(record["body"]) for record in event["Records"]]
        await asyncio.gather(*[__process(chunk, dynamodb_resource, batch_writer) for chunk in chunks])

        batch_ids = {chunk["batchId"] for chunk in chunks}
        await asyncio.gather(*[__check_if_complete(batch_id, dynamodb_resource, sqs_client) for batch_id in batch_ids])


async def __process(message, dynamodb_resource, batch_writer):
    async with trace("Processing {}", json.dumps(message)):
        batch_id = message["batchId"]
        records = message["records"]
        tasks = await asyncio.gather(
            *[batch_tasks_table.get_batch_task(batch_id, record["index"], dynamodb_resource) for record in records])
        for task in tasks:
            index = task["index"]
            request = task["request"]
            item_no = request["itemNo"]
            price = request["price"]
            response = {"success": True, "message": "Ok"}
            await items_table.put_item({"itemNo": str(item_no),
                                        "price": price,
                                        "updateTimestamp": now_epoch_millis()},
                                       batch_writer)
            await batch_tasks_table.put_processed_batch_task(batch_id, index, request, response,
                                                             dynamodb_resource)


async def __check_if_complete(batch_id, dynamodb_resource, sqs_client):
    if not await batch_tasks_table.exist_pending_batch_tasks(batch_id, dynamodb_resource):
        await gather_queue.send_batch_complete_message(batch_id, sqs_client)
