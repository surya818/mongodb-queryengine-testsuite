# MongoDB Query Engine Test Automation Suite

A comprehensive test automation framework for MongoDB Query Engine functionality validation

## 🏗️ Project Structure

```
mongodb-testsuite/
├── src/
│   ├── framework/           # Core testing framework
│   │   ├── database/        # Database connection and management
│   │   ├── queries/         # Query builders and utilities
│   │   └── assertions/      # Custom assertion helpers
│   ├── tests/              # Test suites
│   │   ├── unit/           # Unit tests
│   │   ├── integration/    # Integration tests
│   │   └── performance/    # Performance tests
│   └── utils/              # Shared utilities
├── config/                 # Configuration files
├── data/                   # Test data and fixtures
└── reports/               # Test reports and artifacts
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- MongoDB instance running (default: localhost:27017)
- Sample data (using sample_mflix database)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd mongodb-testsuite
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

Update `config/config.yaml` with your MongoDB connection details:
```yaml
mongo_uri: "mongodb://localhost:27017"
database: "sample_mflix"
```

## 🧪 Running Tests

### All Tests
```bash
make test
# or
pytest
```

### Specific Test Categories
```bash
# Integration tests only
pytest src/tests/integration/

# Unit tests only
pytest src/tests/unit/

# Performance tests only
pytest src/tests/performance/
```

### Verbose Output
```bash
pytest -v
```

## 📊 Test Categories

- **Integration Tests**: Tests that verify component interactions and database operations

## 📊 Regression Suite (Github Actions)

- **Runs on**: Ubuntu, but we can configure for many OSes
- **How is setup done**: Mongo db is installed, verified for startup
- **Test Data**: All the tests are based on the movie database sample, sample_mflix database
- **Reporting**: pytest-html creates a detailed report with console logging too. Here's an example test report
<img width="1720" height="808" alt="image" src="https://github.com/user-attachments/assets/babb8ba6-eedc-4ee7-8ee6-16ef98cde1f7" />

## 🛠️ Current Test coverage
- **Query Parsing**: Tests covering parsing span across different mql syntax
- **Query Selection/Optimization**: Tests covering Execution plans, Winning plans, COLLSCAN vs IDXSCAN, caching, query shapes 


## 🛠️ Development

### Adding New Tests

1. Choose appropriate test category (unit/integration/performance)
2. Create test file following naming convention: `test_*.py`
3. Use framework utilities from `src.framework.*` modules
4. Follow existing patterns for imports and assertions

### Framework Components

- **Database Client** (`src.framework.database.client`): MongoDB connection management
- **Query Utils** (`src.framework.queries.utils`): Reusable query builders
- **Assertions** (`src.framework.assertions.utils`): Custom test assertions

## 📝 Available Commands

Run `make help` to see all available commands.

## 🔧 Configuration

Test behavior can be customized via:
- `pytest.ini`: Test discovery and execution settings
- `config/config.yaml`: Database and environment configuration

## 📋 Dependencies

- `pymongo`: MongoDB Python driver
- `pytest`: Testing framework
- `pyyaml`: YAML configuration parsing

## 🤝 Contributing

1. Follow the existing code structure and naming conventions
2. Add appropriate tests for new functionality
3. Update documentation as needed
4. Ensure all tests pass before submitting changes
