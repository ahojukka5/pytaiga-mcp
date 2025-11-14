# Test Suite Documentation

## Overview

This test suite provides comprehensive unit test coverage for the pytaiga-mcp package. All tests use mocking to simulate the Taiga API without requiring actual API connections.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and test utilities
├── test_taiga_client.py     # TaigaClientWrapper tests
├── test_common.py           # Common utilities and session management tests
├── test_auth.py             # Authentication functions tests
├── test_projects.py         # Project management tests
├── test_user_stories.py     # User story management tests
├── test_tasks_module.py     # Task management tests
├── test_issues.py           # Issue management tests
├── test_epics.py            # Epic management tests
├── test_milestones.py       # Milestone management tests
└── test_wiki_pages.py       # Wiki page management tests
```

## Running Tests

### Run all tests

```bash
pytest
```

### Run tests with coverage

```bash
pytest --cov=src --cov-report=html --cov-report=term
```

### Run specific test file

```bash
pytest tests/test_auth.py
```

### Run specific test class

```bash
pytest tests/test_auth.py::TestLogin
```

### Run specific test function

```bash
pytest tests/test_auth.py::TestLogin::test_login_successful
```

### Run tests with markers

```bash
# Run only auth tests
pytest -m auth

# Run only unit tests (exclude integration)
pytest -m "not integration"
```

## Test Coverage

### Module Coverage

| Module | Test File | Coverage |
|--------|-----------|----------|
| `src/taiga_client.py` | `test_taiga_client.py` | ✓ Complete |
| `src/server/common.py` | `test_common.py` | ✓ Complete |
| `src/server/auth.py` | `test_auth.py` | ✓ Complete |
| `src/server/projects.py` | `test_projects.py` | ✓ Complete |
| `src/server/user_stories.py` | `test_user_stories.py` | ✓ Complete |
| `src/server/tasks.py` | `test_tasks_module.py` | ✓ Complete |
| `src/server/issues.py` | `test_issues.py` | ✓ Complete |
| `src/server/epics.py` | `test_epics.py` | ✓ Complete |
| `src/server/milestones.py` | `test_milestones.py` | ✓ Complete |
| `src/server/wiki.py` | `test_wiki_pages.py` | ✓ Complete |

### Test Categories

Each module's tests cover:

1. **Happy Path Tests**: Normal operation with valid inputs
2. **Error Handling Tests**: Invalid inputs, API errors, network failures
3. **Edge Cases**: Empty results, missing fields, version conflicts
4. **Authentication Tests**: Session validation, permission errors
5. **Data Validation Tests**: Required field validation, type checking

## Key Test Patterns

### 1. Mocking Taiga API

All tests mock the `pytaigaclient.TaigaClient` to avoid real API calls:

```python
@patch('src.taiga_client.TaigaClient')
def test_example(mock_taiga_client_class):
    mock_api = Mock()
    mock_taiga_client_class.return_value = mock_api
    # Test implementation
```

### 2. Using Fixtures

Common test data is provided via pytest fixtures in `conftest.py`:

```python
def test_with_fixtures(authenticated_session, mock_project_data):
    result = get_project(authenticated_session, project_id=1)
    assert result == mock_project_data
```

### 3. Session Management

Tests use the `authenticated_session` fixture for authenticated operations:

```python
def test_example(authenticated_session, mock_taiga_wrapper):
    # Session is automatically created and cleaned up
    result = some_function(authenticated_session)
```

## Fixtures Reference

### Authentication Fixtures

- `mock_taiga_client`: Mock TaigaClient instance
- `mock_taiga_wrapper`: Mock TaigaClientWrapper instance
- `authenticated_session`: Creates and returns a valid session_id

### Data Fixtures

- `mock_project_data`: Sample project data
- `mock_user_story_data`: Sample user story data
- `mock_task_data`: Sample task data
- `mock_issue_data`: Sample issue data
- `mock_epic_data`: Sample epic data
- `mock_milestone_data`: Sample milestone data
- `mock_wiki_page_data`: Sample wiki page data
- `mock_member_data`: Sample project member data
- `mock_status_data`: Sample status data

### List Fixtures

- `sample_projects_list`: List of sample projects
- `sample_user_stories_list`: List of sample user stories
- `sample_tasks_list`: List of sample tasks
- `sample_issues_list`: List of sample issues

### Utility Fixtures

- `setup_mock_api`: Sets up a complete mock API with all resources
- `clear_sessions`: Automatically clears active sessions after tests

## Test Examples

### Testing CRUD Operations

```python
def test_create_item(authenticated_session, mock_taiga_wrapper, mock_data):
    """Test creating an item."""
    mock_taiga_wrapper.api.items.create.return_value = mock_data
    
    result = create_item(authenticated_session, name="Test")
    
    assert result == mock_data
    mock_taiga_wrapper.api.items.create.assert_called_once()
```

### Testing Error Handling

```python
def test_item_not_found(authenticated_session, mock_taiga_wrapper):
    """Test handling of not found error."""
    mock_taiga_wrapper.api.items.get.side_effect = TaigaException("Not found")
    
    with pytest.raises(TaigaException, match="Not found"):
        get_item(authenticated_session, item_id=999)
```

### Testing Authentication

```python
def test_invalid_session():
    """Test operation with invalid session."""
    with pytest.raises(PermissionError):
        some_function("invalid-session")
```

## Best Practices

1. **Isolation**: Each test is independent and doesn't affect others
2. **Mocking**: All external dependencies are mocked
3. **Assertions**: Use specific assertions to verify expected behavior
4. **Cleanup**: Fixtures handle setup and teardown automatically
5. **Naming**: Test names clearly describe what they test
6. **Coverage**: Aim for 100% code coverage
7. **Documentation**: Each test has a docstring explaining its purpose

## Common Issues and Solutions

### Issue: Tests fail with "PermissionError"

**Solution**: Ensure test uses `authenticated_session` fixture

### Issue: Mock not being called

**Solution**: Verify the correct module path in `@patch` decorator

### Issue: Session conflicts between tests

**Solution**: Use `clear_sessions` fixture or `setup_method`/`teardown_method`

### Issue: Fixture not found

**Solution**: Ensure `conftest.py` is in the tests directory

## Extending the Test Suite

To add tests for new functionality:

1. Create new test file in `tests/` directory
2. Import required modules and fixtures
3. Follow existing test patterns
4. Add appropriate markers in pytest.ini
5. Update this documentation

## CI/CD Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml
    
- name: Upload coverage
  uses: codecov/codecov-action@v3
```

## Maintenance

- Review and update tests when adding new features
- Keep fixtures in sync with data models
- Update documentation when patterns change
- Monitor test execution time and optimize slow tests
- Regularly check test coverage and add missing tests
