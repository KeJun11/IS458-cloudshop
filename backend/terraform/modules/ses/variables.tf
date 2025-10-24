variable "project" {
  description = "Project identifier used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, prod)."
  type        = string
}

variable "ses_sender_email" {
  description = "SES sender email address to verify."
  type        = string
}
