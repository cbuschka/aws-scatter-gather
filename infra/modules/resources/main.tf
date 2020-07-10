module "s3-sqs-lambda-sync" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-sync"
}

module "s3-sqs-lambda-async" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-async"
}

module "s3-sqs-lambda-async-chunked" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-async-chunked"
}

module "s3-sqs-lambda-dynamodb" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-dynamodb"
  with_batch_tables = true
  with_work_bucket = false
}

module "s3-notification-sqs-lambda" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-notification-sqs-lambda"
  with_s3_notification_to_queue = true
}
