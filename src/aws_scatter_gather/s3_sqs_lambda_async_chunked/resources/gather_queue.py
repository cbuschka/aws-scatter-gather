from aws_scatter_gather.util import json
import os

SCOPE = os.environ.get("SCOPE", "")

GATHER_QUEUE = "{SCOPE}s3-sqs-lambda-async-chunked-gather-queue.fifo".format(SCOPE=SCOPE)

from aws_scatter_gather.util.trace import trace


async def send_batch_complete_message(batch_id, sqs_client):
    async with trace("Sending complete message for {}", batch_id):
        response = await sqs_client.get_queue_url(QueueName=GATHER_QUEUE)
        queue_url = response["QueueUrl"]
        await sqs_client.send_message(QueueUrl=queue_url,
                                      MessageGroupId=batch_id,
                                      MessageDeduplicationId=batch_id,
                                      MessageBody=json.dumps({"batchId": batch_id}))
