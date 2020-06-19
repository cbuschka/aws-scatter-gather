import asyncio
import json

from aws_scatter_gather.measurement.measurement_recorder import record_batch_finished
from aws_scatter_gather.s3_sqs_lambda_async.resources import work_bucket, output_bucket
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.jsontime import now
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    records = [json.loads(record["body"]) for record in event["Records"]]
    await asyncio.gather(*[__gather(record) for record in records])


async def __gather(record):
    batch_id = record["batchId"]
    with trace("Gathering results for batch batch_id={}", batch_id):
        status = await work_bucket.read_batch_status(batch_id)

        results = await __read_task_results(batch_id, status["taskCount"])

        status["endTime"] = now()
        status["results"] = results
        await output_bucket.write_batch_output(batch_id, {"records": results})

    # await work_bucket.delete_batch_status(batch_id)
    record_batch_finished(batch_id)


async def __read_task_results(batch_id, count):
    return await asyncio.gather(*[work_bucket.read_task_result(batch_id, index) for index in range(count)])
