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
