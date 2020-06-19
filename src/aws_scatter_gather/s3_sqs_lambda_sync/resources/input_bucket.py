import json
import os

import aws_scatter_gather.util.aws as aws
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

INPUT_BUCKET = "{SCOPE}s3-sqs-lambda-sync-input".format(SCOPE=SCOPE)
s3_resource = aws.resource("s3")


def write_batch_input(batch_id, input):
    object_key = "{}.json".format(batch_id)
    with trace("Writing input {}/{}", INPUT_BUCKET, object_key):
        s3_resource.Object(INPUT_BUCKET, object_key) \
            .put(ACL='private', Body=json.dumps(input))


def read_batch_input(bucket_name, object_key) -> dict:
    with trace("Reading input {}/{} from s3", bucket_name, object_key):
        if bucket_name != INPUT_BUCKET:
            raise ValueError("Expected bucket {}, but was {}.".format(INPUT_BUCKET, bucket_name))

        s3_object = s3_resource.Object(bucket_name, object_key)
        json_data = s3_object.get()['Body'].read()
        json_doc = json.loads(json_data)
        return json_doc


def delete_batch_input(bucket_name, object_key):
    with trace("Deleting {}/{} from s3", bucket_name, object_key):
        s3_resource.Object(bucket_name, object_key).delete()
