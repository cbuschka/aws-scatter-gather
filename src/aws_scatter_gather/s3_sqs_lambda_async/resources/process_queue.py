import os

from aws_scatter_gather.util import aioaws

SCOPE = os.environ.get("SCOPE", "")

PROCESS_QUEUE = "{SCOPE}s3-sqs-lambda-async-process-queue".format(SCOPE=SCOPE)

from aws_scatter_gather.util.sqs_batch_sender import AsyncSqsBatchSender


def new_batch_sender():
    return AsyncSqsBatchSender(lambda: aioaws.client("sqs"), queue_name=PROCESS_QUEUE)
