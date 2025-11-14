import uuid
from unittest.mock import MagicMock, patch

import pytest

# Import the server module instead of specific functions
import pytaiga_mcp.server
from pytaiga_mcp.taiga_client import TaigaClientWrapper

# Test constants
TEST_HOST = "https://your-test-taiga-instance.com"
TEST_USERNAME = "test_user"
TEST_PASSWORD = "test_password"


class TestTaigaTools:
    @pytest.fixture
    def session_setup(self):
        """Create a session setup for testing"""
        # Generate a session ID
        session_id = str(uuid.uuid4())

        # Create and return a mock client
        mock_client = MagicMock()
        mock_client.is_authenticated = True

        # Store the mock client in active_sessions
        pytaiga_mcp.server.active_sessions[session_id] = mock_client

        return session_id, mock_client

    def test_login(self):
        """Test the login functionality"""
        with patch.object(TaigaClientWrapper, "login", return_value=True):
            # Clear any existing sessions
            pytaiga_mcp.server.active_sessions.clear()

            # Call the login function
            result = pytaiga_mcp.server.login(TEST_HOST, TEST_USERNAME, TEST_PASSWORD)

            # Verify results
            assert "session_id" in result
            assert result["session_id"] in pytaiga_mcp.server.active_sessions

            # Get the session ID for cleanup
            session_id = result["session_id"]
            pytaiga_mcp.server.active_sessions.clear()

    def test_list_projects(self, session_setup):
        """Test list_projects functionality"""
        session_id, mock_client = session_setup

        # Setup list projects return - return actual dictionaries
        mock_client.api.projects.list.return_value = [{"id": 123, "name": "Test Project"}]

        # List projects and verify
        projects = pytaiga_mcp.server.list_projects(session_id)
        assert len(projects) == 1
        assert projects[0]["name"] == "Test Project"
        assert projects[0]["id"] == 123

    def test_update_project(self, session_setup):
        """Test update_project functionality"""
        session_id, mock_client = session_setup

        # Setup mock project with version
        mock_project_dict = {"id": 123, "name": "Old Name", "version": 1}
        mock_client.api.projects.get.return_value = mock_project_dict

        # Setup update return
        updated_project = {"id": 123, "name": "New Name", "version": 2}
        mock_client.api.projects.update.return_value = updated_project

        # Update the project name using kwargs dict
        result = pytaiga_mcp.server.update_project(session_id, 123, kwargs={"name": "New Name"})

        # Verify the update was called with correct parameters
        mock_client.api.projects.update.assert_called_once_with(
            project_id=123, version=1, project_data={"name": "New Name"}
        )
        assert result["name"] == "New Name"

    def test_list_user_stories(self, session_setup):
        """Test list_user_stories functionality"""
        session_id, mock_client = session_setup

        # Setup list user stories return - return actual dictionaries
        mock_client.api.user_stories.list.return_value = [{"id": 456, "subject": "Test User Story"}]

        # List user stories and verify
        stories = pytaiga_mcp.server.list_user_stories(session_id, 123)
        assert len(stories) == 1
        assert stories[0]["subject"] == "Test User Story"
        assert stories[0]["id"] == 456

        # Verify the correct project filter was used
        mock_client.api.user_stories.list.assert_called_once_with(project=123)

    def test_create_user_story(self, session_setup):
        """Test create_user_story functionality"""
        session_id, mock_client = session_setup

        # Setup create user story return - return actual dictionary
        mock_client.api.user_stories.create.return_value = {"id": 456, "subject": "New Story"}

        # Create user story and verify using kwargs dict
        story = pytaiga_mcp.server.create_user_story(
            session_id, 123, "New Story", kwargs={"description": "Test description"}
        )
        assert story["subject"] == "New Story"
        assert story["id"] == 456

        # Verify the create was called with correct parameters
        mock_client.api.user_stories.create.assert_called_once_with(
            project=123, subject="New Story", description="Test description"
        )

    def test_list_tasks(self, session_setup):
        """Test list_tasks functionality"""
        session_id, mock_client = session_setup

        # Setup list tasks to return a list directly via api.get()
        mock_tasks_list = [{"id": 789, "subject": "Test Task"}]
        mock_client.api.get.return_value = mock_tasks_list

        # List tasks and verify
        tasks = pytaiga_mcp.server.list_tasks(session_id, 123)
        assert len(tasks) == 1
        assert tasks[0]["subject"] == "Test Task"
        assert tasks[0]["id"] == 789

        # Verify the correct call was made to api.get
        mock_client.api.get.assert_called_once_with("/tasks", params={"project": 123})
