resource "aws_lambda_event_source_mapping" "gather_queue_to_gather_lambda" {
  event_source_arn = data.aws_sqs_queue.gather.arn
  function_name = aws_lambda_function.gather_lambda.arn
  batch_size = 1
}
