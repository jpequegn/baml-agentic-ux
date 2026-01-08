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

    def test_rejects_empty_project_name(self):
        """Test that empty project names raise ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            build_substitutions("")

    def test_rejects_whitespace_only_project_name(self):
        """Test that whitespace-only project names raise ValueError."""
        with pytest.raises(ValueError, match="must not be empty"):
            build_substitutions("   ")
