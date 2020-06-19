import json
import os

from aws_scatter_gather.util import aioaws
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")
INPUT_BUCKET = "{SCOPE}s3-sqs-lambda-async-input".format(SCOPE=SCOPE)


async def read_batch_input(bucket_name, object_key) -> dict:
    with trace("Reading input {}/{} from s3", bucket_name, object_key):
        if bucket_name != INPUT_BUCKET:
            raise ValueError("Expected bucket {}, but was {}.".format(INPUT_BUCKET, bucket_name))

        async with aioaws.resource("s3") as s3_resource:
            s3_object = await s3_resource.Object(bucket_name, object_key)
            response = await s3_object.get()
            async with response["Body"] as stream:
                data = await stream.read()
                json_doc = json.loads(data)
                return json_doc


async def delete_batch_input(bucket_name, object_key):
    if bucket_name != INPUT_BUCKET:
        raise ValueError("Expected bucket {}, but was {}.".format(INPUT_BUCKET, bucket_name))
    with trace("Deleting {}/{} from s3", bucket_name, object_key):
        async with aioaws.resource("s3") as s3_resource:
            s3_object = await s3_resource.Object(bucket_name, object_key)
            await s3_object.delete()


async def write_batch_input(batch_id, input):
    object_key = "{}.json".format(batch_id)
    with trace("Writing {}/{}", INPUT_BUCKET, object_key):
        async with aioaws.resource("s3") as s3_resource:
            s3_object = await s3_resource.Object(INPUT_BUCKET, object_key)
            await s3_object.put(ACL='private', Body=json.dumps(input))
