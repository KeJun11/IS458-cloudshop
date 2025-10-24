resource "aws_ses_email_identity" "this" {
  email = var.ses_sender_email
}

resource "aws_sesv2_email_identity_policy" "allow_ses" {
  email_identity = aws_ses_email_identity.this.id
  policy_name    = "${var.project}-${var.environment}-allow-ses"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowSESSend"
        Effect    = "Allow"
        Principal = {
          Service = "ses.amazonaws.com"
        }
        Action   = "ses:SendEmail"
        Resource = aws_ses_email_identity.this.arn
      }
    ]
  })
}
