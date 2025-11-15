"""
Helper module for building properly structured user stories and tasks.

This module provides a systematic way to create well-formed user stories
with proper subject, description, and task breakdown to prevent the common
mistake of dumping everything into the subject field.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class Task:
    """Represents a task within a user story."""

    subject: str
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API calls."""
        result = {"subject": self.subject}
        if self.description:
            result["description"] = self.description
        return result


@dataclass
class UserStory:
    """
    Represents a properly structured user story.

    Best practices:
    - subject: Brief title (5-10 words max)
    - description: Full user story with acceptance criteria, requirements, benefits
    - tasks: List of actionable tasks (3-8 tasks typically)
    - tags: List of tag names (e.g., ["docker", "automation", "infrastructure"])
    """

    subject: str
    description: str
    tasks: list[Task]
    points: int | None = None
    tags: list[str] | None = None

    def validate(self) -> list[str]:
        """
        Validate the user story structure and return list of warnings.

        Returns:
            List of validation warnings (empty if all good)
        """
        warnings = []

        # Check subject length
        if len(self.subject) > 100:
            warnings.append(
                f"Subject is too long ({len(self.subject)} chars). Keep it under 100 chars."
            )

        if len(self.subject.split()) > 15:
            warnings.append(
                f"Subject has too many words ({len(self.subject.split())}). "
                "Keep it to 5-10 words max."
            )

        # Check for newlines in subject (common mistake)
        if "\n" in self.subject:
            warnings.append(
                "Subject contains newlines! Subject should be a single line. "
                "Move detailed content to description."
            )

        # Check description exists and is substantial
        if not self.description or len(self.description) < 50:
            warnings.append(
                "Description is too short or missing. Include user story format, "
                "acceptance criteria, and requirements."
            )

        # Check for acceptance criteria in description
        if "acceptance criteria" not in self.description.lower():
            warnings.append(
                "Description should include 'Acceptance Criteria' section. "
                "What defines 'done' for this story?"
            )

        # Check tasks exist
        if not self.tasks:
            warnings.append("No tasks defined! Break down the story into 3-8 actionable tasks.")

        if len(self.tasks) > 12:
            warnings.append(
                f"Too many tasks ({len(self.tasks)}). Consider splitting into "
                "multiple user stories."
            )

        # Check task subjects are concise
        for i, task in enumerate(self.tasks, 1):
            if len(task.subject) > 80:
                warnings.append(
                    f"Task #{i} subject is too long ({len(task.subject)} chars). "
                    "Keep under 80 chars."
                )

        return warnings

    def to_mcp_params(self) -> dict[str, Any]:
        """
        Convert to parameters for create_user_story MCP call.

        Returns:
            Dictionary with 'subject' and 'kwargs' for create_user_story
        """
        kwargs = {"description": self.description}

        if self.points is not None:
            # Note: Story points are set via points field, not kwargs
            # This would need to be set separately after creation
            pass

        if self.tags:
            kwargs["tags"] = self.tags

        return {"subject": self.subject, "kwargs": kwargs}

    def get_task_params(self, user_story_id: int, project_id: int) -> list[dict[str, Any]]:
        """
        Get parameters for creating tasks via create_task MCP calls.

        Args:
            user_story_id: ID of the created user story
            project_id: Project ID

        Returns:
            List of parameter dictionaries for create_task calls
        """
        return [
            {
                "subject": task.subject,
                "project_id": project_id,
                "kwargs": {
                    "user_story": user_story_id,
                    "description": task.description if task.description else "",
                },
            }
            for task in self.tasks
        ]


def build_user_story(
    subject: str,
    user_story_text: str,
    acceptance_criteria: list[str],
    tasks: list[str | Task],
    technical_requirements: str = "",
    benefits: str = "",
    points: int | None = None,
    tags: list[str] | None = None,
) -> UserStory:
    """
    Build a well-structured user story from components.

    Args:
        subject: Brief title (5-10 words)
        user_story_text: The user story in "As a... I want... so that..." format
        acceptance_criteria: List of acceptance criteria items
        tasks: List of task subjects or Task objects
        technical_requirements: Optional technical details
        benefits: Optional benefits section
        points: Story points estimate
        tags: Optional list of tags (e.g., ["docker", "automation"])

    Returns:
        UserStory object ready for validation and MCP calls

    Example:
        >>> story = build_user_story(
        ...     subject="Container Registry Publishing",
        ...     user_story_text="As a DevOps engineer, I want automated Docker publishing...",
        ...     acceptance_criteria=[
        ...         "GitHub Actions workflow builds images",
        ...         "Images published to ghcr.io",
        ...     ],
        ...     tasks=[
        ...         "Create GitHub Actions workflow",
        ...         "Configure multi-arch builds",
        ...     ],
        ...     points=8
        ... )
        >>> warnings = story.validate()
        >>> if warnings:
        ...     print("⚠️  Warnings:", warnings)
    """
    # Build description
    description_parts = [user_story_text, ""]

    if acceptance_criteria:
        description_parts.append("## Acceptance Criteria\n")
        for criterion in acceptance_criteria:
            description_parts.append(f"- {criterion}")
        description_parts.append("")

    if technical_requirements:
        description_parts.append("## Technical Requirements\n")
        description_parts.append(technical_requirements)
        description_parts.append("")

    if benefits:
        description_parts.append("## Benefits\n")
        description_parts.append(benefits)
        description_parts.append("")

    description = "\n".join(description_parts).strip()

    # Convert tasks to Task objects
    task_objects = []
    for task in tasks:
        if isinstance(task, Task):
            task_objects.append(task)
        else:
            task_objects.append(Task(subject=task))

    return UserStory(
        subject=subject, description=description, tasks=task_objects, points=points, tags=tags
    )


def format_validation_warnings(warnings: list[str]) -> str:
    """Format validation warnings for display."""
    if not warnings:
        return "✅ User story structure looks good!"

    output = ["⚠️  User Story Validation Warnings:\n"]
    for i, warning in enumerate(warnings, 1):
        output.append(f"  {i}. {warning}")

    return "\n".join(output)


# Example usage
if __name__ == "__main__":
    # Good example
    story = build_user_story(
        subject="Automated Container Registry Publishing",
        user_story_text=(
            "As a DevOps engineer, I want pre-built Docker images automatically "
            "published to a container registry when releases are created, so that "
            "I can deploy pytaiga-mcp using standard container tooling."
        ),
        acceptance_criteria=[
            "GitHub Actions workflow automatically builds and publishes Docker images",
            "Images are published to GitHub Container Registry (ghcr.io)",
            "Multi-architecture support (amd64, arm64)",
            "Images are publicly accessible",
            "README includes Docker usage examples",
        ],
        tasks=[
            "Create GitHub Actions workflow",
            "Configure multi-arch builds",
            "Implement tagging strategy",
            "Optimize Dockerfile",
            "Update documentation",
            "Test and verify",
        ],
        technical_requirements=(
            "- Use ghcr.io for container registry\n"
            "- GitHub Actions workflow for automation\n"
            "- Multi-stage Dockerfile for optimization"
        ),
        benefits=(
            "- Instant deployment without building\n"
            "- Consistent environment\n"
            "- Simplified CI/CD"
        ),
        points=8,
    )

    print("=" * 60)
    print("GOOD EXAMPLE")
    print("=" * 60)
    print(format_validation_warnings(story.validate()))
    print("\nSubject:", story.subject)
    print("\nDescription preview:", story.description[:150] + "...")
    print(f"\nTasks ({len(story.tasks)}):")
    for i, task in enumerate(story.tasks, 1):
        print(f"  {i}. {task.subject}")

    # Bad example
    bad_story = UserStory(
        subject=(
            "Automated Container Registry Publishing\n\n"
            "As a DevOps engineer or end user, I want pre-built Docker images..."
        ),
        description="Do the thing",
        tasks=[],
    )

    print("\n\n" + "=" * 60)
    print("BAD EXAMPLE")
    print("=" * 60)
    print(format_validation_warnings(bad_story.validate()))
