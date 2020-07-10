import os


def is_aws():
    env = os.environ.get("ENV", None)
    if env == "aws":
        return True
    return False


def get_localstack_hostname():
    return os.environ.get("LOCALSTACK_HOSTNAME", "localhost")


def get_region_name():
    return "eu-central-1"
