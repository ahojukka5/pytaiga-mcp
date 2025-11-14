"""
Epic management tools for Taiga MCP server.
"""

import logging
from typing import Any

from pytaigaclient.exceptions import TaigaException

from .common import get_api_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool("list_epics", description="Lists epics within a specific project, optionally filtered.")
def list_epics(session_id: str, project_id: int, filters: str = "{}") -> list[dict[str, Any]]:
    """Lists epics for a project. Optional filters like 'status', 'assigned_to' can be passed as keyword arguments."""
    logger.info(
        f"Executing list_epics for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    api = get_api_client(session_id)
    try:
        import json

        filter_dict = json.loads(filters) if filters else {}
        epics = api.epics.list(project_id=project_id, **filter_dict)
        return epics
    except TaigaException as e:
        logger.error(f"Taiga API error listing epics for project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing epics for project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error listing epics: {e}")


@mcp.tool("create_epic", description="Creates a new epic within a project.")
def create_epic(
    session_id: str, project_id: int, subject: str, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Creates an epic. Requires project_id and subject. Optional fields (description, status_id, assigned_to_id, color, etc.) via kwargs JSON string."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing create_epic '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not subject:
        raise ValueError("Epic subject cannot be empty.")
    try:
        epic = api.epics.create(project=project_id, subject=subject, **extra_fields)
        logger.info(f"Epic '{subject}' created successfully (ID: {epic.get('id', 'N/A')}).")
        return epic
    except TaigaException as e:
        logger.error(f"Taiga API error creating epic '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating epic '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating epic: {e}")


@mcp.tool("get_epic", description="Gets detailed information about a specific epic by its ID.")
def get_epic(session_id: str, epic_id: int) -> dict[str, Any]:
    """Retrieves epic details by ID."""
    logger.info(f"Executing get_epic ID {epic_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        epic = api.epics.get(epic_id)
        return epic
    except TaigaException as e:
        logger.error(f"Taiga API error getting epic {epic_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting epic {epic_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting epic: {e}")


@mcp.tool("update_epic", description="Updates details of an existing epic.")
def update_epic(
    session_id: str, epic_id: int, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Updates an epic. Pass fields to update as keyword arguments JSON string (e.g., {\"subject\":\"New Title\", \"status_id\":123})."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing update_epic ID {epic_id} for session {session_id[:8]} with data: {extra_fields}"
    )
    api = get_api_client(session_id)
    try:
        if not extra_fields:
            raise ValueError("No fields provided for update.")

        current_epic = api.epics.get(epic_id)
        version = current_epic.get("version")
        if not version:
            raise ValueError(f"Could not retrieve version for epic {epic_id}.")

        updated_epic = api.epics.edit(epic_id=epic_id, version=version, **extra_fields)
        logger.info(f"Epic {epic_id} update request sent.")
        return updated_epic
    except TaigaException as e:
        logger.error(f"Taiga API error updating epic {epic_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating epic {epic_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating epic: {e}")


@mcp.tool("delete_epic", description="Deletes an epic by its ID.")
def delete_epic(session_id: str, epic_id: int) -> dict[str, Any]:
    """Deletes an epic by ID."""
    logger.warning(f"Executing delete_epic ID {epic_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        api.epics.delete(id=epic_id)
        logger.info(f"Epic {epic_id} deleted successfully.")
        return {"status": "deleted", "epic_id": epic_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting epic {epic_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting epic {epic_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting epic: {e}")


@mcp.tool("assign_epic_to_user", description="Assigns a specific epic to a specific user.")
def assign_epic_to_user(session_id: str, epic_id: int, user_id: int) -> dict[str, Any]:
    """Assigns an epic to a user."""
    logger.info(
        f"Executing assign_epic_to_user: Epic {epic_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return update_epic(session_id, epic_id, kwargs={"assigned_to": user_id})


@mcp.tool(
    "unassign_epic_from_user", description="Unassigns a specific epic (sets assigned user to null)."
)
def unassign_epic_from_user(session_id: str, epic_id: int) -> dict[str, Any]:
    """Unassigns an epic."""
    logger.info(f"Executing unassign_epic_from_user: Epic {epic_id}, session {session_id[:8]}...")
    return update_epic(session_id, epic_id, kwargs={"assigned_to": None})
