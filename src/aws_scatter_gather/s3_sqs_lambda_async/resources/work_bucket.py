import json
import os

from aws_scatter_gather.util.jsontime import now
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

WORK_BUCKET = "{SCOPE}s3-sqs-lambda-async-work".format(SCOPE=SCOPE)


async def write_batch_status(batch_id, record_count, s3_resource):
    async with trace("Writing status for {}", batch_id):
        object_key = "{}/status.json".format(batch_id)
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        await s3_object.put(ACL='private', Body=json.dumps({
            "variant": "s3-sqs-lambda-async",
            "batchId": batch_id,
            "taskCount": record_count,
            "startTime": now()
        }))


# async def delete_batch_status(batch_id):
#    object_key = "{}/status.json".format(batch_id)
#    async with trace("Deleting {}/{} from s3", WORK_BUCKET, object_key):
#        async with aioaws.resource("s3") as s3_resource:
#            s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
#            await s3_object.delete()


async def exists_pending_task(batch_id, s3_resource):
    async with trace("Checking if batch batch_id={} is complete", batch_id):
        s3_bucket = await s3_resource.Bucket(name=WORK_BUCKET)
        async for _ in s3_bucket.objects.filter(Prefix="{}/pending/".format(batch_id), MaxKeys=1):
            return True
        else:
            return False


async def write_pending_task(batch_id, index, request, s3_resource):
    object_key = "{}/pending/{}.json".format(batch_id, index)
    async with trace("Write pending task {}/{} to s3", WORK_BUCKET, object_key):
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        await s3_object.put(ACL='private', Body=json.dumps({"batchId": batch_id,
                                                            "index": index,
                                                            "request": request}))


async def write_task_result(batch_id, index, request, result, s3_resource):
    object_key = "{}/done/{}.json".format(batch_id, index)
    async with trace("Writing task result {}/{} to s3", WORK_BUCKET, object_key):
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        await s3_object.put(ACL='private', Body=json.dumps({"batchId": batch_id,
                                                            "index": index,
                                                            "request": request,
                                                            "response": result}))


async def delete_pending_task(batch_id, index, s3_resource):
    object_key = "{}/pending/{}.json".format(batch_id, index)
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


async def read_task_result(batch_id, index, s3_resource):
    async with trace("Reading task result batch_id={}/index={}", batch_id, index):
        object_key = "{}/done/{}.json".format(batch_id, index)
        s3_object = await s3_resource.Object(WORK_BUCKET, object_key)
        response = await s3_object.get()
        async with response["Body"] as stream:
            data = await stream.read()
            json_doc = json.loads(data)
            return json_doc
