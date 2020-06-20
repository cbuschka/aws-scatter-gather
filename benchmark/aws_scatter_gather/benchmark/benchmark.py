import logging
from collections import namedtuple
from uuid import uuid4

from aws_scatter_gather.benchmark import s3_sqs_lambda_async
from aws_scatter_gather.benchmark import s3_sqs_lambda_sync
from aws_scatter_gather.util.trace import trace

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

Test = namedtuple("Test", ["count", "variants"])
TESTS = [
    Test(11, [s3_sqs_lambda_sync, s3_sqs_lambda_async]),
    Test(101, [s3_sqs_lambda_sync, s3_sqs_lambda_async]),
    Test(1001, [s3_sqs_lambda_sync, s3_sqs_lambda_async])
    # Test(10001, [s3_sqs_lambda_async]),
    # Test(100001, [s3_sqs_lambda_async])
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
    logging.basicConfig(level=logging.INFO)
    run()
