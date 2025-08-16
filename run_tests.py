#!/usr/bin/env python3
"""
Test runner for the Claude Sessions Manager.

This script runs all tests using Python's built-in unittest framework.
"""

import argparse
import sys
import unittest
from pathlib import Path


def discover_and_run_tests(verbosity: int = 2) -> bool:
    """
    Discover and run all tests in the tests directory.
    
    Args:
        verbosity: Test output verbosity level (0=quiet, 1=normal, 2=verbose)
        
    Returns:
        True if all tests passed, False if any tests failed
    """
    # Get the project root directory
    project_root = Path(__file__).parent
    tests_dir = project_root / "tests"
    
    if not tests_dir.exists():
        print(f"Tests directory not found: {tests_dir}")
        return False
    
    # Discover tests
    loader = unittest.TestLoader()
    
    try:
        # Discover all test files in the tests directory
        test_suite = loader.discover(
            start_dir=str(tests_dir),
            pattern="test_*.py",
            top_level_dir=str(project_root)
        )
        
        # Count total tests
        test_count = test_suite.countTestCases()
        if test_count == 0:
            print("No tests found!")
            return False
        
        print(f"Running {test_count} tests...")
        print("=" * 50)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
        result = runner.run(test_suite)
        
        # Print summary
        print("=" * 50)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")
        
        # Return success status
        success = len(result.failures) == 0 and len(result.errors) == 0
        
        if success:
            print("✅ All tests passed!")
        else:
            print("❌ Some tests failed!")
            
            # Print failure details
            if result.failures:
                print("\nFAILURES:")
                for test, traceback in result.failures:
                    print(f"- {test}")
                    print(f"  {traceback.split(chr(10))[-2]}")  # Last meaningful line
            
            if result.errors:
                print("\nERRORS:")
                for test, traceback in result.errors:
                    print(f"- {test}")
                    print(f"  {traceback.split(chr(10))[-2]}")  # Last meaningful line
        
        return success
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return False


def run_specific_test_module(module_name: str, verbosity: int = 2) -> bool:
    """
    Run tests from a specific module.
    
    Args:
        module_name: Name of the test module (e.g., 'test_models')
        verbosity: Test output verbosity level
        
    Returns:
        True if all tests passed, False if any tests failed
    """
    try:
        # Import the test module
        test_module = __import__(f"tests.{module_name}", fromlist=[module_name])
        
        # Create test suite from module
        loader = unittest.TestLoader()
        test_suite = loader.loadTestsFromModule(test_module)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
        result = runner.run(test_suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
        
    except ImportError as e:
        print(f"Could not import test module '{module_name}': {e}")
        return False
    except Exception as e:
        print(f"Error running test module '{module_name}': {e}")
        return False


def main() -> None:
    """Main entry point for the test runner."""
    
    parser = argparse.ArgumentParser(
        description="Run tests for Claude Sessions Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                    # Run all tests
  python run_tests.py -v 1              # Run with less verbose output
  python run_tests.py -m test_models    # Run specific test module
  python run_tests.py --quiet           # Run with minimal output
        """
    )
    
    _ = parser.add_argument(
        "-v", "--verbosity",
        type=int,
        choices=[0, 1, 2],
        default=2,
        help="Test output verbosity (0=quiet, 1=normal, 2=verbose)"
    )
    
    _ = parser.add_argument(
        "-m", "--module",
        type=str,
        help="Run tests from specific module (e.g., 'domain.test_models')"
    )
    
    _ = parser.add_argument(
        "-q", "--quiet",
        action="store_const",
        const=0,
        dest="verbosity",
        help="Quiet output (equivalent to -v 0)"
    )
    
    args = parser.parse_args()
    
    # Run tests
    module: str | None = args.module
    verbosity: int = args.verbosity
    if module:
        success = run_specific_test_module(module, verbosity)
    else:
        success = discover_and_run_tests(verbosity)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()