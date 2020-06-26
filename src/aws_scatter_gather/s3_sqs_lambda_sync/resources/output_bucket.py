from aws_scatter_gather.util import json
import os

from aws_scatter_gather.util import aws
from aws_scatter_gather.util.trace import trace

SCOPE = os.environ.get("SCOPE", "")

OUTPUT_BUCKET = "{SCOPE}s3-sqs-lambda-sync-output".format(SCOPE=SCOPE)
s3_resource = aws.resource("s3")


def write_batch_output(batch_id, output):
    object_key = "{}.json".format(batch_id)
    with trace("Writing output to {}/{}", OUTPUT_BUCKET, object_key):
        s3_resource.Object(OUTPUT_BUCKET, object_key) \
            .put(ACL='private', Body=json.dumps(output))


def read_batch_output(batch_id) -> dict:
    object_key = "{}.json".format(batch_id)
    s3_object = s3_resource.Object(OUTPUT_BUCKET, object_key)
    json_data = s3_object.get()['Body'].read()
    json_doc = json.loads(json_data)
    return json_doc
