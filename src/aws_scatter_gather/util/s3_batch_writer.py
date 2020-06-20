import asyncio


class S3BatchWriter(object):
    def __init__(self, s3_resource, flush_amount=100):
        self._flush_amount = flush_amount or 100
        self._requests_buffer = []
        self._s3_resource = s3_resource
        self._futures = []

    async def put(self, **kwargs):
        await self._add_request_and_process(kwargs)

    async def _add_request_and_process(self, request):
        self._requests_buffer.append(request)
        await self._flush_if_needed()

    async def _flush_if_needed(self):
        if len(self._requests_buffer) >= self._flush_amount:
            await self._flush()

    async def _flush(self):
        await asyncio.gather(*self._futures)
        requests_to_send = self._requests_buffer[:self._flush_amount]
        self._requests_buffer = self._requests_buffer[self._flush_amount:]
        self._futures = [self._put_object(**request) for request in requests_to_send]

    async def _put_object(self, Bucket=None, Key=None, **kwargs):
        s3_object = await self._s3_resource.Object(Bucket, Key)
        await s3_object.put(**kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        while len(self._requests_buffer) > 0:
            await self._flush()
        await asyncio.gather(*self._futures)
