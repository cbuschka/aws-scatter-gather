import os

from aws_scatter_gather.util import aws
from aws_scatter_gather.util.trace import trace

VARIANT = os.environ.get("VARIANT", "unknown")
SCOPE = os.environ.get("SCOPE", "unknown")
COMMITISH = os.environ.get("COMMITISH", "unknown")
ENV = os.environ.get("ENV", "unknown")
TABLE_NAME = "{SCOPE}measurement-events".format(SCOPE=SCOPE)

dynamodb_resource = aws.resource("dynamodb")


def write_measurement(data):
    with trace("Writing measurement event"):
        table = dynamodb_resource.Table(TABLE_NAME)
        table.put_item(Item=data, ReturnValues='NONE')


def scan_measurements():
    table = dynamodb_resource.Table(TABLE_NAME)
    response = table.scan(Limit=100,
                          Select="ALL_ATTRIBUTES")
    last_evaluated_key = response.get("LastEvaluatedKey", None)
    for record in response["Items"]:
        yield record

    while last_evaluated_key is not None:
        response = table.scan(Limit=100,
                              ExclusiveStartKey=last_evaluated_key,
                              Select="ALL_ATTRIBUTES")
        last_evaluated_key = response.get("LastEvaluatedKey", None)
        for record in response["Items"]:
            yield record
