resource "aws_iam_role" "process_lambda_role" {
  name = "${var.scope}${var.variant}-process-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy_doc.json
}

resource "aws_iam_role_policy_attachment" "process_lambda_policy_attachment" {
  role = aws_iam_role.process_lambda_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

variable "process_lambda_source" {
  default = "../../../target/lambda.zip"
}

resource "aws_lambda_function" "process_lambda" {
  source_code_hash = filebase64sha256(var.process_lambda_source)
  filename = var.process_lambda_source
  function_name = "${var.scope}${var.variant}-process"
  role = aws_iam_role.process_lambda_role.arn
  handler = "${var.package_base}/process/process_lambda.handle_event"
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
    aws_iam_role_policy_attachment.process_lambda_policy_attachment
  ]
}
