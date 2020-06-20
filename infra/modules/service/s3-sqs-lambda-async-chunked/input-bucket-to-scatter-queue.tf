resource "aws_s3_bucket_notification" "input_bucket_to_scatter_queue" {
  bucket = data.aws_s3_bucket.input.id
  queue {
    queue_arn = data.aws_sqs_queue.scatter.arn
    events = [
      "s3:ObjectCreated:*"
    ]
  }
}
