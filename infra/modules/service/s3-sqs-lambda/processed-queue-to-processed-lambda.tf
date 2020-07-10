resource "aws_lambda_event_source_mapping" "processed_queue_to_processed_lambda" {
  count = var.with_s3_notification_to_queue ? 1 : 0

  event_source_arn = data.aws_sqs_queue.processed[0].arn
  function_name = aws_lambda_function.processed_lambda[0].arn
  batch_size = 10
}
