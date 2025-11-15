"""
Milestone (sprint) management tools for Taiga MCP server.
"""

import logging
from typing import Any

from pytaigaclient.exceptions import TaigaException

from .common import get_api_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool("list_milestones", description="Lists milestones (sprints) within a specific project.")
def list_milestones(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Lists all milestones for a project."""
    logger.info(f"Executing list_milestones for project {project_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        milestones = api.milestones.list(project=project_id)
        return milestones
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing milestones for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing milestones for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing milestones: {e}")


@mcp.tool("create_milestone", description="Creates a new milestone (sprint) within a project.")
def create_milestone(
    session_id: str,
    project_id: int,
    name: str,
    estimated_start: str,
    estimated_finish: str,
) -> dict[str, Any]:
    """Creates a milestone. Requires project_id, name, estimated_start, and estimated_finish dates (YYYY-MM-DD format)."""
    logger.info(
        f"Executing create_milestone '{name}' in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not name:
        raise ValueError("Milestone name cannot be empty.")
    try:
        milestone = api.milestones.create(
            project=project_id,
            name=name,
            estimated_start=estimated_start,
            estimated_finish=estimated_finish,
        )
        logger.info(f"Milestone '{name}' created successfully (ID: {milestone.get('id', 'N/A')}).")
        return milestone
    except TaigaException as e:
        logger.error(f"Taiga API error creating milestone '{name}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating milestone '{name}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating milestone: {e}")


@mcp.tool(
    "get_milestone", description="Gets detailed information about a specific milestone by its ID."
)
def get_milestone(session_id: str, milestone_id: int) -> dict[str, Any]:
    """Retrieves milestone details by ID."""
    logger.info(f"Executing get_milestone ID {milestone_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        milestone = api.milestones.get(milestone_id)
        return milestone
    except TaigaException as e:
        logger.error(f"Taiga API error getting milestone {milestone_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting milestone {milestone_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting milestone: {e}")


@mcp.tool("update_milestone", description="Updates details of an existing milestone.")
def update_milestone(
    session_id: str, milestone_id: int, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Updates a milestone. Pass fields to update as keyword arguments JSON string (e.g., {\"name\":\"New Name\", \"estimated_finish\":\"2025-12-31\"})."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing update_milestone ID {milestone_id} for session {session_id[:8]} with data: {extra_fields}"
    )
    api = get_api_client(session_id)
    try:
        if not extra_fields:
            raise ValueError("No fields provided for update.")

        current_milestone = api.milestones.get(milestone_id)
        version = current_milestone.get("version")
        if not version:
            raise ValueError(f"Could not retrieve version for milestone {milestone_id}.")

        updated_milestone = api.milestones.edit(
            milestone_id=milestone_id, version=version, **extra_fields
        )
        logger.info(f"Milestone {milestone_id} update request sent.")
        return updated_milestone
    except TaigaException as e:
        logger.error(f"Taiga API error updating milestone {milestone_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating milestone {milestone_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating milestone: {e}")


@mcp.tool("delete_milestone", description="Deletes a milestone by its ID.")
def delete_milestone(session_id: str, milestone_id: int) -> dict[str, Any]:
    """Deletes a milestone by ID."""
    logger.warning(f"Executing delete_milestone ID {milestone_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        api.milestones.delete(id=milestone_id)
        logger.info(f"Milestone {milestone_id} deleted successfully.")
        return {"status": "deleted", "milestone_id": milestone_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting milestone {milestone_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting milestone {milestone_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting milestone: {e}")
