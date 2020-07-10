import os


def get_endpoint_url():
    return "http://{}:4566".format(os.environ.get("LOCALSTACK_HOST", "localhost"))

def get_region_name():
    return "eu-central-1"
