import os
from uuid import uuid4

from aws_scatter_gather.resources import measurement_events_table
from aws_scatter_gather.util.jsontime import now

VARIANT = os.environ.get("VARIANT", "unknown")
SCOPE = os.environ.get("SCOPE", "unknown")
COMMITISH = os.environ.get("COMMITISH", "unknown")
ENV = os.environ.get("ENV", "unknown")
TABLE_NAME = "{SCOPE}measurement-events".format(SCOPE=SCOPE)


def __write(data):
    data["uuid"] = str(uuid4())
    data["scope"] = SCOPE
    data["variant"] = VARIANT
    data["commitish"] = COMMITISH
    data["env"] = ENV
    data["timestamp"] = now()
    measurement_events_table.write_measurement(data)


def record_batch_started(batch_id, count):
    __write({"type": "BATCH_STARTED",
             "batchId": batch_id,
             "count": count})


def record_batch_finished(batch_id):
    __write({"type": "BATCH_FINISHED",
             "batchId": batch_id})
