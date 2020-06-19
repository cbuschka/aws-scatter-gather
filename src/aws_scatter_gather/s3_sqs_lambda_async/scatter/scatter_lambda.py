import asyncio
import json
from typing import Tuple, Optional
from uuid import uuid4

import aws_scatter_gather.util.logger as logger
from aws_scatter_gather.measurement.measurement_recorder import record_batch_started
from aws_scatter_gather.s3_sqs_lambda_async.resources import input_bucket, process_queue, work_bucket
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


def __extract_batch_id(object_key: str):
    if "/" in object_key or not object_key.endswith(".json"):
        raise ValueError("Filename must be <batchId>.json.")
    return object_key[0:-5]


def __get_s3_object_from(event) -> Optional[Tuple]:
    records = event["Records"]
    if len(records) == 0:
        return None
    if len(records) > 1:
        raise ValueError("Only single document processing supported.")
    event = json.loads(records[0]["body"])
    if event.get("Event", None) == "s3:TestEvent":
        return None
    records = event["Records"]
    if len(records) > 1:
        raise ValueError("Only single document processing supported.")
    if len(records) == 0:
        return None
    s3_event = records[0]["s3"]
    bucket_name = s3_event["bucket"]["name"]
    object_key = s3_event["object"]["key"]
    return (bucket_name, object_key)


async def __write_tasks_and_send_messages(batch_id, records):
    with trace("Writing/sending {} tasks for batch {}", len(records), batch_id):
        futures = []
        for index, record in enumerate(records, start=0):
            futures.append(work_bucket.write_pending_task(batch_id, index, record))
        await asyncio.gather(*futures)

        async with process_queue.new_batch_sender() as batch_sender:
            for index, record in enumerate(records, start=0):
                await batch_sender.send_message(message={"Id": str(uuid4()), "MessageBody": json.dumps(
                    {"batchId": batch_id, "index": index, "request": record})})


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    s3_object = __get_s3_object_from(event)
    if s3_object is None:
        return
    batch_id = __extract_batch_id(s3_object[1])
    with trace("Scattering {}", batch_id):
        batch_doc = await input_bucket.read_batch_input(s3_object[0], s3_object[1])
        records = batch_doc.get("records", [])
        record_batch_started(batch_id, len(records))
        await work_bucket.write_batch_status(batch_id, len(records))
        await __write_tasks_and_send_messages(batch_id, records)

    await input_bucket.delete_batch_input(s3_object[0], s3_object[1])
