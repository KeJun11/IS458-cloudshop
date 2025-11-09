project_name     = "test"
env              = "dev"
region           = "us-east-1"
ses_sender_email = "limkejun.4d@gmail.com"

# Stripe Configuration
# Get your test keys from: https://dashboard.stripe.com/test/apikeys
# Note: The actual stripe_secret_key is provided via TF_VAR_stripe_secret_key environment variable
# in CI/CD (from GitHub Secrets) or can be set here for local development
# stripe_secret_key = "sk_test_YOUR_KEY_HERE"  # Uncomment for local dev only

# Stripe Webhook Secret (optional - get after setting up webhook endpoint)
# Get from: https://dashboard.stripe.com/test/webhooks
stripe_webhook_secret = ""  # Leave empty for now, add after webhook is deployed
