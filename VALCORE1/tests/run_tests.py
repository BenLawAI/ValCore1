#!/usr/bin/env python3
"""
VALCORE1 Test Runner
Run all unit and integration tests with reporting
"""

import sys
import unittest
from pathlib import Path

# Add VALCORE1 to Python path
valcore_root = Path(__file__).parent.parent
sys.path.insert(0, str(valcore_root))


def run_all_tests(verbosity=2):
    """
    Run all tests with specified verbosity

    Args:
        verbosity: Test verbosity level (0=quiet, 1=normal, 2=verbose)

    Returns:
        TestResult object
    """
    # Discover and run all tests
    loader = unittest.TestLoader()
    tests_dir = Path(__file__).parent

    # Load unit tests
    unit_tests = loader.discover(str(tests_dir / 'unit'), pattern='test_*.py')

    # Load integration tests
    integration_tests = loader.discover(str(tests_dir / 'integration'), pattern='test_*.py')

    # Combine all tests
    all_tests = unittest.TestSuite([unit_tests, integration_tests])

    # Run tests
    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(all_tests)

    return result


def run_unit_tests_only(verbosity=2):
    """Run only unit tests"""
    loader = unittest.TestLoader()
    tests_dir = Path(__file__).parent

    unit_tests = loader.discover(str(tests_dir / 'unit'), pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(unit_tests)

    return result


def run_integration_tests_only(verbosity=2):
    """Run only integration tests"""
    loader = unittest.TestLoader()
    tests_dir = Path(__file__).parent

    integration_tests = loader.discover(str(tests_dir / 'integration'), pattern='test_*.py')

    runner = unittest.TextTestRunner(verbosity=verbosity)
    result = runner.run(integration_tests)

    return result


def print_summary(result):
    """Print test summary"""
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED")
        print("="*70)
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("="*70)
        return 1


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run VALCORE1 tests')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--verbose', '-v', action='count', default=2, help='Increase verbosity')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')

    args = parser.parse_args()

    # Set verbosity
    verbosity = 0 if args.quiet else args.verbose

    # Run appropriate tests
    if args.unit:
        print("\n🧪 Running Unit Tests Only...")
        result = run_unit_tests_only(verbosity)
    elif args.integration:
        print("\n🔗 Running Integration Tests Only...")
        result = run_integration_tests_only(verbosity)
    else:
        print("\n🧪 Running All Tests...")
        result = run_all_tests(verbosity)

    # Print summary and exit
    exit_code = print_summary(result)
    sys.exit(exit_code)
