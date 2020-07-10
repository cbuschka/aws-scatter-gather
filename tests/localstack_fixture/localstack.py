import asyncio

import aioboto3

from .dynamodb import LocalDynamodb
from .env import get_endpoint_url, get_region_name
from .s3 import LocalS3
from .ses import LocalSes
from .sqs import LocalSqs


class Localstack(object):
    def __init__(self, endpoint_url=None, region_name=None):
        self.endpoint_url = endpoint_url or get_endpoint_url()
        self.region_name = region_name or get_region_name()
        self.dynamodb = LocalDynamodb(endpoint_url=endpoint_url, region_name=region_name)
        self.sqs = LocalSqs(endpoint_url=endpoint_url, region_name=region_name)
        self.s3 = LocalS3(endpoint_url=endpoint_url, region_name=region_name)
        self.ses = LocalSes(endpoint_url=endpoint_url, region_name=region_name)

    async def create(self, spec):
        futures = []
        for service_name in ["s3", "sqs", "dynamodb", "ses"]:
            service_spec = spec.get(service_name, None)
            if service_spec is not None:
                service = getattr(self, service_name, None)
                futures.append(service.create(service_spec))
        await asyncio.gather(*futures)
        return spec

    async def destroy(self, spec):
        futures = []
        for service_name in ["s3", "sqs", "dynamodb", "ses"]:
            service_spec = spec.get(service_name, None)
            service = getattr(self, service_name, None)
            futures.append(service.destroy(service_spec))
        await asyncio.gather(*futures)

    def resource(self, *args, **kwargs):
        kwargs["endpoint_url"] = kwargs.get("endpoint_url", self.endpoint_url)
        kwargs["region_name"] = kwargs.get("region_name", self.region_name)
        return aioboto3.resource(*args, **kwargs)

    def client(self, *args, **kwargs):
        kwargs["endpoint_url"] = kwargs.get("endpoint_url", self.endpoint_url)
        kwargs["region_name"] = kwargs.get("region_name", self.region_name)
        return aioboto3.client(*args, **kwargs)
