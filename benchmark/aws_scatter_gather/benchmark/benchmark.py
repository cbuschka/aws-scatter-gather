import logging
from collections import namedtuple
from uuid import uuid4
import sys

from aws_scatter_gather.benchmark import s3_sqs_lambda_async
from aws_scatter_gather.benchmark import s3_sqs_lambda_async_chunked
from aws_scatter_gather.benchmark import s3_sqs_lambda_sync
from aws_scatter_gather.util.trace import trace

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

Test = namedtuple("Test", ["count", "variants"])
TESTS = [
    Test(11, [s3_sqs_lambda_sync, s3_sqs_lambda_async, s3_sqs_lambda_async_chunked]),
    Test(101, [s3_sqs_lambda_sync, s3_sqs_lambda_async, s3_sqs_lambda_async_chunked]),
    Test(1001, [s3_sqs_lambda_sync, s3_sqs_lambda_async, s3_sqs_lambda_async_chunked]),
    Test(10001, [s3_sqs_lambda_async, s3_sqs_lambda_async_chunked]),
    Test(100001, [s3_sqs_lambda_async_chunked]),
    Test(1000001, [s3_sqs_lambda_async_chunked]),
]


def run():
    for test in TESTS:
        logger.info("Benchmarking with {count} records.".format(count=test.count))
        batch = {"records": [{"index": i, "info": "request#{}".format(i)} for i in range(test.count)]}

        for variant in test.variants:
            with trace("Variant {}...", variant.name()):
                batch_id = str(uuid4())
                variant.run(batch_id, batch)


if __name__ == "__main__":
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 8):
        print("Python 3.8 or higher is required.")
        print("Sorry, your python is {}.{}.".format(sys.version_info.major, sys.version_info.minor))
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    run()
