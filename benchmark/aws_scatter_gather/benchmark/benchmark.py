import logging
from collections import namedtuple
from random import randint
from uuid import uuid4

import sys

from aws_scatter_gather.benchmark import s3_notification_sqs_lambda
from aws_scatter_gather.benchmark import s3_sqs_lambda_async
from aws_scatter_gather.benchmark import s3_sqs_lambda_async_chunked
from aws_scatter_gather.benchmark import s3_sqs_lambda_dynamodb
from aws_scatter_gather.benchmark import s3_sqs_lambda_sync

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

VariantTest = namedtuple("VariantTest", ["maxcount", "variants"])

VARIANT_TESTS = [
    VariantTest(10_000, [s3_sqs_lambda_sync]),
    VariantTest(100_000, [s3_sqs_lambda_async, s3_sqs_lambda_dynamodb]),
    VariantTest(10_000_000, [s3_sqs_lambda_async_chunked, s3_notification_sqs_lambda]),
]


def run(start, end):
    count = start
    while count < end:
        for variant_test in [v for v in VARIANT_TESTS if v.maxcount > count]:
            for variant in variant_test.variants:
                logger.info(
                    "Benchmarking {variant} with {count} records.".format(variant=variant.__name__,
                                                                          count=count + 1))
                batch = {
                    "records": [{"itemNo": "item#{}".format(i), "price": randint(0, 100)} for i in range(count + 1)]}
                batch_id = str(uuid4())
                variant.run(batch_id, batch)
        count = count * 2


if __name__ == "__main__":
    if sys.version_info.major < 3 or (sys.version_info.major == 3 and sys.version_info.minor < 8):
        print("Python 3.8 or higher is required.")
        print("Sorry, your python is {}.{}.".format(sys.version_info.major, sys.version_info.minor))
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    run(int(sys.argv[1] if len(sys.argv) > 1 else 10), int(sys.argv[2] if len(sys.argv) > 2 else 100))
