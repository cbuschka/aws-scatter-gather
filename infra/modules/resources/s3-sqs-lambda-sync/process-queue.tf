resource "aws_sqs_queue" "process_dlq" {
  name = "${var.scope}${var.variant}-process-dlq"
  message_retention_seconds = 86400
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}

resource "aws_sqs_queue" "process" {
  name = "${var.scope}${var.variant}-process-queue"
  delay_seconds = 0
  max_message_size = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  visibility_timeout_seconds = 70
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.process_dlq.arn
    maxReceiveCount = 4
  })
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
