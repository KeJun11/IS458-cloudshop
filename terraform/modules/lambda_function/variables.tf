variable "project" {
  description = "Project identifier used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, prod)."
  type        = string
}

variable "function_name" {
  description = "Short name of the Lambda function (without project/env prefix)."
  type        = string
}

variable "description" {
  description = "Description of the Lambda function."
  type        = string
  default     = ""
}

variable "runtime" {
  description = "Runtime for the Lambda function."
  type        = string
  default     = "python3.12"
}

variable "handler" {
  description = "Handler for the Lambda function."
  type        = string
  default     = "app.lambda_handler"
}

variable "source_dir" {
  description = "Directory containing the Lambda source code."
  type        = string
}

variable "timeout" {
  description = "Timeout for the Lambda function in seconds."
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Memory size for the Lambda function in MB."
  type        = number
  default     = 256
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function."
  type        = map(string)
  default     = {}
}

variable "layers" {
  description = "List of Lambda layer ARNs."
  type        = list(string)
  default     = []
}

variable "policy_statements" {
  description = "Additional IAM policy statements for the Lambda role."
  type = list(object({
    sid       = optional(string)
    effect    = optional(string, "Allow")
    actions   = list(string)
    resources = list(string)
  }))
  default = []
}

variable "reserved_concurrent_executions" {
  description = "Reserved concurrency for the Lambda function."
  type        = number
  default     = null
}

variable "architectures" {
  description = "CPU architectures for the Lambda function."
  type        = list(string)
  default     = ["x86_64"]
}

variable "log_retention_in_days" {
  description = "CloudWatch Logs retention period."
  type        = number
  default     = 14
}

variable "tags" {
  description = "Additional tags to apply to resources."
  type        = map(string)
  default     = {}
}
