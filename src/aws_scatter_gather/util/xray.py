import os

from aws_xray_sdk.core import xray_recorder, patch_all


def is_xray_available():
    return os.environ.get("XRAY", None) is not None


def is_lambda():
    if os.environ.get('AWS_REGION') and not os.environ.get('CODEBUILD_AGENT_NAME'):
        return True
    return False


_xray_enabled = False


def enable_xray():
    global _xray_enabled
    if _xray_enabled:
        return

    if is_lambda() and is_xray_available():
        _xray_enabled = True
        xray_recorder.configure(
            sampling=False,
            context_missing='LOG_ERROR',
            daemon_address='127.0.0.1:3000'
        )
        patch_all()


def xray_profile(func):
    enable_xray()

    def wrapper(*args, **kwargs):
        with xray_recorder.capture(name=func.__name__):
            return func(*args, **kwargs)

    return wrapper


enable_xray()
