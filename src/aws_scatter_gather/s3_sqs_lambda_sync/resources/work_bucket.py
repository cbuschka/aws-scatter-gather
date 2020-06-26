import json
import os

from aws_scatter_gather.util import aws
from aws_scatter_gather.util.jsontime import now
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

WORK_BUCKET = "{SCOPE}s3-sqs-lambda-sync-work".format(SCOPE=SCOPE)
s3_resource = aws.resource("s3")


def exists_pending_task(batch_id):
    with trace("Checking if batch batch_id={} is complete", batch_id):
        for _ in s3_resource.Bucket(name=WORK_BUCKET).objects.filter(Prefix="{}/pending/".format(batch_id), MaxKeys=1):
            return True
    return False


def write_batch_status(batch_id, record_count):
    with trace("Writing status for {}", batch_id):
        object_key = "{}/status.json".format(batch_id)
        s3_resource.Object(WORK_BUCKET, object_key).put(ACL='private', Body=json.dumps({
            "variant": "s3-sqs-lambda-sync",
            "batchId": batch_id,
            "taskCount": record_count,
            "startTime": now()
        }))


#def delete_batch_status(batch_id):
#    with trace("Deleting status for {}", batch_id):
#        object_key = "{}/status.json".format(batch_id)
#        s3_resource.Object(WORK_BUCKET, object_key).delete()


def write_pending_task(batch_id, index, request):
    object_key = "{}/pending/{}.json".format(batch_id, index)
    with trace("Write pending task {}/{} to s3", WORK_BUCKET, object_key):
        s3_resource.Object(WORK_BUCKET, object_key) \
            .put(ACL='private', Body=json.dumps({"batchId": batch_id,
                                                 "index": index,
                                                 "request": request}))


def delete_pending_task(batch_id, index):
    object_key = "{}/pending/{}.json".format(batch_id, index)
    with trace("Deleting {}/{} from s3", WORK_BUCKET, object_key):
        s3_resource.Object(WORK_BUCKET, object_key).delete()


def write_task_result(batch_id, index, request, result):
    object_key = "{}/done/{}.json".format(batch_id, index)
    with trace("Writing task result {}/{} to s3", WORK_BUCKET, object_key):
        s3_resource.Object(WORK_BUCKET, object_key).put(ACL="private", Body=json.dumps(
            {"index": index, "batchId": batch_id, "request": request, "response": result}))


def read_task_result(batch_id, index):
    object_key = "{}/done/{}.json".format(batch_id, index)
    with trace("Reading task result {}/{} to s3", WORK_BUCKET, object_key):
        s3_object = s3_resource.Object(WORK_BUCKET, object_key)
        data = s3_object.get()['Body'].read()
        json_doc = json.loads(data)
        return json_doc


#def delete_task_result(batch_id, index):
#    object_key = "{}/done/{}.json".format(batch_id, index)
#    with trace("Deleting {}/{} from s3", WORK_BUCKET, object_key):
#        s3_resource.Object(WORK_BUCKET, object_key).delete()


def read_batch_status(batch_id):
    with trace("Reading status for batch_id={}", batch_id):
        object_key = "{}/status.json".format(batch_id)
        s3_object = s3_resource.Object(WORK_BUCKET, object_key)
        data = s3_object.get()['Body'].read()
        json_doc = json.loads(data)
        return json_doc
