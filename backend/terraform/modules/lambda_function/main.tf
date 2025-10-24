locals {
  tags = merge(
    {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
      Lambda      = var.function_name
    },
    var.tags,
  )

  policy_statements = concat(
    [
      {
        sid     = "AllowLogging"
        effect  = "Allow"
        actions = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
        ]
        resources = [
          "arn:aws:logs:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:*",
        ]
      }
    ],
    var.policy_statements,
  )
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

data "aws_iam_policy_document" "assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "inline" {
  dynamic "statement" {
    for_each = local.policy_statements
    content {
      sid       = try(statement.value.sid, null)
      effect    = try(statement.value.effect, "Allow")
      actions   = statement.value.actions
      resources = statement.value.resources
    }
  }
}

resource "aws_iam_role" "this" {
  name               = "${var.project}-${var.environment}-${var.function_name}-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
  tags               = local.tags
}

resource "aws_iam_role_policy" "this" {
  name   = "${var.project}-${var.environment}-${var.function_name}-policy"
  role   = aws_iam_role.this.id
  policy = data.aws_iam_policy_document.inline.json
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${aws_lambda_function.this.function_name}"
  retention_in_days = var.log_retention_in_days
  tags              = local.tags
}

data "archive_file" "this" {
  type        = "zip"
  source_dir  = var.source_dir
  output_path = "${path.module}/tmp/${var.function_name}.zip"
}

resource "aws_lambda_function" "this" {
  function_name = "${var.project}-${var.environment}-${var.function_name}"
  description   = var.description
  role          = aws_iam_role.this.arn
  handler       = var.handler
  runtime       = var.runtime
  memory_size   = var.memory_size
  timeout       = var.timeout
  filename      = data.archive_file.this.output_path
  source_code_hash = data.archive_file.this.output_base64sha256
  architectures       = var.architectures
  layers              = var.layers
  publish             = false
  package_type        = "Zip"
  reserved_concurrent_executions = var.reserved_concurrent_executions

  environment {
    variables = var.environment_variables
  }

  depends_on = [
    aws_iam_role_policy.this,
  ]

  tags = local.tags
}
