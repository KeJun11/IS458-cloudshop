# CD Pipeline Pre-Flight Checklist

Use this checklist before your first deployment to ensure everything is configured correctly.

## ✅ Pre-Deployment Checklist

### AWS Configuration

- [ ] **AWS Account**: You have access to an AWS account
- [ ] **IAM User Created**: Created IAM user for CI/CD with programmatic access
- [ ] **Access Keys Generated**: Saved AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
- [ ] **IAM Permissions**: Attached policy with permissions for:
  - [ ] S3 (create, read, write, delete)
  - [ ] CloudFront (create distributions, invalidations)
  - [ ] Lambda (create, update functions)
  - [ ] API Gateway (create, configure APIs)
  - [ ] DynamoDB (create tables, put items)
  - [ ] SQS (create queues)
  - [ ] SES (configure email)
  - [ ] IAM (create roles for Lambda)
  - [ ] CloudWatch Logs

### GitHub Configuration

- [ ] **Repository**: Code pushed to GitHub (KeJun11/IS458-cloudshop)
- [ ] **GitHub Secrets Set**: Added three secrets:
  - [ ] `AWS_ACCESS_KEY_ID`
  - [ ] `AWS_SECRET_ACCESS_KEY`
  - [ ] `AWS_REGION` (e.g., `us-east-1`)
- [ ] **Workflow File Exists**: `.github/workflows/cd-pipeline.yml` is present
- [ ] **Main Branch Protected** (optional): Set up branch protection rules

### Local Testing

- [ ] **Terraform Works Locally**:
  ```powershell
  cd backend/terraform/envs/dev
  terraform init
  terraform plan
  # If errors, fix before pushing
  ```

- [ ] **Frontend Builds Locally**:
  ```powershell
  cd frontend
  npm install
  npm run build
  # Check dist/ folder exists
  ```

- [ ] **Seeder Script Works**:
  ```powershell
  python backend/scripts/seed_products.py --table-name test-table --region us-east-1 --dry-run
  # Should print product data without errors
  ```

### Infrastructure Verification

- [ ] **Terraform Outputs Defined**: Check `backend/terraform/envs/dev/outputs.tf` has:
  - [ ] `static_site_bucket`
  - [ ] `api_endpoint`
  - [ ] `dynamodb_tables`
  - [ ] `cloudfront_domain`

- [ ] **S3 Bucket Configured**: Terraform creates S3 bucket for frontend
- [ ] **CloudFront Configured**: Terraform creates CloudFront distribution
- [ ] **API Gateway Configured**: Terraform creates HTTP API
- [ ] **Lambda Functions Configured**: All Lambda functions defined in Terraform
- [ ] **DynamoDB Tables Configured**: Products, carts, orders, interactions tables

### Frontend Configuration

- [ ] **API Endpoint Variable**: `api.ts` uses `import.meta.env.VITE_API_ENDPOINT`
- [ ] **Build Output**: Vite builds to `dist/` directory (default)
- [ ] **Environment Variables**: Frontend reads from `.env.production` during build

### Backend Configuration

- [ ] **Lambda Functions**: All Lambda code exists in `backend/lambdas/`
- [ ] **Dependencies**: Each Lambda has `requirements.txt`
- [ ] **Seeder Script**: `backend/scripts/seed_products.py` has CLI args support
- [ ] **Product Data**: MOCK_PRODUCTS array has valid image URLs

## 🚀 Ready to Deploy?

If all items above are checked, you're ready! 

### First Deployment Steps:

1. **Commit the workflow files**:
   ```powershell
   git add .github/
   git commit -m "ci: add continuous deployment pipeline"
   git push origin main
   ```

2. **Monitor the deployment**:
   - Go to: https://github.com/KeJun11/IS458-cloudshop/actions
   - Click on the running workflow
   - Watch each step complete

3. **Get your URLs**:
   - After deployment, copy the Frontend URL from the summary
   - Visit the URL to see your live application

4. **Verify functionality**:
   - [ ] Frontend loads
   - [ ] Products display
   - [ ] Can add to cart
   - [ ] Can view cart
   - [ ] Can checkout
   - [ ] Recommendations work

## 🐛 Common First-Time Issues

### Issue: Terraform state conflict
**Symptom**: "Error acquiring the state lock"
**Solution**: 
```powershell
cd backend/terraform/envs/dev
terraform force-unlock LOCK_ID
```

### Issue: S3 bucket name already exists
**Symptom**: "BucketAlreadyExists"
**Solution**: Change bucket name in `backend/terraform/envs/dev/main.tf` (random_id should prevent this)

### Issue: IAM permissions denied
**Symptom**: "User is not authorized to perform: iam:CreateRole"
**Solution**: Add IAM permissions to CI/CD user (see CD_SETUP_GUIDE.md)

### Issue: Frontend shows old content
**Symptom**: Changes not visible after deployment
**Solution**: Wait 5 minutes for CloudFront, or manually invalidate cache

### Issue: No products showing
**Symptom**: Empty products page
**Solution**: Check seeder ran successfully in Actions logs, or run manually

## 📊 Post-Deployment Verification

After first successful deployment:

- [ ] **Visit Frontend URL**: Site loads correctly
- [ ] **Check API**: Browser DevTools → Network tab shows API calls
- [ ] **View Products**: Products page displays items with images
- [ ] **Test Cart**: Can add/remove items
- [ ] **Test Checkout**: Can place an order
- [ ] **Check DynamoDB**: Products table populated
- [ ] **Review CloudWatch**: Lambda logs show successful executions

## 🎯 Success Criteria

Your CD pipeline is working correctly if:

✅ Push to main triggers automatic deployment  
✅ Terraform applies without errors  
✅ Frontend builds successfully  
✅ Files sync to S3  
✅ CloudFront serves the site  
✅ API endpoints respond  
✅ Database has product data  
✅ Application is fully functional  

## 📝 Notes

- First deployment takes ~5-10 minutes
- Subsequent deployments take ~3-5 minutes
- CloudFront cache can take up to 5 minutes to invalidate
- Lambda cold starts may cause first API calls to be slow

---

**Ready?** Go to `QUICK_START_CD.md` for deployment instructions!
