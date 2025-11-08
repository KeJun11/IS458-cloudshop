# 🚀 Quick Start: Continuous Deployment

## ⚡ Setup (One-time, 5 minutes)

### 1️⃣ Add GitHub Secrets
Go to: **GitHub Repository → Settings → Secrets and variables → Actions**

Click **New repository secret** and add these 3 secrets:

```
AWS_ACCESS_KEY_ID        →  AKIA...your-key-id
AWS_SECRET_ACCESS_KEY    →  wJal...your-secret-key
AWS_REGION              →  us-east-1
```

### 2️⃣ Done! 🎉

That's it. Your CD pipeline is now active.

---

## 🔄 Daily Workflow

### Make changes and deploy:

```powershell
# 1. Make your changes to code
# 2. Commit and push to main
git add .
git commit -m "feat: your changes"
git push origin main

# 3. Watch deployment at:
# https://github.com/KeJun11/IS458-cloudshop/actions
```

### What happens automatically:

```
Push to main
    ↓
✅ Terraform creates/updates infrastructure
    ↓
✅ Frontend builds with new API endpoint
    ↓
✅ Files deploy to S3
    ↓
✅ CloudFront cache clears
    ↓
✅ Database seeds with products
    ↓
🎉 LIVE! Visit CloudFront URL
```

---

## 📋 Pipeline Output

After deployment completes, you'll see:

```
✅ DEPLOYMENT COMPLETED SUCCESSFULLY
🌐 Frontend URL: https://d1234abc.cloudfront.net
🔗 API Endpoint: https://xyz123.execute-api.us-east-1.amazonaws.com
📦 S3 Bucket: aws-ecommerce-dev-frontend-is458-2025-abc123
🗃️  Products Table: aws-ecommerce-dev-products
```

Click the Frontend URL to see your live site! 🌐

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| ❌ Pipeline fails | Check Actions tab → View logs |
| ❌ Old content shows | Wait 5 min for CloudFront, or manually invalidate |
| ❌ API errors | Check Lambda logs in CloudWatch |
| ❌ No products | Re-run seeder: `python backend/scripts/seed_products.py --table-name TABLE_NAME --region us-east-1` |

---

## 🧪 Test Before Pushing

```powershell
# Test Terraform
cd backend/terraform/envs/dev
terraform plan

# Test Frontend Build
cd frontend
npm install
npm run build

# Test Seeder (dry-run)
python backend/scripts/seed_products.py --table-name TEMP_TABLE --region us-east-1 --dry-run
```

---

## 📁 Files Created

```
.github/
├── workflows/
│   ├── cd-pipeline.yml    ← Main CD workflow
│   └── README.md          ← Workflow documentation
└── CD_SETUP_GUIDE.md      ← Detailed setup guide
```

---

## 🔒 Security Notes

- ✅ AWS credentials stored in GitHub Secrets (encrypted)
- ✅ Never commit credentials to code
- ✅ Use IAM user with minimal permissions
- ✅ Rotate keys every 90 days

---

## 🎯 Next Steps

1. **Add your GitHub secrets** (see step 1 above)
2. **Push a change** to test the pipeline
3. **Visit your CloudFront URL** to see the live site
4. **Monitor** the Actions tab during deployment

---

## 💡 Pro Tips

- Use **feature branches** and merge via PR
- Watch the **Actions tab** during deployment
- Check **CloudWatch Logs** for Lambda errors
- **Manual trigger**: Actions tab → Continuous Deployment Pipeline → Run workflow

---

## 📞 Quick Commands

```powershell
# View Terraform outputs
cd backend/terraform/envs/dev
terraform output

# Sync frontend manually
aws s3 sync frontend/dist s3://YOUR-BUCKET --delete

# Invalidate CloudFront manually
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"

# Seed database manually
python backend/scripts/seed_products.py --table-name YOUR_TABLE --region us-east-1

# View Lambda logs
aws logs tail /aws/lambda/FUNCTION_NAME --follow
```

---

**Need help?** Check `.github/CD_SETUP_GUIDE.md` for detailed troubleshooting.
