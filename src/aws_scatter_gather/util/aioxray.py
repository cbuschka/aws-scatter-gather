import os

from aws_xray_sdk.core import xray_recorder, patch_all
from aws_xray_sdk.core.async_context import AsyncContext


def is_xray_available():
    return os.environ.get("XRAY", None) is not None


def is_lambda():
    if os.environ.get('AWS_REGION') and not os.environ.get('CODEBUILD_AGENT_NAME'):
        return True
    return False


# if is_lambda() and is_xray_available():
xray_recorder.configure(
    sampling=False,
    context_missing='LOG_ERROR',
    daemon_address='127.0.0.1:3000',
    context=AsyncContext()
)
patch_all()


def xray_profile(func):
    async def wrapper(*args, **kwargs):
        async with xray_recorder.in_segment_async(name=func.__name__):
            return await func(*args, **kwargs)

    return wrapper
