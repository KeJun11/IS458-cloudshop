resource "aws_ses_email_identity" "this" {
  email = var.ses_sender_email
}

# Note: The Lambda function's IAM role grants the necessary SES permissions.
# An identity-based policy is not required here as Lambda uses its execution role
# to send emails via SES.
