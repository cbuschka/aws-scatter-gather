resource "aws_iam_policy" "lambda_policy" {
  name_prefix = "${var.scope}${var.variant}-lambda-policy"
  policy = data.aws_iam_policy_document.lambda_policy_doc.json
}

data "aws_iam_policy_document" "lambda_policy_doc" {

  statement {
    sid = "dynamodbReadWrite"
    effect = "Allow"
    actions = [
      "dynamodb:*",
    ]
    resources = [
      "arn:aws:dynamodb:*:*:*"
    ]
  }

  statement {
    sid = "logsReadWrite"
    effect = "Allow"
    actions = [
      "logs:Create*",
      "logs:Put*",
      "logs:Describe*",
    ]
    resources = [
      "arn:aws:logs:*:*:*"
    ]
  }

  statement {
    sid = "s3ReadWrite"
    effect = "Allow"
    actions = [
      "s3:Get*",
      "s3:Put*",
      "s3:DeleteObject*",
      "s3:List*"
    ]
    resources = [
      "*"
    ]
  }

  statement {
    sid = "sqsReadWrite"
    effect = "Allow"
    actions = [
      "sqs:*",
    ]
    resources = [
      "arn:aws:sqs:*:*:*"
    ]
  }
}
