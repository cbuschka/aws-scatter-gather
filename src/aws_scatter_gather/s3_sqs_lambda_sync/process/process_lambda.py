import json

from aws_scatter_gather.s3_sqs_lambda_sync.resources import work_bucket, gather_queue
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


def handle_event(event, lambda_context):
    records = event["Records"]
    for record in records:
        record = json.loads(record["body"])
        with trace("Processing {}", json.dumps(record)):
            index = record["index"]
            batch_id = record["batchId"]
            request = record["request"]

            work_bucket.write_task_result(batch_id, index, request, {"success": True,
                                                                     "message": "Faked success for {}".format(
                                                                         json.dumps(request.get("info", "noinfo")))})
            work_bucket.delete_pending_task(batch_id, index)
            if not work_bucket.exists_pending_task(batch_id):
                gather_queue.send_batch_complete_message(batch_id)
