// LUI Generator - Requirements to LUI Schema Conversion
// Generates Language User Interface schemas from natural language requirements

// ============================================
// Input Types for Generation
// ============================================

/// Context about the domain for generation
class DomainContext {
  domain_name string @description("Primary domain (e.g., 'e-commerce', 'healthcare')")
  key_concepts string[] @description("Important concepts in this domain")
  existing_terminology TerminologyEntry[]? @description("Domain-specific terms to use")
  target_users string[]? @description("Who will use this interface")
  constraints string[]? @description("Technical or business constraints")
}

class TerminologyEntry {
  term string
  meaning string
  preferred bool @description("Whether this is the preferred term")
}

/// Style preferences for generated content
class StylePreferences {
  tone Tone @description("Overall tone of the interface")
  verbosity Verbosity @description("How detailed responses should be")
  formality Formality @description("Level of formality in language")
  language_code string? @description("Target language (e.g., 'en-US', 'es-ES')")
  brand_voice string? @description("Description of brand voice to match")
}

enum Tone {
  PROFESSIONAL @description("Business-appropriate, neutral")
  FRIENDLY @description("Warm, approachable, conversational")
  TECHNICAL @description("Precise, detailed, expert-level")
  CASUAL @description("Relaxed, informal, everyday language")
  EMPATHETIC @description("Understanding, supportive, patient")
}

enum Verbosity {
  CONCISE @description("Minimal words, direct responses")
  STANDARD @description("Balanced detail and brevity")
  DETAILED @description("Comprehensive explanations")
  ADAPTIVE @description("Adjusts based on context")
}

enum Formality {
  FORMAL @description("Professional, polished language")
  NEUTRAL @description("Neither formal nor informal")
  INFORMAL @description("Casual, friendly language")
  MIXED @description("Adapts to user's style")
}

// ============================================
// Generation Options
// ============================================

/// Options for controlling generation behavior
class GenerationOptions {
  include_examples bool @description("Generate example invocations")
  include_error_handling bool @description("Generate error templates")
  include_accessibility bool @description("Generate accessibility configs")
  max_components int? @description("Limit number of components")
  max_flows int? @description("Limit number of flows")
  component_types LUIComponentType[]? @description("Only generate these types")
}

// ============================================
// Main Generator Function
// ============================================

/// Generate a complete LUI schema from natural language requirements
function GenerateLUIFromRequirements(
  requirements: string,
  domain_context: DomainContext?,
  style_preferences: StylePreferences?,
  options: GenerationOptions?
) -> InterfaceSchema {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert in designing Language User Interfaces (LUI) - interfaces
    optimized for AI agent interaction rather than traditional GUIs.

    Your task is to generate a complete, machine-readable interface schema that
    enables AI agents to understand and interact with an application.

    ## Requirements
    {{ requirements }}

    {% if domain_context %}
    ## Domain Context
    - Domain: {{ domain_context.domain_name }}
    - Key Concepts: {{ domain_context.key_concepts }}
    {% if domain_context.existing_terminology %}
    - Terminology: {{ domain_context.existing_terminology }}
    {% endif %}
    {% if domain_context.target_users %}
    - Target Users: {{ domain_context.target_users }}
    {% endif %}
    {% if domain_context.constraints %}
    - Constraints: {{ domain_context.constraints }}
    {% endif %}
    {% endif %}

    {% if style_preferences %}
    ## Style Preferences
    - Tone: {{ style_preferences.tone }}
    - Verbosity: {{ style_preferences.verbosity }}
    - Formality: {{ style_preferences.formality }}
    {% if style_preferences.brand_voice %}
    - Brand Voice: {{ style_preferences.brand_voice }}
    {% endif %}
    {% endif %}

    {% if options %}
    ## Generation Options
    {% if options.include_examples %}Include example invocations for each component.{% endif %}
    {% if options.include_error_handling %}Include comprehensive error templates.{% endif %}
    {% if options.include_accessibility %}Include accessibility configurations.{% endif %}
    {% if options.max_components %}Maximum {{ options.max_components }} components.{% endif %}
    {% if options.max_flows %}Maximum {{ options.max_flows }} flows.{% endif %}
    {% endif %}

    ## Design Principles
    1. **Agent-First**: Design for AI consumption - clear, unambiguous, machine-readable
    2. **Natural Invocation**: Use phrases humans naturally say
    3. **Complete Coverage**: Address all requirements
    4. **Consistent Style**: Apply style preferences throughout
    5. **Error Recovery**: Include graceful error handling

    ## Output Requirements
    Generate a complete InterfaceSchema with:
    - Unique schema_id and appropriate version
    - Domain information with key concepts
    - LUI components for each identified action/query/input need
    - Conversational flows for multi-step interactions
    - Entity definitions for domain objects
    - Appropriate global context settings

    {{ ctx.output_format }}
  "#
}

// ============================================
// Refinement Function
// ============================================

/// Refine an existing LUI schema based on feedback
function RefineLUISchema(
  schema: InterfaceSchema,
  feedback: string,
  focus_areas: RefinementFocus[]?
) -> RefinementResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    You are an expert at refining Language User Interface schemas.

    ## Current Schema
    {{ schema }}

    ## Feedback
    {{ feedback }}

    {% if focus_areas %}
    ## Focus Areas
    Prioritize improvements in: {{ focus_areas }}
    {% endif %}

    ## Task
    Analyze the feedback and improve the schema. For each change:
    1. Explain why the change addresses the feedback
    2. Consider impact on other parts of the schema
    3. Maintain consistency with existing patterns

    Return both the refined schema and a summary of changes made.

    {{ ctx.output_format }}
  "#
}

/// Areas to focus refinement on
enum RefinementFocus {
  INVOCATION_PATTERNS @description("Improve how components are triggered")
  ERROR_HANDLING @description("Improve error messages and recovery")
  FLOW_LOGIC @description("Improve conversational flow structure")
  ENTITY_COVERAGE @description("Improve entity definitions")
  ACCESSIBILITY @description("Improve accessibility features")
  PERFORMANCE @description("Optimize for faster agent processing")
  CONSISTENCY @description("Improve naming and pattern consistency")
}

class RefinementResult {
  refined_schema InterfaceSchema
  changes_made SchemaChange[]
  feedback_addressed string[] @description("Which feedback points were addressed")
  suggestions string[] @description("Additional improvement suggestions")
}

class SchemaChange {
  change_type ChangeType
  location string @description("Path to changed element")
  description string
  before string?
  after string?
  rationale string
}

enum ChangeType {
  ADDED
  MODIFIED
  REMOVED
  RESTRUCTURED
}

// ============================================
// Analysis Functions
// ============================================

/// Analyze requirements to identify LUI components needed
function AnalyzeRequirements(requirements: string) -> RequirementsAnalysis {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Analyze these requirements to identify what LUI components are needed:

    {{ requirements }}

    Identify:
    1. Actions users need to perform
    2. Information users need to query
    3. Data users need to input
    4. Confirmations required
    5. Navigation patterns
    6. Domain entities

    For each identified need, suggest:
    - Component type (ACTION, QUERY, INPUT, etc.)
    - Possible invocation phrases
    - Required parameters
    - Related components

    {{ ctx.output_format }}
  "#
}

class RequirementsAnalysis {
  identified_needs IdentifiedNeed[]
  suggested_flows FlowSuggestion[]
  domain_entities string[]
  complexity_assessment ComplexityLevel
  estimated_components int
  notes string[]
}

class IdentifiedNeed {
  need_id string
  description string
  component_type LUIComponentType
  suggested_phrases string[]
  parameters string[]
  related_needs string[] @description("IDs of related needs")
  priority Priority
}

enum Priority {
  CRITICAL @description("Must have for MVP")
  HIGH @description("Important feature")
  MEDIUM @description("Nice to have")
  LOW @description("Future consideration")
}

class FlowSuggestion {
  flow_name string
  description string
  trigger_phrases string[]
  involves_needs string[] @description("IDs of needs involved")
  estimated_steps int
}

enum ComplexityLevel {
  SIMPLE @description("Few components, linear flows")
  MODERATE @description("Multiple components, some branching")
  COMPLEX @description("Many components, complex flows")
  ENTERPRISE @description("Large scale, many integrations")
}

// ============================================
// Comparison Function
// ============================================

/// Compare LUI schema with traditional UI to highlight differences
function CompareLUIWithTraditionalUI(
  lui_schema: InterfaceSchema,
  ui_description: string
) -> ComparisonResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Compare this LUI schema with the traditional UI description:

    ## LUI Schema
    {{ lui_schema }}

    ## Traditional UI Description
    {{ ui_description }}

    Analyze:
    1. What can the LUI do that the traditional UI cannot?
    2. What does the traditional UI offer that the LUI doesn't?
    3. How do interaction patterns differ?
    4. What are the accessibility implications?
    5. Where would each approach be preferred?

    {{ ctx.output_format }}
  "#
}

class ComparisonResult {
  lui_advantages string[]
  traditional_advantages string[]
  interaction_differences InteractionDifference[]
  accessibility_comparison AccessibilityComparison
  recommendations string[]
  hybrid_suggestions string[] @description("Ways to combine both approaches")
}

class InteractionDifference {
  aspect string
  lui_approach string
  traditional_approach string
  winner string @description("'lui', 'traditional', or 'tie'")
  reasoning string
}

class AccessibilityComparison {
  lui_accessibility_score float @description("0-1 score")
  traditional_accessibility_score float
  lui_strengths string[]
  traditional_strengths string[]
  improvement_opportunities string[]
}

// ============================================
// Test Cases
// ============================================

test generate_task_manager_lui {
  functions [GenerateLUIFromRequirements]
  args {
    requirements #"
      Build a task management interface where users can:
      - Create tasks with title, description, and due date
      - Assign tasks to team members
      - Set priority levels (low, medium, high, critical)
      - Mark tasks as complete
      - Search and filter tasks
      - Get task status updates
    "#
    domain_context {
      domain_name "project-management"
      key_concepts ["tasks", "projects", "team members", "deadlines", "priorities"]
      existing_terminology null
      target_users ["project managers", "developers", "team leads"]
      constraints null
    }
    style_preferences {
      tone PROFESSIONAL
      verbosity STANDARD
      formality NEUTRAL
      language_code "en-US"
      brand_voice null
    }
    options {
      include_examples true
      include_error_handling true
      include_accessibility true
      max_components null
      max_flows null
      component_types null
    }
  }
}

test generate_customer_support_lui {
  functions [GenerateLUIFromRequirements]
  args {
    requirements #"
      Create a customer support interface that:
      - Allows customers to describe their issue
      - Searches knowledge base for solutions
      - Creates support tickets when needed
      - Tracks ticket status
      - Escalates to human agents
      - Collects customer feedback
    "#
    domain_context {
      domain_name "customer-support"
      key_concepts ["tickets", "issues", "resolution", "escalation", "satisfaction"]
      existing_terminology null
      target_users ["customers", "support agents"]
      constraints ["24/7 availability", "multi-language support"]
    }
    style_preferences {
      tone EMPATHETIC
      verbosity ADAPTIVE
      formality NEUTRAL
      language_code null
      brand_voice "Helpful, patient, solution-focused"
    }
    options null
  }
}

test analyze_ecommerce_requirements {
  functions [AnalyzeRequirements]
  args {
    requirements #"
      E-commerce platform needs:
      - Product browsing and search
      - Shopping cart management
      - Checkout process
      - Order tracking
      - Returns and refunds
      - Product reviews
      - Wishlist functionality
    "#
  }
}
