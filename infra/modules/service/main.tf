module "s3-notification-sqs-lambda" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-notification-sqs-lambda"
  package_base = "aws_scatter_gather/s3_notification_sqs_lambda"
  with_s3_notification_to_queue = true
}
