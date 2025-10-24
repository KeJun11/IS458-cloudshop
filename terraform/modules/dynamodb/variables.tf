variable "project" {
  description = "Project identifier used for tagging."
  type        = string
}

variable "environment" {
  description = "Deployment environment name (e.g., dev, prod)."
  type        = string
}

variable "billing_mode" {
  description = "Billing mode for the DynamoDB tables."
  type        = string
  default     = "PAY_PER_REQUEST"
  validation {
    condition     = contains(["PAY_PER_REQUEST", "PROVISIONED"], var.billing_mode)
    error_message = "Billing mode must be PAY_PER_REQUEST or PROVISIONED."
  }
}

variable "provisioned_read_capacity" {
  description = "Read capacity units when using PROVISIONED billing."
  type        = number
  default     = 1
}

variable "provisioned_write_capacity" {
  description = "Write capacity units when using PROVISIONED billing."
  type        = number
  default     = 1
}

variable "tags" {
  description = "Additional tags to apply to the tables."
  type        = map(string)
  default     = {}
}

variable "seed_products" {
  description = "List of seed products to insert into the Products table."
  type = list(object({
    product_id   = string
    name         = string
    price        = number
    product_type = string
  }))
  default = [
    {
      product_id   = "prod-100"
      name         = "Wireless Headphones"
      price        = 59.99
      product_type = "Electronics"
    },
    {
      product_id   = "prod-200"
      name         = "Paperback Notebook"
      price        = 12.5
      product_type = "Stationery"
    }
  ]
}
