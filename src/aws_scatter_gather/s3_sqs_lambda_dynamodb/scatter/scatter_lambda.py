from typing import Tuple, Optional
from uuid import uuid4

import aws_scatter_gather.util.logger as logger
from aws_scatter_gather.common.validation import validate_input, validate_pending_task
from aws_scatter_gather.measurement.measurement_recorder import record_batch_started, record_scatter_finished
from aws_scatter_gather.s3_sqs_lambda_dynamodb.resources import input_bucket, process_queue, batch_status_table, \
    batch_tasks_table
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import json
from aws_scatter_gather.util import sqs_event, s3_event
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.enumchunks import enumchunks
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)

CHUNK_SIZE = 100


def __extract_batch_id(object_key: str):
    if "/" in object_key or not object_key.endswith(".json"):
        raise ValueError("Filename must be <batchId>.json.")
    return object_key[0:-5]


def __get_s3_object_from(event) -> Optional[Tuple]:
    record = sqs_event.get_single_body(event)
    return s3_event.get_single_s3_object(record)


async def __write_chunks_and_send_messages(batch_id, records, dynamodb_resource, sqs_client):
    async with trace("Writing/sending chunks for batch {}", batch_id):
        async with await batch_tasks_table.new_batch_writer(dynamodb_resource) as batch_writer:
            for index, record in enumerate(records):
                pending_task = {"batchId": batch_id, "index": index, "request": record}
                validate_pending_task(pending_task)
                await batch_tasks_table.put_pending_batch_task(pending_task, batch_writer)

        async with process_queue.new_batch_sender(sqs_client) as batch_sender:
            for chunk_index, chunk in enumchunks(records, CHUNK_SIZE):
                async with trace("Sending chunk {} of tasks for batch_id={}", chunk_index, batch_id):
                    chunk = {"batchId": batch_id, "index": chunk_index,
                             "records": [{"index": chunk_index * CHUNK_SIZE + record_index} for
                                         record_index, record
                                         in enumerate(chunk)]}
                    await batch_sender.send_message(message={"Id": str(uuid4()), "MessageBody": json.dumps(chunk)})


@async_to_sync
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    s3_object = __get_s3_object_key_from(event)
    if s3_object is None:
        return
    batch_id = __extract_batch_id(s3_object[1])
    async with trace("Scattering {}", batch_id):
        async with aioaws.resource("s3") as s3_resource, \
            aioaws.client("sqs") as sqs_client, \
            aioaws.resource("dynamodb") as dynamodb_resource:
            batch_doc = await input_bucket.read_batch_input(s3_object[0], s3_object[1], s3_resource)
            validate_input(batch_doc)
            records = batch_doc.get("records", [])
            record_batch_started(batch_id)
            await batch_status_table.put_batch_status(batch_id, len(records), dynamodb_resource)
            await __write_chunks_and_send_messages(batch_id, records, dynamodb_resource, sqs_client)
            await input_bucket.delete_batch_input(s3_object[0], s3_object[1], s3_resource)
    record_scatter_finished(batch_id, len(records))
