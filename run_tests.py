"""
Helper script to run tests with various options
"""
import sys
import subprocess
from pathlib import Path


def run_command(cmd):
    """Run command and return result"""
    print(f"\n{'='*60}")
    print(f"Running: {' '.join(cmd)}")
    print('='*60)
    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    """Main test runner"""
    if len(sys.argv) < 2:
        print("""
Usage: python run_tests.py [option]

Options:
    all         - Run all tests
    schemas     - Run schema tests only
    coverage    - Run tests with coverage report
    html        - Run tests with HTML coverage report
    verbose     - Run tests with verbose output
    quick       - Run tests without coverage (faster)
    
Examples:
    python run_tests.py all
    python run_tests.py schemas
    python run_tests.py coverage
        """)
        return 1
    
    option = sys.argv[1].lower()
    
    # Ensure we're in the project root
    project_root = Path(__file__).parent
    
    commands = {
        'all': ['pytest', '-v'],
        'schemas': ['pytest', 'tests/test_schemas.py', '-v'],
        'coverage': ['pytest', '--cov=app', '--cov-report=term-missing'],
        'html': ['pytest', '--cov=app', '--cov-report=html'],
        'verbose': ['pytest', '-vv', '-s'],
        'quick': ['pytest', '--tb=short'],
    }
    
    if option not in commands:
        print(f"Error: Unknown option '{option}'")
        print("Run 'python run_tests.py' without arguments to see usage")
        return 1
    
    cmd = commands[option]
    returncode = run_command(cmd)
    
    if option == 'html' and returncode == 0:
        print("\n" + "="*60)
        print("Coverage HTML report generated in: htmlcov/index.html")
        print("="*60)
    
    return returncode


if __name__ == '__main__':
    sys.exit(main())

