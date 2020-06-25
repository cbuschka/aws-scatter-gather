resource "aws_dynamodb_table" "items_table" {
  name = "${var.scope}${var.variant}-items"
  billing_mode = "PAY_PER_REQUEST"
  stream_enabled = false
  hash_key = "itemNo"
  attribute {
    name = "itemNo"
    type = "S"
  }
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
