variable "bucket_name" {
  description = "Name of the S3 bucket to create."
  type        = string
}

variable "project" {
  description = "Project identifier used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, prod)."
  type        = string
}

variable "enable_versioning" {
  description = "Enable versioning on the bucket."
  type        = bool
  default     = true
}

variable "tags" {
  description = "Additional tags to apply to the bucket."
  type        = map(string)
  default     = {}
}
