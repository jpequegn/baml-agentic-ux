"""Tests for {{PROJECT_NAME_TITLE}} integration.

These tests demonstrate expected workflow behavior and serve as documentation.
Generated from the Workflow template on {{CREATED_DATE}}.
"""

import pytest
from integration import (
    load_schema,
    find_component,
    match_invocation,
    generate_feedback,
    get_next_steps,
    get_conditional_path,
    WorkflowState,
)


class TestSchemaLoading:
    """Test schema loading functionality."""

    def test_loads_schema(self):
        """Test that schema loads successfully."""
        schema = load_schema()
        assert schema is not None
        assert "schema_id" in schema
        assert "components" in schema

    def test_schema_has_workflow_components(self):
        """Test that schema has expected workflow components."""
        schema = load_schema()
        assert len(schema["components"]) >= 5

        component_ids = [c["component_id"] for c in schema["components"]]
        assert "start-process" in component_ids
        assert "collect-info" in component_ids
        assert "confirm-action" in component_ids
        assert "branch-decision" in component_ids
        assert "complete-process" in component_ids

    def test_schema_has_workflow_domain(self):
        """Test that schema defines workflow domain."""
        schema = load_schema()
        assert schema["domain"]["subdomain"] == "workflow-patterns"
        assert "state" in schema["domain"]["key_concepts"]


class TestComponentFinding:
    """Test component finding functionality."""

    def test_finds_workflow_component(self):
        """Test finding workflow-specific components."""
        schema = load_schema()
        component = find_component(schema, "start-process")
        assert component is not None
        assert component["component_type"] == "ACTION"

    def test_finds_complete_component(self):
        """Test finding completion component."""
        schema = load_schema()
        component = find_component(schema, "complete-process")
        assert component is not None
        assert component["component_type"] == "FEEDBACK"

    def test_returns_none_for_missing(self):
        """Test that missing components return None."""
        schema = load_schema()
        component = find_component(schema, "nonexistent")
        assert component is None


class TestInvocationMatching:
    """Test invocation pattern matching."""

    def test_matches_start_process(self):
        """Test matching start process invocations."""
        schema = load_schema()
        component = find_component(schema, "start-process")
        assert match_invocation(component, "start process now")
        assert match_invocation(component, "begin workflow please")

    def test_matches_collect_info(self):
        """Test matching info collection invocations."""
        schema = load_schema()
        component = find_component(schema, "collect-info")
        assert match_invocation(component, "provide information")
        assert match_invocation(component, "enter details")

    def test_matches_confirmation(self):
        """Test matching confirmation invocations."""
        schema = load_schema()
        component = find_component(schema, "confirm-action")
        assert match_invocation(component, "confirm everything")
        assert match_invocation(component, "yes proceed")

    def test_no_match_on_unrelated_input(self):
        """Test that unrelated input doesn't match."""
        schema = load_schema()
        component = find_component(schema, "start-process")
        assert not match_invocation(component, "delete everything")


class TestWorkflowState:
    """Test workflow state management."""

    def test_initial_state_is_idle(self):
        """Test that new workflows start in idle state."""
        state = WorkflowState()
        assert state.status == "idle"
        assert state.current_step is None
        assert len(state.collected_data) == 0

    def test_start_workflow(self):
        """Test starting a workflow."""
        state = WorkflowState()
        state.start("checkout")
        assert state.status == "in_progress"
        assert state.current_step == 1
        assert state.collected_data["process_type"] == "checkout"
        assert "Started checkout" in state.history

    def test_add_data_to_workflow(self):
        """Test adding data during workflow."""
        state = WorkflowState()
        state.start("onboarding")
        state.add_data("email", "user@example.com")
        state.add_data("name", "Test User")

        assert state.collected_data["email"] == "user@example.com"
        assert state.collected_data["name"] == "Test User"
        assert len(state.collected_data) == 3  # process_type + email + name

    def test_select_branch(self):
        """Test branch selection."""
        state = WorkflowState()
        state.start("checkout")
        state.select_branch("express")

        assert state.selected_path == "express"
        assert "Selected path: express" in state.history

    def test_confirm_workflow(self):
        """Test confirming workflow."""
        state = WorkflowState()
        state.start("checkout")
        state.confirm()

        assert state.status == "confirmed"
        assert "Confirmed" in state.history

    def test_complete_workflow(self):
        """Test completing workflow."""
        state = WorkflowState()
        state.start("checkout")
        state.complete()

        assert state.status == "completed"
        assert state.current_step is None
        assert "Completed" in state.history


class TestStateTransitions:
    """Test workflow state transition validation."""

    def test_can_start_from_idle(self):
        """Test that workflows can start from idle state."""
        schema = load_schema()
        state = WorkflowState()
        component = find_component(schema, "start-process")

        assert state.can_transition_to("start-process", component)

    def test_can_collect_info_when_in_progress(self):
        """Test that info collection works during workflow."""
        schema = load_schema()
        state = WorkflowState()
        state.start("checkout")
        component = find_component(schema, "collect-info")

        assert state.can_transition_to("collect-info", component)

    def test_can_complete_after_confirm(self):
        """Test that completion works after confirmation."""
        schema = load_schema()
        state = WorkflowState()
        state.start("checkout")
        state.confirm()
        component = find_component(schema, "complete-process")

        assert state.can_transition_to("complete-process", component)

    def test_cannot_complete_without_confirm(self):
        """Test that completion requires confirmation."""
        schema = load_schema()
        state = WorkflowState()
        state.start("checkout")
        # Skip confirmation
        component = find_component(schema, "complete-process")

        assert not state.can_transition_to("complete-process", component)


class TestBranchingLogic:
    """Test conditional workflow branching."""

    def test_get_next_steps(self):
        """Test getting valid next steps from metadata."""
        schema = load_schema()
        component = find_component(schema, "start-process")
        next_steps = get_next_steps(component)

        assert "collect-info" in next_steps
        assert len(next_steps) >= 1

    def test_get_conditional_path(self):
        """Test getting conditional paths from branch decisions."""
        schema = load_schema()
        component = find_component(schema, "branch-decision")

        express_path = get_conditional_path(component, "express")
        standard_path = get_conditional_path(component, "standard")

        # Express should have more steps than standard
        assert len(express_path) > 0
        assert len(standard_path) > 0
        assert express_path != standard_path

    def test_conditional_path_includes_confirm(self):
        """Test that all paths lead to confirmation."""
        schema = load_schema()
        component = find_component(schema, "branch-decision")

        express_path = get_conditional_path(component, "express")
        premium_path = get_conditional_path(component, "premium")

        assert "confirm-action" in express_path
        assert "confirm-action" in premium_path


class TestFeedbackGeneration:
    """Test feedback message generation."""

    def test_generates_start_feedback(self):
        """Test feedback for starting workflow."""
        schema = load_schema()
        component = find_component(schema, "start-process")

        feedback = generate_feedback(
            component,
            success=True,
            context={"process_type": "checkout"}
        )

        assert "checkout" in feedback.lower()
        assert "workflow" in feedback.lower()

    def test_generates_collect_feedback(self):
        """Test feedback for data collection."""
        schema = load_schema()
        component = find_component(schema, "collect-info")

        feedback = generate_feedback(
            component,
            success=True,
            context={"field_name": "email"}
        )

        assert "email" in feedback.lower()

    def test_generates_error_feedback(self):
        """Test error feedback generation."""
        schema = load_schema()
        component = find_component(schema, "collect-info")

        feedback = generate_feedback(
            component,
            success=False,
            context={"field_name": "email", "error": "Invalid format"}
        )

        assert "Invalid format" in feedback

    def test_generates_completion_feedback(self):
        """Test completion feedback with summary."""
        schema = load_schema()
        component = find_component(schema, "complete-process")

        feedback = generate_feedback(
            component,
            success=True,
            context={"summary": "3 fields collected"}
        )

        assert "3 fields collected" in feedback
        assert "completed" in feedback.lower()


class TestConfirmationPattern:
    """Test confirmation requirements."""

    def test_confirm_requires_confirmation(self):
        """Test that confirm component has confirmation enabled."""
        schema = load_schema()
        component = find_component(schema, "confirm-action")

        assert component["feedback"]["confirmation_required"] is True
        assert "confirmation_prompt" in component["feedback"]

    def test_confirmation_prompt_exists(self):
        """Test that confirmation prompt is defined."""
        schema = load_schema()
        component = find_component(schema, "confirm-action")

        prompt = component["feedback"]["confirmation_prompt"]
        assert len(prompt) > 0
        assert "?" in prompt


class TestMetadata:
    """Test workflow metadata and state tracking."""

    def test_start_has_state_changes(self):
        """Test that start component defines state changes."""
        schema = load_schema()
        component = find_component(schema, "start-process")

        assert "metadata" in component
        assert "state_changes" in component["metadata"]
        state_changes = component["metadata"]["state_changes"]
        assert "workflow_status" in state_changes

    def test_complete_is_final_step(self):
        """Test that complete component is marked as final."""
        schema = load_schema()
        component = find_component(schema, "complete-process")

        metadata = component.get("metadata", {})
        assert metadata.get("final_step") is True

    def test_collect_has_validation_flag(self):
        """Test that collect component has validation metadata."""
        schema = load_schema()
        component = find_component(schema, "collect-info")

        metadata = component.get("metadata", {})
        assert metadata.get("validation_required") is True
        assert metadata.get("can_retry") is True
