import aioboto3

from aws_scatter_gather.util import json
from .env import get_endpoint_url, get_region_name


class LocalDynamodb(object):
    def __init__(self, endpoint_url=None, region_name=None):
        self.endpoint_url = endpoint_url or get_endpoint_url()
        self.region_name = region_name or get_region_name()

    async def create(self, spec):
        await self.create_schema(schema=spec)

    async def destroy(self, spec):
        pass

    def new_resource(self):
        return aioboto3.resource('dynamodb', endpoint_url=self.endpoint_url, region_name=self.region_name)

    def new_client(self):
        return aioboto3.client('dynamodb', endpoint_url=self.endpoint_url, region_name=self.region_name)

    async def create_schema(self, schema=None):
        async with self.new_client() as client:
            response = await client.list_tables()
            table_names = response["TableNames"]

            for table_name, table in schema["Tables"].items():
                if table_name in table_names:
                    await client.delete_table(TableName=table_name)

                create_table_args = {
                    "TableName": table_name,
                    "AttributeDefinitions": table["AttributeDefinitions"],
                    "KeySchema": table["KeySchema"],
                    "BillingMode": table.get("BillingMode", "PAY_PER_REQUEST")
                }
                lsi = table.get("LocalSecondaryIndexes", None)
                if lsi:
                    create_table_args["LocalSecondaryIndexes"] = lsi

                gsi = table.get("GlobalSecondaryIndexes", None)
                if gsi:
                    create_table_args["GlobalSecondaryIndexes"] = gsi

                await client.create_table(**create_table_args)

    async def load_items(self, items=None):
        async with self.new_resource() as resource:
            for table_name, items in items.items():
                table = await resource.Table(table_name)
                for item in items:
                    await table.put_item(Item=item)

    async def assert_item_equal(self, table_name=None, key=None, expected_item=None):
        async with self.new_resource() as resource:
            table = await resource.Table(table_name)
            response = await table.get_item(TableName=table_name, Key=key)
            if not "Item" in response:
                raise AssertionError("Item with key={} not found in {}.".format(json.dumps(key), table_name))
            item = response["Item"]
            if json.dumps(item, sort_keys=True) != json.dumps(expected_item, sort_keys=True):
                raise AssertionError("Item {} from {} is not equal to: {}.".format(json.dumps(item),
                                                                                   table_name,
                                                                                   json.dumps(expected_item)))

    async def assert_contains_item(self, table_name=None, key=None):
        async with self.new_resource() as resource:
            table = await resource.Table(table_name)
            response = await table.get_item(TableName=table_name, Key=key)
            if not "Item" in response:
                raise AssertionError("Item with key={} not found in {}.".format(json.dumps(key), table_name))

    async def assert_item_not_present(self, table_name=None, key=None):
        async with self.new_resource() as resource:
            table = await resource.Table(table_name)
            response = await table.get_item(TableName=table_name, Key=key)
            if "Item" in response:
                item = response["Item"]
                raise AssertionError("Item with key={} exists in {}: {}.".format(json.dumps(key), table_name,
                                                                                 json.dumps(item)))

    async def assert_item_contains_values(self, table_name=None, key=None, expected_item=None):
        async with self.new_resource() as resource:
            table = await resource.Table(table_name)
            response = await table.get_item(TableName=table_name, Key=key)
            if not "Item" in response:
                raise AssertionError("Item with key={} not found in {}.".format(json.dumps(key), table_name))
            item = response["Item"]
            for item_key, item_value in expected_item.items():
                if not item_key in item:
                    raise AssertionError(
                        "Item {} is missing the attribute \"{}\".".format(
                            json.dumps(item),
                            item_key))
                if json.dumps(item.get(item_key, None), sort_keys=True) != json.dumps(item_value,
                                                                                      sort_keys=True):
                    raise AssertionError(
                        "Attribute \"{}\" has not expected value {} in {}.".format(item_key, item_value,
                                                                                   json.dumps(item)))


"""
Example schema:
SCHEMA = schema = {"Tables": {
    "stock-batch-status": {
        "AttributeDefinitions": [
            {
                "AttributeName": "batchID",
                "AttributeType": "S"

            }
        ],
        "KeySchema": [
            {
                "AttributeName": "batchID",
                "KeyType": "HASH"
            }
        ]
    },
    "stock-batch-task": {
        "AttributeDefinitions": [
            {
                "AttributeName": "batchID",
                "AttributeType": "S",
            },
            {
                "AttributeName": "pos",
                "AttributeType": "N",
            }
        ],
        "KeySchema": [
            {
                "AttributeName": "batchID",
                "KeyType": "HASH"
            },
            {
                "AttributeName": "pos",
                "KeyType": "RANGE"
            }
        ],
        "LocalSecondaryIndexes": [
        {
            "IndexName": 'pending-stock-batch-tasks',
            "KeySchema": [
                {
                    "AttributeName": "batchID",
                    'KeyType': 'HASH'
                },
                {
                    "AttributeName": "isPending",
                    'KeyType': 'RANGE'
                },
            ],
            "Projection": {
                "ProjectionType": "KEYS_ONLY"
            }
        },
    ],
    }
}}
"""
