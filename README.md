# AWS E-commerce POC IaC

Terraform configuration for a serverless e-commerce proof of concept covering product browsing, cart management, order processing, and recommendation flows. The stack provisions all core AWS services described in `project_requirements.md`.

## Repo Layout

- `terraform/modules/*` – reusable modules for S3, CloudFront, DynamoDB, Lambda, SQS, SES, and API Gateway.
- `terraform/envs/dev` – environment-level wiring that composes the modules and defines outputs.
- `lambdas/*` – placeholder Lambda handlers; replace the bodies with your business logic.
- `.env.example` – centralised configuration surface for Terraform variables.

## Prerequisites

- Terraform **1.6.x** or later.
- AWS CLI credentials with permission to create the listed resources.
- PowerShell 5+ (Windows) or Bash/Zsh (macOS/Linux) to load environment variables.
- Optional: AWS CLI for uploading frontend assets (`aws s3 sync`).

## Configure Variables

1. Copy the environment template and update the values.
   ```powershell
   Copy-Item .env.example .env
   ```
2. Edit `.env` and set at least:

   - `TF_VAR_project_name`
   - `TF_VAR_env`
   - `TF_VAR_region`
   - `TF_VAR_ses_sender_email` (leave blank to skip SES identity creation; required for outbound email).

3. Export the variables into your shell before running Terraform.

   - **PowerShell**
     ```powershell
     Get-Content .env | Where-Object { $_ -and $_ -notmatch '^#' } | ForEach-Object {
       $name, $value = $_ -split '=', 2
       [System.Environment]::SetEnvironmentVariable($name.Trim(), $value.Trim())
     }
     ```
   - **Bash / Zsh**
     ```bash
     set -a
     source .env
     set +a
     ```

   Alternatively, copy `terraform/envs/dev/terraform.tfvars.example` to `terraform/envs/dev/terraform.tfvars` and fill the values there.

## Deploy the Stack

Run Terraform from the environment directory:

```powershell
terraform -chdir=terraform/envs/dev init
terraform -chdir=terraform/envs/dev fmt
terraform -chdir=terraform/envs/dev validate
terraform -chdir=terraform/envs/dev plan
terraform -chdir=terraform/envs/dev apply
```

On successful apply you will receive outputs for:

- `cloudfront_domain` – CDN URL serving the static frontend.
- `api_endpoint` – HTTP API base invoke URL.
- `static_site_bucket` and `invoice_bucket` – S3 buckets for website assets and invoices.
- `order_queue_url` – SQS queue URL for downstream processing.
- `dynamodb_tables` – Logical-to-physical DynamoDB table mapping.

## After Deployment

1. **Verify SES** – Check the console for the “pending verification” email if you supplied `TF_VAR_ses_sender_email`. SES sandbox accounts can only email verified recipients.
2. **Upload frontend assets** – Build your static site and sync it to the bucket:
   ```bash
   aws s3 sync dist/ s3://<static_site_bucket>/
   ```
3. **Smoke test the API** – Use the `api_endpoint` output with the provisioned routes:
   - `GET {api_endpoint}/products`
   - `POST {api_endpoint}/cart`
   - `POST {api_endpoint}/orders`
   - `POST {api_endpoint}/events`
   - `GET {api_endpoint}/recommendations?userId=demo-user`

## Lambda Handlers

Each folder under `lambdas/` contains a minimal placeholder `app.py`. Replace the bodies with real logic, package dependencies in `requirements.txt`, and rerun `terraform -chdir=terraform/envs/dev apply` to update the functions. The Terraform module automatically zips each directory via the `archive_file` data source.

## Cleanup

Destroy the stack when you finish testing to avoid ongoing charges:

```powershell
terraform -chdir=terraform/envs/dev destroy
```

## Notes & Next Stepsx xx

- The infrastructure defaults to `us-east-1` and uses AWS-managed SSL on CloudFront. Add ACM certificates and custom domains later if needed.
- DynamoDB tables run on on-demand capacity with light seed data for demo purposes.
- Extend the Makefile or add CI/CD tooling if you want repeatable pipelines.
