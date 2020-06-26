import json

from aws_scatter_gather.s3_sqs_lambda_sync.resources import items_table
from aws_scatter_gather.s3_sqs_lambda_sync.resources import work_bucket, gather_queue
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.jsontime import now_epoch_millis
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))
    records = event["Records"]
    batch_writer = items_table.new_batch_writer()
    for record in records:
        record = json.loads(record["body"])
        with trace("Processing {}", json.dumps(record)):
            index = record["index"]
            batch_id = record["batchId"]
            request = record["request"]
            item_no = request["itemNo"]
            items_table.put_item({"itemNo": str(item_no),
                                  "updateTimestamp": now_epoch_millis()},
                                 batch_writer)
            work_bucket.write_task_result(batch_id, index, request, {"success": True, "message": "Ok"})
            work_bucket.delete_pending_task(batch_id, index)
            if not work_bucket.exists_pending_task(batch_id):
                gather_queue.send_batch_complete_message(batch_id)
