resource "aws_sqs_queue" "gather_dlq" {
  name = "${var.scope}${var.variant}-gather-dlq.fifo"
  message_retention_seconds = 86400
  fifo_queue = true

  tags = {
    variant = "s3_sqs_lambda_sync"
  }
}

resource "aws_sqs_queue" "gather" {
  name = "${var.scope}${var.variant}-gather-queue.fifo"
  delay_seconds = 0
  fifo_queue = true
  max_message_size = 2048
  message_retention_seconds = 86400
  visibility_timeout_seconds = 910
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.gather_dlq.arn
    maxReceiveCount = 4
  })
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
