module "s3-sqs-lambda-sync" {
  source = "./s3-sqs-lambda-sync"
  scope = var.scope
  commitish = var.commitish
  env = var.env
}

module "s3-sqs-lambda-async" {
  source = "./s3-sqs-lambda-async"
  scope = var.scope
  commitish = var.commitish
  env = var.env
}

module "s3-sqs-lambda-async-chunked" {
  source = "./s3-sqs-lambda-async-chunked"
  scope = var.scope
  commitish = var.commitish
  env = var.env
}
