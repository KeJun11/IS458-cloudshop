# Database Seeding Scripts

This directory contains scripts to seed your DynamoDB tables with initial data.

## Prerequisites

1. **AWS Credentials**: Ensure your AWS credentials are configured

   ```bash
   aws configure
   ```

2. **Python Dependencies**: Install boto3

   ```bash
   pip install boto3
   ```

3. **DynamoDB Table**: Your products table must already be created (via Terraform)

## Get Your Table Name

To find your products table name, run one of these commands:

```bash
# Option 1: From Terraform outputs
cd ../terraform/envs/dev
terraform output dynamodb_tables

# Option 2: Using AWS CLI
aws dynamodb list-tables --region us-east-1
```

The table name should be something like: `aws-ecommerce-dev-products`

## Usage

### Dry Run (Preview)

First, run in dry-run mode to see what would be inserted:

```bash
python seed_products.py --table-name test-dev-products --region us-east-1 --dry-run
```

### Actual Seeding

Once you're satisfied, run without `--dry-run`:

```bash
python seed_products.py --table-name test-dev-products --region us-east-1
```

### Using Default Region

If your region is us-east-1, you can omit the `--region` parameter:

```bash
python seed_products.py --table-name test-dev-products
```

## What Gets Seeded

The script will insert 6 products:

- prod-1: Wireless Bluetooth Headphones ($199.99)
- prod-2: Smart Watch ($299.99)
- prod-3: Laptop Backpack ($79.99)
- prod-4: Wireless Mouse ($49.99)
- prod-5: USB-C Hub ($89.99)
- prod-6: Portable Charger ($39.99)

## Verify the Data

After seeding, verify the products were inserted:

```bash
aws dynamodb scan --table-name aws-ecommerce-dev-products --region us-east-1
```

Or test via your API endpoint:

```bash
curl https://your-api-endpoint/products
```

## Troubleshooting

### Permission Denied

Ensure your AWS credentials have `dynamodb:PutItem` permission on the table.

### Table Not Found

Check that your table name is correct and the table exists in the specified region.

### Already Exists

The script uses `put_item` which will overwrite existing items with the same `productId`.
