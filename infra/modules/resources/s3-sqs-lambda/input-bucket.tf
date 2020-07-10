resource "aws_s3_bucket" "input" {
  bucket = "${var.scope}${var.variant}-input"
  acl = "private"
  force_destroy = true
  versioning {
    enabled = true
  }
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
