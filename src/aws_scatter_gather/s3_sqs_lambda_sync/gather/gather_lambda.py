import json

from aws_scatter_gather.measurement.measurement_recorder import record_batch_finished, record_gather_started
from aws_scatter_gather.s3_sqs_lambda_sync.resources import work_bucket, output_bucket
from aws_scatter_gather.util import logger
from aws_scatter_gather.util.jsontime import now
from aws_scatter_gather.util.trace import trace

logger.configure(name=__name__)


def __read_task_results(batch_id, count):
    results = []
    for index in range(count):
        results.append(work_bucket.read_task_result(batch_id, index))
    return results


def handle_event(event, lambda_context):
    logger.info("Event: {}".format(json.dumps(event, indent=2)))
    records = event["Records"]
    for record in records:
        record = json.loads(record["body"])
        batch_id = record["batchId"]
        record_gather_started(batch_id)
        with trace("Gathering results for batch batch_id={}", batch_id):
            status = work_bucket.read_batch_status(batch_id)

            results = __read_task_results(batch_id, status["taskCount"])

            status["endTime"] = now()
            status["results"] = results
            output_bucket.write_batch_output(batch_id, {"records": results})

        # work_bucket.delete_batch_status(batch_id)
        record_batch_finished(batch_id)
