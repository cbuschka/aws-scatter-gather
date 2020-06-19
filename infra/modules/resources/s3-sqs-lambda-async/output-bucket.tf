resource "aws_s3_bucket" "output" {
  bucket = "${var.scope}${var.variant}-output"
  acl = "private"
  force_destroy = true
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
