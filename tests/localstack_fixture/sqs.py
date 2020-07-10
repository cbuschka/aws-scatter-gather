import aioboto3
from botocore.exceptions import ClientError

from .env import get_endpoint_url, get_region_name


class LocalSqs(object):
    def __init__(self, endpoint_url=None, region_name=None):
        self.endpoint_url = endpoint_url or get_endpoint_url()
        self.region_name = region_name or get_region_name()

    async def create(self, spec):
        await self.create_queues(config=spec, purge=True)

    async def destroy(self, spec):
        pass

    def new_resource(self):
        return aioboto3.resource('sqs', endpoint_url=self.endpoint_url, region_name=self.region_name)

    def new_client(self):
        return aioboto3.client('sqs', endpoint_url=self.endpoint_url, region_name=self.region_name)

    async def get_queue(self, queue_name):
        async with self.new_resource() as resource:
            queue = await resource.get_queue_by_name(QueueName=queue_name)
            return queue

    async def create_queues(self, config, purge=False):
        for queue_name, queue_config in config.items():
            try:
                async with self.new_resource() as resource:
                    queue = await resource.create_queue(QueueName=queue_name,
                                                        Attributes=queue_config.get("Attributes",
                                                                                    {'DelaySeconds': '5'}))
            except ClientError as e:
                if "AWS.SimpleQueueService.QueueNameExists" in e.response["Error"]["Code"]:
                    queue = await self.get_queue(queue_name)
                else:
                    raise

            if purge:
                async with self.new_client() as client:
                    await client.purge_queue(QueueUrl=queue.url)

            queue_config["url"] = queue.url

    async def receive_message(self, queue_name):
        async with self.new_resource() as resource:
            queue = await resource.get_queue_by_name(QueueName=queue_name)
            messages = await queue.receive_messages(MaxNumberOfMessages=1,
                                                    AttributeNames=["ALL"],
                                                    WaitTimeSeconds=10)
            if len(messages) == 0:
                return None
            message = messages[0]
            return await message.body
