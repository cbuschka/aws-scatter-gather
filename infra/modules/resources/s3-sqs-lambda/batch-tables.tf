resource "aws_dynamodb_table" "batch_status" {
  count = var.with_batch_tables ? 1 : 0

  name = "${var.scope}${var.variant}-batch-status"
  billing_mode = "PAY_PER_REQUEST"
  stream_enabled = false
  hash_key = "batchId"
  attribute {
    name = "batchId"
    type = "S"
  }
  ttl {
    enabled = true
    attribute_name = "ttl"
  }
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}

resource "aws_dynamodb_table" "batch_tasks" {
  count = var.with_batch_tables ? 1 : 0

  name = "${var.scope}${var.variant}-batch-tasks"
  billing_mode = "PAY_PER_REQUEST"
  stream_enabled = false
  hash_key = "batchId"
  range_key = "index"
  ttl {
    enabled = true
    attribute_name = "ttl"
  }
  attribute {
    name = "batchId"
    type = "S"
  }
  attribute {
    name = "index"
    type = "N"
  }
  attribute {
    name = "isPending"
    type = "S"
  }
  local_secondary_index {
    name = "${var.scope}${var.variant}-pending-batch-tasks"
    projection_type = "KEYS_ONLY"
    range_key = "isPending"
  }
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}

