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
    # Existing Electronics
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

    # 🏠 Home & Kitchen
    {
        "productId": "prod-7",
        "name": "Aromatherapy Diffuser",
        "description": "Ultrasonic essential oil diffuser with 7-color LED lights",
        "price": Decimal("45.00"),
        "category": "Home & Kitchen",
        "imageUrl": "https://images.unsplash.com/photo-1606813909022-5e3c8f1a2bdf?w=500",
        "stock": 80,
    },
    {
        "productId": "prod-8",
        "name": "Non-Stick Frying Pan",
        "description": "Durable non-stick frying pan with ergonomic handle",
        "price": Decimal("32.99"),
        "category": "Home & Kitchen",
        "imageUrl": "https://images.unsplash.com/photo-1606755962773-0ff9a4c62007?w=500",
        "stock": 100,
    },
    {
        "productId": "prod-9",
        "name": "Electric Kettle",
        "description": "1.7L stainless steel electric kettle with auto shut-off",
        "price": Decimal("59.99"),
        "category": "Home & Kitchen",
        "imageUrl": "https://images.unsplash.com/photo-1586201375754-2637e6a3e89b?w=500",
        "stock": 50,
    },

    # 👕 Fashion
    {
        "productId": "prod-10",
        "name": "Classic Denim Jacket",
        "description": "Timeless unisex denim jacket with a modern cut",
        "price": Decimal("89.99"),
        "category": "Fashion",
        "imageUrl": "https://images.unsplash.com/photo-1514996937319-344454492b37?w=500",
        "stock": 60,
    },
    {
        "productId": "prod-11",
        "name": "White Sneakers",
        "description": "Minimalist white sneakers made from vegan leather",
        "price": Decimal("109.99"),
        "category": "Fashion",
        "imageUrl": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
        "stock": 45,
    },
    {
        "productId": "prod-12",
        "name": "Cotton Hoodie",
        "description": "Soft cotton hoodie for casual everyday wear",
        "price": Decimal("69.99"),
        "category": "Fashion",
        "imageUrl": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=500",
        "stock": 75,
    },

    # ⚽ Sports & Outdoors
    {
        "productId": "prod-13",
        "name": "Yoga Mat",
        "description": "Eco-friendly non-slip yoga mat for all levels",
        "price": Decimal("39.99"),
        "category": "Sports & Outdoors",
        "imageUrl": "https://images.unsplash.com/photo-1599058917212-d750089bc07c?w=500",
        "stock": 120,
    },
    {
        "productId": "prod-14",
        "name": "Hiking Backpack",
        "description": "Water-resistant hiking backpack with 40L capacity",
        "price": Decimal("99.99"),
        "category": "Sports & Outdoors",
        "imageUrl": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=500",
        "stock": 35,
    },
    {
        "productId": "prod-15",
        "name": "Stainless Steel Water Bottle",
        "description": "Insulated water bottle that keeps drinks cold for 24h",
        "price": Decimal("29.99"),
        "category": "Sports & Outdoors",
        "imageUrl": "https://images.unsplash.com/photo-1586864387967-d02ef85d93e0?w=500",
        "stock": 200,
    },

    # 💄 Beauty & Personal Care
    {
        "productId": "prod-16",
        "name": "Facial Cleanser",
        "description": "Gentle foaming cleanser for all skin types",
        "price": Decimal("25.99"),
        "category": "Beauty & Personal Care",
        "imageUrl": "https://images.unsplash.com/photo-1583241800054-4e94d3d2d30d?w=500",
        "stock": 90,
    },
    {
        "productId": "prod-17",
        "name": "Moisturizing Lotion",
        "description": "Hydrating lotion with aloe vera and vitamin E",
        "price": Decimal("19.99"),
        "category": "Beauty & Personal Care",
        "imageUrl": "https://images.unsplash.com/photo-1612817159949-195b2c98f84e?w=500",
        "stock": 110,
    },
    {
        "productId": "prod-18",
        "name": "Hair Dryer",
        "description": "Compact ionic hair dryer with 3 heat settings",
        "price": Decimal("79.99"),
        "category": "Beauty & Personal Care",
        "imageUrl": "https://images.unsplash.com/photo-1603297631963-6fc46f4ee5c3?w=500",
        "stock": 70,
    }
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
