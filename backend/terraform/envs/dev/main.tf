resource "random_id" "bucket_suffix" {
  byte_length = 4
}

locals {
  project              = var.project_name
  environment          = var.env
  common_tags          = merge({ Project = var.project_name, Environment = var.env, ManagedBy = "terraform" }, var.additional_tags)
  lambda_source_root   = abspath("${path.root}/../../../lambdas")
  static_bucket_name   = "${var.project_name}-${var.env}-frontend-is458-2025-${random_id.bucket_suffix.hex}"
  invoice_bucket_name  = "${var.project_name}-${var.env}-invoices-${random_id.bucket_suffix.hex}"
  ses_identity_defined = var.ses_sender_email != ""
}

module "static_site_bucket" {
  source = "../../modules/s3_static_site"

  bucket_name       = local.static_bucket_name
  project           = local.project
  environment       = local.environment
  enable_versioning = true
  tags              = var.additional_tags
}

module "cloudfront" {
  source = "../../modules/cloudfront"

  project                   = local.project
  environment               = local.environment
  origin_bucket_domain_name = module.static_site_bucket.bucket_domain_name
  default_root_object       = var.frontend_index_key
  aliases                   = []
  acm_certificate_arn       = null
  price_class               = "PriceClass_100"
  enable_compression        = true
  tags                      = var.additional_tags
}

resource "aws_s3_bucket_policy" "static_site" {
  bucket = module.static_site_bucket.bucket_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "AllowCloudFrontReadAccess"
        Effect = "Allow"
        Principal = {
          Service = "cloudfront.amazonaws.com"
        }
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          module.static_site_bucket.bucket_arn,
          "${module.static_site_bucket.bucket_arn}/*"
        ]
        Condition = {
          StringEquals = {
            "AWS:SourceArn" = module.cloudfront.distribution_arn
          }
        }
      }
    ]
  })
}

resource "aws_s3_bucket" "invoice" {
  bucket        = local.invoice_bucket_name
  force_destroy = false

  tags = merge(local.common_tags, { Purpose = "order-invoices" })
}

resource "aws_s3_bucket_public_access_block" "invoice" {
  bucket = aws_s3_bucket.invoice.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "invoice" {
  bucket = aws_s3_bucket.invoice.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_versioning" "invoice" {
  bucket = aws_s3_bucket.invoice.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "invoice" {
  bucket = aws_s3_bucket.invoice.id

  rule {
    id     = "expire-old-invoices"
    status = "Enabled"

    # Apply to all objects in the bucket
    filter {
      prefix = ""
    }

    expiration {
      days = var.invoice_bucket_lifecycle_days
    }
  }
}

module "dynamodb" {
  source = "../../modules/dynamodb"

  project      = local.project
  environment  = local.environment
  billing_mode = "PAY_PER_REQUEST"
  tags         = var.additional_tags
}

module "order_queue" {
  source = "../../modules/sqs"

  project     = local.project
  environment = local.environment
  queue_name  = "order-processing"
  tags        = var.additional_tags
}

module "ses" {
  count  = local.ses_identity_defined ? 1 : 0
  source = "../../modules/ses"

  project          = local.project
  environment      = local.environment
  ses_sender_email = var.ses_sender_email
}

locals {
  ses_identity_arn = local.ses_identity_defined ? module.ses[0].email_identity_arn : null
  ses_sender_email = var.ses_sender_email
  dynamodb_arns    = module.dynamodb.table_arns
  dynamodb_names   = module.dynamodb.table_names
}

module "lambda_get_products" {
  source = "../../modules/lambda_function"

  project       = local.project
  environment   = local.environment
  function_name = "get-products"
  description   = "Return catalog products for the store frontend."
  source_dir    = "${local.lambda_source_root}/get_products"

  environment_variables = {
    PRODUCTS_TABLE = local.dynamodb_names["products"]
  }

  policy_statements = [
    {
      sid     = "ReadProductsTable"
      actions = ["dynamodb:GetItem", "dynamodb:Query", "dynamodb:Scan", "dynamodb:DescribeTable"]
      resources = [
        local.dynamodb_arns["products"],
        "${local.dynamodb_arns["products"]}/index/*"
      ]
    }
  ]
}

module "lambda_manage_cart" {
  source = "../../modules/lambda_function"

  project       = local.project
  environment   = local.environment
  function_name = "manage-cart"
  description   = "Create or update a user's shopping cart."
  source_dir    = "${local.lambda_source_root}/manage_cart"

  environment_variables = {
    CARTS_TABLE    = local.dynamodb_names["carts"]
    PRODUCTS_TABLE = local.dynamodb_names["products"]
  }

  policy_statements = [
    {
      sid       = "ManageCartsTable"
      actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:DeleteItem"]
      resources = [local.dynamodb_arns["carts"]]
    },
    {
      sid       = "ReadProductsTable"
      actions   = ["dynamodb:GetItem"]
      resources = [local.dynamodb_arns["products"]]
    }
  ]
}

module "lambda_create_order" {
  source = "../../modules/lambda_function"

  project       = local.project
  environment   = local.environment
  function_name = "create-order"
  description   = "Persist new orders and enqueue them for processing."
  source_dir    = "${local.lambda_source_root}/create_order"

  environment_variables = {
    ORDERS_TABLE     = local.dynamodb_names["orders"]
    CARTS_TABLE      = local.dynamodb_names["carts"]
    ORDER_QUEUE_URL  = module.order_queue.queue_url
    ORDER_QUEUE_ARN  = module.order_queue.queue_arn
    INVOICE_BUCKET   = aws_s3_bucket.invoice.bucket
    SES_SENDER_EMAIL = local.ses_sender_email
  }

  policy_statements = [
    {
      sid     = "ManageOrdersTable"
      actions = ["dynamodb:PutItem", "dynamodb:UpdateItem", "dynamodb:GetItem", "dynamodb:Query"]
      resources = [
        local.dynamodb_arns["orders"],
        "${local.dynamodb_arns["orders"]}/index/*"
      ]
    },
    {
      sid       = "ReadCarts"
      actions   = ["dynamodb:GetItem", "dynamodb:DeleteItem"]
      resources = [local.dynamodb_arns["carts"]]
    },
    {
      sid       = "SendOrderQueue"
      actions   = ["sqs:SendMessage"]
      resources = [module.order_queue.queue_arn]
    },
    {
      sid       = "WriteInvoices"
      actions   = ["s3:PutObject"]
      resources = ["${aws_s3_bucket.invoice.arn}/*"]
    }
  ]
}

module "lambda_process_order" {
  source = "../../modules/lambda_function"

  project       = local.project
  environment   = local.environment
  function_name = "process-order"
  description   = "Process queued orders, send confirmation emails, and archive invoices."
  source_dir    = "${local.lambda_source_root}/process_order"

  environment_variables = {
    ORDERS_TABLE     = local.dynamodb_names["orders"]
    CARTS_TABLE      = local.dynamodb_names["carts"]
    ORDER_QUEUE_ARN  = module.order_queue.queue_arn
    INVOICE_BUCKET   = aws_s3_bucket.invoice.bucket
    SES_SENDER_EMAIL = local.ses_sender_email
  }

  policy_statements = [
    {
      sid       = "UpdateOrders"
      actions   = ["dynamodb:GetItem", "dynamodb:UpdateItem"]
      resources = [local.dynamodb_arns["orders"]]
    },
    {
      sid       = "ManageCarts"
      actions   = ["dynamodb:UpdateItem"]
      resources = [local.dynamodb_arns["carts"]]
    },
    {
      sid       = "ManageQueue"
      actions   = ["sqs:DeleteMessage", "sqs:GetQueueAttributes", "sqs:ReceiveMessage"]
      resources = [module.order_queue.queue_arn]
    },
    {
      sid       = "StoreInvoices"
      actions   = ["s3:PutObject"]
      resources = ["${aws_s3_bucket.invoice.arn}/*"]
    },
    {
      sid       = "SendEmails"
      actions   = ["ses:SendEmail", "ses:SendRawEmail", "ses:GetIdentityVerificationAttributes"]
      resources = local.ses_identity_arn != null ? [local.ses_identity_arn] : ["*"]
    }
  ]
}

module "lambda_track_event" {
  source = "../../modules/lambda_function"

  project       = local.project
  environment   = local.environment
  function_name = "track-event"
  description   = "Capture product interaction events."
  source_dir    = "${local.lambda_source_root}/track_event"

  environment_variables = {
    INTERACTIONS_TABLE = local.dynamodb_names["interactions"]
  }

  policy_statements = [
    {
      sid       = "WriteInteractions"
      actions   = ["dynamodb:PutItem"]
      resources = [local.dynamodb_arns["interactions"]]
    }
  ]
}

module "lambda_get_recommendations" {
  source = "../../modules/lambda_function"

  project       = local.project
  environment   = local.environment
  function_name = "get-recommendations"
  description   = "Return product recommendations based on user interaction history."
  source_dir    = "${local.lambda_source_root}/get_recommendations"

  environment_variables = {
    INTERACTIONS_TABLE = local.dynamodb_names["interactions"]
    PRODUCTS_TABLE     = local.dynamodb_names["products"]
    PRODUCT_TYPE_GSI   = "category-index"
  }

  policy_statements = [
    {
      sid     = "ReadInteractions"
      actions = ["dynamodb:Query", "dynamodb:GetItem"]
      resources = [
        local.dynamodb_arns["interactions"],
        "${local.dynamodb_arns["interactions"]}/index/*"
      ]
    },
    {
      sid     = "ReadProducts"
      actions = ["dynamodb:Query", "dynamodb:Scan", "dynamodb:GetItem"]
      resources = [
        local.dynamodb_arns["products"],
        "${local.dynamodb_arns["products"]}/index/*"
      ]
    }
  ]
}

module "http_api" {
  source = "../../modules/apigw_http"

  project     = local.project
  environment = local.environment
  stage_name  = "$default"
  tags        = var.additional_tags

  routes = [
    {
      route_key  = "GET /products"
      lambda_arn = module.lambda_get_products.function_arn
    },
    {
      route_key  = "GET /products/{id}"
      lambda_arn = module.lambda_get_products.function_arn
    },
    {
      route_key  = "GET /cart"
      lambda_arn = module.lambda_manage_cart.function_arn
    },
    {
      route_key  = "POST /cart"
      lambda_arn = module.lambda_manage_cart.function_arn
    },
    {
      route_key  = "PUT /cart"
      lambda_arn = module.lambda_manage_cart.function_arn
    },
    {
      route_key  = "DELETE /cart"
      lambda_arn = module.lambda_manage_cart.function_arn
    },
    {
      route_key  = "GET /orders"
      lambda_arn = module.lambda_create_order.function_arn
    },
    {
      route_key  = "POST /orders"
      lambda_arn = module.lambda_create_order.function_arn
    },
    {
      route_key  = "GET /orders/{id}"
      lambda_arn = module.lambda_create_order.function_arn
    },
    {
      route_key  = "POST /events"
      lambda_arn = module.lambda_track_event.function_arn
    },
    {
      route_key  = "GET /recommendations"
      lambda_arn = module.lambda_get_recommendations.function_arn
    }
  ]
}

resource "aws_lambda_event_source_mapping" "process_order_queue" {
  event_source_arn = module.order_queue.queue_arn
  function_name    = module.lambda_process_order.function_arn
  enabled          = true
  batch_size       = 1
}
