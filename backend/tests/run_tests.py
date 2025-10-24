#!/usr/bin/env python3
"""
Test Runner for IS458 CloudShop API Tests
"""

import subprocess
import sys
import os

def run_order_debug_test():
    """Run just the order creation test for debugging"""
    print("🧪 Running Order Creation Debug Test...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "test_api_routes.py", "debug-order"
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running debug test: {e}")
        return False

def run_full_tests():
    """Run all pytest tests"""
    print("🧪 Running Full API Test Suite...")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", "test_api_routes.py", "-v", "--tb=short"
        ], cwd=os.path.dirname(__file__))
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running full tests: {e}")
        return False

def run_specific_test(test_name):
    """Run a specific test class or method"""
    print(f"🧪 Running Specific Test: {test_name}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", f"test_api_routes.py::{test_name}", "-v", "-s"
        ], cwd=os.path.dirname(__file__))
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running specific test: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "debug":
            success = run_order_debug_test()
        elif command == "full":
            success = run_full_tests()
        elif command.startswith("test"):
            success = run_specific_test(sys.argv[1])
        else:
            print("❌ Unknown command")
            success = False
    else:
        print("Available commands:")
        print("  python run_tests.py debug     - Run order creation debug test")
        print("  python run_tests.py full      - Run all tests")
        print("  python run_tests.py TestOrdersAPI - Run specific test class")
        print("  python run_tests.py TestOrdersAPI::test_create_order - Run specific test method")
        success = True
    
    sys.exit(0 if success else 1)
