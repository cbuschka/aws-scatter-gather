# Learnings

## s3 sqs lambda
* check lambda defaults for timeout and memory
* check sqs defaults for visibility, batch size, delay
* logging to cloud watch logs for measurements is inefficient
because of the sequence token gets invalidated when logging concurrently
into the same stream
* sync. io is very slow

## dynamodb
* dynamodb on demand scaling
```
[ERROR] ClientError: An error occurred (ThrottlingException) when calling the PutItem operation (reached max retries: 9): Throughput exceeds the current capacity of your table or index. DynamoDB is automatically scaling your table or index so please try again shortly. If exceptions persist, check if you have a hot key: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/bp-partition-key-design.html
Traceback (most recent call last):
  File "/var/task/aws_scatter_gather/util/async_util.py", line 7, in wrapper
    result = loop.run_until_complete(f(*args, **kwargs))
  File "/var/lang/lib/python3.8/asyncio/base_events.py", line 616, in run_until_complete
    return future.result()
  File "/var/task/aws_scatter_gather/s3_sqs_lambda_dynamodb/process/process_lambda.py", line 22, in handle_event
    await asyncio.gather(*[__process(chunk, dynamodb_resource, batch_writer) for chunk in chunks])
  File "/var/task/aws_scatter_gather/s3_sqs_lambda_dynamodb/process/process_lambda.py", line 44, in __process
    await batch_tasks_table.put_processed_batch_task(batch_id, index, request, response,
  File "/var/task/aws_scatter_gather/s3_sqs_lambda_dynamodb/resources/batch_tasks_table.py", line 42, in put_processed_batch_task
    await table.put_item(Item={"batchId": batch_id,
  File "/var/task/aioboto3/resources/factory.py", line 239, in do_action
    response = await action(self, *args, **kwargs)
  File "/var/task/aioboto3/resources/action.py", line 41, in __call__
    response = await getattr(parent.meta.client, operation_name)(**params)
  File "/var/task/aiobotocore/client.py", line 125, in _make_api_call
    raise error_class(parsed_response, operation_name)
```
