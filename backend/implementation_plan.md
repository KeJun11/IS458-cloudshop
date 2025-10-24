# Implementation Plan – AWS E‑commerce POC

This plan translates the requirements in `project_requirements.md` into actionable work. It outlines Terraform structure, Makefile tasks, and pytest coverage for Lambda functions. Assumptions are explicit so you can adjust before building.

---

## Assumptions and Decisions

- Language/runtime: Python 3.12 for all Lambda functions.
- Regions:
  - Application region: variable `var.region` (default `us-east-1`).
  - CloudFront ACM certificates must be in `us-east-1` (separate `aws` provider alias `us_east_1`).
- API type: API Gateway HTTP API (v2) with Lambda proxy integrations and permissive CORS for POC.
- Auth: No authentication for POC (public API). Add Cognito/JWT later if needed.
- DynamoDB capacity: On-demand (PAY_PER_REQUEST) for all tables.
- S3 for frontend: Private bucket with CloudFront Origin Access Control (OAC). No direct public access.
- SES: Use `aws_ses_email_identity` for sender verification. If account is in SES sandbox, test emails must be to verified recipients or request production access (manual step).
- SQS: Standard queue with DLQ, 5-minute visibility timeout, redrive policy.
- Invoices bucket: Private S3 bucket with SSE-S3 encryption and lifecycle for cleanup (optional).
- Packaging: Terraform `archive_file` to zip Lambda code from `lambdas/<function>` folders.
- Seeding: Minimal product seed items via Terraform for demo only.

Items needing confirmation (defaults proposed):

1. Custom domains with Route53 and ACM for `www` and `api`? Default: none; use CloudFront domain and API default invoke URL.
2. Frontend app stack (React/Vue static assets) and build pipeline? Default: manual upload to S3; CI skipped.
3. `UserInteractions-Table` sort key: Use `productId` as SK; store `productType` as an attribute and add optional GSI on `productType`.
4. Email sender identity for SES (e.g., `no-reply@example.com`).
5. Region preference for app workloads (default `us-east-1`).

---

## Repository Layout

```
terraform/
  modules/
    apigw_http/
    cloudfront/
    dynamodb/
    iam/
    lambda/
    s3_static_site/
    ses/
    sqs/
  envs/
    dev/
      versions.tf
      providers.tf
      variables.tf
      main.tf
      outputs.tf
      terraform.tfvars        # env-specific values

lambdas/
  get_products/
    app.py
    requirements.txt
  manage_cart/
    app.py
    requirements.txt
  create_order/
    app.py
    requirements.txt
  process_order/
    app.py
    requirements.txt
  track_event/
    app.py
    requirements.txt
  get_recommendations/
    app.py
    requirements.txt

frontend/                    # optional: built static assets go here

tests/
  unit/
    test_get_products.py
    test_manage_cart.py
    test_create_order.py
    test_process_order.py
    test_track_event.py
    test_get_recommendations.py

Makefile                     # terraform fmt/validate/plan/apply/destroy
requirements-dev.txt         # pytest, moto, boto3
```

---

## Terraform – Environment Skeleton (dev)

Create `terraform/envs/dev` with the following files (content summarized):

- `versions.tf`
  - Require Terraform ~> 1.6
  - `aws` provider ~> 5.x, `archive` ~> 2.x

- `providers.tf`
  - Default `aws` provider in `var.region`.
  - Aliased provider `aws.us_east_1` pinned to `us-east-1` for CloudFront ACM.

- `variables.tf` (key inputs)
  - `project_name` (string)
  - `env` (string, e.g., `dev`)
  - `region` (string, default `us-east-1`)
  - `ses_sender_email` (string)
  - `frontend_index_key` (string, default `index.html`)
  - `invoice_bucket_lifecycle_days` (number, default 30)
  - Domain vars (optional): `domain_name`, `api_subdomain`, `web_subdomain`

- `main.tf` (wire modules and resources) – high-level:
  - S3 static site bucket (private) via `s3_static_site` module.
  - CloudFront with OAC pointing to the site bucket via `cloudfront` module.
  - DynamoDB tables via `dynamodb` module:
    - `Products` (PK `productId` [S], GSI `productType-index` [PK: `productType`])
    - `Carts` (PK `userId` [S])
    - `Orders` (PK `orderId` [S], GSI `userId-index` [PK: `userId`])
    - `UserInteractions` (PK `userId` [S], SK `productId` [S])
  - SQS + DLQ via `sqs` module (output queue URL and ARN).
  - SES identity via `ses` module (sender verification only; sandbox note).
  - IAM roles/policies for each Lambda via `iam` module (least-privilege).
  - Lambda functions via `lambda` module with `archive_file` sources:
    - `get_products`: read `Products`
    - `manage_cart`: read/write `Carts`
    - `create_order`: write `Orders`, read `Carts`, send to SQS, put to invoice S3
    - `process_order`: SQS event source mapping; send SES; update `Orders`; put invoice to S3
    - `track_event`: write `UserInteractions`
    - `get_recommendations`: read `UserInteractions`; query `Products` GSI
  - API Gateway HTTP API via `apigw_http` module and route integrations:
    - `GET /products` -> `get_products`
    - `POST /cart` -> `manage_cart`
    - `POST /orders` -> `create_order`
    - `POST /events` -> `track_event`
    - `GET /recommendations` -> `get_recommendations`
  - S3 invoices bucket (private, SSE-S3) as a standalone resource or small module.
  - Optional: seed a few product items into `Products` via `aws_dynamodb_table_item` (demo only).

- `outputs.tf` (key outputs)
  - `cloudfront_domain_name`
  - `api_endpoint_url`
  - `site_bucket_name`
  - `invoice_bucket_name`
  - `sqs_queue_url`
  - `dynamodb_table_names` (object)

- `terraform.tfvars` (dev defaults)
  - `project_name = "ecom-poc"`
  - `env = "dev"`
  - `region = "us-east-1"`
  - `ses_sender_email = "no-reply@example.com"`

---

## Terraform – Module Notes (summaries)

1. `modules/s3_static_site`
   - Inputs: `bucket_name`, `index_key`, `logging` (optional)
   - Resources: `aws_s3_bucket`, `aws_s3_bucket_policy`, block public access, versioning (optional)
   - Output: `bucket_id`, `bucket_arn`

2. `modules/cloudfront`
   - Inputs: `oac_enabled` (true), `origin_bucket_domain_name`, `acm_certificate_arn` (optional), `default_root_object`
   - Resources: `aws_cloudfront_origin_access_control`, `aws_cloudfront_distribution`
   - Set custom error responses to serve `/index.html` on 404 for SPA.
   - Output: `domain_name`, `distribution_id`

3. `modules/dynamodb`
   - Create four tables with on-demand billing and server-side encryption.
   - Outputs: table names and ARNs per table.

4. `modules/sqs`
   - Create main queue and DLQ, set redrive policy, visibility timeout.
   - Outputs: `queue_url`, `queue_arn`, `dlq_arn`

5. `modules/ses`
   - Verify sender email via `aws_ses_email_identity`.
   - Note: Sandbox limitations documented in module README.

6. `modules/iam`
   - One execution role per Lambda with inline policies:
     - Logs: `logs:CreateLogGroup/Stream`, `logs:PutLogEvents`
     - DDB least-privilege per function
     - SQS send/receive as needed
     - SES `SendEmail` for `process_order`
     - S3 `PutObject` for invoice bucket as needed
   - Outputs: role ARNs per function

7. `modules/lambda`
   - Inputs per function: `function_name`, `role_arn`, `source_dir`, `environment` (map), `timeout`, `memory_size`
   - Resources: `archive_file`, `aws_lambda_function`, optional `aws_lambda_event_source_mapping` for SQS consumer
   - Outputs: ARNs and names

8. `modules/apigw_http`
   - Resources: `aws_apigatewayv2_api`, `aws_apigatewayv2_stage`, `aws_apigatewayv2_integration`, `aws_apigatewayv2_route`, `aws_lambda_permission`
   - Inputs: list of route->lambda mappings, CORS config
   - Output: API base URL

---

## Lambda – Environment Variables

Populate via Terraform for each function:

- Common: `PROJECT_NAME`, `ENV`, `REGION`
- `get_products`: `PRODUCTS_TABLE`
- `manage_cart`: `CARTS_TABLE`
- `create_order`: `ORDERS_TABLE`, `CARTS_TABLE`, `ORDER_QUEUE_URL`, `INVOICE_BUCKET`, `SES_SENDER_EMAIL`
- `process_order`: `ORDERS_TABLE`, `ORDER_QUEUE_ARN` (for permissions), `INVOICE_BUCKET`, `SES_SENDER_EMAIL`
- `track_event`: `INTERACTIONS_TABLE`
- `get_recommendations`: `INTERACTIONS_TABLE`, `PRODUCTS_TABLE`, `PRODUCT_TYPE_GSI` (e.g., `productType-index`)

Suggested defaults: `TIMEOUT=30`, `MEMORY=256` for most functions.

---

## Makefile – Terraform Tasks

Create a `Makefile` at repo root with these targets (env dir selectable via `ENV?=dev`):

```
ENV ?= dev
TF_DIR := terraform/envs/$(ENV)

.PHONY: init fmt validate plan apply destroy output

init:
	terraform -chdir=$(TF_DIR) init

fmt:
	terraform -chdir=$(TF_DIR) fmt -recursive

validate:
	terraform -chdir=$(TF_DIR) validate

plan:
	terraform -chdir=$(TF_DIR) plan

apply:
	terraform -chdir=$(TF_DIR) apply -auto-approve

destroy:
	terraform -chdir=$(TF_DIR) destroy -auto-approve

output:
	terraform -chdir=$(TF_DIR) output
```

Note for Windows: If `make` is unavailable, provide an equivalent PowerShell script later (optional).

---

## Python Dev Setup and Testing

- Create `requirements-dev.txt` with: `pytest`, `moto[boto3]`, `boto3`, `botocore`, `pytest-cov` (optional), `requests` (if needed for code).
- Each Lambda folder has its own `requirements.txt` for runtime deps (likely only `boto3`/`botocore` not needed in AWS but useful for local tests).
- `pytest.ini` (optional) to configure markers and test paths.

### Unit Test Coverage (moto mocks)

- `tests/unit/test_get_products.py`
  - Create `Products` table in moto; seed 2-3 items; invoke handler; assert JSON structure.

- `tests/unit/test_manage_cart.py`
  - Create `Carts` table; call handler with POST body; assert upserted item.

- `tests/unit/test_create_order.py`
  - Create `Orders` + `Carts` + SQS (moto) + invoice bucket; call handler; assert order item with PENDING and SQS message sent; verify S3 object creation where appropriate (can be delegated to `process_order`).

- `tests/unit/test_process_order.py`
  - Create SQS with message `{orderId, userEmail}`; create `Orders` table; SES mock; S3 mock; run consumer logic; assert order status updated and SES send called.

- `tests/unit/test_track_event.py`
  - Create `UserInteractions` table; call handler; assert write succeeded.

- `tests/unit/test_get_recommendations.py`
  - Seed interactions (productType tallies) + Products table with GSI; assert top category recommendations returned.

Run tests:

```
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
pytest -q
```

---

## Manual Steps and Caveats

- SES sandbox: Either verify recipient addresses used in tests/emails or request production access in the console.
- Custom domains: If desired, provision Route53 hosted zone, request ACM certs (CloudFront in `us-east-1`, API in app region), and attach to CloudFront/API Gateway. DNS validation requires manual or Terraform-managed records.
- Frontend deployment: This plan assumes you copy built assets to the S3 bucket (manual). CI/CD can be added later.
- Data seeding: Terraform-managed table items are for demo only; use scripts for larger datasets.

---

## High-Level To‑Do Checklist

- [ ] Confirm assumptions requiring input (domains, region, SES sender)
- [ ] Scaffold Terraform env `terraform/envs/dev` files
- [ ] Implement modules: `s3_static_site`, `cloudfront`, `dynamodb`, `sqs`, `ses`, `iam`, `lambda`, `apigw_http`
- [ ] Wire modules in `main.tf` with outputs and variables
- [ ] Create invoices S3 bucket and lifecycle policy
- [ ] Add minimal product seed data
- [ ] Create Makefile targets
- [ ] Write Lambda handlers (Python) for 6 functions
- [ ] Add unit tests with moto for all functions
- [ ] `make init fmt validate plan` and iterate
- [ ] `make apply` to deploy POC (after SES/email checks)
- [ ] Smoke test API routes and CloudFront URL

---

## Outputs You Should Expect After `apply`

- CloudFront distribution domain for the frontend
- API Gateway base invoke URL
- S3 bucket names (site, invoices)
- SQS queue URL
- DynamoDB table names

---

## Notes for Future Enhancements

- Add Cognito or JWT auth for API routes.
- CI/CD with GitHub Actions for Terraform plan/apply and Lambda testing.
- WAF on CloudFront/API Gateway for basic security hardening.
- Observability: X-Ray tracing and structured application logs.
- Parameterize envs (`staging`, `prod`) via workspaces or separate `envs/` folders.

