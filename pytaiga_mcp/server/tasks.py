"""
Task management tools for Taiga MCP server.
"""

import logging
from typing import Any

from pytaigaclient.exceptions import TaigaException

from .common import get_api_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool("list_tasks", description="Lists tasks within a specific project, optionally filtered.")
def list_tasks(session_id: str, project_id: int, filters: str = "{}") -> list[dict[str, Any]]:
    """Lists tasks for a project. Optional filters like 'milestone', 'status', 'user_story', 'assigned_to' can be passed as keyword arguments."""
    logger.info(
        f"Executing list_tasks for project {project_id}, session {session_id[:8]}, filters: {filters}"
    )
    api = get_api_client(session_id)
    try:
        import json

        filter_dict = json.loads(filters) if filters else {}
        # Add project_id to the filters
        filter_dict["project"] = project_id
        # Call client.get directly with params (workaround for pytaigaclient bug)
        tasks = api.get("/tasks", params=filter_dict)
        return tasks
    except TaigaException as e:
        logger.error(f"Taiga API error listing tasks for project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing tasks for project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error listing tasks: {e}")


@mcp.tool("create_task", description="Creates a new task within a project.")
def create_task(
    session_id: str, project_id: int, subject: str, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Creates a task. Requires project_id and subject. Optional fields (description, milestone_id, status_id, user_story_id, assigned_to_id, etc.) via kwargs dict."""
    logger.info(
        f"Executing create_task '{subject}' in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not subject:
        raise ValueError("Task subject cannot be empty.")
    try:
        extra_fields = kwargs if kwargs else {}
        task = api.tasks.create(project=project_id, subject=subject, data=extra_fields)
        logger.info(f"Task '{subject}' created successfully (ID: {task.get('id', 'N/A')}).")
        return task
    except TaigaException as e:
        logger.error(f"Taiga API error creating task '{subject}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating task '{subject}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating task: {e}")


@mcp.tool("get_task", description="Gets detailed information about a specific task by its ID.")
def get_task(session_id: str, task_id: int) -> dict[str, Any]:
    """Retrieves task details by ID."""
    logger.info(f"Executing get_task ID {task_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        task = api.tasks.get(task_id)
        return task
    except TaigaException as e:
        logger.error(f"Taiga API error getting task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting task: {e}")


@mcp.tool("update_task", description="Updates details of an existing task.")
def update_task(
    session_id: str, task_id: int, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Updates a task. Pass fields to update as keyword arguments JSON string (e.g., {\"subject\":\"New Title\", \"status_id\":123})."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing update_task ID {task_id} for session {session_id[:8]} with data: {extra_fields}"
    )
    api = get_api_client(session_id)
    try:
        if not extra_fields:
            raise ValueError("No fields provided for update.")

        current_task = api.tasks.get(task_id)
        version = current_task.get("version")
        if version is None:
            raise ValueError(f"Could not retrieve version for task {task_id}.")

        updated_task = api.tasks.edit(task_id=task_id, version=version, data=extra_fields)
        logger.info(f"Task {task_id} update request sent.")
        return updated_task
    except TaigaException as e:
        logger.error(f"Taiga API error updating task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating task: {e}")


@mcp.tool("delete_task", description="Deletes a task by its ID.")
def delete_task(session_id: str, task_id: int) -> dict[str, Any]:
    """Deletes a task by ID."""
    logger.warning(f"Executing delete_task ID {task_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        api.tasks.delete(task_id)
        logger.info(f"Task {task_id} deleted successfully.")
        return {"status": "deleted", "task_id": task_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting task: {e}")


@mcp.tool("assign_task_to_user", description="Assigns a specific task to a specific user.")
def assign_task_to_user(session_id: str, task_id: int, user_id: int) -> dict[str, Any]:
    """Assigns a task to a user."""
    logger.info(
        f"Executing assign_task_to_user: Task {task_id} -> User {user_id}, session {session_id[:8]}..."
    )
    return update_task(session_id, task_id, kwargs={"assigned_to": user_id})


@mcp.tool(
    "unassign_task_from_user", description="Unassigns a specific task (sets assigned user to null)."
)
def unassign_task_from_user(session_id: str, task_id: int) -> dict[str, Any]:
    """Unassigns a task."""
    logger.info(f"Executing unassign_task_from_user: Task {task_id}, session {session_id[:8]}...")
    return update_task(session_id, task_id, kwargs={"assigned_to": None})


@mcp.tool(
    "get_task_by_ref",
    description="Gets a task by its reference number within a project.",
)
def get_task_by_ref(session_id: str, project_id: int, ref: int) -> dict[str, Any]:
    """Retrieves a task by its reference number in a project."""
    logger.info(
        f"Executing get_task_by_ref #{ref} in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        task = api.tasks.get_by_ref(project=project_id, ref=ref)
        return task
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting task by ref #{ref} in project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting task by ref #{ref} in project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting task by ref: {e}")


@mcp.tool(
    "upvote_task",
    description="Adds a vote (star) to a task.",
)
def upvote_task(session_id: str, task_id: int) -> dict[str, Any]:
    """Votes for a task."""
    logger.info(f"Executing upvote_task ID {task_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.tasks.upvote(task_id)
        logger.info(f"Task {task_id} upvoted successfully.")
        return result if result else {"status": "upvoted", "task_id": task_id}
    except TaigaException as e:
        logger.error(f"Taiga API error upvoting task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error upvoting task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error upvoting task: {e}")


@mcp.tool(
    "downvote_task",
    description="Removes your vote (star) from a task.",
)
def downvote_task(session_id: str, task_id: int) -> dict[str, Any]:
    """Removes vote from a task."""
    logger.info(f"Executing downvote_task ID {task_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.tasks.downvote(task_id)
        logger.info(f"Task {task_id} downvoted successfully.")
        return result if result else {"status": "downvoted", "task_id": task_id}
    except TaigaException as e:
        logger.error(f"Taiga API error downvoting task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error downvoting task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error downvoting task: {e}")


@mcp.tool(
    "watch_task",
    description="Watch a task to receive notifications about changes.",
)
def watch_task(session_id: str, task_id: int) -> dict[str, Any]:
    """Watches a task."""
    logger.info(f"Executing watch_task ID {task_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.tasks.watch(task_id)
        logger.info(f"Task {task_id} watched successfully.")
        return result if result else {"status": "watching", "task_id": task_id}
    except TaigaException as e:
        logger.error(f"Taiga API error watching task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error watching task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error watching task: {e}")


@mcp.tool(
    "unwatch_task",
    description="Stop watching a task.",
)
def unwatch_task(session_id: str, task_id: int) -> dict[str, Any]:
    """Unwatches a task."""
    logger.info(f"Executing unwatch_task ID {task_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        result = api.tasks.unwatch(task_id)
        logger.info(f"Task {task_id} unwatched successfully.")
        return result if result else {"status": "unwatched", "task_id": task_id}
    except TaigaException as e:
        logger.error(f"Taiga API error unwatching task {task_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error unwatching task {task_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error unwatching task: {e}")


@mcp.tool(
    "get_task_statuses",
    description="Lists the available statuses for tasks within a specific project.",
)
def get_task_statuses(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Retrieves the list of task statuses for a project."""
    logger.info(
        f"Executing get_task_statuses for project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        statuses = api.task_statuses.list(project=project_id)
        return statuses
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting task statuses for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting task statuses for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting task statuses: {e}")
