variable "project" {
  description = "Project identifier used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, prod)."
  type        = string
}

variable "queue_name" {
  description = "Base name for the primary queue."
  type        = string
  default     = "order-processing"
}

variable "visibility_timeout_seconds" {
  description = "Visibility timeout for the primary and DLQ queues."
  type        = number
  default     = 300
}

variable "message_retention_seconds" {
  description = "Message retention for the primary queue."
  type        = number
  default     = 345600
}

variable "dlq_message_retention_seconds" {
  description = "Message retention for the dead-letter queue."
  type        = number
  default     = 1209600
}

variable "receive_wait_time_seconds" {
  description = "Long polling wait time."
  type        = number
  default     = 0
}

variable "max_receive_count" {
  description = "Max receive count before messages move to the DLQ."
  type        = number
  default     = 5
}

variable "tags" {
  description = "Additional tags to apply to the queues."
  type        = map(string)
  default     = {}
}
