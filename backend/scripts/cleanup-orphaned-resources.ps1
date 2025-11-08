# AWS Orphaned Resource Cleanup Script
# Deletes resources that are no longer tracked in Terraform state

$PROJECT = "test"
$ENV = "dev"
$REGION = "us-east-1"

Write-Host "=================================================="-ForegroundColor Yellow
Write-Host "AWS RESOURCE CLEANUP SCRIPT" -ForegroundColor Yellow
Write-Host "==================================================" -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Type 'DELETE' to confirm deletion of all resources"

if ($confirm -ne "DELETE") {
    Write-Host "Deletion cancelled." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting cleanup..." -ForegroundColor Yellow

# 1. Lambda Functions
Write-Host ""
Write-Host "Deleting Lambda Functions..." -ForegroundColor Cyan
$lambdas = @("get-products", "manage-cart", "create-order", "process-order", "track-event", "get-recommendations")
foreach ($lambda in $lambdas) {
    Write-Host "  Deleting $PROJECT-$ENV-$lambda..." -NoNewline
    aws lambda delete-function --function-name "$PROJECT-$ENV-$lambda" --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Skipped" -ForegroundColor Gray }
}

# 2. API Gateway
Write-Host ""
Write-Host "Deleting API Gateway..." -ForegroundColor Cyan
$apiId = aws apigatewayv2 get-apis --region $REGION 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty Items | Where-Object { $_.Name -eq "$PROJECT-$ENV-http-api" } | Select-Object -ExpandProperty ApiId -First 1
if ($apiId) {
    Write-Host "  Deleting API $apiId..." -NoNewline
    aws apigatewayv2 delete-api --api-id $apiId --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Failed" -ForegroundColor Red }
} else {
    Write-Host "  API not found" -ForegroundColor Gray
}

# 3. S3 Buckets
Write-Host ""
Write-Host "Deleting S3 Buckets..." -ForegroundColor Cyan
$allBuckets = aws s3api list-buckets 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty Buckets | Select-Object -ExpandProperty Name

$frontendBucket = $allBuckets | Where-Object { $_ -like "$PROJECT-$ENV-frontend*" } | Select-Object -First 1
if ($frontendBucket) {
    Write-Host "  Emptying $frontendBucket..." -NoNewline
    aws s3 rm "s3://$frontendBucket" --recursive 2>$null
    Write-Host " Done" -ForegroundColor Green
    Write-Host "  Deleting $frontendBucket..." -NoNewline
    aws s3api delete-bucket --bucket $frontendBucket --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Failed" -ForegroundColor Red }
}

$invoiceBucket = $allBuckets | Where-Object { $_ -like "$PROJECT-$ENV-invoices*" } | Select-Object -First 1
if ($invoiceBucket) {
    Write-Host "  Emptying $invoiceBucket..." -NoNewline
    aws s3 rm "s3://$invoiceBucket" --recursive 2>$null
    Write-Host " Done" -ForegroundColor Green
    Write-Host "  Deleting $invoiceBucket..." -NoNewline
    aws s3api delete-bucket --bucket $invoiceBucket --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Failed" -ForegroundColor Red }
}

# 4. DynamoDB Tables
Write-Host ""
Write-Host "Deleting DynamoDB Tables..." -ForegroundColor Cyan
$tables = @("products", "carts", "orders", "user-interactions")
foreach ($table in $tables) {
    Write-Host "  Deleting $PROJECT-$ENV-$table..." -NoNewline
    aws dynamodb delete-table --table-name "$PROJECT-$ENV-$table" --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Skipped" -ForegroundColor Gray }
}

# 5. SQS Queues
Write-Host ""
Write-Host "Deleting SQS Queues..." -ForegroundColor Cyan
$queueUrl = aws sqs get-queue-url --queue-name "order-processing-$ENV" --region $REGION 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty QueueUrl
if ($queueUrl) {
    Write-Host "  Deleting main queue..." -NoNewline
    aws sqs delete-queue --queue-url $queueUrl --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Failed" -ForegroundColor Red }
}

$dlqUrl = aws sqs get-queue-url --queue-name "order-processing-dlq-$ENV" --region $REGION 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty QueueUrl
if ($dlqUrl) {
    Write-Host "  Deleting DLQ..." -NoNewline
    aws sqs delete-queue --queue-url $dlqUrl --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Failed" -ForegroundColor Red }
}

# 6. CloudWatch Resources
Write-Host ""
Write-Host "Deleting CloudWatch Resources..." -ForegroundColor Cyan
Write-Host "  Deleting dashboard..." -NoNewline
aws cloudwatch delete-dashboards --dashboard-names "$PROJECT-$ENV-monitoring" --region $REGION 2>$null
if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Skipped" -ForegroundColor Gray }

Write-Host "  Deleting alarms..." -NoNewline
aws cloudwatch delete-alarms --alarm-names "$PROJECT-$ENV-api-5xx-errors" "$PROJECT-$ENV-lambda-high-errors" "$PROJECT-$ENV-dynamodb-system-errors" "$PROJECT-$ENV-sqs-high-queue-depth" "$PROJECT-$ENV-sqs-dlq-messages" --region $REGION 2>$null
if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Skipped" -ForegroundColor Gray }

# Delete Lambda Log Groups
foreach ($lambda in $lambdas) {
    Write-Host "  Deleting /aws/lambda/$PROJECT-$ENV-$lambda logs..." -NoNewline
    aws logs delete-log-group --log-group-name "/aws/lambda/$PROJECT-$ENV-$lambda" --region $REGION 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Skipped" -ForegroundColor Gray }
}

# 7. IAM Roles
Write-Host ""
Write-Host "Deleting IAM Roles..." -ForegroundColor Cyan
foreach ($lambda in $lambdas) {
    $roleName = "$PROJECT-$ENV-$lambda-role"
    Write-Host "  Deleting $roleName..." -NoNewline
    
    # Delete inline policies first
    $policies = aws iam list-role-policies --role-name $roleName 2>$null | ConvertFrom-Json | Select-Object -ExpandProperty PolicyNames
    foreach ($policy in $policies) {
        aws iam delete-role-policy --role-name $roleName --policy-name $policy 2>$null
    }
    
    # Delete the role
    aws iam delete-role --role-name $roleName 2>$null
    if ($?) { Write-Host " Done" -ForegroundColor Green } else { Write-Host " Skipped" -ForegroundColor Gray }
}

# 8. CloudFront (manual)
Write-Host ""
Write-Host "CloudFront Distribution..." -ForegroundColor Cyan
Write-Host "  CloudFront must be disabled first, then deleted manually" -ForegroundColor Yellow
Write-Host "  Check AWS Console > CloudFront to disable and delete" -ForegroundColor Yellow

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "CLEANUP COMPLETED" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Verify deletion in AWS Console" -ForegroundColor Cyan
Write-Host ""
