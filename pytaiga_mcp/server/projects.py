"""
Project management tools for Taiga MCP server.
"""

import logging
from typing import Any

from pytaigaclient.exceptions import TaigaException

from .common import get_api_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool(
    "list_projects",
    description="Lists projects accessible to the user associated with the provided session_id.",
)
def list_projects(session_id: str) -> list[dict[str, Any]]:
    """Lists projects accessible by the authenticated user."""
    logger.info(f"Executing list_projects for session {session_id[:8]}...")
    from .common import get_authenticated_client

    wrapper = get_authenticated_client(session_id)
    api = wrapper.api
    if api is None:
        raise PermissionError("Client is authenticated but API instance is unavailable.")
    try:
        # Get user_id from the wrapper and filter by member
        user_id = wrapper.user_id
        if user_id is None:
            logger.warning("User ID not available in session, falling back to unfiltered list")
            projects = api.projects.list()
        else:
            # Filter projects by member parameter to get only user's projects
            projects = api.projects.list(member=user_id)

        logger.info(
            f"list_projects successful for session {session_id[:8]}, found {len(projects)} projects."
        )
        return projects
    except TaigaException as e:
        logger.error(f"Taiga API error listing projects: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error listing projects: {e}", exc_info=True)
        raise RuntimeError(f"Server error listing projects: {e}")


@mcp.tool(
    "list_all_projects",
    description="Lists all projects visible to the user (requires admin privileges for full list). Uses the provided session_id.",
)
def list_all_projects(session_id: str) -> list[dict[str, Any]]:
    """
    Lists all projects visible to the authenticated user.

    Note: This is actually the same as list_projects since Taiga API filters by member.
    To see truly all public projects (not just member projects), don't pass the member parameter.
    However, that's not usually what users want - they want their projects.
    """
    logger.info(f"Executing list_all_projects for session {session_id[:8]}...")
    # For now, this is the same as list_projects - it lists the user's projects
    # If we really want ALL public projects, we would call without member parameter:
    # return api.projects.list()
    return list_projects(session_id)


@mcp.tool(
    "get_project", description="Gets detailed information about a specific project by its ID."
)
def get_project(session_id: str, project_id: int) -> dict[str, Any]:
    """Retrieves project details by ID."""
    logger.info(f"Executing get_project ID {project_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        project = api.projects.get(project_id)
        return project
    except TaigaException as e:
        logger.error(f"Taiga API error getting project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting project: {e}")


@mcp.tool(
    "get_project_by_slug",
    description="Gets detailed information about a specific project by its slug.",
)
def get_project_by_slug(session_id: str, slug: str) -> dict[str, Any]:
    """Retrieves project details by slug."""
    logger.info(f"Executing get_project_by_slug '{slug}' for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        project = api.projects.get(slug=slug)
        return project
    except TaigaException as e:
        logger.error(f"Taiga API error getting project by slug '{slug}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting project by slug '{slug}': {e}", exc_info=True)
        raise RuntimeError(f"Server error getting project by slug: {e}")


@mcp.tool("create_project", description="Creates a new project.")
def create_project(
    session_id: str, name: str, description: str, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Creates a new project. Requires name and description. Optional args (e.g., is_private) via kwargs JSON string."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing create_project '{name}' for session {session_id[:8]} with data: {extra_fields}"
    )
    api = get_api_client(session_id)
    if not name or not description:
        raise ValueError("Project name and description are required.")
    try:
        new_project = api.projects.create(name=name, description=description, **extra_fields)
        logger.info(f"Project '{name}' created successfully (ID: {new_project.get('id', 'N/A')}).")
        return new_project
    except TaigaException as e:
        logger.error(f"Taiga API error creating project '{name}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating project '{name}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating project: {e}")


@mcp.tool("update_project", description="Updates details of an existing project.")
def update_project(
    session_id: str, project_id: int, kwargs: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Updates a project. Pass fields to update as keyword arguments JSON string (e.g., {\"name\":\"New Name\", \"description\":\"New Desc\"})."""
    extra_fields = kwargs if kwargs else {}
    logger.info(
        f"Executing update_project ID {project_id} for session {session_id[:8]} with data: {extra_fields}"
    )
    api = get_api_client(session_id)
    try:
        if not extra_fields:
            raise ValueError("No fields provided for update.")

        current_project = api.projects.get(project_id=project_id)
        version = current_project.get("version")
        if version is None:
            raise ValueError(f"Could not retrieve version for project {project_id}.")

        updated_project = api.projects.update(
            project_id=project_id, version=version, project_data=extra_fields
        )
        logger.info(f"Project {project_id} update request sent.")
        return updated_project
    except TaigaException as e:
        logger.error(f"Taiga API error updating project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating project: {e}")


@mcp.tool("delete_project", description="Deletes a project by its ID. This is irreversible.")
def delete_project(session_id: str, project_id: int) -> dict[str, Any]:
    """Deletes a project by ID."""
    logger.warning(f"Executing delete_project ID {project_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        api.projects.delete(id=project_id)
        logger.info(f"Project {project_id} deleted successfully.")
        return {"status": "deleted", "project_id": project_id}
    except TaigaException as e:
        logger.error(f"Taiga API error deleting project {project_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error deleting project {project_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error deleting project: {e}")


@mcp.tool("get_project_members", description="Lists members of a specific project.")
def get_project_members(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Retrieves the list of members for a project."""
    logger.info(
        f"Executing get_project_members for project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        members = api.memberships.list(project=project_id)
        return members
    except TaigaException as e:
        logger.error(
            f"Taiga API error getting project members for project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error getting project members for project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error getting project members: {e}")


@mcp.tool(
    "invite_project_user",
    description="Invites a user to a project by email with a specific role.",
)
def invite_project_user(
    session_id: str, project_id: int, email: str, role_id: int
) -> dict[str, Any]:
    """Invites a user via email to join the project with the specified role ID."""
    logger.info(
        f"Executing invite_project_user {email} to project {project_id} (role {role_id}), session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not email:
        raise ValueError("Email cannot be empty.")
    try:
        invitation = api.memberships.create(project=project_id, email=email, role=role_id)
        logger.info(f"Invitation sent to {email} for project {project_id}.")
        return invitation
    except TaigaException as e:
        logger.error(
            f"Taiga API error inviting user {email} to project {project_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error inviting user {email} to project {project_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error inviting user: {e}")
