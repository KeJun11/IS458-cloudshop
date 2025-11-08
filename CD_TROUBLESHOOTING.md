# CD Pipeline Troubleshooting Guide

Quick solutions to common deployment issues.

## 🔴 Pipeline Failures

### ❌ Error: "Terraform state lock"

**Symptom:**
```
Error: Error acquiring the state lock
Lock ID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

**Cause:** Previous Terraform run didn't complete properly

**Solution:**
```powershell
cd backend/terraform/envs/dev
terraform force-unlock LOCK_ID
# Replace LOCK_ID with the ID from error message
```

---

### ❌ Error: "InvalidAccessKeyId"

**Symptom:**
```
Error: The AWS Access Key Id you provided does not exist in our records
```

**Cause:** AWS credentials not set or incorrect

**Solution:**
1. Verify GitHub Secrets are set correctly:
   - Go to Settings → Secrets and variables → Actions
   - Check `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
2. Test credentials locally:
   ```powershell
   aws sts get-caller-identity
   ```

---

### ❌ Error: "Access Denied" during Terraform

**Symptom:**
```
Error: Error creating S3 bucket: AccessDenied
```

**Cause:** IAM user lacks required permissions

**Solution:**
Add these permissions to your CI/CD IAM user:
- S3: `s3:CreateBucket`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket`
- CloudFront: `cloudfront:CreateDistribution`, `cloudfront:UpdateDistribution`
- Lambda: `lambda:CreateFunction`, `lambda:UpdateFunctionCode`
- IAM: `iam:CreateRole`, `iam:AttachRolePolicy`
- DynamoDB: `dynamodb:CreateTable`, `dynamodb:PutItem`

See `.github/CD_SETUP_GUIDE.md` for complete IAM policy.

---

### ❌ Error: "BucketAlreadyExists"

**Symptom:**
```
Error: Error creating S3 bucket: BucketAlreadyExists
```

**Cause:** Bucket name collision (rare with random suffix)

**Solution:**
```powershell
cd backend/terraform/envs/dev
terraform destroy -target=random_id.bucket_suffix
terraform apply
```

---

### ❌ Error: "npm ERR! code ELIFECYCLE"

**Symptom:**
```
npm ERR! code ELIFECYCLE
npm ERR! errno 1
```

**Cause:** Frontend build failure

**Solution:**
1. Test build locally:
   ```powershell
   cd frontend
   npm install
   npm run build
   ```
2. Fix any TypeScript or build errors
3. Commit and push fixes

---

### ❌ Error: "No such file or directory: dist"

**Symptom:**
```
Error: Cannot find dist/ directory
```

**Cause:** Vite build didn't complete

**Solution:**
Check workflow uses correct build command:
```yaml
- name: Build Frontend
  run: npm run build
```

Not `npm run dev` (dev server doesn't create dist/)

---

## 🟡 Deployment Issues

### ⚠️ Issue: Frontend shows old content

**Symptom:** Changes not visible after deployment

**Cause:** CloudFront cache not invalidated or still propagating

**Solution 1 - Wait:**
CloudFront invalidation takes 3-5 minutes. Wait and refresh.

**Solution 2 - Manual invalidation:**
```powershell
# Get distribution ID
aws cloudfront list-distributions --query "DistributionList.Items[*].[Id,DomainName]" --output table

# Invalidate cache
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"
```

**Solution 3 - Hard refresh:**
- Chrome/Edge: `Ctrl + Shift + R`
- Firefox: `Ctrl + F5`
- Safari: `Cmd + Shift + R`

---

### ⚠️ Issue: API returns 404 or 500 errors

**Symptom:** Browser console shows API errors

**Cause 1:** API Gateway not deployed
**Solution:**
```powershell
cd backend/terraform/envs/dev
terraform apply -target=module.http_api
```

**Cause 2:** Lambda function error
**Solution:**
Check CloudWatch logs:
```powershell
aws logs tail /aws/lambda/aws-ecommerce-dev-get-products --follow
```

**Cause 3:** CORS issue
**Solution:**
Add CORS headers in Lambda response:
```python
return {
    'statusCode': 200,
    'headers': {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type'
    },
    'body': json.dumps(data)
}
```

---

### ⚠️ Issue: Products page is empty

**Symptom:** No products display on frontend

**Cause 1:** Seeder didn't run
**Solution:**
Run seeder manually:
```powershell
# Get table name from Terraform
cd backend/terraform/envs/dev
$TABLE_NAME = terraform output -raw dynamodb_tables | ConvertFrom-Json | Select-Object -ExpandProperty products

# Run seeder
python backend/scripts/seed_products.py --table-name $TABLE_NAME --region us-east-1
```

**Cause 2:** DynamoDB table empty
**Solution:**
Check table:
```powershell
aws dynamodb scan --table-name YOUR_TABLE_NAME --limit 5
```

**Cause 3:** Frontend not calling API
**Solution:**
Check browser DevTools → Network tab for API calls

---

### ⚠️ Issue: S3 sync fails with "Access Denied"

**Symptom:**
```
upload failed: dist/index.html to s3://bucket-name/index.html
An error occurred (AccessDenied)
```

**Cause:** IAM user lacks S3 permissions

**Solution:**
Add to IAM policy:
```json
{
  "Effect": "Allow",
  "Action": [
    "s3:PutObject",
    "s3:PutObjectAcl",
    "s3:DeleteObject",
    "s3:ListBucket"
  ],
  "Resource": [
    "arn:aws:s3:::*-frontend-*",
    "arn:aws:s3:::*-frontend-*/*"
  ]
}
```

---

## 🟢 Testing & Verification

### ✅ Test Terraform locally before pushing

```powershell
cd backend/terraform/envs/dev

# Initialize
terraform init

# Validate syntax
terraform validate

# Plan (see what will change)
terraform plan

# Apply if plan looks good
terraform apply
```

---

### ✅ Test Frontend build locally

```powershell
cd frontend

# Install dependencies
npm install

# Build
npm run build

# Verify dist/ folder created
ls dist/

# Preview build
npm run preview
```

---

### ✅ Test Seeder locally

```powershell
# Dry run (safe, doesn't write)
python backend/scripts/seed_products.py `
  --table-name test-table `
  --region us-east-1 `
  --dry-run

# Check output for any errors
```

---

### ✅ Verify AWS credentials

```powershell
# Check which AWS account you're using
aws sts get-caller-identity

# Test S3 access
aws s3 ls

# Test DynamoDB access
aws dynamodb list-tables
```

---

## 🔧 Manual Deployment Steps

If CD pipeline fails completely, deploy manually:

### 1. Deploy Infrastructure
```powershell
cd backend/terraform/envs/dev
terraform init
terraform plan
terraform apply
```

### 2. Get Outputs
```powershell
$OUTPUTS = terraform output -json | ConvertFrom-Json
$S3_BUCKET = $OUTPUTS.static_site_bucket.value
$API_ENDPOINT = $OUTPUTS.api_endpoint.value
$PRODUCTS_TABLE = $OUTPUTS.dynamodb_tables.value.products
```

### 3. Build Frontend
```powershell
cd ../../../frontend
echo "VITE_API_ENDPOINT=$API_ENDPOINT" > .env.production
npm install
npm run build
```

### 4. Deploy Frontend
```powershell
aws s3 sync dist/ s3://$S3_BUCKET --delete
```

### 5. Invalidate CloudFront
```powershell
$DIST_ID = aws cloudfront list-distributions --query "DistributionList.Items[?contains(Origins.Items[0].DomainName, '$S3_BUCKET')].Id" --output text
aws cloudfront create-invalidation --distribution-id $DIST_ID --paths "/*"
```

### 6. Seed Database
```powershell
cd ../backend/scripts
python seed_products.py --table-name $PRODUCTS_TABLE --region us-east-1
```

---

## 📊 Debugging Checklist

Use this checklist when things go wrong:

- [ ] **GitHub Actions logs**: View full output in Actions tab
- [ ] **AWS CloudWatch logs**: Check Lambda execution logs
- [ ] **Browser DevTools**: Console for errors, Network for API calls
- [ ] **Terraform state**: Verify `terraform show` output
- [ ] **S3 bucket**: Check files uploaded correctly
- [ ] **CloudFront**: Verify distribution is deployed
- [ ] **DynamoDB**: Verify tables exist and have data
- [ ] **API Gateway**: Test endpoints directly (Postman/curl)
- [ ] **IAM permissions**: Verify CI/CD user has required access
- [ ] **GitHub Secrets**: Confirm secrets are set correctly

---

## 🆘 Emergency Rollback

If deployment breaks production:

### Quick Rollback
```powershell
# Revert last commit
git revert HEAD
git push origin main
# CD pipeline will auto-deploy previous version
```

### Manual Rollback
```powershell
# Find previous working commit
git log --oneline

# Reset to that commit
git reset --hard COMMIT_HASH
git push --force origin main
```

**⚠️ Warning:** Force push overwrites history. Use only in emergencies.

---

## 📞 Getting Help

### Check Logs
1. **GitHub Actions**: Repo → Actions → Click failed workflow → View logs
2. **CloudWatch**: AWS Console → CloudWatch → Log groups → `/aws/lambda/FUNCTION_NAME`
3. **Browser**: DevTools (F12) → Console + Network tabs

### Useful Commands
```powershell
# View all Terraform outputs
cd backend/terraform/envs/dev
terraform output

# List S3 buckets
aws s3 ls

# List DynamoDB tables
aws dynamodb list-tables

# View CloudFront distributions
aws cloudfront list-distributions --output table

# Tail Lambda logs live
aws logs tail /aws/lambda/FUNCTION_NAME --follow

# Check API Gateway
aws apigatewayv2 get-apis --output table
```

### Common Questions

**Q: How long should deployment take?**  
A: 5-7 minutes. If >10 min, check for issues.

**Q: Can I run multiple deployments simultaneously?**  
A: No. Wait for current deployment to finish.

**Q: How do I skip steps in the pipeline?**  
A: You can't skip. Fix the failing step or deploy manually.

**Q: Can I rollback infrastructure changes?**  
A: Yes, but be careful. Revert Terraform code and re-run apply.

**Q: What if I accidentally deleted the S3 bucket?**  
A: Run `terraform apply` to recreate it.

---

## 🎓 Prevention Tips

### Before Every Push:
1. ✅ Test locally first
2. ✅ Run `terraform plan` to preview changes
3. ✅ Run `npm run build` to verify frontend builds
4. ✅ Commit descriptive messages
5. ✅ Push during low-traffic times for production

### Regular Maintenance:
- 🔄 Rotate AWS keys every 90 days
- 🔍 Review CloudWatch logs weekly
- 📊 Monitor AWS costs
- 🔒 Update IAM policies as needed
- 📦 Update dependencies regularly

---

**Still stuck?** Review these docs:
- Setup: `.github/CD_SETUP_GUIDE.md`
- Checklist: `CD_CHECKLIST.md`
- Summary: `CD_PIPELINE_SUMMARY.md`
