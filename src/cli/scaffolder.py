"""Template scaffolding utilities."""

from datetime import date
from typing import Any


def build_substitutions(project_name: str) -> dict[str, Any]:
    """Build substitution variables for template customization.

    Args:
        project_name: The project name (e.g., "my-task-app")

    Returns:
        Dictionary of substitution variables

    Raises:
        ValueError: If project_name is empty or contains only whitespace
    """
    if not project_name or not project_name.strip():
        raise ValueError("project_name must not be empty or whitespace-only")

    # Convert to snake_case
    snake_name = project_name.replace("-", "_")

    # Convert to Title Case
    words = project_name.replace("-", " ").replace("_", " ").split()
    title_name = " ".join(word.capitalize() for word in words)

    return {
        "PROJECT_NAME": project_name,
        "PROJECT_NAME_SNAKE": snake_name,
        "PROJECT_NAME_TITLE": title_name,
        "SCHEMA_ID": f"{project_name}-v1",
        "CREATED_DATE": date.today().isoformat(),
    }


def apply_substitutions(content: str, substitutions: dict[str, Any]) -> str:
    """Apply substitutions to template content.

    Args:
        content: Template content with {{VARIABLE}} placeholders
        substitutions: Dictionary of variable names to values

    Returns:
        Content with substitutions applied
    """
    result = content
    for key, value in substitutions.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result
