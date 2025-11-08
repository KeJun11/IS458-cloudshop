output "dashboard_name" {
  description = "Name of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_name
}

output "dashboard_arn" {
  description = "ARN of the CloudWatch dashboard"
  value       = aws_cloudwatch_dashboard.main.dashboard_arn
}

output "alarm_arns" {
  description = "ARNs of all CloudWatch alarms"
  value = {
    api_5xx_errors          = aws_cloudwatch_metric_alarm.api_5xx_errors.arn
    lambda_errors           = aws_cloudwatch_metric_alarm.lambda_errors.arn
    dynamodb_system_errors  = aws_cloudwatch_metric_alarm.dynamodb_system_errors.arn
    sqs_high_queue_depth    = aws_cloudwatch_metric_alarm.sqs_high_queue_depth.arn
    sqs_dlq_messages        = aws_cloudwatch_metric_alarm.sqs_dlq_messages.arn
  }
}
