import os

import aioboto3


def __configure(kwargs):
    if not "endpoint_url" in kwargs:
        localstack_hostname = os.environ.get("LOCALSTACK_HOSTNAME", None)
        if localstack_hostname is not None:
            kwargs["endpoint_url"] = "http://{}:4566".format(localstack_hostname)
    if not "region_name" in kwargs:
        kwargs["region_name"] = "eu-central-1"


def resource(*args, **kwargs):
    __configure(kwargs)
    return aioboto3.resource(*args, **kwargs)


def client(*args, **kwargs):
    __configure(kwargs)
    return aioboto3.client(*args, **kwargs)
