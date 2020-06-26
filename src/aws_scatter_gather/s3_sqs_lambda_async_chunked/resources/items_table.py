import os

from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

ITEMS_TABLE = "{SCOPE}s3-sqs-lambda-async-chunked-items".format(SCOPE=SCOPE)


async def get_item(item_no, dynamodb_resource):
    async with trace("Get item {}", item_no):
        table = await dynamodb_resource.Table(ITEMS_TABLE)
        response = await table.get_item(Key={"itemNo": item_no})
        return response.get('Item', None)


async def new_batch_writer(dynamodb_resource):
    table = await dynamodb_resource.Table(ITEMS_TABLE)
    return table.batch_writer(overwrite_by_pkeys=["itemNo"])


async def put_item(item, batch_writer):
    async with trace("Put item {}", item.get("itemNo", None)):
        await batch_writer.put_item(Item=item)
