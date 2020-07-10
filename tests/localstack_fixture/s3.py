import aioboto3
from botocore.exceptions import ClientError

from .env import get_endpoint_url, get_region_name


class LocalS3(object):
    def __init__(self, endpoint_url=None, region_name=None):
        self.endpoint_url = endpoint_url or get_endpoint_url()
        self.region_name = region_name or get_region_name()

    def new_client(self):
        return aioboto3.client('s3', endpoint_url=self.endpoint_url, region_name=self.region_name)

    def new_resource(self):
        return aioboto3.resource('s3', endpoint_url=self.endpoint_url, region_name=self.region_name)

    async def create(self, spec):
        await self.create_buckets(config=spec.get("buckets", {}), recreate=True)

    async def destroy(self, spec):
        pass

    async def list_bucket_names(self):
        async with self.new_client() as client:
            response = await client.list_buckets()
            return [b["Name"] for b in response["Buckets"]]

    async def create_buckets(self, config, recreate=True, CreateBucketConfiguration=None):
        bucket_names = await self.list_bucket_names()
        for key, bucket_config in config.items():
            bucket_name = bucket_config.get("BucketName", key)
            bucket_exists = bucket_name in bucket_names
            if bucket_exists and recreate:
                await self.delete_bucket(bucket_name)
                bucket_exists = False

            if not bucket_exists:
                try:
                    kwargs = {
                        "ACL": bucket_config.get("ACL", "private"),
                        "Bucket": bucket_name
                    }
                    if CreateBucketConfiguration is not None:
                        kwargs["CreateBucketConfiguration"] = CreateBucketConfiguration

                    async with self.new_client() as client:
                        await client.create_bucket(**kwargs)

                    objects = bucket_config.get("Objects", [])
                    if len(objects) > 0:
                        await self.create_objects(bucket_name, objects)

                except ClientError:
                    raise

    async def create_objects(self, bucket_name, objects):
        for key, object in objects.items():
            object_key = object.get("Key", key)
            data = object["Data"]
            await self.put_file(bucket_name, object_key, data)

    async def put_file(self, bucket_name, object_key, data):
        async with self.new_resource() as resource:
            object = await resource.Object(bucket_name, object_key)
            await object.put(ACL="public-read-write", Body=data)

    async def delete_bucket(self, bucket_name, delete_keys=True):
        if delete_keys:
            keys = await self.list_object_keys(bucket_name)
            delete_objects = [{"Key": key} for key in keys]
            if len(delete_objects) > 0:
                async with self.new_client() as client:
                    await client.delete_objects(Bucket=bucket_name, Delete={"Objects": delete_objects})
        async with self.new_client() as client:
            await client.delete_bucket(Bucket=bucket_name)

    async def list_object_keys(self, bucket_name):
        async with self.new_client() as client:
            response = await client.list_objects(Bucket=bucket_name)
            objects = response.get("Contents", [])
            keys = [o["Key"] for o in objects]
            return keys

    async def exists_object(self, bucket_name, key):
        return key in await self.list_object_keys(bucket_name)

    async def assert_object_exists(self, bucket_name, key):
        if not await self.exists_object(bucket_name, key):
            raise ValueError("Object {} does not exist in {}.".format(key, bucket_name))

    async def assert_object_not_exists(self, bucket_name, key):
        if await self.exists_object(bucket_name, key):
            raise ValueError("Object {} does not exist in {}.".format(key, bucket_name))
