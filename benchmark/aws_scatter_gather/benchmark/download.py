import csv
import os

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
            batch["batchStartTime"] = timestamp
        if record["type"] == "GATHER_STARTED":
            batch["gatherStartTime"] = timestamp
        if record["type"] == "SCATTER_FINISHED":
            batch["scatterEndTime"] = timestamp
        if record["type"] == "BATCH_FINISHED":
            batch["batchEndTime"] = timestamp
        for key in ["variant", "count", "scope", "commitish", "env"]:
            if key in record:
                batch[key] = record[key]
        if "batchStartTime" in batch and "batchEndTime" in batch and "count" in batch:
            start_time = jsontime.parse(batch["batchStartTime"])
            end_time = jsontime.parse(batch["batchEndTime"])
            duration_in_secs = (end_time - start_time).total_seconds()
            batch["batchDurationInSeconds"] = str(duration_in_secs)
            batch["batchDurationPerRecordInSeconds"] = str(float(duration_in_secs) / float(batch["count"]))
            batch["outcome"] = "success"
        else:
            batch["outcome"] = "failure"

        if "batchStartTime" in batch and "scatterEndTime" in batch and "count" in batch:
            start_time = jsontime.parse(batch["batchStartTime"])
            scatter_end_time = jsontime.parse(batch["scatterEndTime"])
            scatter_duration_in_secs = (scatter_end_time - start_time).total_seconds()
            batch["scatterDurationInSeconds"] = str(scatter_duration_in_secs)
            batch["scatterDurationPerRecordInSeconds"] = str(float(scatter_duration_in_secs) / float(batch["count"]))

        if "batchEndTime" in batch and "gatherStartTime" in batch and "count" in batch:
            start_time = jsontime.parse(batch["gatherStartTime"])
            end_time = jsontime.parse(batch["batchEndTime"])
            duration_in_secs = (end_time - start_time).total_seconds()
            batch["gatherDurationInSeconds"] = str(duration_in_secs)
            batch["gatherDurationPerRecordInSeconds"] = str(float(duration_in_secs) / float(batch["count"]))

        batches[batch_id] = batch

    return batches


def download():
    batches = __collect_measurements()
    filename = "measurements.csv"
    isnew = not os.path.isfile(filename)
    with open(filename, 'a') as fileout:
        csvout = csv.writer(fileout, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        keys = ["commitish", "variant", "env", "scope", "batchId",
                "count",
                "scatterDurationInSeconds", "scatterDurationPerRecordInSeconds",
                "gatherDurationInSeconds", "gatherDurationPerRecordInSeconds",
                "batchStartTime", "batchEndTime", "batchDurationInSeconds", "batchDurationPerRecordInSeconds",
                "outcome"]
        if isnew:
            csvout.writerow(keys)
        for key, batch in batches.items():
            csvout.writerow([batch.get(key, "") for key in keys])


if __name__ == "__main__":
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 8):
        print("Python 3.8 or higher is required.")
        print("Sorry, your python is {}.{}.".format(sys.version_info.major, sys.version_info.minor))
        sys.exit(1)

    download()
