resource "aws_sqs_queue" "scatter_dlq" {
  name = "${var.scope}${var.variant}-scatter-dlq"
  message_retention_seconds = 86400
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}

resource "aws_sqs_queue" "scatter" {
  name = "${var.scope}${var.variant}-scatter-queue"
  delay_seconds = 0
  max_message_size = 2048
  message_retention_seconds = 86400
  receive_wait_time_seconds = 10
  visibility_timeout_seconds = 910
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.scatter_dlq.arn
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
        "ArnEquals": { "aws:SourceArn": "${aws_s3_bucket.input.arn}" }
      }
    }
  ]
}
POLICY

  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
