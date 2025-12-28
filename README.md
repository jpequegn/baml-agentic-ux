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
│   └── lui_schema_export/       # Multi-format exporters
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
│   └── BLOG_POST.md             # Shareable summary
│
└── tests/                       # 254 test cases
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
uv run pytest  # 254 tests
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
