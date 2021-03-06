from typing import Tuple, Optional

import aws_scatter_gather.util.logger as logger
from aws_scatter_gather.common.validation import validate_input, validate_pending_chunk_of_tasks
from aws_scatter_gather.measurement.measurement_recorder import record_batch_started, record_scatter_finished
from aws_scatter_gather.s3_notification_sqs_lambda.resources import input_bucket, \
    work_bucket
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util import json
from aws_scatter_gather.util import sqs_event, s3_event
from aws_scatter_gather.util.aioxray import xray_profile
from aws_scatter_gather.util.async_util import async_to_sync
from aws_scatter_gather.util.enumchunks import enumchunks
from aws_scatter_gather.util.s3_batch_writer import S3BatchWriter
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)

CHUNK_SIZE = 100


def __extract_batch_id(object_key: str):
    if "/" in object_key or not object_key.endswith(".json"):
        raise ValueError("Filename must be <batchId>.json.")
    return object_key[0:-5]


def __get_s3_object_from(event) -> Optional[Tuple]:
    record = sqs_event.get_single_body(event)
    if s3_event.is_s3_test_event(record):
        return None
    return s3_event.get_single_s3_object(record)


async def __write_chunks(batch_id, records, s3_resource, sqs_client):
    async with trace("Writing chunks for batch {}", batch_id):
        async with S3BatchWriter(s3_resource=s3_resource, flush_amount=CHUNK_SIZE) as batch_writer:
            for chunk_index, chunk in enumchunks(records, CHUNK_SIZE):
                chunk = {"batchId": batch_id, "index": chunk_index,
                         "records": [{"request": record, "index": chunk_index + record_index} for record_index, record
                                     in enumerate(chunk)]}
                validate_pending_chunk_of_tasks(chunk)
                await work_bucket.write_pending_chunk(batch_id, chunk_index, chunk, batch_writer)


@async_to_sync
@xray_profile
async def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))

    s3_object = __get_s3_object_from(event)
    if s3_object is None:
        logger.info("Is s3 test event. Skipping.")
        return

    batch_id = __extract_batch_id(s3_object[1])
    async with trace("Scattering {}", batch_id):
        async with aioaws.resource("s3") as s3_resource, aioaws.client("sqs") as sqs_client:
            batch_doc = await input_bucket.read_batch_input(s3_object[0], s3_object[1], s3_resource)
            validate_input(batch_doc)
            records = batch_doc.get("records", [])
            record_batch_started(batch_id)
            await work_bucket.write_batch_status(batch_id, len(records), CHUNK_SIZE, s3_resource)
            await __write_chunks(batch_id, records, s3_resource, sqs_client)
            await input_bucket.delete_batch_input(s3_object[0], s3_object[1], s3_resource)
    record_scatter_finished(batch_id, len(records))
