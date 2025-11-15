"""
User story management tools for Taiga MCP server.
"""

import logging
from typing import Any

from pytaigaclient.exceptions import TaigaException

from .common import get_api_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool(
    "list_user_stories",
    description="Lists user stories within a specific project, optionally filtered.",
)
def list_user_stories(
    session_id: str, project_id: int, filters: str = "{}"
) -> list[dict[str, Any]]:
    """Lists user stories for a project. Optional filters like 'milestone', 'status', 'assigned_to' can be passed as keyword arguments."""
    logger.info(
        f"Executing list_user_stories for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    api = get_api_client(session_id)
    try:
        import json

        filter_dict = json.loads(filters) if filters else {}
        stories = api.user_stories.list(project=project_id, **filter_dict)
        return stories
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing user stories for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing user stories for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing user stories: {e}")


@mcp.tool("create_user_story", description="Creates a new user story within a project.")
def create_user_story(
    session_id: str, project_id: int, subject: str, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Creates a user story. Requires project_id and subject. Optional fields (description, milestone_id, status_id, assigned_to_id, etc.) via kwargs JSON string."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing create_user_story '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not subject:
        raise ValueError("User story subject cannot be empty.")
    try:
        story = api.user_stories.create(project=project_id, subject=subject, **extra_fields)
        logger.info(f"User story '{subject}' created successfully (ID: {story.get('id', 'N/A')}).")
        return story
    except TaigaException as e:
        logger.error(f"Taiga API error creating user story '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating user story '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating user story: {e}")


@mcp.tool(
    "get_user_story", description="Gets detailed information about a specific user story by its ID."
)
def get_user_story(session_id: str, user_story_id: int) -> dict[str, Any]:
    """Retrieves user story details by ID."""
    logger.info(f"Executing get_user_story ID {user_story_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        story = api.user_stories.get(user_story_id)
        return story
    except TaigaException as e:
        logger.error(f"Taiga API error getting user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting user story: {e}")


@mcp.tool("update_user_story", description="Updates details of an existing user story.")
def update_user_story(
    session_id: str, user_story_id: int, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Updates a user story. Pass fields to update as keyword arguments dict (e.g., {\"subject\":\"New Title\", \"status_id\":123})."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing update_user_story ID {user_story_id} for session {session_id[:8]} with data: {extra_fields}"
    )
    api = get_api_client(session_id)
    try:
        if not extra_fields:
            raise ValueError("No fields provided for update.")

        current_story = api.user_stories.get(user_story_id)
        version = current_story.get("version")
        if version is None:
            raise ValueError(f"Could not retrieve version for user story {user_story_id}.")

        updated_story = api.user_stories.edit(
            user_story_id=user_story_id, version=version, **extra_fields
        )
        logger.info(f"User story {user_story_id} update request sent.")
        return updated_story
    except TaigaException as e:
        logger.error(f"Taiga API error updating user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating user story: {e}")


@mcp.tool("delete_user_story", description="Deletes a user story by its ID.")
def delete_user_story(session_id: str, user_story_id: int) -> dict[str, Any]:
    """Deletes a user story by ID."""
    logger.warning(
        f"Executing delete_user_story ID {user_story_id} for session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        api.user_stories.delete(id=user_story_id)
        logger.info(f"User story {user_story_id} deleted successfully.")
        return {"status": "deleted", "user_story_id": user_story_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting user story: {e}")


@mcp.tool(
    "assign_user_story_to_user", description="Assigns a specific user story to a specific user."
)
def assign_user_story_to_user(session_id: str, user_story_id: int, user_id: int) -> dict[str, Any]:
    """Assigns a user story to a user."""
    logger.info(
        f"Executing assign_user_story_to_user: US {user_story_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return update_user_story(session_id, user_story_id, kwargs={"assigned_to": user_id})


@mcp.tool(
    "unassign_user_story_from_user",
    description="Unassigns a specific user story (sets assigned user to null).",
)
def unassign_user_story_from_user(session_id: str, user_story_id: int) -> dict[str, Any]:
    """Unassigns a user story."""
    logger.info(
        f"Executing unassign_user_story_from_user: US {user_story_id}, session {session_id[:8]}..."
    )
    return update_user_story(session_id, user_story_id, kwargs={"assigned_to": None})


@mcp.tool(
    "get_user_story_statuses",
    description="Lists the available statuses for user stories within a specific project.",
)
def get_user_story_statuses(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Retrieves the list of user story statuses for a project."""
    logger.info(
        f"Executing get_user_story_statuses for project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        statuses = api.userstory_statuses.list(project_id=project_id)
        return statuses
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting user story statuses for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting user story statuses for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting user story statuses: {e}")


@mcp.tool(
    "get_user_story_by_ref",
    description="Gets a user story by its reference number within a project.",
)
def get_user_story_by_ref(session_id: str, project_id: int, ref: int) -> dict[str, Any]:
    """Retrieves a user story by its reference number in a project."""
    logger.info(
        f"Executing get_user_story_by_ref #{ref} in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        story = api.user_stories.get_by_ref(project=project_id, ref=ref)
        return story
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting user story by ref #{ref} in project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting user story by ref #{ref} in project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting user story by ref: {e}")


@mcp.tool(
    "upvote_user_story",
    description="Adds a vote (star) to a user story.",
)
def upvote_user_story(session_id: str, user_story_id: int) -> dict[str, Any]:
    """Votes for a user story."""
    logger.info(f"Executing upvote_user_story ID {user_story_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.user_stories.upvote(user_story_id)
        logger.info(f"User story {user_story_id} upvoted successfully.")
        return result if result else {"status": "upvoted", "user_story_id": user_story_id}
    except TaigaException as e:
        logger.error(f"Taiga API error upvoting user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error upvoting user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error upvoting user story: {e}")


@mcp.tool(
    "downvote_user_story",
    description="Removes your vote (star) from a user story.",
)
def downvote_user_story(session_id: str, user_story_id: int) -> dict[str, Any]:
    """Removes vote from a user story."""
    logger.info(f"Executing downvote_user_story ID {user_story_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.user_stories.downvote(user_story_id)
        logger.info(f"User story {user_story_id} downvoted successfully.")
        return result if result else {"status": "downvoted", "user_story_id": user_story_id}
    except TaigaException as e:
        logger.error(f"Taiga API error downvoting user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error downvoting user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error downvoting user story: {e}")


@mcp.tool(
    "watch_user_story",
    description="Watch a user story to receive notifications about changes.",
)
def watch_user_story(session_id: str, user_story_id: int) -> dict[str, Any]:
    """Watches a user story."""
    logger.info(f"Executing watch_user_story ID {user_story_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.user_stories.watch(user_story_id)
        logger.info(f"User story {user_story_id} watched successfully.")
        return result if result else {"status": "watching", "user_story_id": user_story_id}
    except TaigaException as e:
        logger.error(f"Taiga API error watching user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error watching user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error watching user story: {e}")


@mcp.tool(
    "unwatch_user_story",
    description="Stop watching a user story.",
)
def unwatch_user_story(session_id: str, user_story_id: int) -> dict[str, Any]:
    """Unwatches a user story."""
    logger.info(f"Executing unwatch_user_story ID {user_story_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.user_stories.unwatch(user_story_id)
        logger.info(f"User story {user_story_id} unwatched successfully.")
        return result if result else {"status": "unwatched", "user_story_id": user_story_id}
    except TaigaException as e:
        logger.error(f"Taiga API error unwatching user story {user_story_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error unwatching user story {user_story_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error unwatching user story: {e}")
