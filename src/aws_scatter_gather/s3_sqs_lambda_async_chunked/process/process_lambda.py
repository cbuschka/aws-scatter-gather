import asyncio
import json

from aws_scatter_gather.s3_sqs_lambda_async_chunked.resources import work_bucket, gather_queue
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    async with aioaws.client("sqs") as sqs_client, aioaws.resource("s3") as s3_resource:
        chunks = [json.loads(record["body"]) for record in event["Records"]]
        await asyncio.gather(*[__process(chunk, s3_resource) for chunk in chunks])

        batch_ids = {chunk["batchId"] for chunk in chunks}
        await asyncio.gather(*[__check_if_complete(batch_id, s3_resource, sqs_client) for batch_id in batch_ids])


async def __process(message, s3_resource):
    async with trace("Processing {}", json.dumps(message)):
        batch_id = message["batchId"]
        index = message["index"]
        chunk = await work_bucket.read_pending_chunk(batch_id, index, s3_resource)
        for record in chunk["records"]:
            request = record["request"]
            record["response"] = {"success": True,
                                  "message": "Faked success for {}".format(
                                      json.dumps(request.get("info", "noinfo")))}
        await work_bucket.write_chunk_result(batch_id, index, chunk, s3_resource)
        await work_bucket.delete_pending_chunk(batch_id, index, s3_resource)


async def __check_if_complete(batch_id, s3_resource, sqs_client):
    if not await work_bucket.exists_pending_chunk(batch_id, s3_resource):
        await gather_queue.send_batch_complete_message(batch_id, sqs_client)
