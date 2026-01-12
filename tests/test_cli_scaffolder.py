"""Tests for template scaffolder."""

import pytest
from src.cli.scaffolder import build_substitutions, apply_substitutions, scaffold_template


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

    def test_rejects_empty_project_name(self):
        """Test that empty project names raise ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            build_substitutions("")

    def test_rejects_whitespace_only_project_name(self):
        """Test that whitespace-only project names raise ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            build_substitutions("   ")


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
