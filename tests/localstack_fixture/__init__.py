from .dynamodb import LocalDynamodb
from .localstack import Localstack
from .s3 import LocalS3
from .ses import LocalSes
from .sqs import LocalSqs

localstack = Localstack()
dynamodb = localstack.dynamodb
sqs = localstack.sqs
s3 = localstack.s3
ses = localstack.ses


async def create(spec=None):
    await localstack.create(spec)


async def destroy(spec=None):
    await localstack.destroy(spec)
