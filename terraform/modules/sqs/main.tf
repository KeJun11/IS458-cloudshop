locals {
  queue_name = "${var.queue_name}-${var.environment}"
  dlq_name   = "${var.queue_name}-dlq-${var.environment}"
  base_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_sqs_queue" "dlq" {
  name                        = local.dlq_name
  message_retention_seconds   = var.dlq_message_retention_seconds
  visibility_timeout_seconds  = var.visibility_timeout_seconds
  receive_wait_time_seconds   = var.receive_wait_time_seconds
  sqs_managed_sse_enabled     = true

  tags = merge(local.base_tags, var.tags)
}

resource "aws_sqs_queue" "this" {
  name                        = local.queue_name
  message_retention_seconds   = var.message_retention_seconds
  visibility_timeout_seconds  = var.visibility_timeout_seconds
  receive_wait_time_seconds   = var.receive_wait_time_seconds
  sqs_managed_sse_enabled     = true
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = var.max_receive_count
  })

  tags = merge(local.base_tags, var.tags)
}
