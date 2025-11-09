project_name     = "test"
env              = "dev"
region           = "us-east-1"
ses_sender_email = "limkejun.4d@gmail.com"

# Stripe Configuration
# Get your test keys from: https://dashboard.stripe.com/test/apikeys
stripe_secret_key = "sk_test_YOUR_STRIPE_SECRET_KEY_HERE"

# Stripe Webhook Secret (optional - get after setting up webhook endpoint)
# Get from: https://dashboard.stripe.com/test/webhooks
stripe_webhook_secret = ""  # Leave empty for now, add after webhook is deployed
