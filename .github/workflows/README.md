# GitHub Actions Workflows

## CD Pipeline

This workflow automatically deploys your application when you push to the `main` branch.

### What it does:

1. **Terraform Infrastructure** - Provisions/updates AWS infrastructure
2. **Build Frontend** - Compiles React app with Vite
3. **Deploy to S3** - Syncs build files to S3 bucket
4. **Update API Endpoint** - Configures frontend with new API URL
5. **Seed Database** - Populates DynamoDB with product data
6. **Invalidate Cache** - Clears CloudFront cache

### Required GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM secret key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region for deployment | `us-east-1` |

### Required IAM Permissions

Your AWS credentials need permissions for:

- **Terraform**: Full access to manage resources (S3, Lambda, API Gateway, DynamoDB, CloudFront, SES, SQS, IAM roles)
- **S3**: `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket`, `s3:GetObject`
- **CloudFront**: `cloudfront:CreateInvalidation`, `cloudfront:ListDistributions`
- **DynamoDB**: `dynamodb:PutItem`, `dynamodb:BatchWriteItem`

### Manual Trigger

You can also trigger the deployment manually:

1. Go to **Actions** tab
2. Select **Continuous Deployment Pipeline**
3. Click **Run workflow**
4. Select `main` branch
5. Click **Run workflow**

### Testing Locally

Before pushing to `main`, test each step locally:

```powershell
# 1. Terraform
cd backend/terraform/envs/dev
terraform init
terraform plan
terraform apply

# 2. Frontend build
cd frontend
npm install
npm run build

# 3. Seed database (dry-run)
python backend/scripts/seed_products.py --table-name YOUR_TABLE_NAME --region us-east-1 --dry-run
```

### Troubleshooting

**Pipeline fails at Terraform step:**
- Check that AWS credentials are valid
- Ensure IAM permissions are sufficient
- Review Terraform state file isn't corrupted

**Frontend deployment fails:**
- Verify S3 bucket exists and is accessible
- Check build completed successfully
- Ensure CloudFront distribution is configured

**Seeding fails:**
- Confirm DynamoDB table exists
- Check IAM permissions for DynamoDB
- Verify table name in Terraform outputs

**API endpoint not updating:**
- Check `.env.production` file is created during build
- Ensure frontend code reads `import.meta.env.VITE_API_ENDPOINT`
- Verify CloudFront cache was invalidated
