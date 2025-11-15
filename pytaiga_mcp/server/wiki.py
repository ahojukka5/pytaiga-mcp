"""
Wiki page management tools for Taiga MCP server.

NOTE: In Taiga, wiki pages and wiki bookmarks are separate concepts:
- Wiki pages = content (created via API, visible in "all wiki pages")
- Wiki bookmarks = sidebar shortcuts (created via UI "Add bookmark" button)

Pages created via create_wiki_page() are fully functional and discoverable
through "all wiki pages" view. They just won't appear in the bookmark sidebar
unless the user manually adds them as bookmarks.
"""

import logging
from typing import Any

from pytaigaclient.exceptions import TaigaException

from .common import get_api_client, mcp

logger = logging.getLogger(__name__)


@mcp.tool("list_wiki_pages", description="Lists wiki pages within a specific project.")
def list_wiki_pages(session_id: str, project_id: int) -> list[dict[str, Any]]:
    """Lists all wiki pages for a project."""
    logger.info(f"Executing list_wiki_pages for project {project_id}, session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        # Use direct API call with params (consistent with tasks pattern)
        wiki_pages = api.get("/wiki", params={"project": project_id})
        return wiki_pages
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing wiki pages for project {project_id}: {e}", exc_info=False
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing wiki pages for project {project_id}: {e}", exc_info=True
        )
        raise RuntimeError(f"Server error listing wiki pages: {e}")


@mcp.tool("create_wiki_page", description="Creates a new wiki page within a project.")
def create_wiki_page(
    session_id: str,
    project_id: int,
    slug: str,
    content: str,
    kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Creates a wiki page. Requires project_id, slug, and content.

    Note: Created pages appear in "all wiki pages" view but won't be in the
    bookmark sidebar unless user manually adds them via "Add bookmark" button.
    """
    logger.info(
        f"Executing create_wiki_page '{slug}' in project {project_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not slug or not content:
        raise ValueError("Wiki page slug and content cannot be empty.")
    try:
        extra_fields = kwargs if kwargs else {}
        wiki_page = api.wiki.create(
            project=project_id, slug=slug, content=content, data=extra_fields
        )
        logger.info(f"Wiki page '{slug}' created successfully (ID: {wiki_page.get('id', 'N/A')}).")
        return wiki_page
    except TaigaException as e:
        logger.error(f"Taiga API error creating wiki page '{slug}': {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error creating wiki page '{slug}': {e}", exc_info=True)
        raise RuntimeError(f"Server error creating wiki page: {e}")


@mcp.tool("get_wiki_page", description="Gets a specific wiki page by its ID.")
def get_wiki_page(session_id: str, wiki_page_id: int) -> dict[str, Any]:
    """Retrieves wiki page details by ID."""
    logger.info(f"Executing get_wiki_page ID {wiki_page_id} for session {session_id[:8]}...")
    api = get_api_client(session_id)
    try:
        wiki_page = api.wiki.get(wiki_page_id)
        return wiki_page
    except TaigaException as e:
        logger.error(f"Taiga API error getting wiki page {wiki_page_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error getting wiki page {wiki_page_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error getting wiki page: {e}")


@mcp.tool("update_wiki_page", description="Updates an existing wiki page.")
def update_wiki_page(
    session_id: str,
    wiki_page_id: int,
    content: str,
    version: int,
    kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Updates a wiki page. Requires wiki_page_id, content, and version."""
    logger.info(
        f"Executing update_wiki_page ID {wiki_page_id} (version {version}), session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    if not content:
        raise ValueError("Wiki page content cannot be empty.")
    try:
        extra_fields = kwargs if kwargs else {}
        # Use PATCH to update the wiki page
        update_data = {"content": content, "version": version, **extra_fields}
        wiki_page = api.patch(f"/wiki/{wiki_page_id}", json=update_data)
        logger.info(f"Wiki page {wiki_page_id} updated successfully (version {version}).")
        return wiki_page
    except TaigaException as e:
        logger.error(f"Taiga API error updating wiki page {wiki_page_id}: {e}", exc_info=False)
        raise e
    except Exception as e:
        logger.error(f"Unexpected error updating wiki page {wiki_page_id}: {e}", exc_info=True)
        raise RuntimeError(f"Server error updating wiki page: {e}")


@mcp.tool(
    "create_wiki_attachment",
    description="Creates an attachment for a wiki page by uploading a file.",
)
def create_wiki_attachment(
    session_id: str,
    project_id: int,
    wiki_page_id: int,
    file_path: str,
    description: str | None = None,
) -> dict[str, Any]:
    """
    Uploads a file as an attachment to a wiki page.

    Args:
        session_id: MCP session ID
        project_id: Project ID
        wiki_page_id: Wiki page ID to attach to
        file_path: Absolute path to the file to upload
        description: Optional description for the attachment

    Returns:
        Attachment details including id, url, thumbnail_url, name, size
    """
    logger.info(
        f"Executing create_wiki_attachment for wiki page {wiki_page_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        with open(file_path, "rb") as f:
            attachment = api.wiki.create_attachment(
                project=project_id,
                object_id=wiki_page_id,
                attached_file=f,
                description=description,
            )
        if not attachment:
            raise RuntimeError("Attachment creation returned None")
        logger.info(
            f"Attachment created successfully (ID: {attachment.get('id', 'N/A')}, "
            f"URL: {attachment.get('url', 'N/A')})."
        )
        return attachment
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise ValueError(f"File not found: {file_path}")
    except TaigaException as e:
        logger.error(
            f"Taiga API error creating wiki attachment for page {wiki_page_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error creating wiki attachment for page {wiki_page_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error creating wiki attachment: {e}")


@mcp.tool("list_wiki_attachments", description="Lists all attachments for a specific wiki page.")
def list_wiki_attachments(
    session_id: str, project_id: int, wiki_page_id: int
) -> list[dict[str, Any]]:
    """Lists all attachments for a wiki page."""
    logger.info(
        f"Executing list_wiki_attachments for wiki page {wiki_page_id}, session {session_id[:8]}..."
    )
    api = get_api_client(session_id)
    try:
        attachments = api.wiki.list_attachments(project=project_id, object_id=wiki_page_id)
        return attachments
    except TaigaException as e:
        logger.error(
            f"Taiga API error listing wiki attachments for page {wiki_page_id}: {e}",
            exc_info=False,
        )
        raise e
    except Exception as e:
        logger.error(
            f"Unexpected error listing wiki attachments for page {wiki_page_id}: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Server error listing wiki attachments: {e}")
