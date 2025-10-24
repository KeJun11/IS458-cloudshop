variable "project" {
  description = "Project identifier used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, prod)."
  type        = string
}

variable "origin_bucket_domain_name" {
  description = "Domain name of the S3 origin bucket."
  type        = string
}

variable "default_root_object" {
  description = "Default root object served by CloudFront."
  type        = string
  default     = "index.html"
}

variable "aliases" {
  description = "Optional aliases (CNAMEs) for the distribution."
  type        = list(string)
  default     = []
}

variable "acm_certificate_arn" {
  description = "Optional ACM certificate ARN for custom domains."
  type        = string
  default     = null
}

variable "enable_compression" {
  description = "Whether to enable response compression."
  type        = bool
  default     = true
}

variable "price_class" {
  description = "Price class for the CloudFront distribution."
  type        = string
  default     = "PriceClass_100"
}

variable "tags" {
  description = "Additional tags to apply to the distribution."
  type        = map(string)
  default     = {}
}
