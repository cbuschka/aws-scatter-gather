import json
import os

from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")
OUTPUT_BUCKET = "{SCOPE}s3-sqs-lambda-async-output".format(SCOPE=SCOPE)


async def read_batch_output(batch_id) -> dict:
    object_key = "{}.json".format(batch_id)
    async with aioaws.resource("s3") as s3_resource:
        s3_object = await s3_resource.Object(OUTPUT_BUCKET, object_key)
        response = await s3_object.get()
        async with response["Body"] as stream:
            data = await stream.read()
            json_doc = json.loads(data)
            return json_doc


async def write_batch_output(batch_id, output):
    object_key = "{}.json".format(batch_id)
    with trace("Writing batch output {}/{} to s3", OUTPUT_BUCKET, object_key):
        async with aioaws.resource("s3") as s3_resource:
            s3_object = await s3_resource.Object(OUTPUT_BUCKET, object_key)
            await s3_object.put(ACL='private', Body=json.dumps(output))

