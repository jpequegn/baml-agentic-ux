# LUI Starter Templates Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Create a CLI tool that scaffolds educational LUI templates for developers learning BAML patterns.

**Architecture:** Python CLI using questionary for interactive prompts, bundled templates in `src/templates/`, string substitution for customization.

**Tech Stack:** Python 3.12, questionary (interactive prompts), rich (terminal styling), pytest

---

## Task 1: Create CLI Module Structure

**Files:**
- Create: `src/cli/__init__.py`
- Create: `src/cli/__main__.py`

**Step 1: Create CLI package init**

```python
# src/cli/__init__.py
"""CLI module for baml-agentic-ux."""

from .init_command import main

__all__ = ["main"]
```

**Step 2: Create CLI entry point**

```python
# src/cli/__main__.py
"""Entry point for python -m baml_agentic_ux."""

from src.cli import main

if __name__ == "__main__":
    main()
```

**Step 3: Verify directory structure exists**

Run: `ls -la src/cli/`
Expected: Shows `__init__.py` and `__main__.py`

**Step 4: Commit**

```bash
git add src/cli/
git commit -m "feat(cli): Add CLI module structure"
```

---

## Task 2: Add CLI Dependencies

**Files:**
- Modify: `pyproject.toml`

**Step 1: Add questionary and rich dependencies**

Add to `[project.dependencies]` in pyproject.toml:
```toml
dependencies = [
    "baml-py>=0.215.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0.0",
    "questionary>=2.0.0",
    "rich>=13.0.0",
]
```

**Step 2: Add CLI entry point script**

Add to pyproject.toml:
```toml
[project.scripts]
baml-agentic-ux = "src.cli:main"
```

**Step 3: Install dependencies**

Run: `uv sync`
Expected: questionary and rich installed

**Step 4: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "feat(cli): Add questionary and rich dependencies"
```

---

## Task 3: Implement Scaffolder Core

**Files:**
- Create: `src/cli/scaffolder.py`
- Create: `tests/test_cli_scaffolder.py`

**Step 1: Write failing test for substitution building**

```python
# tests/test_cli_scaffolder.py
"""Tests for template scaffolder."""

import pytest
from src.cli.scaffolder import build_substitutions


class TestBuildSubstitutions:
    """Test substitution variable building."""

    def test_builds_all_variables(self):
        """Test that all substitution variables are created."""
        result = build_substitutions("my-task-app")

        assert result["PROJECT_NAME"] == "my-task-app"
        assert result["PROJECT_NAME_SNAKE"] == "my_task_app"
        assert result["PROJECT_NAME_TITLE"] == "My Task App"
        assert result["SCHEMA_ID"] == "my-task-app-v1"
        assert "CREATED_DATE" in result

    def test_handles_single_word(self):
        """Test single word project names."""
        result = build_substitutions("myapp")

        assert result["PROJECT_NAME"] == "myapp"
        assert result["PROJECT_NAME_SNAKE"] == "myapp"
        assert result["PROJECT_NAME_TITLE"] == "Myapp"

    def test_handles_underscores(self):
        """Test project names with underscores."""
        result = build_substitutions("my_cool_app")

        assert result["PROJECT_NAME_SNAKE"] == "my_cool_app"
        assert result["PROJECT_NAME_TITLE"] == "My Cool App"
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_scaffolder.py -v`
Expected: FAIL with "ModuleNotFoundError" or "cannot import name"

**Step 3: Write minimal implementation**

```python
# src/cli/scaffolder.py
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
    """
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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_scaffolder.py -v`
Expected: All 3 tests PASS

**Step 5: Commit**

```bash
git add src/cli/scaffolder.py tests/test_cli_scaffolder.py
git commit -m "feat(cli): Add substitution variable builder"
```

---

## Task 4: Implement Template Application

**Files:**
- Modify: `src/cli/scaffolder.py`
- Modify: `tests/test_cli_scaffolder.py`

**Step 1: Write failing test for template application**

Add to `tests/test_cli_scaffolder.py`:

```python
class TestApplySubstitutions:
    """Test applying substitutions to template content."""

    def test_replaces_all_variables(self):
        """Test that all variables are replaced."""
        content = "# {{PROJECT_NAME_TITLE}}\n\nSchema ID: {{SCHEMA_ID}}"
        subs = {"PROJECT_NAME_TITLE": "My App", "SCHEMA_ID": "my-app-v1"}

        result = apply_substitutions(content, subs)

        assert result == "# My App\n\nSchema ID: my-app-v1"

    def test_leaves_unknown_variables(self):
        """Test that unknown variables are left unchanged."""
        content = "Hello {{UNKNOWN}}"
        subs = {"PROJECT_NAME": "test"}

        result = apply_substitutions(content, subs)

        assert result == "Hello {{UNKNOWN}}"
```

Update import at top:
```python
from src.cli.scaffolder import build_substitutions, apply_substitutions
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_scaffolder.py::TestApplySubstitutions -v`
Expected: FAIL with "cannot import name 'apply_substitutions'"

**Step 3: Write minimal implementation**

Add to `src/cli/scaffolder.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_scaffolder.py -v`
Expected: All 5 tests PASS

**Step 5: Commit**

```bash
git add src/cli/scaffolder.py tests/test_cli_scaffolder.py
git commit -m "feat(cli): Add template substitution application"
```

---

## Task 5: Implement Template Scaffolding

**Files:**
- Modify: `src/cli/scaffolder.py`
- Modify: `tests/test_cli_scaffolder.py`

**Step 1: Write failing test for scaffolding**

Add to `tests/test_cli_scaffolder.py`:

```python
import tempfile
import shutil


class TestScaffoldTemplate:
    """Test full template scaffolding."""

    def test_copies_and_customizes_files(self, tmp_path):
        """Test that files are copied and customized."""
        # Create a mock template directory
        template_dir = tmp_path / "templates" / "crud"
        template_dir.mkdir(parents=True)

        # Create template files
        (template_dir / "schema.json").write_text('{"schema_id": "{{SCHEMA_ID}}"}')
        (template_dir / "README.md").write_text("# {{PROJECT_NAME_TITLE}}")

        output_dir = tmp_path / "output"

        scaffold_template(
            template_dir=template_dir,
            project_name="my-app",
            output_dir=output_dir,
        )

        # Verify files exist and are customized
        assert (output_dir / "schema.json").exists()
        assert (output_dir / "README.md").exists()

        schema_content = (output_dir / "schema.json").read_text()
        assert '"schema_id": "my-app-v1"' in schema_content

        readme_content = (output_dir / "README.md").read_text()
        assert "# My App" in readme_content

    def test_creates_output_directory(self, tmp_path):
        """Test that output directory is created if it doesn't exist."""
        template_dir = tmp_path / "templates" / "test"
        template_dir.mkdir(parents=True)
        (template_dir / "file.txt").write_text("test")

        output_dir = tmp_path / "new" / "nested" / "output"

        scaffold_template(
            template_dir=template_dir,
            project_name="test",
            output_dir=output_dir,
        )

        assert output_dir.exists()
        assert (output_dir / "file.txt").exists()
```

Update import:
```python
from src.cli.scaffolder import build_substitutions, apply_substitutions, scaffold_template
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_scaffolder.py::TestScaffoldTemplate -v`
Expected: FAIL with "cannot import name 'scaffold_template'"

**Step 3: Write minimal implementation**

Add to `src/cli/scaffolder.py`:

```python
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
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_scaffolder.py -v`
Expected: All 7 tests PASS

**Step 5: Commit**

```bash
git add src/cli/scaffolder.py tests/test_cli_scaffolder.py
git commit -m "feat(cli): Add template scaffolding function"
```

---

## Task 6: Create Templates Directory Structure

**Files:**
- Create: `src/templates/__init__.py`
- Create: `src/templates/crud/`
- Create: `src/templates/search/`
- Create: `src/templates/workflow/`
- Create: `src/templates/support/`

**Step 1: Create templates package**

```python
# src/templates/__init__.py
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
```

**Step 2: Create template directories**

```bash
mkdir -p src/templates/crud src/templates/search src/templates/workflow src/templates/support
```

**Step 3: Create placeholder files**

Create empty `.gitkeep` files in each directory to preserve structure:

```bash
touch src/templates/crud/.gitkeep
touch src/templates/search/.gitkeep
touch src/templates/workflow/.gitkeep
touch src/templates/support/.gitkeep
```

**Step 4: Commit**

```bash
git add src/templates/
git commit -m "feat(templates): Create template directory structure"
```

---

## Task 7: Create CRUD Template - Schema

**Files:**
- Create: `src/templates/crud/schema.json`

**Step 1: Create CRUD schema based on existing task_manager_schema.json**

```json
{
  "schema_id": "{{SCHEMA_ID}}",
  "name": "{{PROJECT_NAME_TITLE}} LUI",
  "description": "A Language User Interface for {{PROJECT_NAME_TITLE}}",
  "version": "1.0.0",
  "domain": {
    "domain_name": "{{PROJECT_NAME}}",
    "subdomain": "crud-operations",
    "description": "Basic CRUD operations demonstrating LUI patterns",
    "key_concepts": ["items", "create", "read", "update", "delete"]
  },
  "components": [
    {
      "component_id": "create-item",
      "component_type": "ACTION",
      "intent": "Create a new item",
      "description": "Demonstrates ACTION component type with required parameters",
      "invocation": {
        "primary_phrase": "create item",
        "alternate_phrases": ["add item", "new item", "make item"],
        "examples": [
          "Create an item called test",
          "Add a new item",
          "Make item with name report"
        ]
      },
      "parameters": [
        {
          "name": "title",
          "type": "string",
          "required": true,
          "description": "Title of the item"
        },
        {
          "name": "description",
          "type": "string",
          "required": false,
          "description": "Optional description"
        }
      ],
      "feedback": {
        "success_template": "Created item '{title}' successfully",
        "error_template": "Could not create item: {error}",
        "confirmation_required": false
      }
    },
    {
      "component_id": "list-items",
      "component_type": "QUERY",
      "intent": "List all items",
      "description": "Demonstrates QUERY component type for retrieving data",
      "invocation": {
        "primary_phrase": "list items",
        "alternate_phrases": ["show items", "my items", "get items"],
        "examples": [
          "Show me my items",
          "List all items",
          "What items do I have?"
        ]
      },
      "feedback": {
        "success_template": "Here are your items",
        "error_template": "Could not retrieve items: {error}",
        "confirmation_required": false
      }
    },
    {
      "component_id": "update-item",
      "component_type": "ACTION",
      "intent": "Update an existing item",
      "description": "Demonstrates updating with entity reference",
      "invocation": {
        "primary_phrase": "update item",
        "alternate_phrases": ["edit item", "change item", "modify item"],
        "examples": [
          "Update item 123",
          "Edit the latest item",
          "Change item title to 'New Title'"
        ]
      },
      "parameters": [
        {
          "name": "item_id",
          "type": "string",
          "required": true,
          "description": "ID or reference to the item"
        },
        {
          "name": "title",
          "type": "string",
          "required": false,
          "description": "New title"
        }
      ],
      "feedback": {
        "success_template": "Updated item successfully",
        "error_template": "Could not update item: {error}",
        "confirmation_required": false
      }
    },
    {
      "component_id": "delete-item",
      "component_type": "ACTION",
      "intent": "Delete an item",
      "description": "Demonstrates confirmation for destructive actions",
      "invocation": {
        "primary_phrase": "delete item",
        "alternate_phrases": ["remove item", "trash item"],
        "examples": [
          "Delete item 123",
          "Remove the old item"
        ]
      },
      "parameters": [
        {
          "name": "item_id",
          "type": "string",
          "required": true,
          "description": "ID or reference to the item"
        }
      ],
      "feedback": {
        "success_template": "Item deleted",
        "error_template": "Could not delete item: {error}",
        "confirmation_required": true,
        "confirmation_prompt": "Are you sure you want to delete this item? This cannot be undone."
      }
    },
    {
      "component_id": "help",
      "component_type": "FEEDBACK",
      "intent": "Get help with using the interface",
      "description": "Demonstrates FEEDBACK component type for discoverability",
      "invocation": {
        "primary_phrase": "help",
        "alternate_phrases": ["what can you do", "commands", "?"],
        "examples": [
          "Help",
          "What can you do?",
          "Show me commands"
        ]
      },
      "feedback": {
        "success_template": "I can help you manage items. You can create, list, update, or delete items. Try 'create item' or 'list items' to get started!",
        "error_template": "Sorry, I couldn't load help",
        "confirmation_required": false
      }
    }
  ]
}
```

**Step 2: Remove .gitkeep**

```bash
rm src/templates/crud/.gitkeep
```

**Step 3: Commit**

```bash
git add src/templates/crud/schema.json
git commit -m "feat(templates): Add CRUD template schema"
```

---

## Task 8: Create CRUD Template - README

**Files:**
- Create: `src/templates/crud/README.md`

**Step 1: Create educational README**

```markdown
# {{PROJECT_NAME_TITLE}} - CRUD Template

This template demonstrates fundamental LUI (Language User Interface) patterns using BAML.

## What You'll Learn

1. **Component Types** - ACTION, QUERY, and FEEDBACK components
2. **Invocation Patterns** - Primary phrases, alternates, and examples
3. **Feedback Templates** - Success, error, and confirmation messages
4. **Destructive Action Confirmation** - Protecting users from accidents

## Quick Start

```bash
# Load the schema
python integration.py

# Run tests
pytest test_integration.py -v
```

## Schema Structure

### Components

| Component | Type | Purpose |
|-----------|------|---------|
| `create-item` | ACTION | Create new items |
| `list-items` | QUERY | Retrieve items |
| `update-item` | ACTION | Modify existing items |
| `delete-item` | ACTION | Remove items (with confirmation) |
| `help` | FEEDBACK | Discoverability |

### Key Patterns Demonstrated

#### 1. Invocation Triad
Every component defines three levels of invocation:
- `primary_phrase`: The main way to invoke ("create item")
- `alternate_phrases`: Common variations ("add item", "new item")
- `examples`: Full example sentences for intent matching

#### 2. Feedback Templates
Use template variables for dynamic responses:
```json
"success_template": "Created item '{title}' successfully"
```
The `{title}` placeholder is filled from extracted parameters.

#### 3. Confirmation for Destructive Actions
The delete component sets:
```json
"confirmation_required": true,
"confirmation_prompt": "Are you sure...?"
```
This prevents accidental data loss.

## Files

- `schema.json` - The LUI schema definition
- `integration.py` - Python code demonstrating schema usage
- `test_integration.py` - Tests showing expected behavior
- `README.md` - This file

## Next Steps

1. Modify the schema to match your domain
2. Add more components as needed
3. Test with the LUI simulator
4. Export to OpenAPI or MCP format

Generated on: {{CREATED_DATE}}
```

**Step 2: Commit**

```bash
git add src/templates/crud/README.md
git commit -m "feat(templates): Add CRUD template README"
```

---

## Task 9: Create CRUD Template - Integration Code

**Files:**
- Create: `src/templates/crud/integration.py`

**Step 1: Create integration example**

```python
"""{{PROJECT_NAME_TITLE}} - Integration Example.

This module demonstrates how to use a LUI schema with the BAML client.
Generated from the CRUD template on {{CREATED_DATE}}.
"""

import json
from pathlib import Path


def load_schema() -> dict:
    """Load the LUI schema from schema.json.

    Returns:
        The parsed schema dictionary
    """
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


def find_component(schema: dict, component_id: str) -> dict | None:
    """Find a component by ID in the schema.

    Args:
        schema: The loaded schema
        component_id: ID of the component to find

    Returns:
        The component dictionary or None if not found
    """
    for component in schema.get("components", []):
        if component.get("component_id") == component_id:
            return component
    return None


def match_invocation(component: dict, user_input: str) -> bool:
    """Check if user input matches a component's invocation patterns.

    This is a simplified matcher - in production, use BAML's
    ExtractIntent function for intelligent matching.

    Args:
        component: The component to match against
        user_input: The user's input text

    Returns:
        True if the input matches any invocation pattern
    """
    invocation = component.get("invocation", {})
    user_lower = user_input.lower()

    # Check primary phrase
    if invocation.get("primary_phrase", "").lower() in user_lower:
        return True

    # Check alternate phrases
    for alt in invocation.get("alternate_phrases", []):
        if alt.lower() in user_lower:
            return True

    return False


def generate_feedback(component: dict, success: bool, context: dict = None) -> str:
    """Generate feedback message for a component action.

    Args:
        component: The component that was invoked
        success: Whether the action succeeded
        context: Dictionary of values to substitute in template

    Returns:
        The formatted feedback message
    """
    feedback = component.get("feedback", {})
    context = context or {}

    if success:
        template = feedback.get("success_template", "Done")
    else:
        template = feedback.get("error_template", "An error occurred")

    # Simple template substitution
    result = template
    for key, value in context.items():
        result = result.replace(f"{{{key}}}", str(value))

    return result


def main():
    """Demonstrate schema usage."""
    schema = load_schema()
    print(f"Loaded schema: {schema['name']}")
    print(f"Components: {len(schema['components'])}")
    print()

    # Demo: Find and invoke the create-item component
    create_component = find_component(schema, "create-item")
    if create_component:
        print(f"Found component: {create_component['component_id']}")
        print(f"  Intent: {create_component['intent']}")
        print(f"  Type: {create_component['component_type']}")

        # Simulate matching
        test_input = "create an item called test"
        if match_invocation(create_component, test_input):
            print(f"  Matched input: '{test_input}'")

            # Generate success feedback
            feedback = generate_feedback(
                create_component,
                success=True,
                context={"title": "test"}
            )
            print(f"  Feedback: {feedback}")


if __name__ == "__main__":
    main()
```

**Step 2: Commit**

```bash
git add src/templates/crud/integration.py
git commit -m "feat(templates): Add CRUD template integration code"
```

---

## Task 10: Create CRUD Template - Tests

**Files:**
- Create: `src/templates/crud/test_integration.py`

**Step 1: Create test file**

```python
"""Tests for {{PROJECT_NAME_TITLE}} integration.

These tests demonstrate expected behavior and serve as documentation.
Generated from the CRUD template on {{CREATED_DATE}}.
"""

import pytest
from integration import (
    load_schema,
    find_component,
    match_invocation,
    generate_feedback,
)


class TestSchemaLoading:
    """Test schema loading functionality."""

    def test_loads_schema(self):
        """Test that schema loads successfully."""
        schema = load_schema()
        assert schema is not None
        assert "schema_id" in schema
        assert "components" in schema

    def test_schema_has_components(self):
        """Test that schema has expected components."""
        schema = load_schema()
        assert len(schema["components"]) >= 5


class TestComponentFinding:
    """Test component finding functionality."""

    def test_finds_existing_component(self):
        """Test finding a component that exists."""
        schema = load_schema()
        component = find_component(schema, "create-item")
        assert component is not None
        assert component["component_type"] == "ACTION"

    def test_returns_none_for_missing(self):
        """Test that missing components return None."""
        schema = load_schema()
        component = find_component(schema, "nonexistent")
        assert component is None


class TestInvocationMatching:
    """Test invocation pattern matching."""

    def test_matches_primary_phrase(self):
        """Test matching on primary phrase."""
        schema = load_schema()
        component = find_component(schema, "create-item")
        assert match_invocation(component, "create item please")

    def test_matches_alternate_phrase(self):
        """Test matching on alternate phrases."""
        schema = load_schema()
        component = find_component(schema, "create-item")
        assert match_invocation(component, "add item now")

    def test_no_match_on_unrelated_input(self):
        """Test that unrelated input doesn't match."""
        schema = load_schema()
        component = find_component(schema, "create-item")
        assert not match_invocation(component, "delete everything")


class TestFeedbackGeneration:
    """Test feedback message generation."""

    def test_generates_success_feedback(self):
        """Test success feedback with template variables."""
        schema = load_schema()
        component = find_component(schema, "create-item")

        feedback = generate_feedback(
            component,
            success=True,
            context={"title": "My Item"}
        )

        assert "My Item" in feedback
        assert "successfully" in feedback.lower()

    def test_generates_error_feedback(self):
        """Test error feedback generation."""
        schema = load_schema()
        component = find_component(schema, "create-item")

        feedback = generate_feedback(
            component,
            success=False,
            context={"error": "Invalid input"}
        )

        assert "Invalid input" in feedback


class TestDeleteConfirmation:
    """Test destructive action confirmation pattern."""

    def test_delete_requires_confirmation(self):
        """Test that delete component requires confirmation."""
        schema = load_schema()
        component = find_component(schema, "delete-item")

        assert component["feedback"]["confirmation_required"] is True
        assert "confirmation_prompt" in component["feedback"]
```

**Step 2: Commit**

```bash
git add src/templates/crud/test_integration.py
git commit -m "feat(templates): Add CRUD template tests"
```

---

## Task 11: Implement Init Command

**Files:**
- Create: `src/cli/init_command.py`
- Create: `tests/test_cli_init.py`

**Step 1: Write failing test for CLI parsing**

```python
# tests/test_cli_init.py
"""Tests for init command."""

import pytest
from unittest.mock import patch, MagicMock
from src.cli.init_command import parse_args, InitArgs


class TestParseArgs:
    """Test argument parsing."""

    def test_parses_template_flag(self):
        """Test parsing --template flag."""
        args = parse_args(["--template", "crud", "--name", "test"])
        assert args.template == "crud"

    def test_parses_short_template_flag(self):
        """Test parsing -t flag."""
        args = parse_args(["-t", "crud", "-n", "test"])
        assert args.template == "crud"

    def test_parses_name_flag(self):
        """Test parsing --name flag."""
        args = parse_args(["--template", "crud", "--name", "my-app"])
        assert args.name == "my-app"

    def test_parses_output_flag(self):
        """Test parsing --output flag."""
        args = parse_args(["-t", "crud", "-n", "test", "-o", "/tmp/out"])
        assert args.output == "/tmp/out"

    def test_list_flag(self):
        """Test parsing --list flag."""
        args = parse_args(["--list"])
        assert args.list_templates is True

    def test_force_flag(self):
        """Test parsing --force flag."""
        args = parse_args(["-t", "crud", "-n", "test", "--force"])
        assert args.force is True
```

**Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_cli_init.py -v`
Expected: FAIL with import error

**Step 3: Write minimal implementation**

```python
# src/cli/init_command.py
"""Init command for scaffolding LUI templates."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from src.templates import AVAILABLE_TEMPLATES, get_template_dir
from src.cli.scaffolder import scaffold_template

console = Console()


@dataclass
class InitArgs:
    """Parsed arguments for init command."""
    template: Optional[str] = None
    name: Optional[str] = None
    output: Optional[str] = None
    force: bool = False
    list_templates: bool = False


def parse_args(args: list[str] = None) -> InitArgs:
    """Parse command line arguments.

    Args:
        args: List of arguments (defaults to sys.argv[1:])

    Returns:
        Parsed InitArgs
    """
    parser = argparse.ArgumentParser(
        description="Scaffold a LUI template project",
        prog="baml-agentic-ux init",
    )

    parser.add_argument(
        "-t", "--template",
        help="Template name (crud, search, workflow, support)",
    )
    parser.add_argument(
        "-n", "--name",
        help="Project name",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (defaults to ./<name>)",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing directory",
    )
    parser.add_argument(
        "--list",
        dest="list_templates",
        action="store_true",
        help="List available templates",
    )

    parsed = parser.parse_args(args)

    return InitArgs(
        template=parsed.template,
        name=parsed.name,
        output=parsed.output,
        force=parsed.force,
        list_templates=parsed.list_templates,
    )


def list_templates() -> None:
    """Display available templates."""
    table = Table(title="Available Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")

    for name, desc in AVAILABLE_TEMPLATES.items():
        table.add_row(name, desc)

    console.print(table)


def run_interactive() -> InitArgs:
    """Run interactive mode to gather arguments.

    Returns:
        InitArgs populated from user input
    """
    import questionary

    console.print("\n[bold]Welcome to BAML Agentic UX![/bold] Let's scaffold a LUI project.\n")

    # Select template
    template_choices = [
        questionary.Choice(f"{name} - {desc}", value=name)
        for name, desc in AVAILABLE_TEMPLATES.items()
    ]

    template = questionary.select(
        "Select a template:",
        choices=template_choices,
    ).ask()

    if not template:
        sys.exit(1)

    # Get project name
    name = questionary.text(
        "Project name:",
        validate=lambda x: len(x) > 0 or "Name is required",
    ).ask()

    if not name:
        sys.exit(1)

    # Get output directory
    default_output = f"./{name}"
    output = questionary.text(
        "Output directory:",
        default=default_output,
    ).ask()

    if not output:
        output = default_output

    return InitArgs(
        template=template,
        name=name,
        output=output,
        force=False,
        list_templates=False,
    )


def run_scaffold(args: InitArgs) -> None:
    """Run the scaffolding process.

    Args:
        args: Parsed arguments
    """
    template_dir = get_template_dir(args.template)
    output_dir = Path(args.output or f"./{args.name}")

    if output_dir.exists() and not args.force:
        console.print(f"[red]Error:[/red] Directory {output_dir} already exists.")
        console.print("Use --force to overwrite.")
        sys.exit(1)

    console.print(f"\n[bold]Creating project...[/bold]")

    created_files = scaffold_template(
        template_dir=template_dir,
        project_name=args.name,
        output_dir=output_dir,
    )

    for f in created_files:
        console.print(f"  [green]+[/green] Created {f.name}")

    console.print(f"\n[bold green]Done![/bold green] Next steps:")
    console.print(f"  cd {output_dir}")
    console.print(f"  cat README.md        # Start here to learn the patterns")
    console.print(f"  python integration.py  # Run the example")


def main(args: list[str] = None) -> None:
    """Main entry point for init command.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])
    """
    parsed = parse_args(args)

    if parsed.list_templates:
        list_templates()
        return

    # If template and name provided, run directly
    if parsed.template and parsed.name:
        run_scaffold(parsed)
        return

    # Otherwise, run interactive mode
    interactive_args = run_interactive()
    run_scaffold(interactive_args)
```

**Step 4: Run test to verify it passes**

Run: `uv run pytest tests/test_cli_init.py -v`
Expected: All 6 tests PASS

**Step 5: Commit**

```bash
git add src/cli/init_command.py tests/test_cli_init.py
git commit -m "feat(cli): Implement init command with argument parsing"
```

---

## Task 12: Create Remaining Templates (Search, Workflow, Support)

**Files:**
- Create: `src/templates/search/schema.json`
- Create: `src/templates/search/README.md`
- Create: `src/templates/search/integration.py`
- Create: `src/templates/search/test_integration.py`
- Create: `src/templates/workflow/` (same structure)
- Create: `src/templates/support/` (same structure)

**Note:** This task creates simplified versions of the remaining templates. The full content follows the same patterns as the CRUD template. For brevity, create minimal working versions that demonstrate the key patterns for each template type.

**Step 1: Create Search template files**

Follow the CRUD template structure but focus on:
- Search components with filter parameters
- Pagination patterns
- Faceted search concepts

**Step 2: Create Workflow template files**

Focus on:
- Multi-step flow components
- State transitions
- Branching logic

**Step 3: Create Support template files**

Focus on:
- FAQ matching
- Ticket lifecycle
- Escalation patterns

**Step 4: Commit each template**

```bash
git add src/templates/search/
git commit -m "feat(templates): Add search template"

git add src/templates/workflow/
git commit -m "feat(templates): Add workflow template"

git add src/templates/support/
git commit -m "feat(templates): Add support template"
```

---

## Task 13: Integration Testing

**Files:**
- Create: `tests/test_cli_integration.py`

**Step 1: Write integration test**

```python
# tests/test_cli_integration.py
"""Integration tests for CLI."""

import subprocess
import tempfile
from pathlib import Path

import pytest


class TestCLIIntegration:
    """End-to-end CLI tests."""

    def test_list_templates(self):
        """Test --list flag shows templates."""
        result = subprocess.run(
            ["uv", "run", "python", "-m", "src.cli", "init", "--list"],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert "crud" in result.stdout
        assert "search" in result.stdout

    def test_scaffold_crud_template(self, tmp_path):
        """Test scaffolding CRUD template."""
        output_dir = tmp_path / "test-project"

        result = subprocess.run(
            [
                "uv", "run", "python", "-m", "src.cli", "init",
                "-t", "crud",
                "-n", "test-project",
                "-o", str(output_dir),
            ],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0
        assert (output_dir / "schema.json").exists()
        assert (output_dir / "README.md").exists()
        assert (output_dir / "integration.py").exists()
        assert (output_dir / "test_integration.py").exists()

    def test_scaffold_customizes_content(self, tmp_path):
        """Test that scaffolded content is customized."""
        output_dir = tmp_path / "my-app"

        subprocess.run(
            [
                "uv", "run", "python", "-m", "src.cli", "init",
                "-t", "crud",
                "-n", "my-cool-app",
                "-o", str(output_dir),
            ],
            capture_output=True,
        )

        schema_content = (output_dir / "schema.json").read_text()
        assert "my-cool-app-v1" in schema_content

        readme_content = (output_dir / "README.md").read_text()
        assert "My Cool App" in readme_content
```

**Step 2: Run integration tests**

Run: `uv run pytest tests/test_cli_integration.py -v`
Expected: All tests PASS

**Step 3: Commit**

```bash
git add tests/test_cli_integration.py
git commit -m "test(cli): Add CLI integration tests"
```

---

## Task 14: Final Verification and Documentation

**Files:**
- Modify: `README.md` (project root)

**Step 1: Run full test suite**

Run: `uv run pytest --tb=short -q`
Expected: All tests pass

**Step 2: Test CLI manually**

```bash
# List templates
uv run python -m src.cli init --list

# Scaffold in temp directory
cd /tmp
uv run python -m src.cli init -t crud -n demo-app
cd demo-app
cat README.md
python integration.py
pytest test_integration.py -v
```

**Step 3: Update project README**

Add CLI usage section to the project README.md.

**Step 4: Final commit**

```bash
git add README.md
git commit -m "docs: Add CLI usage to README"
```

---

## Task 15: Close Issue and Sync

**Step 1: Close the beads issue**

```bash
bd close baml-agentic-ux-aqk --reason="Implemented LUI Starter Templates CLI"
```

**Step 2: Sync beads**

```bash
bd sync
```

**Step 3: Push feature branch**

```bash
git push -u origin feature/lui-starter-templates
```

---

## Summary

This plan implements the LUI Starter Templates feature in 15 tasks:

1. Tasks 1-2: CLI module structure and dependencies
2. Tasks 3-5: Scaffolder core implementation (TDD)
3. Tasks 6-10: CRUD template creation
4. Task 11: Init command implementation
5. Task 12: Remaining templates (search, workflow, support)
6. Tasks 13-14: Integration testing and documentation
7. Task 15: Issue closure and push

**Total estimated steps:** ~75 bite-sized actions
**Key patterns:** TDD, frequent commits, educational templates
