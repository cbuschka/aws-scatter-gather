import os

from aws_scatter_gather.util import dynamodb
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

_TABLE_NAME = "{SCOPE}s3-sqs-lambda-dynamodb-batch-status".format(SCOPE=SCOPE)


async def put_batch_status(batch_id, record_count, dynamodb_resource):
    async with trace("Put batch status for batch_id={}", batch_id):
        table = await dynamodb_resource.Table(_TABLE_NAME)
        await table.put_item(Item={"batchId": batch_id, "taskCount": record_count})


async def get_batch_status(batch_id, dynamodb_resource):
    async with trace("Get batch status for batch_id={}", batch_id):
        table = await dynamodb_resource.Table(_TABLE_NAME)
        response = await table.get_item(Key={"batchId": batch_id})
        return dynamodb.clean(response["Item"])
