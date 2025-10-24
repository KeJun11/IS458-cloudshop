output "email_identity_arn" {
  description = "ARN of the SES email identity."
  value       = aws_ses_email_identity.this.arn
}

output "email_identity" {
  description = "Verified SES email identity."
  value       = aws_ses_email_identity.this.email
}
