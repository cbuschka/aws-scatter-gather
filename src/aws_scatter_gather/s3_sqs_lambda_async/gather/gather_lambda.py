import asyncio
from aws_scatter_gather.util import json

from aws_scatter_gather.common.validation import validate_processed_task
from aws_scatter_gather.measurement.measurement_recorder import record_batch_finished, record_gather_started
from aws_scatter_gather.s3_sqs_lambda_async.resources import work_bucket, output_bucket
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.jsontime import now
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    async with aioaws.resource("s3") as s3_resource:
        records = [json.loads(record["body"]) for record in event["Records"]]
        await asyncio.gather(*[__gather(record, s3_resource) for record in records])


async def __gather(record, s3_resource):
    batch_id = record["batchId"]
    record_gather_started(batch_id)
    async with trace("Gathering results for batch batch_id={}", batch_id):
        status = await work_bucket.read_batch_status(batch_id, s3_resource)

        results = await __read_task_results(batch_id, status["taskCount"], s3_resource)

        status["endTime"] = now()
        status["results"] = results
        batch_output = {"records": results}
        await output_bucket.write_batch_output(batch_id, batch_output, s3_resource)

    # await work_bucket.delete_batch_status(batch_id)
    record_batch_finished(batch_id)


async def __read_task_results(batch_id, count, s3_resource):
    return await asyncio.gather(
        *[__read_and_validate_task_result(batch_id, index, s3_resource) for index in range(count)])


async def __read_and_validate_task_result(batch_id, index, s3_resource):
    processed_task = await work_bucket.read_task_result(batch_id, index, s3_resource)
    validate_processed_task(processed_task)
    return processed_task
