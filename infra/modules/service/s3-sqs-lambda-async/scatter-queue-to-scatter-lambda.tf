resource "aws_lambda_event_source_mapping" "scatter_queue_to_scatter_lambda" {
  event_source_arn = data.aws_sqs_queue.scatter.arn
  function_name = aws_lambda_function.scatter_lambda.arn
  batch_size = 1
}
