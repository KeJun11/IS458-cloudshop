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
