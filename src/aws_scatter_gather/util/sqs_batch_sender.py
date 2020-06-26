from aws_scatter_gather.util import logger


class SqsBatchSender(object):
    def __init__(self, sqs_client, queue_name=None, flush_amount=10, retry_count=10):
        self._client = sqs_client
        self._queue_name = queue_name
        self._queue_url = None
        self._flush_amount = flush_amount or 10
        self._messages_buffer = []
        self._retry_count = retry_count

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

        logger.info("Flushing buffer of %d message(s)...", len(self._messages_buffer))
        messages_to_send = self._messages_buffer[:self._flush_amount]
        self._messages_buffer = self._messages_buffer[self._flush_amount:]
        response = self._client.send_message_batch(QueueUrl=self._queue_url, Entries=messages_to_send)
        retryable_ids = [entry["Id"] for entry in response.get("Failed", []) if entry["SenderFault"] is False]
        if len(retryable_ids) > 0:
            logger.info("%d message(s) retryable... putting back.", len(retryable_ids))
            retryable_messages = [m for m in messages_to_send if m["Id"] in retryable_ids]
            self._messages_buffer.extend(retryable_messages)

        sender_faults = [entry for entry in response.get("Failed", []) if entry["SenderFault"] is True]
        if len(sender_faults) > 0:
            sender_fault = sender_faults[0]
            raise ValueError(
                "Sending message {} failed: code={}, message={}".format(sender_fault["Id"], sender_fault["Code"],
                                                                        sender_fault["Message"]))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        for _ in range(self._retry_count):
            if len(self._messages_buffer) == 0:
                return
            self._flush()

        if len(self._messages_buffer) > 0:
            raise ValueError("Sending messages failed.")


class AsyncSqsBatchSender(object):
    def __init__(self, sqs_client, queue_name, flush_amount=10, retry_count=10):
        self._sqs_client = sqs_client
        self._queue_name = queue_name
        self._queue_url = None
        self._flush_amount = flush_amount or 10
        self._messages_buffer = []
        self._retry_count = retry_count

    async def send_message(self, message):
        await self._add_message_and_process(message)

    async def _add_message_and_process(self, message):
        self._messages_buffer.append(message)
        await self._flush_if_needed()

    async def _flush_if_needed(self):
        if len(self._messages_buffer) >= self._flush_amount:
            await self._flush()

    async def _flush(self):
        if self._queue_url is None:
            response = await self._sqs_client.get_queue_url(QueueName=self._queue_name)
            self._queue_url = response["QueueUrl"]

        logger.info("Flushing buffer of %d message(s)...", len(self._messages_buffer))
        messages_to_send = self._messages_buffer[:self._flush_amount]
        self._messages_buffer = self._messages_buffer[self._flush_amount:]
        response = await self._sqs_client.send_message_batch(QueueUrl=self._queue_url, Entries=messages_to_send)
        retryable_ids = [entry["Id"] for entry in response.get("Failed", []) if entry["SenderFault"] is False]
        if len(retryable_ids) > 0:
            logger.info("%d message(s) retryable... putting back.", len(retryable_ids))
            retryable_messages = [m for m in messages_to_send if m["Id"] in retryable_ids]
            self._messages_buffer.extend(retryable_messages)

        sender_faults = [entry for entry in response.get("Failed", []) if entry["SenderFault"] is True]
        if len(sender_faults) > 0:
            sender_fault = sender_faults[0]
            raise ValueError(
                "Sending message {} failed: code={}, message={}".format(sender_fault["Id"], sender_fault["Code"],
                                                                            sender_fault["Message"]))

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, tb):
        for _ in range(self._retry_count):
            if len(self._messages_buffer) == 0:
                return
            await self._flush()

        if len(self._messages_buffer) > 0:
            raise ValueError("Sending messages failed.")
