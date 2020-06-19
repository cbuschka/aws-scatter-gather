class SqsBatchSender(object):
    def __init__(self, sqs_client, queue_url=None, queue_name=None, flush_amount=10):
        if queue_name is None and queue_url is None:
            raise ValueError("Either queue_name or queue_url is required.")
        if queue_name is not None and queue_url is None:
            response = sqs_client.get_queue_url(QueueName=queue_name)
            queue_url = response["QueueUrl"]

        self._client = sqs_client
        self._queue_url = queue_url
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
        while len(self._messages_buffer) > 0:
            messages_to_send = self._messages_buffer[:self._flush_amount]
            self._messages_buffer = self._messages_buffer[self._flush_amount:]
            self._client.send_message_batch(QueueUrl=self._queue_url, Entries=messages_to_send)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self._flush()
