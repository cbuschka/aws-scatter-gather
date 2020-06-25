import os

from aws_scatter_gather.util import aws
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

ITEMS_TABLE = "{SCOPE}s3-sqs-lambda-sync-items".format(SCOPE=SCOPE)
dynamodb_resource = aws.resource("dynamodb")


def get_item(item_no):
    with trace("Get item {}", item_no):
        table = dynamodb_resource.Table(ITEMS_TABLE)
        response = table.get_item(Key={"itemNo": item_no})
        return response.get('Item', None)


def new_batch_writer():
    table = dynamodb_resource.Table(ITEMS_TABLE)
    return table.batch_writer()


def put_item(item, batch_writer):
    with trace("Put item {}", item.get("itemNo", None)):
        batch_writer.put_item(Item=item)
