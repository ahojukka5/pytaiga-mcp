"""
Shared pytest fixtures for testing the Taiga MCP server.

Provides common mocks and test data for all test modules.
"""

from unittest.mock import Mock

import pytest

from pytaiga_mcp.server.common import active_sessions
from pytaiga_mcp.taiga_client import TaigaClientWrapper


@pytest.fixture
def mock_taiga_client():
    """Create a mock TaigaClient instance."""
    mock_client = Mock()
    mock_client.auth_token = "mock-auth-token"
    return mock_client


@pytest.fixture
def mock_taiga_wrapper():
    """Create a mock TaigaClientWrapper instance."""
    wrapper = Mock(spec=TaigaClientWrapper)
    wrapper.host = "https://api.taiga.io"
    wrapper.is_authenticated = True
    wrapper.user_id = 123
    wrapper.username = "testuser"
    wrapper.api = Mock()
    wrapper.api.auth_token = "test-token-123"
    return wrapper


@pytest.fixture
def authenticated_session(mock_taiga_wrapper):
    """Create an authenticated session and return session_id."""
    session_id = "test-session-123"
    active_sessions[session_id] = mock_taiga_wrapper
    yield session_id
    # Cleanup
    active_sessions.clear()


@pytest.fixture
def mock_project_data():
    """Provide sample project data."""
    return {
        "id": 1,
        "name": "Test Project",
        "slug": "test-project",
        "description": "A test project",
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
        "owner": 123,
        "members": [123, 456],
        "is_private": False,
        "version": 1,
    }


@pytest.fixture
def mock_user_story_data():
    """Provide sample user story data."""
    return {
        "id": 101,
        "ref": 1,
        "project": 1,
        "subject": "Test User Story",
        "description": "A test user story",
        "status": 1,
        "is_closed": False,
        "assigned_to": None,
        "milestone": None,
        "version": 1,
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_task_data():
    """Provide sample task data."""
    return {
        "id": 201,
        "ref": 1,
        "project": 1,
        "subject": "Test Task",
        "description": "A test task",
        "status": 1,
        "is_closed": False,
        "assigned_to": None,
        "user_story": None,
        "milestone": None,
        "version": 1,
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_issue_data():
    """Provide sample issue data."""
    return {
        "id": 301,
        "ref": 1,
        "project": 1,
        "subject": "Test Issue",
        "description": "A test issue",
        "status": 1,
        "priority": 1,
        "severity": 1,
        "type": 1,
        "is_closed": False,
        "assigned_to": None,
        "version": 1,
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_epic_data():
    """Provide sample epic data."""
    return {
        "id": 401,
        "ref": 1,
        "project": 1,
        "subject": "Test Epic",
        "description": "A test epic",
        "status": 1,
        "color": "#FF0000",
        "assigned_to": None,
        "version": 1,
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_milestone_data():
    """Provide sample milestone data."""
    return {
        "id": 501,
        "project": 1,
        "name": "Sprint 1",
        "slug": "sprint-1",
        "estimated_start": "2024-01-01",
        "estimated_finish": "2024-01-14",
        "closed": False,
        "version": 1,
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_wiki_page_data():
    """Provide sample wiki page data."""
    return {
        "id": 601,
        "project": 1,
        "slug": "home",
        "content": "Welcome to the wiki",
        "version": 1,
        "created_date": "2024-01-01T00:00:00Z",
        "modified_date": "2024-01-01T00:00:00Z",
    }


@pytest.fixture
def mock_member_data():
    """Provide sample project member data."""
    return {
        "id": 1,
        "user": 123,
        "project": 1,
        "role": 1,
        "is_admin": False,
        "email": "test@example.com",
        "full_name": "Test User",
    }


@pytest.fixture
def mock_status_data():
    """Provide sample status data."""
    return {
        "id": 1,
        "name": "New",
        "slug": "new",
        "order": 1,
        "is_closed": False,
        "color": "#999999",
        "project": 1,
    }


@pytest.fixture
def setup_mock_api(mock_taiga_wrapper):
    """Setup a mock API with common resources."""
    api = mock_taiga_wrapper.api

    # Setup common resources
    api.projects = Mock()
    api.user_stories = Mock()
    api.tasks = Mock()
    api.issues = Mock()
    api.epics = Mock()
    api.milestones = Mock()
    api.wiki = Mock()
    api.memberships = Mock()
    api.userstory_statuses = Mock()
    api.issue_statuses = Mock()
    api.issue_priorities = Mock()
    api.issue_severities = Mock()
    api.issue_types = Mock()

    # Setup common methods
    api.get = Mock()
    api.post = Mock()
    api.patch = Mock()
    api.delete = Mock()

    return api


@pytest.fixture(autouse=True)
def clear_sessions():
    """Automatically clear active sessions after each test."""
    yield
    active_sessions.clear()


@pytest.fixture
def sample_projects_list(mock_project_data):
    """Provide a list of sample projects."""
    return [
        mock_project_data,
        {**mock_project_data, "id": 2, "name": "Another Project", "slug": "another-project"},
        {**mock_project_data, "id": 3, "name": "Third Project", "slug": "third-project"},
    ]


@pytest.fixture
def sample_user_stories_list(mock_user_story_data):
    """Provide a list of sample user stories."""
    return [
        mock_user_story_data,
        {**mock_user_story_data, "id": 102, "ref": 2, "subject": "Second User Story"},
        {**mock_user_story_data, "id": 103, "ref": 3, "subject": "Third User Story"},
    ]


@pytest.fixture
def sample_tasks_list(mock_task_data):
    """Provide a list of sample tasks."""
    return [mock_task_data, {**mock_task_data, "id": 202, "ref": 2, "subject": "Second Task"}]


@pytest.fixture
def sample_issues_list(mock_issue_data):
    """Provide a list of sample issues."""
    return [mock_issue_data, {**mock_issue_data, "id": 302, "ref": 2, "subject": "Second Issue"}]
