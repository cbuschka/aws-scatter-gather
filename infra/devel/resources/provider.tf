provider "aws" {
  region = "eu-central-1"
  version = "~> 2.66"
  access_key = "123"
  secret_key = "xyz"
  skip_credentials_validation = true
  skip_requesting_account_id = true
  skip_metadata_api_check = true
  s3_force_path_style = true
  endpoints {
    apigateway = "http://localhost:4566"
    cloudformation = "http://localhost:4566"
    cloudwatchlogs = "http://localhost:4566"
    cloudwatch = "http://localhost:4566"
    cloudwatchevents = "http://localhost:4566"
    dynamodb = "http://localhost:4566"
    es = "http://localhost:4566"
    firehose = "http://localhost:4566"
    iam = "http://localhost:4566"
    kinesis = "http://localhost:4566"
    lambda = "http://localhost:4566"
    route53 = "http://localhost:4566"
    redshift = "http://localhost:4566"
    s3 = "http://localhost:4566"
    secretsmanager = "http://localhost:4566"
    ses = "http://localhost:4566"
    sns = "http://localhost:4566"
    sqs = "http://localhost:4566"
    ssm = "http://localhost:4566"
    stepfunctions = "http://localhost:4566"
    sts = "http://localhost:4566"
  }
}
