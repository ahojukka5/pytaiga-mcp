"""
Issue management tools for Taiga MCP server.
"""

import logging
from typing import Any

from pytaigaclient.exceptions import TaigaException

from .common import get_api_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool("list_issues", description="Lists issues within a specific project, optionally filtered.")
def list_issues(session_id: str, project_id: int, filters: str = "{}") -> list[dict[str, Any]]:
    """Lists issues for a project. Optional filters like 'milestone', 'status', 'priority', 'severity', 'type', 'assigned_to' can be passed as kwargs."""
    logger.info(
        f"Executing list_issues for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    api = get_api_client(session_id)
    try:
        import json

        filter_dict = json.loads(filters) if filters else {}
        query_params = {"project": project_id, **filter_dict}
        issues = api.issues.list(query_params=query_params)
        return issues
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing issues for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing issues for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing issues: {e}")


@mcp.tool("create_issue", description="Creates a new issue within a project.")
def create_issue(
    session_id: str,
    project_id: int,
    subject: str,
    priority_id: int,
    status_id: int,
    severity_id: int,
    type_id: int,
    kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Creates an issue. Requires project_id, subject, priority_id, status_id, severity_id, type_id. Optional fields (description, assigned_to_id, etc.) via kwargs JSON string."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing create_issue '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not subject:
        raise ValueError("Issue subject cannot be empty.")
    try:
        data = {
            "priority": priority_id,
            "status": status_id,
            "type": type_id,
            "severity": severity_id,
            **extra_fields,
        }
        issue = api.issues.create(project=project_id, subject=subject, data=data)
        logger.info(f"Issue '{subject}' created successfully (ID: {issue.get('id', 'N/A')}).")
        return issue
    except TaigaException as e:
        logger.error(f"Taiga API error creating issue '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating issue '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating issue: {e}")


@mcp.tool("get_issue", description="Gets detailed information about a specific issue by its ID.")
def get_issue(session_id: str, issue_id: int) -> dict[str, Any]:
    """Retrieves issue details by ID."""
    logger.info(f"Executing get_issue ID {issue_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        issue = api.issues.get(issue_id)
        return issue
    except TaigaException as e:
        logger.error(f"Taiga API error getting issue {issue_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting issue {issue_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting issue: {e}")


@mcp.tool("update_issue", description="Updates details of an existing issue.")
def update_issue(
    session_id: str, issue_id: int, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Updates an issue. Pass fields to update as keyword arguments JSON string (e.g., {\"subject\":\"New Title\", \"status_id\":123})."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing update_issue ID {issue_id} for session {session_id[:8]} with data: {extra_fields}"
    )
    api = get_api_client(session_id)
    try:
        if not extra_fields:
            raise ValueError("No fields provided for update.")

        current_issue = api.issues.get(issue_id)
        version = current_issue.get("version")
        if not version:
            raise ValueError(f"Could not retrieve version for issue {issue_id}.")

        updated_issue = api.issues.edit(issue_id=issue_id, version=version, **extra_fields)
        logger.info(f"Issue {issue_id} update request sent.")
        return updated_issue
    except TaigaException as e:
        logger.error(f"Taiga API error updating issue {issue_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating issue {issue_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating issue: {e}")


@mcp.tool("delete_issue", description="Deletes an issue by its ID.")
def delete_issue(session_id: str, issue_id: int) -> dict[str, Any]:
    """Deletes an issue by ID."""
    logger.warning(f"Executing delete_issue ID {issue_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        api.issues.delete(issue_id)
        logger.info(f"Issue {issue_id} deleted successfully.")
        return {"status": "deleted", "issue_id": issue_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting issue {issue_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting issue {issue_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting issue: {e}")


@mcp.tool("assign_issue_to_user", description="Assigns a specific issue to a specific user.")
def assign_issue_to_user(session_id: str, issue_id: int, user_id: int) -> dict[str, Any]:
    """Assigns an issue to a user."""
    logger.info(
        f"Executing assign_issue_to_user: Issue {issue_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return update_issue(session_id, issue_id, kwargs={"assigned_to": user_id})


@mcp.tool(
    "unassign_issue_from_user",
    description="Unassigns a specific issue (sets assigned user to null).",
)
def unassign_issue_from_user(session_id: str, issue_id: int) -> dict[str, Any]:
    """Unassigns an issue."""
    logger.info(
        f"Executing unassign_issue_from_user: Issue {issue_id}, session {session_id[:8]}..."
    )
    return update_issue(session_id, issue_id, kwargs={"assigned_to": None})


@mcp.tool(
    "get_issue_statuses",
    description="Lists the available statuses for issues within a specific project.",
)
def get_issue_statuses(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Retrieves the list of issue statuses for a project."""
    logger.info(
        f"Executing get_issue_statuses for project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        statuses = api.issue_statuses.list(query_params={"project": project_id})
        return statuses
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue statuses for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue statuses for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error getting issue statuses: {e}")


@mcp.tool(
    "get_issue_priorities",
    description="Lists the available priorities for issues within a specific project.",
)
def get_issue_priorities(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Retrieves the list of issue priorities for a project."""
    logger.info(
        f"Executing get_issue_priorities for project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        priorities = api.issue_priorities.list(query_params={"project": project_id})
        return priorities
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue priorities for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue priorities for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting issue priorities: {e}")


@mcp.tool(
    "get_issue_severities",
    description="Lists the available severities for issues within a specific project.",
)
def get_issue_severities(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Retrieves the list of issue severities for a project."""
    logger.info(
        f"Executing get_issue_severities for project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        severities = api.issue_severities.list(query_params={"project": project_id})
        return severities
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue severities for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue severities for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting issue severities: {e}")


@mcp.tool(
    "get_issue_types", description="Lists the available types for issues within a specific project."
)
def get_issue_types(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Retrieves the list of issue types for a project."""
    logger.info(f"Executing get_issue_types for project {project_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        types = api.issue_types.list(query_params={"project": project_id})
        return types
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting issue types for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting issue types for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error getting issue types: {e}")
