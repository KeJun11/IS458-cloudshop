variable "project_name" {
  description = "Short name of the project used for resource naming."
  type        = string
}

variable "env" {
  description = "Deployment environment (e.g., dev, staging, prod)."
  type        = string
}

variable "region" {
  description = "AWS region to deploy resources into."
  type        = string
  default     = "us-east-1"
}

variable "ses_sender_email" {
  description = "Email address to verify in SES for sending notifications."
  type        = string
  default     = ""
}

variable "stripe_secret_key" {
  description = "Stripe secret key for payment processing (get from Stripe Dashboard)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "stripe_webhook_secret" {
  description = "Stripe webhook signing secret for verifying webhook events"
  type        = string
  sensitive   = true
  default     = ""
}

variable "frontend_index_key" {
  description = "Default root object served by CloudFront."
  type        = string
  default     = "index.html"
}

variable "invoice_bucket_lifecycle_days" {
  description = "Number of days before expiring generated invoices."
  type        = number
  default     = 30
}

variable "additional_tags" {
  description = "Additional tags to merge into all resources."
  type        = map(string)
  default     = {}
}
