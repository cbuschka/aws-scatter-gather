resource "aws_s3_bucket_notification" "work_bucket_pending_to_process_queue" {
  count = var.with_s3_notification_to_queue ? 1 : 0

  bucket = data.aws_s3_bucket.work[0].id
  queue {
    queue_arn = data.aws_sqs_queue.process.arn
    events = [
      "s3:ObjectCreated:*"
    ]
    filter_suffix = ".pending.json"
  }

  queue {
    queue_arn = data.aws_sqs_queue.processed[0].arn
    events = [
      "s3:ObjectCreated:*"
    ]
    filter_suffix = ".done.json"
  }
}
