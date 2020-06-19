import os

from aws_scatter_gather.util import aws

SCOPE = os.environ.get("SCOPE", "")

PROCESS_QUEUE = "{SCOPE}s3-sqs-lambda-sync-process-queue".format(SCOPE=SCOPE)
sqs_client = aws.client("sqs")
from aws_scatter_gather.util.sqs_batch_sender import SqsBatchSender


def new_batch_sender():
    return SqsBatchSender(sqs_client, queue_name=PROCESS_QUEUE)
