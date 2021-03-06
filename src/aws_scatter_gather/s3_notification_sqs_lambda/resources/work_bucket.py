import os

from aws_scatter_gather.util import json
from aws_scatter_gather.util.jsontime import now
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

WORK_BUCKET = "{SCOPE}s3-notification-sqs-lambda-work".format(SCOPE=SCOPE)


async def write_batch_status(batch_id, record_count, chunk_size, s3_resource):
    async with trace("Writing status for {}", batch_id):
        object_key = "{}/status.json".format(batch_id)
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        await s3_object.put(ACL='private', Body=json.dumps({
            "variant": "s3-notification-sqs-lambda",
            "batchId": batch_id,
            "chunkSize": chunk_size,
            "taskCount": record_count,
            "startTime": now()
        }))


# async def delete_batch_status(batch_id):
#    object_key = "{}/status.json".format(batch_id)
#    async with trace("Deleting {}/{} from s3", WORK_BUCKET, object_key):
#        async with aioaws.resource("s3") as s3_resource:
#            s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
#            await s3_object.delete()


async def exists_pending_chunk(batch_id, s3_resource):
    async with trace("Checking if batch batch_id={} is complete", batch_id):
        s3_bucket = await s3_resource.Bucket(name=WORK_BUCKET)
        async for _ in s3_bucket.objects.filter(Prefix="{}/pending/".format(batch_id), MaxKeys=1):
            return True
        else:
            return False


async def write_pending_chunk(batch_id, index, chunk, batch_writer):
    object_key = "{}/pending/{}.pending.json".format(batch_id, index)
    async with trace("Write pending chunk {}/{} to s3", WORK_BUCKET, object_key):
        await batch_writer.put(Bucket=WORK_BUCKET, Key=object_key,
                               ACL='private',
                               Body=json.dumps(chunk))


async def write_chunk_result(batch_id, index, chunk, s3_resource):
    object_key = "{}/done/{}.done.json".format(batch_id, index)
    async with trace("Writing chunk result {}/{} to s3", WORK_BUCKET, object_key):
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        await s3_object.put(ACL='private', Body=json.dumps(chunk))


async def delete_pending_chunk(batch_id, index, s3_resource):
    object_key = "{}/pending/{}.pending.json".format(batch_id, index)
    async with trace("Deleting {}/{} from s3", WORK_BUCKET, object_key):
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        await s3_object.delete()


async def read_batch_status(batch_id, s3_resource):
    async with trace("Reading status for batch_id={}", batch_id):
        object_key = "{}/status.json".format(batch_id)
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        response = await s3_object.get()
        async with response["Body"] as stream:
            data = await stream.read()
            json_doc = json.loads(data)
            return json_doc


async def read_pending_chunk(s3_bucket, s3_object_key, s3_resource):
    async with trace("Reading pending chunk bucket={}/key={}", s3_bucket, s3_object_key):
        s3_object = await s3_resource.Object(s3_bucket, s3_object_key)
        response = await s3_object.get()
        async with response["Body"] as stream:
            data = await stream.read()
            json_doc = json.loads(data)
            return json_doc


async def read_chunk_result(batch_id, index, s3_resource):
    async with trace("Reading chunk result batch_id={}/index={}", batch_id, index):
        object_key = "{}/done/{}.done.json".format(batch_id, index)
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        response = await s3_object.get()
        async with response["Body"] as stream:
            data = await stream.read()
            json_doc = json.loads(data)
            return json_doc
