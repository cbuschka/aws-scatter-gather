resource "aws_lambda_event_source_mapping" "process_queue_to_process_lambda" {
  event_source_arn = data.aws_sqs_queue.process.arn
  function_name = aws_lambda_function.process_lambda.arn
  batch_size = 10
}
