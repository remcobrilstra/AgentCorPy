#!/usr/bin/env python3
"""
Test Runner for AgentCorp Framework

This script runs all test suites for the AgentCorp framework.
Run with: python run_tests.py
"""

import os
import sys
import subprocess
from pathlib import Path

def run_test_file(test_file_path, description):
    """Run a single test file and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"File: {test_file_path}")
    print('='*60)

    try:
        # Set PYTHONPATH to include the project root
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent)

        # Run the test file
        result = subprocess.run([
            sys.executable, str(test_file_path)
        ], capture_output=True, text=True, cwd=Path(__file__).parent, env=env)

        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")

        return success

    except Exception as e:
        print(f"❌ ERROR running {description}: {e}")
        return False

def main():
    """Run all test suites"""
    print("🚀 AgentCorp Framework Test Runner")
    print("=" * 50)

    # Get the project root directory
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"

    # Define test files to run
    test_files = [
        (tests_dir / "test_framework.py", "Framework Core Tests"),
        (tests_dir / "test_filesystem_tools.py", "Filesystem Tools Tests"),
        (tests_dir / "test_filesystem_tools_integration.py", "Filesystem Tools Integration Tests"),
        (tests_dir / "test_terminal_tools.py", "Terminal Tools Tests"),
        (tests_dir / "test_agent.py", "Agent and Prompt Tests"),
    ]

    # Check if test files exist
    missing_files = []
    for test_file, _ in test_files:
        if not test_file.exists():
            missing_files.append(test_file)

    if missing_files:
        print("❌ Missing test files:")
        for missing in missing_files:
            print(f"  - {missing}")
        return False

    # Run all tests
    results = []
    for test_file, description in test_files:
        success = run_test_file(test_file, description)
        results.append((description, success))

    # Summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print('='*60)

    passed = 0
    total = len(results)

    for description, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {description}")
        if success:
            passed += 1

    print(f"\nResults: {passed}/{total} test suites passed")

    if passed == total:
        print("🎉 All tests passed!")
        return True
    else:
        print("❌ Some tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)