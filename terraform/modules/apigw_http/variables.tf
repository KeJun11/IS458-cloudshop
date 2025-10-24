variable "project" {
  description = "Project identifier used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, prod)."
  type        = string
}

variable "stage_name" {
  description = "Stage name for the HTTP API."
  type        = string
  default     = "$default"
}

variable "routes" {
  description = "List of routes to configure for the API."
  type = list(object({
    route_key               = string
    lambda_arn              = string
    payload_format_version  = optional(string, "2.0")
    integration_method      = optional(string, "POST")
  }))
}

variable "cors_allowed_origins" {
  description = "CORS allowed origins."
  type        = list(string)
  default     = ["*"]
}

variable "cors_allowed_methods" {
  description = "CORS allowed methods."
  type        = list(string)
  default     = ["GET", "POST", "OPTIONS"]
}

variable "cors_allowed_headers" {
  description = "CORS allowed headers."
  type        = list(string)
  default     = ["*"]
}

variable "cors_expose_headers" {
  description = "CORS exposed headers."
  type        = list(string)
  default     = []
}

variable "cors_max_age" {
  description = "CORS max age in seconds."
  type        = number
  default     = 600
}

variable "default_throttling_burst_limit" {
  description = "Default burst limit for routes."
  type        = number
  default     = 50
}

variable "default_throttling_rate_limit" {
  description = "Default rate limit for routes."
  type        = number
  default     = 100
}

variable "integration_timeout_milliseconds" {
  description = "Timeout for Lambda proxy integrations."
  type        = number
  default     = 29000
}

variable "tags" {
  description = "Additional tags to apply to API resources."
  type        = map(string)
  default     = {}
}
