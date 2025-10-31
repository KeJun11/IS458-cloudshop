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

# This is the sample seed product, can change if you want
variable "seed_products" {
  description = "List of seed products to insert into the Products table."
  type = list(object({
    product_id  = string
    name        = string
    description = string
    price       = number
    category    = string
    image_url   = string
    stock       = number
  }))
  default = [
    {
      product_id  = "prod-100"
      name        = "Wireless Headphones"
      description = "High-quality wireless headphones with noise cancellation"
      price       = 59.99
      category    = "Electronics"
      image_url   = "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500"
      stock       = 50
    },
    {
      product_id  = "prod-200"
      name        = "Paperback Notebook"
      description = "Premium quality notebook for writing and sketching"
      price       = 12.5
      category    = "Stationery"
      image_url   = "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500"
      stock       = 100
    }
  ]
}
