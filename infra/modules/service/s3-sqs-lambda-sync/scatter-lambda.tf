resource "aws_iam_role" "scatter_lambda_role" {
  name = "${var.scope}scatter-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "scatter_lambda_policy_attachment" {
  role = aws_iam_role.scatter_lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

variable "scatter_lambda_source" {
  default = "../../../target/lambda.zip"
}

resource "aws_lambda_function" "scatter_lambda" {
  source_code_hash = filebase64sha256(var.scatter_lambda_source)
  filename = var.scatter_lambda_source
  function_name = "${var.scope}scatter"
  role = aws_iam_role.scatter_lambda_role.arn
  handler = "aws_scatter_gather/s3_sqs_lambda_sync/scatter/scatter_lambda.handle_event"
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
    aws_iam_role_policy_attachment.scatter_lambda_policy_attachment
  ]
}
