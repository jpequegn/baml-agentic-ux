"""LUI Starter Templates.

Templates for learning BAML LUI patterns:
- crud: Basic CRUD operations (create, read, update, delete)
- search: Search & discovery with filters
- workflow: Multi-step conversational flows
- support: Help desk & support patterns
"""

from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent
AVAILABLE_TEMPLATES = {
    "crud": "CRUD operations (create, read, update, delete)",
    "search": "Search & discovery with filters",
    "workflow": "Multi-step conversational flows",
    "support": "Help desk & support patterns",
}


def get_template_dir(template_name: str) -> Path:
    """Get the directory path for a template.

    Args:
        template_name: Name of the template (crud, search, workflow, support)

    Returns:
        Path to the template directory

    Raises:
        ValueError: If template name is not recognized
    """
    if template_name not in AVAILABLE_TEMPLATES:
        valid = ", ".join(AVAILABLE_TEMPLATES.keys())
        raise ValueError(f"Unknown template: {template_name}. Valid templates: {valid}")
    return TEMPLATES_DIR / template_name
