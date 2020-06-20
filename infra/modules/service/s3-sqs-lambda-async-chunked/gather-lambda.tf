resource "aws_iam_role" "gather_lambda_role" {
  name = "${var.scope}${var.variant}-gather-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "gather_lambda_policy_attachment" {
  role = aws_iam_role.gather_lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

variable "gather_lambda_source" {
  default = "../../../target/lambda.zip"
}

resource "aws_lambda_function" "gather_lambda" {
  source_code_hash = filebase64sha256(var.gather_lambda_source)
  filename = var.gather_lambda_source
  function_name = "${var.scope}${var.variant}-gather"
  role = aws_iam_role.gather_lambda_role.arn
  handler = "aws_scatter_gather/s3_sqs_lambda_async_chunked/gather/gather_lambda.handle_event"
  runtime = "python3.8"
  memory_size = 3008
  timeout = 900
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
    aws_iam_role_policy_attachment.gather_lambda_policy_attachment
  ]
}
