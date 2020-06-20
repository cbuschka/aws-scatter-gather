import logging
from uuid import uuid4

from aws_scatter_gather.benchmark import s3_sqs_lambda_async
#from aws_scatter_gather.benchmark import s3_sqs_lambda_sync

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

RECORD_COUNT = 1001


def run():
    batch = {"records": [{"index": i, "info": "request#{}".format(i)} for i in range(RECORD_COUNT)]}
    batch_id = str(uuid4())
    #s3_sqs_lambda_sync.run(batch_id, batch)

    batch_id = str(uuid4())
    s3_sqs_lambda_async.run(batch_id, batch)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
