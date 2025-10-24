locals {
  table_definitions = {
    products = {
      name     = "${var.project}-${var.environment}-products"
      hash_key = "productId"
      attributes = [
        {
          name = "productId"
          type = "S"
        },
        {
          name = "category"
          type = "S"
        },
      ]
      global_secondary_indexes = [
        {
          name            = "category-index"
          hash_key        = "category"
          projection_type = "ALL"
        }
      ]
    }
    carts = {
      name     = "${var.project}-${var.environment}-carts"
      hash_key = "userId"
      attributes = [
        {
          name = "userId"
          type = "S"
        }
      ]
      global_secondary_indexes = []
    }
    orders = {
      name     = "${var.project}-${var.environment}-orders"
      hash_key = "orderId"
      attributes = [
        {
          name = "orderId"
          type = "S"
        },
        {
          name = "userId"
          type = "S"
        }
      ]
      global_secondary_indexes = [
        {
          name            = "userId-index"
          hash_key        = "userId"
          projection_type = "ALL"
        }
      ]
    }
    interactions = {
      name      = "${var.project}-${var.environment}-user-interactions"
      hash_key  = "userId"
      range_key = "productId"
      attributes = [
        {
          name = "userId"
          type = "S"
        },
        {
          name = "productId"
          type = "S"
        },
        {
          name = "category"
          type = "S"
        }
      ]
      global_secondary_indexes = [
        {
          name            = "category-index"
          hash_key        = "category"
          projection_type = "ALL"
        }
      ]
    }
  }
}

resource "aws_dynamodb_table" "this" {
  for_each = local.table_definitions

  name         = each.value.name
  billing_mode = var.billing_mode
  hash_key     = each.value.hash_key
  range_key    = try(each.value.range_key, null)

  dynamic "attribute" {
    for_each = each.value.attributes
    content {
      name = attribute.value.name
      type = attribute.value.type
    }
  }

  dynamic "global_secondary_index" {
    for_each = each.value.global_secondary_indexes
    content {
      name               = global_secondary_index.value.name
      hash_key           = global_secondary_index.value.hash_key
      projection_type    = global_secondary_index.value.projection_type
      write_capacity     = var.billing_mode == "PROVISIONED" ? var.provisioned_write_capacity : null
      read_capacity      = var.billing_mode == "PROVISIONED" ? var.provisioned_read_capacity : null
      range_key          = try(global_secondary_index.value.range_key, null)
    }
  }

  tags = merge(
    {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "terraform"
      TableAlias  = each.key
    },
    var.tags,
  )
}

resource "aws_dynamodb_table_item" "seed_products" {
  for_each = { for item in var.seed_products : item.product_id => item }

  table_name = aws_dynamodb_table.this["products"].name
  hash_key   = "productId"

  item = jsonencode({
    productId   = { S = each.value.product_id }
    name        = { S = each.value.name }
    description = { S = each.value.description }
    price       = { N = tostring(each.value.price) }
    category    = { S = each.value.category }
    imageUrl    = { S = each.value.image_url }
    stock       = { N = tostring(each.value.stock) }
  })

  lifecycle {
    ignore_changes = [
      item,
    ]
  }
}
