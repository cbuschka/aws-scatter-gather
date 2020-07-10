from typing import Tuple, Optional
from uuid import uuid4

from aws_scatter_gather.common.validation import validate_input
from aws_scatter_gather.measurement.measurement_recorder import record_batch_started, record_scatter_finished
from aws_scatter_gather.s3_sqs_lambda_sync.resources import input_bucket, process_queue, work_bucket
from aws_scatter_gather.util import json
from aws_scatter_gather.util import logger
from aws_scatter_gather.util import sqs_event, s3_event
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


def __extract_batch_id(object_key: str):
    if "/" in object_key or not object_key.endswith(".json"):
        raise ValueError("Filename must be <batchId>.json.")
    return object_key[0:-5]


def __get_s3_object_from(event) -> Optional[Tuple]:
    record = sqs_event.get_single_body(event)
    return s3_event.get_single_s3_object(record)


def __write_tasks_and_send_messages(batch_id, records):
    with trace("Writing/sending {} tasks for batch {}", len(records), batch_id):
        with process_queue.new_batch_sender() as batch_sender:
            for index, record in enumerate(records, start=0):
                work_bucket.write_pending_task(batch_id, index, record)
                batch_sender.send_message(message={"Id": str(uuid4()), "MessageBody": json.dumps(
                    {"batchId": batch_id, "index": index, "request": record})})


def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))
    s3_object = __get_s3_object_from(event)
    if s3_object is None:
        return
    batch_id = __extract_batch_id(s3_object[1])
    record_batch_started(batch_id)
    with trace("Scattering {}", batch_id):
        batch_doc = input_bucket.read_batch_input(s3_object[0], s3_object[1])
        validate_input(batch_doc)
        records = batch_doc.get("records", [])
        work_bucket.write_batch_status(batch_id, len(records))
        __write_tasks_and_send_messages(batch_id, records)

    input_bucket.delete_batch_input(s3_object[0], s3_object[1])
    record_scatter_finished(batch_id, len(records))
