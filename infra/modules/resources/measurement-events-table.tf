resource "aws_dynamodb_table" "measurement_events_table" {
  name = "${var.scope}measurement-events"
  billing_mode = "PAY_PER_REQUEST"
  stream_enabled = false
  hash_key = "uuid"
  ttl {
    enabled = true
    attribute_name = "ttl"
  }
  attribute {
    name = "uuid"
    type = "S"
  }
}

