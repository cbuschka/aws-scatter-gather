import json
import unittest
from uuid import uuid4

from aws_scatter_gather.s3_sqs_lambda_async.resources import input_bucket
from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util.async_util import async_to_sync
from localstack_fixture import localstack

SPEC = {
    "s3": {
        "buckets": {
            input_bucket.INPUT_BUCKET: {}
        }
    }
}


class InputBucketTest(unittest.TestCase):
    @async_to_sync
    async def setUp(self) -> None:
        aioaws.set_factory(localstack)
        self.spec = await localstack.create(SPEC)
        self.batch_id = str(uuid4())

    @async_to_sync
    async def tearDown(self) -> None:
        await localstack.destroy(self.spec)

    @async_to_sync
    async def test_it(self):
        async with localstack.resource("s3") as s3_resource:
            await input_bucket.write_batch_input(self.batch_id, json.dumps({"records": []}), s3_resource)

        await localstack.s3.assert_object_exists("s3-sqs-lambda-async-input", f"{self.batch_id}.json")
