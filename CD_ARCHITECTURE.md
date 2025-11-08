# CD Pipeline Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CONTINUOUS DEPLOYMENT PIPELINE                      │
│                         IS458 CloudShop E-Commerce Platform                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│ TRIGGER: Push to main branch                                              │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ STEP 1: INFRASTRUCTURE (Terraform)                                        │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ terraform    │ -> │ terraform    │ -> │ terraform    │               │
│  │ init         │    │ plan         │    │ apply        │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                                                                            │
│  Creates/Updates:                                                          │
│  ✓ S3 Bucket (frontend)        ✓ API Gateway                             │
│  ✓ CloudFront Distribution     ✓ Lambda Functions (6x)                   │
│  ✓ DynamoDB Tables (4x)        ✓ SQS Queue                               │
│  ✓ IAM Roles                   ✓ SES Configuration                       │
│                                                                            │
│  Outputs:                                                                  │
│  📦 s3_bucket_name: aws-ecommerce-dev-frontend-is458-2025-abc123         │
│  🔗 api_endpoint: https://abc123.execute-api.us-east-1.amazonaws.com     │
│  🗃️  dynamodb_tables.products: aws-ecommerce-dev-products               │
│  🌐 cloudfront_domain: d1234567890abc.cloudfront.net                     │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ STEP 2: FRONTEND BUILD                                                     │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ npm ci       │ -> │ Create       │ -> │ npm run      │               │
│  │ (install)    │    │ .env.prod    │    │ build        │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                            │                      │                        │
│                            │                      ▼                        │
│                            │            ┌──────────────────┐              │
│                            │            │ dist/            │              │
│                            │            │  ├─ index.html   │              │
│                            │            │  ├─ assets/      │              │
│                            │            │  └─ ...          │              │
│                            │            └──────────────────┘              │
│                            ▼                                               │
│                  VITE_API_ENDPOINT=                                        │
│                  https://abc123.execute-api...                            │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ STEP 3: DEPLOY TO S3                                                       │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ aws s3 sync  │ -> │ Set cache    │ -> │ Update       │               │
│  │ dist/ to S3  │    │ headers      │    │ index.html   │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                                                                            │
│  Files uploaded to:                                                        │
│  s3://aws-ecommerce-dev-frontend-is458-2025-abc123/                       │
│                                                                            │
│  Cache-Control headers:                                                    │
│  • Static assets (JS/CSS/images): max-age=31536000 (1 year)              │
│  • index.html: max-age=0, must-revalidate                                │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ STEP 4: CLOUDFRONT INVALIDATION                                           │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ Find CF      │ -> │ Create       │ -> │ Wait for     │               │
│  │ distribution │    │ invalidation │    │ propagation  │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                                                                            │
│  Invalidates: /* (all paths)                                              │
│  Time: 3-5 minutes to propagate globally                                  │
│                                                                            │
│  Result: Users see fresh content immediately                              │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ STEP 5: SEED DATABASE                                                      │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐               │
│  │ Install      │ -> │ Run          │ -> │ Populate     │               │
│  │ Python/boto3 │    │ seed_products│    │ DynamoDB     │               │
│  └──────────────┘    └──────────────┘    └──────────────┘               │
│                                                                            │
│  Script: backend/scripts/seed_products.py                                 │
│  Table: aws-ecommerce-dev-products                                        │
│                                                                            │
│  Data inserted:                                                            │
│  • 19 products                                                             │
│  • Categories: Electronics, Accessories, Gaming, Beauty, Fitness          │
│  • Fields: productId, name, description, price, category, imageUrl, stock │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌───────────────────────────────────────────────────────────────────────────┐
│ DEPLOYMENT COMPLETE ✅                                                    │
├───────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  Summary:                                                                  │
│  🌐 Frontend: https://d1234567890abc.cloudfront.net                      │
│  🔗 API: https://abc123.execute-api.us-east-1.amazonaws.com              │
│  📦 S3: aws-ecommerce-dev-frontend-is458-2025-abc123                     │
│  🗃️  DB: aws-ecommerce-dev-products (19 products seeded)                │
│                                                                            │
│  Time: ~5-7 minutes                                                        │
│  Status: All systems operational                                          │
│                                                                            │
└───────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                            AWS ARCHITECTURE
═══════════════════════════════════════════════════════════════════════════

                           ┌─────────────────┐
                           │   CloudFront    │
                           │  Distribution   │ <- CDN (Global)
                           └────────┬────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
            ┌───────▼────────┐            ┌────────▼────────┐
            │   S3 Bucket    │            │   API Gateway   │
            │   (Frontend)   │            │   (HTTP API)    │
            └────────────────┘            └────────┬────────┘
                                                   │
                                    ┌──────────────┴──────────────┐
                                    │                             │
                            ┌───────▼────────┐          ┌────────▼────────┐
                            │ Lambda         │          │ Lambda          │
                            │ Functions (6x) │          │ Functions       │
                            └───────┬────────┘          └────────┬────────┘
                                    │                            │
                    ┌───────────────┴─────────────┬──────────────┘
                    │                             │
            ┌───────▼────────┐            ┌──────▼──────┐
            │   DynamoDB     │            │  SQS Queue  │
            │   Tables (4x)  │            └──────┬──────┘
            │                │                   │
            │ • products     │            ┌──────▼──────┐
            │ • carts        │            │   Lambda    │
            │ • orders       │            │ (Processor) │
            │ • interactions │            └──────┬──────┘
            └────────────────┘                   │
                                         ┌───────▼───────┐
                                         │  SES (Email)  │
                                         │  S3 (Invoice) │
                                         └───────────────┘


═══════════════════════════════════════════════════════════════════════════
                        DATA FLOW (User Request)
═══════════════════════════════════════════════════════════════════════════

1. User visits: https://d1234567890abc.cloudfront.net
                         │
                         ▼
2. CloudFront serves index.html from S3 cache
                         │
                         ▼
3. Browser loads React app with VITE_API_ENDPOINT configured
                         │
                         ▼
4. App calls: GET https://abc123.execute-api.../products
                         │
                         ▼
5. API Gateway routes to Lambda (get_products)
                         │
                         ▼
6. Lambda queries DynamoDB products table
                         │
                         ▼
7. Returns JSON product data
                         │
                         ▼
8. Frontend displays products with images


═══════════════════════════════════════════════════════════════════════════
                        SECRETS & CONFIGURATION
═══════════════════════════════════════════════════════════════════════════

GitHub Secrets (Encrypted):
  ┌────────────────────────────────────────┐
  │ AWS_ACCESS_KEY_ID                      │
  │ AWS_SECRET_ACCESS_KEY                  │
  │ AWS_REGION                             │
  └────────────────────────────────────────┘
                    │
                    ▼
            Used by GitHub Actions
                    │
                    ├──> Terraform (provision infra)
                    ├──> AWS CLI (S3 sync, CloudFront)
                    └──> Python/boto3 (DynamoDB seed)


Environment Variables (Runtime):
  ┌────────────────────────────────────────┐
  │ Frontend (.env.production):            │
  │   VITE_API_ENDPOINT                    │
  │                                        │
  │ Lambda Functions:                      │
  │   ORDERS_TABLE                         │
  │   CARTS_TABLE                          │
  │   PRODUCTS_TABLE                       │
  │   INTERACTIONS_TABLE                   │
  │   ORDER_QUEUE_URL                      │
  │   INVOICE_BUCKET                       │
  │   SES_SENDER_EMAIL                     │
  └────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
                          COST BREAKDOWN (Monthly)
═══════════════════════════════════════════════════════════════════════════

Service                 Free Tier          Estimated Cost (Low Traffic)
─────────────────────────────────────────────────────────────────────────
S3                      5 GB               $0.02 - $0.50
CloudFront              1 TB transfer      $0.00 - $1.00
Lambda                  1M requests        $0.00 - $5.00
API Gateway             1M requests        $1.00 - $3.00
DynamoDB                25 GB + 200M ops   $0.00 - $2.00
SQS                     1M requests        $0.00
SES                     2000 emails/day    $0.00 - $1.00
CloudWatch Logs         5 GB               $0.00 - $1.00
─────────────────────────────────────────────────────────────────────────
TOTAL                                      $1.00 - $13.50 /month

* Assumes <1000 users/day, <10K requests/day
* Most services stay within free tier limits


═══════════════════════════════════════════════════════════════════════════
                        MONITORING & LOGGING
═══════════════════════════════════════════════════════════════════════════

GitHub Actions:
  • Deployment logs
  • Step-by-step execution
  • Success/failure status
  • Deployment time metrics

CloudWatch:
  • Lambda function logs
  • API Gateway access logs
  • Error rates and latency
  • Custom metrics

CloudFront:
  • Access logs
  • Cache hit ratio
  • Geographic distribution
  • Bandwidth usage

DynamoDB:
  • Read/write capacity metrics
  • Throttled requests
  • Table size

X-Ray (optional):
  • Distributed tracing
  • Performance bottlenecks
  • Service map


═══════════════════════════════════════════════════════════════════════════
                        SECURITY FEATURES
═══════════════════════════════════════════════════════════════════════════

✓ HTTPS Only (CloudFront + API Gateway)
✓ S3 Bucket Private (CloudFront OAI)
✓ IAM Least Privilege
✓ Secrets Encrypted (GitHub Secrets)
✓ No Credentials in Code
✓ DynamoDB Encryption at Rest
✓ S3 Versioning Enabled
✓ CloudWatch Logging
✓ CORS Configured
✓ Lambda in VPC (optional)


═══════════════════════════════════════════════════════════════════════════
                        DISASTER RECOVERY
═══════════════════════════════════════════════════════════════════════════

Backup Strategy:
  • Terraform state → S3 (versioned)
  • DynamoDB → Point-in-time recovery (optional)
  • S3 frontend → Versioning enabled
  • Git repository → Source of truth

Recovery Plan:
  1. Revert to last known good commit
  2. Run CD pipeline (auto-deploy)
  3. Or manually: terraform apply + manual deployment
  
RTO (Recovery Time Objective): ~10 minutes
RPO (Recovery Point Objective): Last commit


═══════════════════════════════════════════════════════════════════════════

Created by: CD Pipeline Setup
Version: 1.0
Last Updated: 2025-11-08
