# CloudWatch Monitoring Module

This module creates a CloudWatch dashboard and alarms for monitoring the IS458 CloudShop application.

## What's Included

### CloudWatch Dashboard

A comprehensive dashboard showing:

- **API Gateway**: Request count, 4XX errors, 5XX errors
- **Lambda**: Total invocations, errors, and throttles
- **DynamoDB**: Request latency and errors across all tables
- **SQS**: Queue depth and message age

### CloudWatch Alarms

Five alarms that monitor critical metrics:

1. **API Gateway 5XX Errors** - Triggers when >10 server errors in 5 minutes
2. **Lambda Errors** - Triggers when >5 total errors across all functions in 5 minutes
3. **DynamoDB System Errors** - Triggers on any DynamoDB system errors
4. **SQS High Queue Depth** - Triggers when >100 messages waiting in queue
5. **SQS Dead Letter Queue** - Triggers when any messages fail and end up in DLQ

## Accessing the Dashboard

### After Deployment

1. Run `terraform apply` to deploy the monitoring
2. Go to **AWS Console** → **CloudWatch** → **Dashboards**
3. Look for: `test-dev-monitoring`

### Viewing Alarms

1. Go to **AWS Console** → **CloudWatch** → **Alarms**
2. Filter by: `test-dev-*`

## For Your Presentation

### What to Show

1. **Dashboard**: Shows real-time metrics across all services
2. **Alarms**: Shows proactive monitoring (even if they're in "OK" state)

### What to Say

> "We've implemented comprehensive CloudWatch monitoring via Infrastructure as Code. Our dashboard shows real-time metrics for API Gateway, Lambda, DynamoDB, and SQS. We've also configured alarms that will alert us if error rates exceed thresholds, queue depth grows too large, or any system errors occur."

### Key Points

- ✅ All services are monitored
- ✅ Dashboard shows services are working (metrics flowing)
- ✅ Alarms are preventive (don't need to trigger to show value)
- ✅ Everything is deployed via Terraform (Infrastructure as Code)

## Editing the Dashboard

Yes! You can edit the Terraform-created dashboard in AWS Console:

1. Go to CloudWatch → Dashboards → `test-dev-monitoring`
2. Click **Actions** → **Edit**
3. Add/remove widgets as needed
4. Click **Save**

**Note**: Manual changes will be overwritten if you run `terraform apply` again. To preserve changes, update the Terraform code instead.
