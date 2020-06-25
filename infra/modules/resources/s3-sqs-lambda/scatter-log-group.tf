resource "aws_cloudwatch_log_group" "scatter_log_group" {
  name = "/aws/lambda/${var.scope}${var.variant}-scatter"
  retention_in_days = 1
  tags = {
    variant = "${var.scope}${var.variant}"
  }
}
