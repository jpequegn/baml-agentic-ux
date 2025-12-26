// Schema Examples and Generator Functions
// Demonstrates interface schema usage and LLM-based generation

/// Generate a complete interface schema from a product description
function GenerateInterfaceSchema(
  product_description: string,
  target_users: string,
  key_features: string[]
) -> InterfaceSchema {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert at designing agent-friendly interface schemas.

    Create a complete InterfaceSchema for the following product:

    Product Description: {{ product_description }}
    Target Users: {{ target_users }}
    Key Features: {{ key_features }}

    Generate a schema that includes:
    1. Clear domain information with key concepts
    2. LUI components for each major feature
    3. Conversational flows for common user journeys
    4. Entity definitions for domain objects
    5. Appropriate global context settings

    Ensure the schema enables AI agents to understand and interact with
    the interface effectively.

    {{ ctx.output_format }}
  "#
}

/// Generate conversational flows for a set of user stories
function GenerateConversationalFlows(
  user_stories: string[],
  available_components: LUIComponent[]
) -> ConversationalFlow[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Create conversational flows for these user stories:
    {{ user_stories }}

    Available components to reference:
    {{ available_components }}

    For each user story, design a multi-step conversational flow that:
    - Has clear trigger intents
    - Uses available components where appropriate
    - Includes proper error handling
    - Has meaningful transitions between steps

    {{ ctx.output_format }}
  "#
}

/// Extract entity definitions from a domain description
function ExtractEntityDefinitions(
  domain_description: string,
  sample_data: string?
) -> EntityDefinition[] {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyze this domain and extract entity definitions:

    Domain: {{ domain_description }}

    {% if sample_data %}
    Sample Data: {{ sample_data }}
    {% endif %}

    Identify:
    1. All entities in the domain
    2. Their attributes with appropriate types
    3. Relationships between entities
    4. Example instances for agent understanding

    {{ ctx.output_format }}
  "#
}

/// Validate an interface schema for completeness and consistency
function ValidateInterfaceSchema(schema: InterfaceSchema) -> SchemaValidationResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Validate this interface schema for completeness and consistency:

    {{ schema }}

    Check for:
    1. All components have required fields
    2. Flow references point to existing components
    3. Entity relationships are bidirectional
    4. No orphaned elements
    5. Proper coverage of declared features

    {{ ctx.output_format }}
  "#
}

class SchemaValidationResult {
  is_valid bool
  errors SchemaError[]
  warnings SchemaWarning[]
  suggestions string[]
  coverage_score float @description("0-1 score of feature coverage")
}

class SchemaError {
  error_code string
  message string
  location string @description("Path to problematic element")
  severity string
}

class SchemaWarning {
  warning_code string
  message string
  location string
  suggestion string?
}

// ============================================
// Test Cases
// ============================================

test generate_ecommerce_schema {
  functions [GenerateInterfaceSchema]
  args {
    product_description "An e-commerce platform for selling handmade crafts"
    target_users "Craft enthusiasts, small business owners, gift shoppers"
    key_features ["Browse products", "Search by category", "Add to cart", "Checkout", "Track orders"]
  }
}

test generate_task_manager_schema {
  functions [GenerateInterfaceSchema]
  args {
    product_description "A task management app for teams"
    target_users "Project managers, team leads, developers"
    key_features ["Create tasks", "Assign to team members", "Set due dates", "Track progress", "Generate reports"]
  }
}

test extract_crm_entities {
  functions [ExtractEntityDefinitions]
  args {
    domain_description "Customer Relationship Management system for sales teams"
    sample_data #"
      Contact: John Smith, john@acme.com, Sales Manager at Acme Corp
      Deal: Enterprise License, $50,000, Negotiation stage
      Activity: Call scheduled for 2025-01-20
    "#
  }
}
