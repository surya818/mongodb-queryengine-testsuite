# MongoDB Query Engine Test Automation Suite

## Project Overview
Production-grade test automation suite for MongoDB Query Engine functionality and performance validation.

## Project Structure (Production Grade)
```
mongodb-testsuite/
├── src/
│   ├── framework/           # Core testing framework
│   │   ├── database/        # Database connection (client.py)
│   │   ├── queries/         # Query builders (utils.py)
│   │   └── assertions/      # Custom assertions (utils.py)
│   ├── tests/              # Test suites
│   │   ├── unit/           # Unit tests
│   │   ├── integration/    # Integration tests (test_query_parsing.py)
│   │   └── performance/    # Performance tests
│   └── utils/              # Shared utilities
├── config/                 # Configuration (config.yaml)
├── data/                   # Test data and fixtures
├── docs/                   # Documentation
├── logs/                   # Test execution logs
├── reports/               # Test reports and artifacts
├── pytest.ini            # Test configuration
├── .gitignore            # Git exclusions
├── Makefile              # Task automation
└── README.md             # Project documentation
```

## Development Environment
- Platform: macOS (Darwin 24.4.0)
- Working Directory: `/Users/surya.rekha/Data/code/2025/db/mongodb-testsuite`
- Python: 3.9.6 with virtual environment (.venv)
- Not currently a git repository

## Commands
- `make test`: Run all tests
- `make test-integration`: Run integration tests
- `pytest -v`: Verbose test execution
- `make help`: Show all available commands

## Notes
- Project restructured to production-grade standards on 2025-09-13
- Test suite focuses on MongoDB Query Engine validation
- All tests passing successfully with new structure
- Framework properly modularized with proper Python package structure
- Added comprehensive parsing tests for top 3 priority scenarios:
- Added comprehensive query optimization tests:
  - Enhanced with detailed query logging for debugging and monitoring
- Total: 23 test functions covering critical parsing and optimization functionality