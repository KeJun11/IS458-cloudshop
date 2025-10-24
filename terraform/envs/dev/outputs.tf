output "cloudfront_domain" {
  description = "CloudFront domain for the frontend."
  value       = module.cloudfront.distribution_domain_name
}

output "static_site_bucket" {
  description = "Name of the S3 bucket hosting frontend assets."
  value       = module.static_site_bucket.bucket_id
}

output "invoice_bucket" {
  description = "Name of the invoice storage bucket."
  value       = aws_s3_bucket.invoice.bucket
}

output "api_endpoint" {
  description = "Base invoke URL for the HTTP API."
  value       = module.http_api.api_endpoint
}

output "order_queue_url" {
  description = "URL of the order processing queue."
  value       = module.order_queue.queue_url
}

output "dynamodb_tables" {
  description = "Map of logical table keys to names."
  value       = module.dynamodb.table_names
}

output "ses_identity" {
  description = "SES email identity if configured."
  value       = local.ses_identity_arn
  sensitive   = false
}
