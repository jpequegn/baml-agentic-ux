# Conversational Test Case Library

A comprehensive library of reusable test cases for testing conversational AI systems.

**Part of Task 6.9: Test Case Library**
**Issue #97 - Phase 6: Conversational Testing Framework**

## Overview

This library provides 150+ test cases organized by category, covering:

- **Happy Path** - Standard successful interactions
- **Error Handling** - Graceful handling of errors and edge cases
- **Edge Cases** - Boundary conditions and unusual inputs
- **Adversarial** - Security and manipulation resistance
- **Multi-Turn** - Complex multi-turn conversations

## Directory Structure

```
tests/conversations/
├── README.md                      # This file
├── happy_path/
│   ├── single_intent.yaml         # 21 tests - Simple single-intent interactions
│   ├── entity_extraction.yaml     # 20 tests - Entity extraction scenarios
│   └── confirmation_flows.yaml    # 16 tests - Confirmation dialogs
├── error_handling/
│   ├── unknown_intent.yaml        # 16 tests - Unrecognized intent handling
│   ├── missing_parameters.yaml    # 16 tests - Missing required parameters
│   └── system_errors.yaml         # 14 tests - System error recovery
├── edge_cases/
│   ├── empty_input.yaml           # 12 tests - Empty/whitespace inputs
│   ├── long_input.yaml            # 10 tests - Very long inputs
│   ├── special_characters.yaml    # 18 tests - Special character handling
│   ├── unicode_handling.yaml      # 18 tests - Unicode and emoji support
│   └── context_switching.yaml     # 12 tests - Rapid context switches
├── adversarial/
│   ├── injection_attempts.yaml    # 16 tests - Prompt injection resistance
│   ├── malicious_input.yaml       # 17 tests - Malicious input patterns
│   └── boundary_testing.yaml      # 20 tests - System boundary testing
├── multi_turn/
│   ├── task_management.yaml       # 8 tests - Task CRUD flows
│   ├── calendar_scheduling.yaml   # 8 tests - Calendar scheduling flows
│   └── context_retention.yaml     # 12 tests - Context retention tests
└── templates/
    ├── base_templates.yaml        # Reusable test templates
    └── assertion_patterns.yaml    # Common assertion patterns
```

## Test Case Format

Each test case follows the YAML schema defined in `tests/fixtures/conversations/`:

```yaml
- test_id: hp-si-001                    # Unique identifier
  name: Basic Greeting                  # Human-readable name
  description: Test basic greeting      # Description
  category: intent_recognition          # Category
  priority: critical|high|medium|low    # Priority level
  tags:                                 # Filterable tags
    - greeting
    - simple
  setup:                                # Optional test setup
    initial_context:
      key: value
    mock_responses:
      - trigger_pattern: "api_call"
        response_type: error
        response_data: "timeout"
  turns:                                # Conversation turns
    - turn_number: 1
      role: user|assistant
      input: "Hello"
      expected_intent: greeting
      expected_entities:
        - entity_type: name
          value: "John"
      assertions:
        - assertion_id: friendly-response
          assertion_type: response_pattern
          target: response
          operator: matches
          expected_value: "(?i)(hi|hello|hey)"
```

## Test Categories

### Happy Path Tests (57 tests)

Standard successful interaction patterns:

| Suite | Tests | Description |
|-------|-------|-------------|
| single_intent | 21 | Simple single-intent recognition |
| entity_extraction | 20 | Entity extraction scenarios |
| confirmation_flows | 16 | Confirmation and parameter flows |

### Error Handling Tests (46 tests)

Graceful error handling:

| Suite | Tests | Description |
|-------|-------|-------------|
| unknown_intent | 16 | Unrecognized intent handling |
| missing_parameters | 16 | Missing required parameters |
| system_errors | 14 | System error recovery |

### Edge Case Tests (70 tests)

Boundary conditions and unusual inputs:

| Suite | Tests | Description |
|-------|-------|-------------|
| empty_input | 12 | Empty and whitespace handling |
| long_input | 10 | Very long input handling |
| special_characters | 18 | Special character handling |
| unicode_handling | 18 | Unicode, emoji, i18n support |
| context_switching | 12 | Rapid context switches |

### Adversarial Tests (53 tests)

Security and manipulation resistance:

| Suite | Tests | Description |
|-------|-------|-------------|
| injection_attempts | 16 | Prompt injection resistance |
| malicious_input | 17 | Malicious input patterns |
| boundary_testing | 20 | System boundary testing |

### Multi-Turn Tests (28 tests)

Complex multi-turn conversations:

| Suite | Tests | Description |
|-------|-------|-------------|
| task_management | 8 | Task CRUD lifecycle |
| calendar_scheduling | 8 | Calendar scheduling flows |
| context_retention | 12 | Context retention tests |

## Assertion Types

### Response Pattern
```yaml
assertion_type: response_pattern
operator: matches|not_matches|contains|not_contains
expected_value: "(?i)(pattern)"
```

### Entity Validation
```yaml
assertion_type: entity_present|entity_value
target: entity_name
operator: equals|contains|matches
expected_value: "expected"
```

### Context Requirements
```yaml
context_requirements:
  - key: context_key
    match_type: exists|equals|contains
    value_match: "expected"
```

## Priority Levels

- **critical** - Core functionality, must pass
- **high** - Important functionality
- **medium** - Standard functionality
- **low** - Nice-to-have, edge cases

## Tags

Common tags for filtering:

- Intent: `greeting`, `task_create`, `meeting_schedule`
- Category: `intent-recognition`, `entity-extraction`, `dialogue-flow`
- Type: `security`, `boundary`, `edge-case`
- Domain: `task`, `calendar`, `reminder`

## Using Templates

Templates in `templates/` provide reusable patterns:

### Base Templates
```yaml
template_ref: intent-recognition-basic
test_id: my-test-001
input: "Create a task"
expected_intent: task_create
```

### Assertion Patterns
```yaml
assertion_pattern_ref: safe-and-helpful
# Includes: no-error-in-response, no-technical-jargon, offers-help
```

## Running Tests

```bash
# Run all conversation tests
convtest run tests/conversations/

# Run specific category
convtest run tests/conversations/happy_path/

# Run with tag filter
convtest run tests/conversations/ --tags security

# Run with priority filter
convtest run tests/conversations/ --priority critical
```

## Adding New Tests

1. Choose the appropriate category directory
2. Follow the YAML schema format
3. Use consistent test_id naming: `{category}-{subcategory}-{number}`
4. Add relevant tags for filtering
5. Set appropriate priority level
6. Use assertion patterns from templates when applicable

## Test ID Conventions

| Category | Prefix | Example |
|----------|--------|---------|
| Happy Path Single Intent | hp-si | hp-si-001 |
| Happy Path Entity Extraction | hp-ee | hp-ee-001 |
| Happy Path Confirmation | hp-cf | hp-cf-001 |
| Error Handling Unknown Intent | eh-ui | eh-ui-001 |
| Error Handling Missing Params | eh-mp | eh-mp-001 |
| Error Handling System Errors | eh-se | eh-se-001 |
| Edge Case Empty Input | ec-ei | ec-ei-001 |
| Edge Case Long Input | ec-li | ec-li-001 |
| Edge Case Special Chars | ec-sc | ec-sc-001 |
| Edge Case Unicode | ec-uh | ec-uh-001 |
| Edge Case Context Switch | ec-cs | ec-cs-001 |
| Adversarial Injection | adv-ia | adv-ia-001 |
| Adversarial Malicious | adv-mi | adv-mi-001 |
| Adversarial Boundary | adv-bt | adv-bt-001 |
| Multi-Turn Task Mgmt | mt-tm | mt-tm-001 |
| Multi-Turn Calendar | mt-cs | mt-cs-001 |
| Multi-Turn Context | mt-cr | mt-cr-001 |

## Contributing

When adding tests:

1. Ensure unique test_id
2. Follow existing patterns
3. Add comprehensive assertions
4. Document expected behavior
5. Tag appropriately for filtering
