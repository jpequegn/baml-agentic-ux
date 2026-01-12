"""Template scaffolding utilities."""

from datetime import date
from pathlib import Path
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


def scaffold_template(
    template_dir: Path,
    project_name: str,
    output_dir: Path,
) -> list[Path]:
    """Scaffold a template to the output directory.

    Args:
        template_dir: Path to the template directory
        project_name: Name for the new project
        output_dir: Where to create the scaffolded project

    Returns:
        List of created file paths
    """
    substitutions = build_substitutions(project_name)
    output_dir.mkdir(parents=True, exist_ok=True)

    created_files = []

    for template_file in template_dir.iterdir():
        if template_file.is_file():
            content = template_file.read_text()
            customized = apply_substitutions(content, substitutions)

            output_file = output_dir / template_file.name
            output_file.write_text(customized)
            created_files.append(output_file)

    return created_files
