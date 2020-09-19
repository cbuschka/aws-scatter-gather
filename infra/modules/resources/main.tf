module "s3-notification-sqs-lambda" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-notification-sqs-lambda"
  with_s3_notification_to_queue = true
}
