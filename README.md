# BAML Agentic UX

A comprehensive framework for building type-safe Language User Interfaces (LUI) using BAML.

## Overview

This project provides a complete toolkit for designing, generating, simulating, and analyzing conversational interfaces for AI-powered applications. Built on BAML's type-safe approach to AI interactions, it demonstrates how to create robust, testable language interfaces.

## Features

- **Schema Definition** - Structured LUI component definitions with invocation patterns
- **LUI Generation** - Generate schemas from natural language requirements
- **GUI-to-LUI Conversion** - Convert traditional GUI specifications to conversational interfaces
- **Intent Extraction** - Parse user input into structured intents with disambiguation
- **Response Generation** - Generate contextual, personality-aware responses
- **Interactive Simulator** - Test LUI schemas with simulated conversations
- **Multi-Format Export** - Export to OpenAPI, MCP, TypeScript, Markdown
- **Usability Analysis** - Evaluate LUI quality with Nielsen's heuristics

## Project Structure

```
baml-agentic-ux/
├── baml_src/                    # BAML type definitions
│   ├── lui_components.baml      # Core LUI component types
│   ├── lui_context.baml         # Context management types
│   ├── conversational_flows.baml # Flow definitions
│   ├── entity_definitions.baml  # Domain entity types
│   ├── interface_schema.baml    # Main schema type
│   ├── lui_generator.baml       # Generation functions
│   ├── gui_converter.baml       # GUI conversion functions
│   ├── intent_extraction.baml   # Intent parsing
│   ├── response_generation.baml # Response generation
│   └── usability_analysis.baml  # Usability evaluation
│
├── src/
│   ├── lui_simulator/           # Interactive simulator module
│   ├── lui_schema_export/       # Multi-format exporters
│   └── context_primitives/      # Session state management
│
├── examples/
│   ├── task_manager_schema.json # Example: Task management LUI
│   └── p3_podcast_schema.json   # Example: Podcast processor LUI
│
├── case_studies/
│   └── p3_podcast_processor/    # Real-world application case study
│
├── docs/
│   ├── RESEARCH_SYNTHESIS.md    # Complete research findings
│   ├── BLOG_POST.md             # Shareable summary
│   └── testing/                 # Testing framework documentation
│       ├── user-guide.md        # Complete usage guide
│       └── api-reference.md     # API documentation
│
└── tests/                       # 3700+ test cases
    └── conversations/           # Conversational test suites
```

## Quick Start

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [BAML CLI](https://docs.boundaryml.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/jpequegn/baml-agentic-ux.git
cd baml-agentic-ux

# Install dependencies
uv sync

# Generate BAML client code
uv run baml-cli generate
```

### Run Tests

```bash
uv run pytest  # 3700+ tests
```

### Example: Load and Explore a Schema

```python
import json
from src.lui_simulator.simulator import load_schema_from_dict

# Load a schema
with open("examples/task_manager_schema.json") as f:
    schema = load_schema_from_dict(json.load(f))

print(f"Schema: {schema.name}")
print(f"Components: {len(schema.components)}")
for component in schema.components:
    print(f"  - {component.intent}: '{component.invocation.primary_phrase}'")
```

### Example: Export to OpenAPI

```python
from src.lui_schema_export.openapi import export_to_openapi

openapi_spec = export_to_openapi(schema)
print(json.dumps(openapi_spec, indent=2))
```

## Key Concepts

### 1. LUI Components

The building blocks of conversational interfaces:

```baml
class LUIComponent {
  component_id string
  component_type LUIComponentType  // ACTION, QUERY, NAVIGATION, SETTING, COMPOUND
  intent string
  invocation InvocationPattern
  parameters ComponentParameter[]
  feedback FeedbackConfig
}
```

### 2. Invocation Patterns

Multiple ways to invoke the same action:

```json
{
  "primary_phrase": "create task",
  "alternate_phrases": ["add task", "new task"],
  "examples": ["Create a task to review code"]
}
```

### 3. Intent Extraction

Parse user input into structured intents:

```baml
function ExtractIntent(
  user_input: string,
  available_components: LUIComponent[]
) -> IntentExtraction {
  // Returns detected intent, confidence, parameters, ambiguity
}
```

### 4. Usability Analysis

Evaluate LUI quality with comprehensive analysis:

```baml
function AnalyzeLUIUsability(
  schema: InterfaceSchema,
  target_users: UserPersona[]?
) -> UsabilityAnalysis {
  // Returns scores, issues, recommendations
}
```

## Design Patterns

| Pattern | Description |
|---------|-------------|
| **Invocation Triad** | Primary phrase + alternates + examples |
| **Feedback Templates** | Parameterized success/error messages |
| **Confirmation Gates** | Confirm destructive actions |
| **Entity Resolution** | Multiple ways to reference entities |
| **Composite Actions** | Single invocations for workflows |
| **Weighted Scoring** | Category-based usability assessment |

## Case Study: P3 Podcast Processor

We applied this framework to a real CLI application:

| CLI Command | LUI Equivalent |
|-------------|----------------|
| `p3 fetch --max-episodes 5` | "Fetch the latest 5 episodes" |
| `p3 transcribe --episode-id 42` | "Transcribe episode 42" |
| `p3 digest && p3 export` | "Process and export today's podcasts" |

See [case_studies/p3_podcast_processor/](case_studies/p3_podcast_processor/) for the complete analysis.

## Research Findings

Key insights from building this framework:

1. **Type Safety Matters** - BAML's structured approach catches errors early
2. **Ambiguity is Normal** - Plan for disambiguation from day one
3. **Context is Critical** - Conversational state enables natural interaction
4. **Hybrid is Best** - Neither GUI nor LUI is universally superior

See [docs/RESEARCH_SYNTHESIS.md](docs/RESEARCH_SYNTHESIS.md) for the complete research document.

## BAML Functions

| Function | Purpose |
|----------|---------|
| `GenerateLUIFromRequirements` | Create LUI from natural language |
| `ConvertGUIToLUI` | Convert GUI spec to LUI |
| `ExtractIntent` | Parse user input |
| `GenerateResponse` | Create contextual responses |
| `AnalyzeLUIUsability` | Evaluate LUI quality |
| `EvaluateHeuristics` | Nielsen's heuristics check |
| `AnalyzeForPersona` | Persona-specific analysis |

## Export Formats

| Format | Use Case |
|--------|----------|
| OpenAPI | REST API documentation |
| MCP | AI tool definitions |
| TypeScript | Frontend type safety |
| Markdown | Human-readable docs |

## Conversational Testing Framework

A comprehensive testing framework for validating LUI components, intent extraction, and dialogue quality.

### Quick Start

```bash
# Generate configuration file
convtest generate config

# Run conversation tests
convtest run tests/conversations/

# Check quality gates
convtest check-gates test-results.json
```

### Features

- **YAML-based test definitions** - Declarative test cases with assertions
- **Multi-turn conversation testing** - Validate dialogue flows
- **Quality metrics** - Coherence, naturalness, and accuracy scoring
- **CI/CD integration** - Quality gates for automated pipelines
- **Multiple output formats** - Text, JSON, JUnit, HTML, Markdown

### Example Test

```yaml
tests:
  - test_id: greeting-test
    name: Basic Greeting Test
    category: intent_recognition
    priority: high
    turns:
      - turn_number: 1
        role: user
        input: "Hello, I need help"
        expected_intent: greeting
        assertions:
          - assertion_id: friendly-response
            assertion_type: response_pattern
            target: response
            operator: matches
            expected_value: "(?i)(hello|hi|hey)"
```

### Quality Gates

| Metric | Default | Type |
|--------|---------|------|
| Pass Rate | ≥95% | Blocking |
| Intent Accuracy | ≥95% | Blocking |
| Coherence | ≥0.85 | Warning |
| Naturalness | ≥0.80 | Warning |

### Documentation

- [User Guide](docs/testing/user-guide.md) - Complete usage guide
- [API Reference](docs/testing/api-reference.md) - Detailed API documentation

## Context Primitives

Session state management for multi-turn Language User Interfaces.

### Features

- **Session Management** - Create, retrieve, and expire sessions with metadata
- **Conversation History** - Track multi-turn conversations with windowing and summarization
- **Context Variables** - Type-safe key-value storage for session state
- **Multiple Backends** - In-memory (dev), Redis (cache), PostgreSQL (persist), Hybrid (production)
- **BAML Integration** - Seamless context injection into BAML functions
- **Decorator System** - Declarative context injection with `@contextual`, `@persist_result`, etc.

### Quick Start

```python
from src.context_primitives import (
    ContextConfig, InMemoryContextProvider, ConversationTurn,
    init_context_system_async, session_scope, contextual
)
from datetime import datetime, timezone

# Simple usage with provider
config = ContextConfig(max_history_turns=20, ttl_seconds=3600)
provider = InMemoryContextProvider(config)

session = await provider.create_session("user_123")
turn = ConversationTurn(
    turn_id=1,
    timestamp=datetime.now(timezone.utc),
    user_input="Hello!",
    assistant_response="Hi there!"
)
await provider.add_turn("user_123", turn)

# Or use decorators
await init_context_system_async(config=config)

@contextual(inject_history=True, inject_variables=True)
async def chat(user_input: str, *, context, **kwargs):
    history = context.history
    return f"You said: {user_input}"

async with session_scope("user_123"):
    response = await chat("Hello!")
```

### Storage Backends

| Backend | Use Case | Persistence | Performance |
|---------|----------|-------------|-------------|
| Memory | Development, testing | None | Fastest |
| Redis | Production caching | Optional | Very fast |
| PostgreSQL | Long-term storage | Full ACID | Good |
| Hybrid | Production systems | Redis + PG | Optimal |

### Documentation

- [User Guide](docs/context_primitives/USER_GUIDE.md) - Complete usage guide
- [API Reference](docs/context_primitives/API_REFERENCE.md) - Detailed API documentation
- [Architecture](docs/context_primitives/ARCHITECTURE.md) - Design and internals

## Contributing

Contributions welcome! Areas of interest:

- Additional export formats
- Enhanced usability metrics
- Multi-modal LUI support
- Accessibility improvements

## License

MIT

## Acknowledgments

- [BAML](https://github.com/BoundaryML/baml) for type-safe AI interactions
- Nielsen Norman Group for usability heuristics
- The conversational AI research community
