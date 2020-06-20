import logging
from uuid import uuid4

from aws_scatter_gather.benchmark import s3_sqs_lambda_async
from aws_scatter_gather.benchmark import s3_sqs_lambda_sync
from aws_scatter_gather.util.trace import trace

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def run():
    for count in [11, 101, 1001]:
        logger.info("Benchmarking with {count} records.".format(count=count))
        batch = {"records": [{"index": i, "info": "request#{}".format(i)} for i in range(count)]}

        with trace("Variant s3_sqs_lambda_sync..."):
            batch_id = str(uuid4())
            s3_sqs_lambda_sync.run(batch_id, batch)

        with trace("Variant s3_sqs_lambda_async..."):
            batch_id = str(uuid4())
            s3_sqs_lambda_async.run(batch_id, batch)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
