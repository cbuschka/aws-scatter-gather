# Learnings

## s3 sqs lambda
* check lambda defaults for timeout and memory
* check sqs defaults for visibility, batch size, delay
* logging to cloud watch logs for measurements is inefficient
because of the sequence token gets invalidated when logging concurrently
into the same stream
* sync. io is very slow
