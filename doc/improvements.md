# Improvements

## s3 sqs lambda
* enable s3 versions, archive input on delete event
* enable s3 version, test batch completion on delete event
* expire s3 entries
* periodically scan for unprocessed input
* periodically scan for completed batch
* use async io (DONE)
* create chunks of batches (DONE)
* pros/cons
* watchdog messages
* introduce real operations into process lambda
* time scatter, process, gather seperately (DONE)

## More variants
* s3 sqs lambda dynamodb
* s3 sqs lambda stepfunctions
