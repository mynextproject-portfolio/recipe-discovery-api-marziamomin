#!/usr/bin/env python3
"""
Test runner script for Recipe Discovery API integration tests
"""
import subprocess
import sys

def run_tests():
    """Run all integration tests using pytest"""
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest", 
            "test_integration.py", 
            "-v", 
            "--tb=short"
        ], check=True)
        print("\nAll tests passed!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nTests failed with exit code {e.returncode}")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
