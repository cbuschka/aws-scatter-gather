from aws_scatter_gather.util import json
import os

from aws_scatter_gather.util import aws
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

GATHER_QUEUE = "{SCOPE}s3-sqs-lambda-sync-gather-queue.fifo".format(SCOPE=SCOPE)
sqs_client = aws.client("sqs")


def send_batch_complete_message(batch_id):
    with trace("Sending complete message for {}", batch_id):
        queue_url = sqs_client.get_queue_url(QueueName=GATHER_QUEUE)["QueueUrl"]
        sqs_client.send_message(QueueUrl=queue_url,
                                MessageGroupId=batch_id,
                                MessageDeduplicationId=batch_id,
                                MessageBody=json.dumps({"batchId": batch_id}))
