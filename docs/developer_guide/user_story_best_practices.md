# User Story Creation Best Practices

## The Problem

When creating user stories programmatically, it's easy to make these mistakes:

1. **Dump everything in the subject field** - Subject becomes a multi-paragraph essay
2. **Empty or minimal description** - All the details are in the wrong place
3. **No tasks created** - Story has no actionable breakdown
4. **Poor structure** - Missing acceptance criteria, requirements, or benefits

These mistakes make stories hard to read, track, and work with.

## The Solution

Use the `story_builder` helper module to systematically create well-structured stories.

### Quick Start

```python
from pytaiga_mcp.helpers import build_user_story, format_validation_warnings

# Build a well-structured user story
story = build_user_story(
    subject="Add OAuth Support",  # Short title
    user_story_text="As a developer, I want OAuth authentication so that users can login with GitHub",
    acceptance_criteria=[
        "GitHub OAuth integration works",
        "Users can login with GitHub account",
        "Token is securely stored",
    ],
    tasks=[
        "Implement GitHub OAuth flow",
        "Add OAuth configuration",
        "Update authentication UI",
        "Write tests",
    ],
    points=5
)

# Validate before creating
warnings = story.validate()
if warnings:
    print(format_validation_warnings(warnings))
else:
    # Create in Taiga
    params = story.to_mcp_params()
    # Use mcp_taiga_create_user_story with params
```

### Structure Rules

#### Subject (Title)

- **Length**: 5-10 words maximum
- **Format**: Single line, no newlines
- **Content**: Brief description only
- **Examples**:
  - ✅ "Automated Container Registry Publishing"
  - ✅ "Add OAuth Support"
  - ✅ "Improve Error Messages"
  - ❌ "Automated Container Registry Publishing\n\nAs a DevOps engineer..." (too long)
  - ❌ "Implement support for automated Docker image publishing to container registry with multi-arch builds" (too wordy)

#### Description

- **Required sections**:
  1. User story ("As a... I want... so that...")
  2. Acceptance Criteria (bullet list)
  3. Technical Requirements (optional but recommended)
  4. Benefits (optional but recommended)
- **Format**: Markdown with headers
- **Length**: Substantial (at least 50 characters, typically 200-1000)

#### Tasks

- **Count**: 3-8 tasks per story (not 0, not 20)
- **Format**: Action-oriented, concise subjects
- **Length**: Under 80 characters per task
- **Examples**:
  - ✅ "Create GitHub Actions workflow"
  - ✅ "Update documentation"
  - ❌ "We need to create a comprehensive GitHub Actions workflow that handles building and publishing Docker images to the container registry with multi-architecture support" (too long)

### Using the Builder

```python
from pytaiga_mcp.helpers import build_user_story, Task

# Simple version
story = build_user_story(
    subject="Feature Name",
    user_story_text="As a USER, I want FEATURE so that BENEFIT",
    acceptance_criteria=["Criterion 1", "Criterion 2"],
    tasks=["Task 1", "Task 2"],
    points=3
)

# Advanced version with detailed tasks
story = build_user_story(
    subject="Advanced Feature",
    user_story_text="As a USER...",
    acceptance_criteria=["Criterion 1", "Criterion 2"],
    tasks=[
        Task("Main task", "Detailed description of what this involves"),
        Task("Another task", "More details here"),
    ],
    technical_requirements="- Requirement 1\n- Requirement 2",
    benefits="- Benefit 1\n- Benefit 2",
    points=8
)

# Validate
warnings = story.validate()
print(format_validation_warnings(warnings))

# Convert to MCP parameters
story_params = story.to_mcp_params()
# {'subject': 'Feature Name', 'kwargs': {'description': '...'}}

# After creating the story, get task parameters
task_params = story.get_task_params(
    user_story_id=12345,
    project_id=1000
)
# Returns list of dicts ready for mcp_taiga_create_task
```

### Validation Warnings

The `validate()` method checks for common mistakes:

1. **Subject too long** - Over 100 characters
2. **Subject too wordy** - More than 15 words
3. **Newlines in subject** - Multi-line subjects
4. **Description too short** - Less than 50 characters
5. **Missing acceptance criteria** - No "Acceptance Criteria" section
6. **No tasks** - Empty task list
7. **Too many tasks** - More than 12 tasks
8. **Task subjects too long** - Over 80 characters

Fix warnings before creating the story in Taiga!

### Example: Good vs Bad

#### ❌ Bad Example

```python
# DON'T DO THIS
story = UserStory(
    subject="""Automated Container Registry Publishing

As a DevOps engineer or end user, I want pre-built Docker images 
automatically published to a container registry when releases are 
created, so that I can deploy pytaiga-mcp using standard container 
tooling without building from source.

Acceptance Criteria:
- GitHub Actions workflow automatically builds and publishes
- Images published to ghcr.io
- Multi-architecture support

Technical Requirements:
- Use ghcr.io
- GitHub Actions
- Multi-stage Dockerfile""",  # Everything in subject!
    description="",  # Empty description
    tasks=[]  # No tasks
)
```

#### ✅ Good Example

```python
# DO THIS
story = build_user_story(
    subject="Automated Container Registry Publishing",  # Brief title
    user_story_text=(
        "As a DevOps engineer or end user, I want pre-built Docker images "
        "automatically published to a container registry when releases are "
        "created, so that I can deploy pytaiga-mcp using standard container "
        "tooling without building from source."
    ),
    acceptance_criteria=[
        "GitHub Actions workflow automatically builds and publishes",
        "Images published to GitHub Container Registry (ghcr.io)",
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
        "- Instant deployment\n"
        "- Consistent environment\n"
        "- Simplified CI/CD"
    ),
    points=8
)

# Always validate!
warnings = story.validate()
if warnings:
    print("⚠️  Fix these issues:")
    for warning in warnings:
        print(f"  - {warning}")
```

### Integration with MCP

```python
from pytaiga_mcp.helpers import build_user_story, format_validation_warnings

# 1. Build the story
story = build_user_story(...)

# 2. Validate
warnings = story.validate()
if warnings:
    print(format_validation_warnings(warnings))
    # Fix issues before proceeding!
    raise ValueError("Story validation failed")

# 3. Create user story in Taiga
params = story.to_mcp_params()
result = mcp_taiga_create_user_story(
    session_id=session_id,
    project_id=project_id,
    subject=params["subject"],
    kwargs=params["kwargs"]
)
user_story_id = result["id"]

# 4. Create tasks
task_params = story.get_task_params(
    user_story_id=user_story_id,
    project_id=project_id
)
for task_param in task_params:
    mcp_taiga_create_task(
        session_id=session_id,
        **task_param
    )
```

### Testing

```python
from pytaiga_mcp.helpers import build_user_story

def test_story_structure():
    story = build_user_story(
        subject="Test Story",
        user_story_text="As a tester, I want validation so that bugs are caught",
        acceptance_criteria=["Tests pass", "Coverage is high"],
        tasks=["Write tests", "Run tests"],
        points=2
    )
    
    # Should have no warnings
    warnings = story.validate()
    assert len(warnings) == 0, f"Validation failed: {warnings}"
    
    # Subject should be clean
    assert "\n" not in story.subject
    assert len(story.subject) < 100
    
    # Description should have structure
    assert "Acceptance Criteria" in story.description
    
    # Tasks should exist
    assert len(story.tasks) >= 2
```

## Summary Checklist

When creating user stories:

- [ ] Use `build_user_story()` helper
- [ ] Keep subject to 5-10 words
- [ ] Include proper user story format in description
- [ ] Add acceptance criteria section
- [ ] Create 3-8 actionable tasks
- [ ] Run `validate()` before creating in Taiga
- [ ] Fix all validation warnings
- [ ] Create tasks after creating story

**Remember**: The helper exists to prevent catastrophes. Use it!
