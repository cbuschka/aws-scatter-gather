import os
from decimal import Decimal

from aws_scatter_gather.util import dynamodb

from boto3.dynamodb.conditions import Key

from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

_TABLE_NAME = "{SCOPE}s3-sqs-lambda-dynamodb-batch-tasks".format(SCOPE=SCOPE)
_PENDING_INDEX_NAME = "{SCOPE}s3-sqs-lambda-dynamodb-pending-batch-tasks".format(SCOPE=SCOPE)


async def exist_pending_batch_tasks(batch_id, dynamodb_resource):
    async with trace("Checking if batch batch_id={} is complete", batch_id):
        table = await dynamodb_resource.Table(_TABLE_NAME)
        response = await table.query(IndexName=_PENDING_INDEX_NAME,
                                     Limit=1,
                                     ConsistentRead=True,
                                     KeyConditionExpression=Key("batchId").eq(batch_id))
        return len(response.get("Items", [])) > 0


async def new_batch_writer(dynamodb_resource):
    table = await dynamodb_resource.Table(_TABLE_NAME)
    return table.batch_writer()


async def put_pending_batch_task(pending_task, batch_writer):
    async with trace("Put pending batch task for batch_id={},index={}", pending_task["batchId"],
                     pending_task["index"]):
        pending_task = pending_task.copy()
        pending_task["isPending"] = "y"
        await batch_writer.put_item(Item=pending_task)


async def put_processed_batch_task(batch_id, index, request, response, dynamodb_resource):
    async with trace("Put processed batch task for batch_id={},index={}", batch_id, index):
        table = await dynamodb_resource.Table(_TABLE_NAME)
        await table.put_item(Item={"batchId": batch_id,
                                   "index": index,
                                   "request": request,
                                   "response": response
                                   # NO isPending!!!
                                   })


async def get_batch_task(batch_id, index, dynamodb_resource):
    async with trace("Get pending batch task for batch_id={},index={}", batch_id, index):
        table = await dynamodb_resource.Table(_TABLE_NAME)
        response = await table.get_item(Key={"batchId": batch_id,
                                             "index": index})
        if not "Item" in response:
            raise ValueError("Batch task batchId={}/index={} not found.".format(batch_id, index))
        return dynamodb.clean(response["Item"])
