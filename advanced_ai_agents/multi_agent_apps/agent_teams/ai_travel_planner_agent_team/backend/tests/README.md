# Backend Tests

This directory contains the test suite for the TripCraft AI backend.

## Test Structure

```
tests/
├── conftest.py           # Pytest fixtures and configuration
├── unit/                 # Unit tests
│   ├── test_models.py    # Pydantic model tests
│   └── test_repositories.py  # Repository function tests
└── integration/          # Integration tests
    └── test_api.py       # API endpoint tests
```

## Setup

1. Install test dependencies:
```bash
pip install -e ".[dev]"
```

Or with uv:
```bash
uv pip install -e ".[dev]"
```

2. Set up environment variables (create a `.env.test` file):
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/test_db
BACKEND_API_URL=http://localhost:8000
```

## Running Tests

### Run all tests:
```bash
pytest
```

### Run unit tests only:
```bash
pytest -m unit
```

### Run integration tests only:
```bash
pytest -m integration
```

### Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

### Run specific test file:
```bash
pytest tests/unit/test_models.py
```

### Run specific test:
```bash
pytest tests/unit/test_models.py::TestTravelDates::test_travel_dates_creation
```

### Run in verbose mode:
```bash
pytest -v
```

### Run with output (disable capture):
```bash
pytest -s
```

## Test Markers

- `@pytest.mark.unit` - Unit tests (fast, no external dependencies)
- `@pytest.mark.integration` - Integration tests (may require database, APIs)
- `@pytest.mark.slow` - Slow running tests

## Coverage

After running tests with coverage, open the HTML report:
```bash
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
xdg-open htmlcov/index.html # Linux
```

## CI/CD

Tests are configured to run automatically in CI/CD pipelines. The pytest.ini file contains the configuration.

## Writing New Tests

1. Place unit tests in `tests/unit/`
2. Place integration tests in `tests/integration/`
3. Use appropriate markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
4. Follow the naming convention: `test_*.py` for files, `test_*` for functions
5. Use fixtures from `conftest.py` for common test data

## Troubleshooting

### Import Errors
Make sure the backend directory is in your Python path. The conftest.py handles this automatically.

### Database Connection Errors
Ensure your test database is running and the connection string in `.env.test` is correct.

### Async Test Issues
All async tests should use the `@pytest.mark.asyncio` decorator and the `asyncio_mode = auto` configuration.
