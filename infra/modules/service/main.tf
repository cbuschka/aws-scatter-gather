module "s3-sqs-lambda-sync" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-sync"
  package_base = "aws_scatter_gather/s3_sqs_lambda_sync"
}

module "s3-sqs-lambda-async" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-async"
  package_base = "aws_scatter_gather/s3_sqs_lambda_async"
}

module "s3-sqs-lambda-async-chunked" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-async-chunked"
  package_base = "aws_scatter_gather/s3_sqs_lambda_async_chunked"
}

module "s3-sqs-lambda-dynamodb" {
  source = "./s3-sqs-lambda"
  scope = var.scope
  commitish = var.commitish
  env = var.env
  variant = "s3-sqs-lambda-dynamodb"
  package_base = "aws_scatter_gather/s3_sqs_lambda_dynamodb"
  with_batch_tables = true
  with_work_bucket = false
}
