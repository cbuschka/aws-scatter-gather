resource "aws_s3_bucket" "work" {
  bucket = "${var.scope}${var.variant}-work"
  acl = "private"
  force_destroy = true
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
