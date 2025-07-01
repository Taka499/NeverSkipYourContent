#!/usr/bin/env python3
"""Test runner for web search MCP server."""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, check=True, cwd=Path(__file__).parent.parent)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        return False
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="Run web search server tests")
    parser.add_argument(
        "--unit", 
        action="store_true", 
        help="Run only unit tests (fast, no external dependencies)"
    )
    parser.add_argument(
        "--integration", 
        action="store_true", 
        help="Run integration tests (may require API keys)"
    )
    parser.add_argument(
        "--provider", 
        choices=["duckduckgo", "serpapi", "perplexity", "tavily", "claude"],
        help="Test specific provider only"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Run tests with coverage report"
    )
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true", 
        help="Verbose output"
    )
    parser.add_argument(
        "--parallel", "-n",
        type=int,
        help="Run tests in parallel (requires pytest-xdist)"
    )
    args = parser.parse_args()
    
    # Base pytest command
    pytest_cmd = ["python", "-m", "pytest", "tests/"]
    
    # Add verbosity
    if args.verbose:
        pytest_cmd.append("-vv")
    
    # Add parallel execution
    if args.parallel:
        pytest_cmd.extend(["-n", str(args.parallel)])
    
    # Add coverage
    if args.coverage:
        pytest_cmd.extend([
            "--cov=src/web_search", 
            "--cov-report=html", 
            "--cov-report=term-missing",
            "--cov-report=xml"
        ])
    
    # Filter by test type
    if args.unit:
        pytest_cmd.extend(["-m", "not integration"])
    elif args.integration:
        pytest_cmd.extend(["-m", "integration", "--run-integration"])
    
    # Filter by provider
    if args.provider:
        pytest_cmd.extend(["-k", args.provider])
    
    print("Web Search MCP Server Test Runner")
    print("=" * 40)
    
    # Check dependencies
    dependencies_ok = True
    
    # Check if pytest is available
    if not run_command(["python", "-c", "import pytest"], "Checking pytest availability"):
        print("\n❌ pytest is not installed. Install with: uv add --dev pytest pytest-asyncio")
        dependencies_ok = False
    
    # Check if web_search module is available
    if not run_command(
        ["python", "-c", "import sys; sys.path.insert(0, 'src'); import web_search"], 
        "Checking web_search module availability"
    ):
        print("\n❌ web_search module not found. Make sure you're in the correct directory.")
        dependencies_ok = False
    
    if not dependencies_ok:
        return 1
    
    # Run the tests
    success = run_command(pytest_cmd, "Running tests")
    
    if success:
        print("\n🎉 All tests passed!")
        
        if args.coverage:
            print("\n📊 Coverage report generated:")
            print("  - HTML: htmlcov/index.html")
            print("  - XML: coverage.xml")
    else:
        print("\n💥 Some tests failed. Check the output above for details.")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())