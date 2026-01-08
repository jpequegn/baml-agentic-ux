# LUI Starter Templates Design

**Issue:** baml-agentic-ux-aqk
**Date:** 2026-01-08
**Status:** Approved

## Overview

LUI Starter Templates provide pre-built, educational templates that demonstrate best practices for building Language User Interfaces with BAML. Developers can scaffold complete working examples via a CLI tool.

## Goals

1. **Learning tool** - Templates demonstrate best practices, patterns, and BAML conventions
2. **Quick scaffolding** - Developers get a working schema + code in seconds
3. **Comprehensive coverage** - Four template categories cover common LUI patterns

## Template Categories

| Template | Purpose | Key Patterns |
|----------|---------|--------------|
| **crud** | Basic CRUD operations | Component types, invocation patterns, confirmation for destructive actions |
| **search** | Search & discovery | Filter parameters, entity resolution, pagination, faceted search |
| **workflow** | Multi-step flows | State transitions, branching logic, progress tracking, resumable sessions |
| **support** | Help desk patterns | FAQ matching, escalation, ticket lifecycle, agent handoff |

## CLI Interface

### Usage

```bash
# Interactive mode (default)
python -m baml_agentic_ux init

# Flag mode for scripting
python -m baml_agentic_ux init --template crud --name my-task-app --output ./projects

# List available templates
python -m baml_agentic_ux init --list
```

### Interactive Flow

```
$ python -m baml_agentic_ux init

Welcome to BAML Agentic UX! Let's scaffold a LUI project.

? Select a template:
  > crud        - CRUD operations (create, read, update, delete)
    search      - Search & discovery with filters
    workflow    - Multi-step conversational flows
    support     - Help desk & support patterns

? Project name: my-task-app
? Output directory: [./my-task-app]

Creating project...
  + Created my-task-app/schema.json
  + Created my-task-app/integration.py
  + Created my-task-app/test_integration.py
  + Created my-task-app/README.md

Done! Next steps:
  cd my-task-app
  cat README.md        # Start here to learn the patterns
  python integration.py  # Run the example
```

### CLI Flags

| Flag | Short | Description |
|------|-------|-------------|
| `--template` | `-t` | Template name (crud, search, workflow, support) |
| `--name` | `-n` | Project name (used in schema_id and file headers) |
| `--output` | `-o` | Output directory (defaults to `./<name>`) |
| `--force` | `-f` | Overwrite existing directory |
| `--list` | | List available templates with descriptions |

## Template Structure

Each template is a self-contained directory:

```
src/templates/
├── __init__.py
├── crud/
│   ├── README.md              # Learning guide explaining patterns used
│   ├── schema.json            # The LUI schema
│   ├── integration.py         # Python code showing how to use the schema
│   └── test_integration.py    # Tests demonstrating expected behavior
├── search/
│   └── ... (same structure)
├── workflow/
│   └── ... (same structure)
└── support/
    └── ... (same structure)
```

### File Purposes

- **README.md** - Learning centerpiece; explains why each pattern is used
- **schema.json** - LUI schema using existing format from `examples/`
- **integration.py** - Real usage with `baml_client` (loading, intent extraction, response generation)
- **test_integration.py** - Validates patterns work; serves as additional documentation

## Template Customization

### Substitution Variables

```python
{
    "PROJECT_NAME": "my-task-app",           # From --name flag
    "PROJECT_NAME_SNAKE": "my_task_app",     # For Python identifiers
    "PROJECT_NAME_TITLE": "My Task App",     # For display
    "SCHEMA_ID": "my-task-app-v1",           # For schema_id field
    "CREATED_DATE": "2026-01-08",            # Generation timestamp
}
```

### What Gets Customized

- `schema.json`: `schema_id`, `name`, `description` fields
- `integration.py`: Module docstring, schema path reference
- `test_integration.py`: Test class name, docstrings
- `README.md`: Project name in title and examples

### What Stays Static

- All components, invocations, and patterns (the learning content)
- Inline comments explaining "why"
- Test assertions and integration code logic

### Implementation

Simple string replacement using `{{VARIABLE}}` markers:

```python
def scaffold_template(template_name: str, project_name: str, output_dir: Path):
    template_dir = Path(__file__).parent.parent / "templates" / template_name
    substitutions = build_substitutions(project_name)

    for file in template_dir.iterdir():
        content = file.read_text()
        customized = apply_substitutions(content, substitutions)
        (output_dir / file.name).write_text(customized)
```

## Template Content Details

### 1. CRUD Template

**Schema**: Task manager with 6 components
**Components**: create-task, list-tasks, update-task, delete-task, complete-task, help
**Teaches**:
- Component types (ACTION, QUERY, FEEDBACK)
- Invocation patterns with alternate phrases
- Confirmation for destructive actions
- Feedback templates with variables

**Based on**: Existing `examples/task_manager_schema.json`

### 2. Search Template

**Schema**: Knowledge base with article search
**Components**: search-articles, browse-categories, get-article, related-content, suggest-topics
**Teaches**:
- Filter parameters
- Entity resolution ("the latest article" → ID)
- Pagination patterns
- Faceted search
- Result ranking hints

### 3. Workflow Template

**Schema**: User onboarding wizard
**Components**: start-onboarding, collect-info, set-preferences, confirm-setup, skip-step, go-back
**Teaches**:
- Multi-step flows
- State transitions
- Branching logic (skip steps based on answers)
- Progress tracking
- Resumable sessions

### 4. Support Template

**Schema**: IT helpdesk with ticket lifecycle
**Components**: describe-issue, search-solutions, create-ticket, check-status, escalate, provide-feedback
**Teaches**:
- FAQ matching
- Escalation patterns
- Ticket states
- Agent handoff
- Satisfaction collection
- Knowledge base fallback

## File Organization

### New Files

```
src/
├── cli/
│   ├── __init__.py
│   ├── __main__.py          # Entry point for python -m baml_agentic_ux
│   ├── init_command.py      # The init command logic
│   └── scaffolder.py        # Template copying & substitution
├── templates/
│   ├── __init__.py
│   ├── crud/
│   │   ├── README.md
│   │   ├── schema.json
│   │   ├── integration.py
│   │   └── test_integration.py
│   ├── search/
│   │   └── ...
│   ├── workflow/
│   │   └── ...
│   └── support/
│       └── ...
```

### Dependencies

Add to `pyproject.toml`:
- `questionary` - Interactive prompts
- `rich` - Styled terminal output

### pyproject.toml Entry Point

```toml
[project.scripts]
baml-agentic-ux = "src.cli:main"
```

Enables `baml-agentic-ux init` after pip install.

## Test Coverage

- `tests/test_cli_init.py` - CLI argument parsing, interactive flow mocking
- `tests/test_scaffolder.py` - Template substitution, file creation
- `tests/test_templates/` - Validate each template's schema loads and integration runs

## Implementation Checklist

- [ ] Create `src/cli/` module structure
- [ ] Implement `__main__.py` entry point
- [ ] Implement `init_command.py` with argument parsing
- [ ] Implement `scaffolder.py` with template copying
- [ ] Create `src/templates/` directory structure
- [ ] Create CRUD template (schema, integration, tests, README)
- [ ] Create Search template
- [ ] Create Workflow template
- [ ] Create Support template
- [ ] Add dependencies to pyproject.toml
- [ ] Add entry point to pyproject.toml
- [ ] Write CLI tests
- [ ] Write scaffolder tests
- [ ] Write template validation tests
- [ ] Update project README with CLI usage
