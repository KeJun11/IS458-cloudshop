output "api_id" {
  description = "ID of the HTTP API."
  value       = aws_apigatewayv2_api.this.id
}

output "api_endpoint" {
  description = "Base invoke URL for the HTTP API."
  value       = aws_apigatewayv2_api.this.api_endpoint
}

output "execution_arn" {
  description = "Execution ARN for the HTTP API."
  value       = aws_apigatewayv2_api.this.execution_arn
}

output "stage_name" {
  description = "Name of the deployed stage."
  value       = aws_apigatewayv2_stage.this.name
}
