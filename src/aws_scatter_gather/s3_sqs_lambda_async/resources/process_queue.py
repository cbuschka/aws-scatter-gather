import os

SCOPE = os.environ.get("SCOPE", "")

PROCESS_QUEUE = "{SCOPE}s3-sqs-lambda-async-process-queue".format(SCOPE=SCOPE)

from aws_scatter_gather.util.sqs_batch_sender import AsyncSqsBatchSender


def new_batch_sender(sqs_client):
    return AsyncSqsBatchSender(sqs_client, queue_name=PROCESS_QUEUE)
