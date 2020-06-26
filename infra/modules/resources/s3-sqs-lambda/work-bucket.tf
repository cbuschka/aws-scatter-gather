resource "aws_s3_bucket" "work" {
  count = var.with_work_bucket ? 1 : 0

  bucket = "${var.scope}${var.variant}-work"
  acl = "private"
  force_destroy = true
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
