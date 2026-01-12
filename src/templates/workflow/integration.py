"""{{PROJECT_NAME_TITLE}} - Integration Example.

This module demonstrates how to use a workflow LUI schema with state management.
Generated from the Workflow template on {{CREATED_DATE}}.
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Any


class WorkflowState:
    """Manages state for multi-step workflows."""

    def __init__(self):
        """Initialize workflow state."""
        self.status = "idle"
        self.current_step = None
        self.collected_data = {}
        self.selected_path = None
        self.history = []

    def start(self, process_type: str):
        """Start a new workflow."""
        self.status = "in_progress"
        self.current_step = 1
        self.collected_data = {"process_type": process_type}
        self.history.append(f"Started {process_type}")

    def add_data(self, field_name: str, field_value: str):
        """Add collected data to workflow state."""
        self.collected_data[field_name] = field_value
        self.history.append(f"Collected {field_name}")

    def select_branch(self, choice: str):
        """Record a branching decision."""
        self.selected_path = choice
        self.history.append(f"Selected path: {choice}")

    def confirm(self):
        """Mark workflow as confirmed."""
        self.status = "confirmed"
        self.history.append("Confirmed")

    def complete(self):
        """Complete the workflow."""
        self.status = "completed"
        self.current_step = None
        self.history.append("Completed")

    def can_transition_to(self, component_id: str, component: dict) -> bool:
        """Check if transition to a component is valid.

        Args:
            component_id: The ID of the component to transition to
            component: The component dictionary

        Returns:
            True if transition is allowed
        """
        # Start is only allowed from idle state
        if self.status == "idle" and component_id == "start-process":
            return True

        # Complete is only allowed from confirmed state
        if component_id == "complete-process":
            return self.status == "confirmed"

        # Other actions are allowed during in_progress
        if self.status == "in_progress":
            metadata = component.get("metadata", {})
            requires_complete = metadata.get("requires_complete_state", False)

            if requires_complete:
                # Check if we have required data
                required_fields = metadata.get("required_fields", [])
                return all(field in self.collected_data for field in required_fields)

            return True

        return False


def load_schema() -> dict:
    """Load the LUI schema from schema.json.

    Returns:
        The parsed schema dictionary
    """
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


def find_component(schema: dict, component_id: str) -> Optional[dict]:
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


def get_next_steps(component: dict) -> List[str]:
    """Get valid next steps from a component's metadata.

    Args:
        component: The component to check

    Returns:
        List of valid next component IDs
    """
    metadata = component.get("metadata", {})
    return metadata.get("next_steps", [])


def get_conditional_path(component: dict, choice: str) -> List[str]:
    """Get the workflow path for a branching decision.

    Args:
        component: The branching component
        choice: The user's choice

    Returns:
        List of component IDs for the selected path
    """
    metadata = component.get("metadata", {})
    conditional_paths = metadata.get("conditional_paths", {})
    return conditional_paths.get(choice, [])


def generate_feedback(
    component: dict,
    success: bool,
    context: Optional[Dict[str, Any]] = None
) -> str:
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
    """Demonstrate workflow state management."""
    schema = load_schema()
    state = WorkflowState()

    print(f"Loaded schema: {schema['name']}")
    print(f"Components: {len(schema['components'])}")
    print()

    # Simulate a workflow execution
    print("=== Simulating Checkout Workflow ===\n")

    # Step 1: Start process
    start_component = find_component(schema, "start-process")
    if state.can_transition_to("start-process", start_component):
        state.start("checkout")
        feedback = generate_feedback(
            start_component,
            success=True,
            context={"process_type": "checkout"}
        )
        print(f"1. Start: {feedback}")
        print(f"   State: {state.status}, Step: {state.current_step}\n")

    # Step 2: Collect shipping info
    collect_component = find_component(schema, "collect-info")
    if state.can_transition_to("collect-info", collect_component):
        state.add_data("shipping_address", "123 Main St")
        feedback = generate_feedback(
            collect_component,
            success=True,
            context={"field_name": "shipping_address"}
        )
        print(f"2. Collect: {feedback}")
        print(f"   Data: {state.collected_data}\n")

    # Step 3: Collect email
    state.add_data("email", "user@example.com")
    feedback = generate_feedback(
        collect_component,
        success=True,
        context={"field_name": "email"}
    )
    print(f"3. Collect: {feedback}")
    print(f"   Data: {state.collected_data}\n")

    # Step 4: Branch decision (shipping speed)
    branch_component = find_component(schema, "branch-decision")
    if state.can_transition_to("branch-decision", branch_component):
        state.select_branch("express")
        feedback = generate_feedback(
            branch_component,
            success=True,
            context={"choice": "express"}
        )
        print(f"4. Branch: {feedback}")
        print(f"   Selected path: {state.selected_path}")

        # Get conditional path
        path = get_conditional_path(branch_component, "express")
        print(f"   Next steps: {path}\n")

    # Step 5: Confirm
    confirm_component = find_component(schema, "confirm-action")
    if state.can_transition_to("confirm-action", confirm_component):
        state.confirm()
        feedback = generate_feedback(
            confirm_component,
            success=True,
            context={}
        )
        print(f"5. Confirm: {feedback}")
        print(f"   State: {state.status}\n")

    # Step 6: Complete
    complete_component = find_component(schema, "complete-process")
    if state.can_transition_to("complete-process", complete_component):
        state.complete()
        summary = f"Collected {len(state.collected_data)} fields, selected {state.selected_path} path"
        feedback = generate_feedback(
            complete_component,
            success=True,
            context={"summary": summary}
        )
        print(f"6. Complete: {feedback}")
        print(f"   State: {state.status}")
        print(f"   History: {state.history}")


if __name__ == "__main__":
    main()
