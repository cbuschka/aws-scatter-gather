data "aws_s3_bucket" "input" {
  bucket = "${var.scope}${var.variant}-input"
}
data "aws_s3_bucket" "output" {
  bucket = "${var.scope}${var.variant}-output"
}
data "aws_s3_bucket" "work" {
  count = var.with_work_bucket ? 1 : 0

  bucket = "${var.scope}${var.variant}-work"
}
data "aws_sqs_queue" "gather" {
  name = "${var.scope}${var.variant}-gather-queue.fifo"
}
data "aws_sqs_queue" "process_dlq" {
  name = "${var.scope}${var.variant}-process-dlq"
}
data "aws_sqs_queue" "process" {
  name = "${var.scope}${var.variant}-process-queue"
}
data "aws_sqs_queue" "scatter" {
  name = "${var.scope}${var.variant}-scatter-queue"
}
data "aws_dynamodb_table" "items_table" {
  name = "${var.scope}${var.variant}-items"
}
data "aws_dynamodb_table" "batch_status" {
  count = var.with_batch_tables ? 1 : 0

  name = "${var.scope}${var.variant}-batch-status"
}
data "aws_dynamodb_table" "batch_tasks" {
  count = var.with_batch_tables ? 1 : 0

  name = "${var.scope}${var.variant}-batch-tasks"
}

