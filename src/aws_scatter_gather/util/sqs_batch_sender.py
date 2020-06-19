class SqsBatchSender(object):
    def __init__(self, sqs_client, queue_name=None, flush_amount=10):
        self._client = sqs_client
        self._queue_name = queue_name
        self._queue_url = None
        self._flush_amount = flush_amount or 10
        self._messages_buffer = []

    def send_message(self, message):
        self._add_message_and_process(message)

    def _add_message_and_process(self, message):
        self._messages_buffer.append(message)
        self._flush_if_needed()

    def _flush_if_needed(self):
        if len(self._messages_buffer) >= self._flush_amount:
            self._flush()

    def _flush(self):
        if self._queue_url is None:
            response = self._client.get_queue_url(QueueName=self._queue_name)
            self._queue_url = response["QueueUrl"]

        while len(self._messages_buffer) > 0:
            messages_to_send = self._messages_buffer[:self._flush_amount]
            self._messages_buffer = self._messages_buffer[self._flush_amount:]
            response = self._client.send_message_batch(QueueUrl=self._queue_url, Entries=messages_to_send)
            failed_ids = [entry["Id"] for entry in response.get("Failed", [])]
            failed_messages = [m for m in messages_to_send if m["Id"] in failed_ids]
            self._messages_buffer.extend(failed_messages)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._flush()


class AsyncSqsBatchSender(object):
    def __init__(self, sqs_client_factory, queue_name, flush_amount=10):
        self._client_factory = sqs_client_factory
        self._queue_name = queue_name
        self._queue_url = None
        self._flush_amount = flush_amount or 10
        self._messages_buffer = []

    async def send_message(self, message):
        await self._add_message_and_process(message)

    async def _add_message_and_process(self, message):
        self._messages_buffer.append(message)
        await self._flush_if_needed()

    async def _flush_if_needed(self):
        if len(self._messages_buffer) >= self._flush_amount:
            await self._flush()

    async def _flush(self):
        async with self._client_factory() as _client:
            if self._queue_url is None:
                response = await _client.get_queue_url(QueueName=self._queue_name)
                self._queue_url = response["QueueUrl"]

            messages_to_send = self._messages_buffer[:self._flush_amount]
            self._messages_buffer = self._messages_buffer[self._flush_amount:]
            response = await _client.send_message_batch(QueueUrl=self._queue_url, Entries=messages_to_send)
            failed_ids = [entry["Id"] for entry in response.get("Failed", [])]
            failed_messages = [m for m in messages_to_send if m["Id"] in failed_ids]
            self._messages_buffer.extend(failed_messages)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        while len(self._messages_buffer) > 0:
            await self._flush()
