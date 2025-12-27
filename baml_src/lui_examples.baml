// Example LUI Components and Test Cases
// Demonstrates how to define real-world LUI components

/// Function to generate LUI components from a description
function GenerateLUIComponent(description: string, domain: string) -> LUIComponent {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert at designing Language User Interface (LUI) components.

    Given a description of a user interface need, generate a complete LUI component
    that an AI agent could use to understand and invoke the functionality.

    Domain: {{ domain }}
    Description: {{ description }}

    Generate a LUIComponent with:
    - Clear intent description
    - Natural invocation patterns with examples
    - Well-typed parameters with extraction hints
    - Conversational feedback templates

    {{ ctx.output_format }}
  "#
}

/// Function to validate if a user utterance matches a component
function MatchUtterance(utterance: string, component: LUIComponent) -> UtteranceMatch {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyze if the user utterance matches the given LUI component.

    User said: "{{ utterance }}"

    Component:
    - Intent: {{ component.intent }}
    - Primary phrase: {{ component.invocation.primary_phrase }}
    - Alternate phrases: {{ component.invocation.alternate_phrases }}
    - Examples: {{ component.invocation.examples }}

    Determine:
    1. Does this utterance match the component's intent?
    2. What parameters can be extracted?
    3. What clarifications might be needed?

    {{ ctx.output_format }}
  "#
}

class UtteranceMatch {
  matches bool @description("Whether the utterance matches the component")
  confidence float @description("Confidence score 0-1")
  extracted_parameters ExtractedParameter[]
  missing_required_parameters string[]
  clarification_needed string? @description("Question to ask if clarification needed")
}

class ExtractedParameter {
  parameter_name string @description("Name of the parameter")
  extracted_value string @description("The value extracted from input")
  source_text string? @description("Original text this was extracted from")
  confidence float @description("Confidence in extraction (0-1)")
}

// ============================================
// Test Cases with Sample Components
// ============================================

test send_message_component {
  functions [GenerateLUIComponent]
  args {
    description "A component that allows users to send messages to other users"
    domain "messaging"
  }
}

test search_documents_component {
  functions [GenerateLUIComponent]
  args {
    description "A component for searching through a document library with filters for date, author, and type"
    domain "document-management"
  }
}

test create_task_component {
  functions [GenerateLUIComponent]
  args {
    description "A component for creating new tasks with title, description, due date, and assignee"
    domain "project-management"
  }
}
