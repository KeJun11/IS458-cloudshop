locals {
  alarm_name_prefix = "${var.project}-${var.environment}"
  
  # Lambda function names for individual monitoring
  lambda_functions = [
    "${var.project}-${var.environment}-get-products",
    "${var.project}-${var.environment}-manage-cart",
    "${var.project}-${var.environment}-create-order",
    "${var.project}-${var.environment}-process-order",
    "${var.project}-${var.environment}-track-event",
    "${var.project}-${var.environment}-get-recommendations"
  ]
  
  # DynamoDB table names for individual monitoring
  dynamodb_tables = [
    "${var.project}-${var.environment}-products",
    "${var.project}-${var.environment}-carts",
    "${var.project}-${var.environment}-orders",
    "${var.project}-${var.environment}-user-interactions"
  ]
}

# CloudWatch Dashboard
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project}-${var.environment}-monitoring"

  dashboard_body = jsonencode({
    widgets = [
      # API Request Count
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApiGateway", "Count"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API Requests"
          period  = 300
        }
        width  = 12
        height = 6
        x      = 0
        y      = 0
      },

      # API Errors (5XX)
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/ApiGateway", "5xx", "Stage", "$default", "ApiId", var.api_gateway_id]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "API Error"
          period  = 300
        }
        width  = 12
        height = 6
        x      = 12
        y      = 0
      },

      # Lambda Invocations by Function
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", "test-dev-create-order", "Resource", "test-dev-create-order"],
            ["...", "test-dev-get-products", ".", "test-dev-get-products"],
            ["...", "test-dev-get-recommendations", ".", "test-dev-get-recommendations"],
            ["...", "test-dev-manage-cart", ".", "test-dev-manage-cart"],
            ["...", "test-dev-process-order", ".", "test-dev-process-order"],
            ["...", "test-dev-track-event", ".", "test-dev-track-event"]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.aws_region
          title   = "Lambda Invocations"
          period  = 300
        }
        width  = 12
        height = 6
        x      = 0
        y      = 6
      },

      # Lambda Errors by Function
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/Lambda", "Errors", "FunctionName", "test-dev-create-order", "Resource", "test-dev-create-order"],
            ["...", "test-dev-get-products", ".", "test-dev-get-products"],
            ["...", "test-dev-get-recommendations", ".", "test-dev-get-recommendations"],
            ["...", "test-dev-manage-cart", ".", "test-dev-manage-cart"],
            ["...", "test-dev-process-order", ".", "test-dev-process-order"],
            ["...", "test-dev-track-event", ".", "test-dev-track-event"]
          ]
          view    = "timeSeries"
          stacked = true
          region  = var.aws_region
          title   = "Lambda Errors"
          period  = 300
        }
        width  = 12
        height = 6
        x      = 12
        y      = 6
      },

      # DynamoDB Request Latency (by table and operation)
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "SuccessfulRequestLatency", "TableName", "test-dev-carts", "Operation", "GetItem"],
            ["...", "test-dev-products", ".", "."],
            ["...", "test-dev-user-interactions", ".", "Query"],
            ["...", "test-dev-products", ".", "Scan"],
            ["...", "test-dev-carts", ".", "UpdateItem"],
            ["...", "test-dev-orders", ".", "PutItem"],
            ["...", "UpdateItem"],
            ["...", "test-dev-carts", ".", "PutItem"],
            ["...", "Scan"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "DynamoDB Request Latency"
          period  = 300
        }
        width  = 12
        height = 6
        x      = 0
        y      = 12
      },

      # DynamoDB Capacity Units
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/DynamoDB", "ConsumedReadCapacityUnits", "TableName", "test-dev-carts"],
            [".", "ConsumedWriteCapacityUnits", ".", "test-dev-orders"],
            ["...", "test-dev-products"],
            [".", "ConsumedReadCapacityUnits", ".", "test-dev-user-interactions"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "DynamoDB"
          period  = 300
        }
        width  = 12
        height = 6
        x      = 12
        y      = 12
      },

      # SQS Queue Throughput
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/SQS", "NumberOfMessagesSent", "QueueName", var.sqs_queue_name],
            [".", "NumberOfMessagesDeleted", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "SQS"
          period  = 300
          stat    = "Average"
        }
        width  = 12
        height = 6
        x      = 0
        y      = 18
      },

      # SES Emails Sent
      {
        type = "metric"
        properties = {
          metrics = [
            ["AWS/SES", "Send"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Emails Sent"
          period  = 300
          stat    = "Average"
        }
        width  = 12
        height = 6
        x      = 12
        y      = 18
      }
    ]
  })
}

# CloudWatch Alarms

# API Gateway - High 5XX Error Rate
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "${local.alarm_name_prefix}-api-5xx-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "5xx"
  namespace           = "AWS/ApiGatewayV2"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "Triggers when API Gateway has more than 10 5XX errors in 5 minutes"
  treat_missing_data  = "notBreaching"

  dimensions = {
    ApiId = var.api_gateway_id
  }

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# Lambda - High Error Rate (aggregate across all functions)
resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
  alarm_name          = "${local.alarm_name_prefix}-lambda-high-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = 300
  statistic           = "Sum"
  threshold           = 5
  alarm_description   = "Triggers when Lambda functions have more than 5 errors in 5 minutes"
  treat_missing_data  = "notBreaching"

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# DynamoDB - System Errors
resource "aws_cloudwatch_metric_alarm" "dynamodb_system_errors" {
  alarm_name          = "${local.alarm_name_prefix}-dynamodb-system-errors"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "SystemErrors"
  namespace           = "AWS/DynamoDB"
  period              = 300
  statistic           = "Sum"
  threshold           = 0
  alarm_description   = "Triggers when DynamoDB has any system errors"
  treat_missing_data  = "notBreaching"

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# SQS - High Queue Depth
resource "aws_cloudwatch_metric_alarm" "sqs_high_queue_depth" {
  alarm_name          = "${local.alarm_name_prefix}-sqs-high-queue-depth"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Average"
  threshold           = 100
  alarm_description   = "Triggers when SQS queue has more than 100 messages waiting"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = var.sqs_queue_name
  }

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

# SQS - Messages in Dead Letter Queue
resource "aws_cloudwatch_metric_alarm" "sqs_dlq_messages" {
  alarm_name          = "${local.alarm_name_prefix}-sqs-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 60
  statistic           = "Average"
  threshold           = 0
  alarm_description   = "Triggers when there are failed messages in the Dead Letter Queue"
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = var.sqs_dlq_name
  }

  tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}
