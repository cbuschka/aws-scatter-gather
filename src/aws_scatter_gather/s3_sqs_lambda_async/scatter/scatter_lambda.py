from typing import Tuple, Optional
from uuid import uuid4

import aws_scatter_gather.util.logger as logger
from aws_scatter_gather.common.validation import validate_input, validate_pending_task
from aws_scatter_gather.measurement.measurement_recorder import record_batch_started, record_scatter_finished
from aws_scatter_gather.s3_sqs_lambda_async.resources import input_bucket, process_queue, work_bucket
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import json
from aws_scatter_gather.util import sqs_event, s3_event
from aws_scatter_gather.util.aioaws import enable_xray
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.s3_batch_writer import S3BatchWriter
from aws_scatter_gather.util.trace import trace

enable_xray()

logger.configure(name=__name__)


def __extract_batch_id(object_key: str):
    if "/" in object_key or not object_key.endswith(".json"):
        raise ValueError("Filename must be <batchId>.json.")
    return object_key[0:-5]


def __get_s3_object_from(event) -> Optional[Tuple]:
    record = sqs_event.get_single_body(event)
    return s3_event.get_single_s3_object(record)


async def __write_tasks_and_send_messages(batch_id, records, s3_resource, sqs_client):
    async with trace("Writing/sending {} tasks for batch {}", len(records), batch_id):
        async with S3BatchWriter(s3_resource=s3_resource, flush_amount=100) as batch_writer:
            for index, record in enumerate(records, start=0):
                pending_task = {"batchId": batch_id, "index": index, "request": record}
                validate_pending_task(pending_task)
                await work_bucket.write_pending_task(batch_id, index, pending_task, batch_writer)

        async with process_queue.new_batch_sender(sqs_client) as batch_sender:
            for index, record in enumerate(records, start=0):
                pending_task = {"batchId": batch_id, "index": index, "request": record}
                validate_pending_task(pending_task)
                await batch_sender.send_message(message={"Id": str(uuid4()), "MessageBody": json.dumps(pending_task)})


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    s3_object = __get_s3_object_from(event)
    if s3_object is None:
        return
    batch_id = __extract_batch_id(s3_object[1])
    async with trace("Scattering {}", batch_id):
        async with aioaws.resource("s3") as s3_resource, aioaws.client("sqs") as sqs_client:
            batch_doc = await input_bucket.read_batch_input(s3_object[0], s3_object[1], s3_resource)
            validate_input(batch_doc)
            records = batch_doc.get("records", [])
            record_batch_started(batch_id)
            await work_bucket.write_batch_status(batch_id, len(records), s3_resource)
            await __write_tasks_and_send_messages(batch_id, records, s3_resource, sqs_client)

            await input_bucket.delete_batch_input(s3_object[0], s3_object[1], s3_resource)
    record_scatter_finished(batch_id, len(records))
