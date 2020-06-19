module "s3-sqs-lambda-sync" {
  source = "./s3-sqs-lambda-sync"
  scope = var.scope
  commitish = var.commitish
  env = var.env
}
