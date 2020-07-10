resource "aws_iam_role" "processed_lambda_role" {
  count = var.with_s3_notification_to_queue ? 1 : 0

  name = "${var.scope}${var.variant}-processed-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "processed_lambda_policy_attachment" {
  count = var.with_s3_notification_to_queue ? 1 : 0

  role = aws_iam_role.processed_lambda_role[0].name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

variable "processed_lambda_source" {
  default = "../../../target/lambda.zip"
}

resource "aws_lambda_function" "processed_lambda" {
  count = var.with_s3_notification_to_queue ? 1 : 0

  source_code_hash = filebase64sha256(var.processed_lambda_source)
  filename = var.processed_lambda_source
  function_name = "${var.scope}${var.variant}-processed"
  role = aws_iam_role.processed_lambda_role[0].arn
  handler = "${var.package_base}/processed/processed_lambda.handle_event"
  runtime = "python3.8"
  memory_size = 512
  timeout = 60
  environment {
    variables = {
      SCOPE = var.scope
      VARIANT = var.variant
      COMMITISH = var.commitish
      ENV = var.env
    }
  }
  tags = {
    variant = "${var.scope}${var.variant}"
  }
  depends_on = [
    aws_iam_role_policy_attachment.processed_lambda_policy_attachment[0]
  ]
}
