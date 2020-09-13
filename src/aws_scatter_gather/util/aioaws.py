import aioboto3
from aws_xray_sdk.core import patch_all
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core.async_context import AsyncContext

from aws_scatter_gather.util import env


class _Factory(object):
    def __configure(self, kwargs):
        if not env.is_aws() and not "endpoint_url" in kwargs:
            localstack_hostname = env.get_localstack_hostname()
            kwargs["endpoint_url"] = "http://{}:4566".format(localstack_hostname)
        if not "region_name" in kwargs:
            kwargs["region_name"] = env.get_region_name()

    def resource(self, *args, **kwargs):
        self.__configure(kwargs)
        return aioboto3.resource(*args, **kwargs)

    def client(self, *args, **kwargs):
        self.__configure(kwargs)
        return aioboto3.client(*args, **kwargs)


_factory = _Factory()


def set_factory(new_factory):
    global _factory
    _factory = new_factory


def resource(*args, **kwargs):
    return _factory.resource(*args, **kwargs)


def client(*args, **kwargs):
    return _factory.client(*args, **kwargs)


def enable_xray():
    xray_recorder.configure(
        sampling=False,
        context_missing='LOG_ERROR',
        daemon_address='127.0.0.1:3000',
        context=AsyncContext()
    )
    patch_all()
