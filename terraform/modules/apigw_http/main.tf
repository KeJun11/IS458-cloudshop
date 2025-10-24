locals {
  routes = { for route in var.routes : route.route_key => route }
  tags = merge(
    {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags,
  )
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_apigatewayv2_api" "this" {
  name          = "${var.project}-${var.environment}-http-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_credentials = false
    allow_headers     = var.cors_allowed_headers
    allow_methods     = var.cors_allowed_methods
    allow_origins     = var.cors_allowed_origins
    expose_headers    = var.cors_expose_headers
    max_age           = var.cors_max_age
  }

  tags = local.tags
}

resource "aws_apigatewayv2_stage" "this" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = var.stage_name
  auto_deploy = true

  default_route_settings {
    throttling_burst_limit = var.default_throttling_burst_limit
    throttling_rate_limit  = var.default_throttling_rate_limit
  }

  tags = local.tags
}

resource "aws_apigatewayv2_integration" "lambda" {
  for_each = local.routes

  api_id           = aws_apigatewayv2_api.this.id
  integration_type = "AWS_PROXY"
  integration_uri  = each.value.lambda_arn
  integration_method = each.value.integration_method
  payload_format_version = each.value.payload_format_version
  timeout_milliseconds   = var.integration_timeout_milliseconds
}

resource "aws_apigatewayv2_route" "this" {
  for_each = local.routes

  api_id    = aws_apigatewayv2_api.this.id
  route_key = each.key
  target    = "integrations/${aws_apigatewayv2_integration.lambda[each.key].id}"
}

resource "aws_lambda_permission" "apigw" {
  for_each = local.routes

  # AWS Lambda statement_id must contain only letters, numbers, underscores, or dashes.
  # Route keys like "GET /products" include spaces and slashes, so sanitize them.
  statement_id  = "AllowExecutionFromAPIGateway-${replace(replace(each.key, " ", "_"), "/", "_")}"
  action        = "lambda:InvokeFunction"
  function_name = each.value.lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.this.execution_arn}/*"
}

