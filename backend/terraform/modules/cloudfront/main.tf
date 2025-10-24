locals {
  default_tags = {
    Project     = var.project
    Environment = var.environment
    ManagedBy   = "terraform"
  }
}

resource "aws_cloudfront_origin_access_control" "this" {
  name                              = "${var.project}-${var.environment}-oac"
  description                       = "Origin access control for ${var.project} ${var.environment}"
  origin_access_control_origin_type = "s3"
  signing_behavior                  = "always"
  signing_protocol                  = "sigv4"
}

resource "aws_cloudfront_distribution" "this" {
  enabled             = true
  comment             = "${var.project}-${var.environment} static site distribution"
  default_root_object = var.default_root_object

  origin {
    domain_name              = var.origin_bucket_domain_name
    origin_id                = "s3-${var.origin_bucket_domain_name}"
    origin_access_control_id = aws_cloudfront_origin_access_control.this.id
  }

  default_cache_behavior {
    cache_policy_id        = data.aws_cloudfront_cache_policy.caching_optimized.id
    origin_request_policy_id = data.aws_cloudfront_origin_request_policy.cors_s3_origin.id
    target_origin_id       = "s3-${var.origin_bucket_domain_name}"

    allowed_methods = [
      "GET",
      "HEAD",
      "OPTIONS",
    ]

    cached_methods = [
      "GET",
      "HEAD",
    ]

    viewer_protocol_policy = "redirect-to-https"
    compress               = var.enable_compression
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn            = var.acm_certificate_arn
    cloudfront_default_certificate = var.acm_certificate_arn == null
    minimum_protocol_version       = var.acm_certificate_arn == null ? "TLSv1" : "TLSv1.2_2021"
    ssl_support_method             = var.acm_certificate_arn == null ? null : "sni-only"
  }

  aliases = var.aliases

  price_class = var.price_class

  tags = merge(
    local.default_tags,
    var.tags,
  )
}

data "aws_cloudfront_cache_policy" "caching_optimized" {
  name = "Managed-CachingOptimized"
}

data "aws_cloudfront_origin_request_policy" "cors_s3_origin" {
  name = "Managed-CORS-S3Origin"
}
