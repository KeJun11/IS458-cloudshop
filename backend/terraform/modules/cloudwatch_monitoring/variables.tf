variable "project" {
  description = "Project name"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "aws_region" {
  description = "AWS region for CloudWatch dashboard"
  type        = string
}

variable "api_gateway_id" {
  description = "API Gateway ID for alarms"
  type        = string
}

variable "sqs_queue_name" {
  description = "SQS queue name for monitoring"
  type        = string
}

variable "sqs_dlq_name" {
  description = "SQS Dead Letter Queue name for monitoring"
  type        = string
}
