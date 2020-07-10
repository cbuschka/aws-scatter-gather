resource "aws_sqs_queue" "processed_dlq" {
  name = "${var.scope}${var.variant}-processed-dlq"
  message_retention_seconds = 86400

  tags = {
    variant = "${var.scope}${var.variant}"
  }
}

resource "aws_sqs_queue" "processed" {
  count = var.with_s3_notification_to_queue ? 1 : 0

  name = "${var.scope}${var.variant}-processed-queue"
  delay_seconds = 0
  max_message_size = 2048
  message_retention_seconds = 86400
  visibility_timeout_seconds = 910
  receive_wait_time_seconds = 10
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.processed_dlq.arn
    maxReceiveCount = 4
  })

  policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:*:*:*",
      "Condition": {
        "ArnEquals": { "aws:SourceArn": "arn:aws:s3:*:*:*" }
      }
    }
  ]
}
POLICY

  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
