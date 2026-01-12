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
