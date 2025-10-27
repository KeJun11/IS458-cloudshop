#!/usr/bin/env python3
"""
Script to seed the DynamoDB products table with initial product data.
This uploads the mock product data to your DynamoDB table.

Usage:
    python seed_products.py --table-name <table-name> [--region <region>]
    
Example:
    python seed_products.py --table-name aws-ecommerce-dev-products --region us-east-1
"""

import argparse
import boto3
from decimal import Decimal
import json

# Mock product data (matching your frontend mockProducts)
MOCK_PRODUCTS = [
    {
        "productId": "prod-1",
        "name": "Wireless Bluetooth Headphones",
        "description": "High-quality wireless headphones with noise cancellation",
        "price": Decimal("199.99"),
        "category": "Electronics",
        "imageUrl": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "stock": 50,
    },
    {
        "productId": "prod-2",
        "name": "Smart Watch",
        "description": "Feature-rich smartwatch with health tracking",
        "price": Decimal("299.99"),
        "category": "Electronics",
        "imageUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500",
        "stock": 30,
    },
    {
        "productId": "prod-3",
        "name": "Laptop Backpack",
        "description": "Durable laptop backpack with multiple compartments",
        "price": Decimal("79.99"),
        "category": "Accessories",
        "imageUrl": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=500",
        "stock": 100,
    },
    {
        "productId": "prod-4",
        "name": "Wireless Mouse",
        "description": "Ergonomic wireless mouse with precision tracking",
        "price": Decimal("49.99"),
        "category": "Electronics",
        "imageUrl": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500",
        "stock": 75,
    },
    {
        "productId": "prod-5",
        "name": "USB-C Hub",
        "description": "Multi-port USB-C hub with HDMI and charging support",
        "price": Decimal("89.99"),
        "category": "Electronics",
        "imageUrl": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=500",
        "stock": 40,
    },
    {
        "productId": "prod-6",
        "name": "Portable Charger",
        "description": "20000mAh portable battery pack with fast charging",
        "price": Decimal("39.99"),
        "category": "Electronics",
        "imageUrl": "https://images.unsplash.com/photo-1609592806955-d5b6c3b2e3c5?w=500",
        "stock": 60,
    },
]


def seed_products(table_name, region="us-east-1", dry_run=False):
    """
    Seed the DynamoDB products table with mock data.
    
    Args:
        table_name: Name of the DynamoDB table
        region: AWS region (default: us-east-1)
        dry_run: If True, only print what would be done without actually inserting
    """
    print(f"{'[DRY RUN] ' if dry_run else ''}Seeding products table: {table_name}")
    print(f"Region: {region}")
    print(f"Number of products to insert: {len(MOCK_PRODUCTS)}\n")
    
    if dry_run:
        print("Products that would be inserted:")
        for product in MOCK_PRODUCTS:
            print(f"  - {product['productId']}: {product['name']} (${product['price']})")
        print("\nRun without --dry-run to actually insert the data.")
        return
    
    # Initialize DynamoDB client
    dynamodb = boto3.resource('dynamodb', region_name=region)
    table = dynamodb.Table(table_name)
    
    # Insert products
    success_count = 0
    error_count = 0
    
    for product in MOCK_PRODUCTS:
        try:
            table.put_item(Item=product)
            print(f"✓ Inserted: {product['productId']} - {product['name']}")
            success_count += 1
        except Exception as e:
            print(f"✗ Failed to insert {product['productId']}: {str(e)}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Seeding completed!")
    print(f"  Successful: {success_count}")
    print(f"  Failed: {error_count}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="Seed DynamoDB products table with initial data"
    )
    parser.add_argument(
        "--table-name",
        required=True,
        help="Name of the DynamoDB products table"
    )
    parser.add_argument(
        "--region",
        default="us-east-1",
        help="AWS region (default: us-east-1)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without actually inserting data"
    )
    
    args = parser.parse_args()
    
    seed_products(
        table_name=args.table_name,
        region=args.region,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
