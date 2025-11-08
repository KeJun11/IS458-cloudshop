# Terraform Remote State Setup
# Run this ONCE to create the S3 bucket and DynamoDB table for storing Terraform state

# 1. Create S3 bucket for state storage
Write-Host "Creating S3 bucket for Terraform state..." -ForegroundColor Yellow
aws s3api create-bucket `
    --bucket is458-cloudshop-terraform-state `
    --region us-east-1

# 2. Enable versioning on the bucket
Write-Host "Enabling versioning..." -ForegroundColor Yellow
aws s3api put-bucket-versioning `
    --bucket is458-cloudshop-terraform-state `
    --versioning-configuration Status=Enabled

# 3. Enable encryption
Write-Host "Enabling encryption..." -ForegroundColor Yellow
aws s3api put-bucket-encryption `
    --bucket is458-cloudshop-terraform-state `
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

# 4. Block public access
Write-Host "Blocking public access..." -ForegroundColor Yellow
aws s3api put-public-access-block `
    --bucket is458-cloudshop-terraform-state `
    --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# 5. Create DynamoDB table for state locking
Write-Host "Creating DynamoDB table for state locking..." -ForegroundColor Yellow
aws dynamodb create-table `
    --table-name is458-cloudshop-terraform-locks `
    --attribute-definitions AttributeName=LockID,AttributeType=S `
    --key-schema AttributeName=LockID,KeyType=HASH `
    --billing-mode PAY_PER_REQUEST `
    --region us-east-1

Write-Host ""
Write-Host "✅ Remote state infrastructure created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Run: cd backend/terraform/envs/dev"
Write-Host "2. Run: terraform init -migrate-state"
Write-Host "3. Type 'yes' when prompted to migrate existing state to S3"
Write-Host ""
