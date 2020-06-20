import csv

import sys

from aws_scatter_gather.resources import measurement_events_table
from aws_scatter_gather.util import jsontime


def __collect_measurements():
    batches = {}
    for record in measurement_events_table.scan_measurements():
        batch_id = record["batchId"]
        timestamp = record["timestamp"]
        batch = batches.get(batch_id, {"batchId": batch_id})
        if "count" in record:
            batch["count"] = record["count"]
        if record["type"] == "BATCH_STARTED":
            batch["startTime"] = timestamp
        if record["type"] == "BATCH_FINISHED":
            batch["endTime"] = timestamp
        for key in ["variant", "count", "scope", "commitish", "env"]:
            if key in record:
                batch[key] = record[key]
        if "startTime" in batch and "endTime" in batch and "count" in batch:
            start_time = jsontime.parse(batch["startTime"])
            end_time = jsontime.parse(batch["endTime"])
            duration_in_secs = (end_time - start_time).total_seconds()
            batch["durationInSeconds"] = str(duration_in_secs)
            batch["relativeDurationInSeconds"] = str(round(duration_in_secs / int(batch["count"]), 2))
            batch["outcome"] = "success"
        else:
            batch["outcome"] = "failure"

        batches[batch_id] = batch

    return batches


def summarize():
    batches = __collect_measurements()
    csvout = csv.writer(sys.stdout, dialect='excel', quoting=csv.QUOTE_MINIMAL)
    keys = ["commitish", "variant", "env", "scope", "batchId", "count", "startTime", "endTime", "durationInSeconds",
            "relativeDurationInSeconds", "outcome"]
    csvout.writerow(keys)
    for key, batch in batches.items():
        csvout.writerow([batch.get(key, "") for key in keys])


if __name__ == "__main__":
    summarize()
