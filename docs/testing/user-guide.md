# Conversational Testing Framework - User Guide

This guide covers how to use the Conversational Testing Framework to validate LUI (Language User Interface) components, intent extraction, and dialogue flow quality.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Installation](#installation)
3. [Writing Test Cases](#writing-test-cases)
4. [Running Tests](#running-tests)
5. [Configuration](#configuration)
6. [Quality Gates](#quality-gates)
7. [CI/CD Integration](#cicd-integration)

## Quick Start

```bash
# Generate configuration file
convtest generate config

# Generate a test template
convtest generate template -o my-tests.yaml

# Run tests
convtest run tests/conversations/

# Check quality gates
convtest check-gates test-results.json
```

## Installation

The testing framework is included in the main package. Install dependencies:

```bash
uv sync --dev
```

## Writing Test Cases

Test cases are defined in YAML files. Each file can contain a test suite with multiple tests.

### Basic Test Structure

```yaml
suite_id: my-test-suite
name: My Test Suite
description: Tests for my conversational features

tests:
  - test_id: test-001
    name: Basic Greeting Test
    description: Verify the system responds to greetings appropriately
    category: intent_recognition
    priority: high
    tags:
      - greeting
      - smoke
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
            severity: error
    expected_outcome:
      success_condition: all_pass
```

### Test Categories

Available categories for organizing tests:

- `intent_recognition` - Intent detection accuracy
- `entity_extraction` - Entity parsing
- `dialogue_flow` - Multi-turn conversation flow
- `edge_cases` - Boundary conditions
- `error_handling` - Error recovery
- `security` - Security validation
- `quality_assurance` - General QA

### Test Priorities

- `critical` - Must pass for deployment
- `high` - Important functionality
- `medium` - Standard features
- `low` - Nice-to-have
- `exploratory` - Experimental tests

### Assertion Types

#### Response Pattern
Match response against regex patterns:

```yaml
assertions:
  - assertion_id: pattern-check
    assertion_type: response_pattern
    target: response
    operator: matches
    expected_value: "(?i)task.*created"
```

#### Intent Match
Verify detected intent:

```yaml
assertions:
  - assertion_id: intent-check
    assertion_type: intent_match
    target: intent
    operator: equals
    expected_value: "task_create"
```

#### Entity Validation
Check extracted entities:

```yaml
assertions:
  - assertion_id: entity-check
    assertion_type: entity_present
    target: entities
    operator: contains
    expected_value: "task_name"
```

#### Latency Check
Verify response time:

```yaml
assertions:
  - assertion_id: latency-check
    assertion_type: latency
    target: latency
    operator: less_than
    threshold: 500
```

### Assertion Operators

| Operator | Description |
|----------|-------------|
| `equals` | Exact match |
| `not_equals` | Not equal |
| `contains` | Contains substring |
| `not_contains` | Does not contain |
| `matches` | Regex match |
| `not_matches` | Regex doesn't match |
| `greater_than` | Numeric comparison |
| `less_than` | Numeric comparison |
| `in_set` | Value in comma-separated list |
| `semantic_similar` | Semantic similarity check |

### Multi-Turn Tests

Test complex conversation flows:

```yaml
tests:
  - test_id: booking-flow
    name: Flight Booking Flow
    category: dialogue_flow
    turns:
      - turn_number: 1
        role: user
        input: "I want to book a flight"
        expected_intent: booking_start

      - turn_number: 2
        role: assistant
        input: "I'd be happy to help you book a flight. Where would you like to go?"

      - turn_number: 3
        role: user
        input: "From NYC to LA"
        expected_entities:
          - entity_type: origin
            value: "NYC"
          - entity_type: destination
            value: "LA"
```

### Test Setup

Configure initial context and mock responses:

```yaml
tests:
  - test_id: context-test
    name: Test with Context
    setup:
      initial_context:
        user_name: "John"
        user_id: "12345"
      initial_entities:
        - entity_type: location
          value: "New York"
```

## Running Tests

### Basic Usage

```bash
# Run all tests in a directory
convtest run tests/conversations/

# Run a specific test file
convtest run tests/conversations/happy_path/single_intent.yaml

# Run with verbose output
convtest run tests/ -v

# Run with JSON output
convtest run tests/ -o json

# Run with timeout
convtest run tests/ --timeout 60

# Run with parallel execution
convtest run tests/ --parallel
```

### Filtering Tests

```bash
# Filter by pattern
convtest run tests/ -k "greeting"

# Validate tests without running
convtest validate tests/conversations/
```

### Viewing Coverage

```bash
# Show test coverage statistics
convtest coverage tests/conversations/

# JSON output for CI
convtest coverage tests/ -o json
```

### Listing Tests

```bash
# List all tests
convtest list-tests tests/conversations/

# Filter by category
convtest list-tests tests/ --category intent_recognition

# Filter by priority
convtest list-tests tests/ --priority high

# Filter by tags
convtest list-tests tests/ --tags "smoke,critical"
```

## Configuration

### Configuration File

Create `convtest.yaml` in your project root:

```yaml
# Quality thresholds
quality_gates:
  min_pass_rate: 95.0
  min_intent_accuracy: 95.0
  min_coherence: 0.85
  min_naturalness: 0.80
  min_coverage: 70.0
  blocking_metrics:
    - pass_rate
    - intent_accuracy
  warning_metrics:
    - coherence
    - naturalness
    - coverage

# Execution settings
execution:
  parallel: false
  max_workers: 4
  timeout_seconds: 30
  retry_count: 0
  stop_on_failure: false

# Reporting
reporting:
  output_dir: test-reports
  formats:
    - html
    - json
    - junit
  include_logs: true
  include_metrics: true

# Paths
paths:
  test_dirs:
    - tests/conversations
  fixtures_dir: tests/fixtures
  templates_dir: tests/conversations/templates

# Logging
logging:
  level: INFO
  verbose: false
  quiet: false
```

### Environment Variables

Override configuration via environment variables:

| Variable | Description |
|----------|-------------|
| `CONVTEST_MIN_PASS_RATE` | Minimum pass rate (%) |
| `CONVTEST_MIN_INTENT_ACCURACY` | Minimum intent accuracy (%) |
| `CONVTEST_MIN_COHERENCE` | Minimum coherence score |
| `CONVTEST_MIN_NATURALNESS` | Minimum naturalness score |
| `CONVTEST_MIN_COVERAGE` | Minimum coverage (%) |
| `CONVTEST_PARALLEL` | Enable parallel execution |
| `CONVTEST_MAX_WORKERS` | Max parallel workers |
| `CONVTEST_TIMEOUT` | Default timeout (seconds) |
| `CONVTEST_OUTPUT_DIR` | Report output directory |
| `CONVTEST_LOG_LEVEL` | Log level |
| `CONVTEST_VERBOSE` | Enable verbose output |
| `CONVTEST_STRICT_MODE` | Enable strict mode |

### Generate Configuration

```bash
# Generate default config file
convtest generate config

# Generate to specific path
convtest generate config -o custom-config.yaml

# Force overwrite existing
convtest generate config --force
```

## Quality Gates

Quality gates enforce minimum standards for test results.

### Blocking Metrics

Tests must meet these thresholds to pass:

- **Pass Rate**: ≥95% of tests must pass
- **Intent Accuracy**: ≥95% intent recognition accuracy

### Warning Metrics

These generate warnings but don't block:

- **Coherence**: ≥0.85 dialogue coherence score
- **Naturalness**: ≥0.80 response naturalness score
- **Coverage**: ≥70% test coverage

### Checking Quality Gates

```bash
# Check gates against results file
convtest check-gates test-results.json

# JSON output for CI
convtest check-gates test-results.json -o json
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All quality gates passed |
| 1 | Blocking quality gates failed |

## CI/CD Integration

### GitHub Actions

```yaml
name: Conversational Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install uv
          uv sync --dev

      - name: Run conversation tests
        run: |
          uv run convtest run tests/conversations/ -o json > results.json

      - name: Check quality gates
        run: |
          uv run convtest check-gates results.json
```

### GitLab CI

```yaml
conversational-tests:
  stage: test
  script:
    - pip install uv
    - uv sync --dev
    - uv run convtest run tests/conversations/ -o json > results.json
    - uv run convtest check-gates results.json
  artifacts:
    reports:
      junit: test-results.xml
```

## Best Practices

1. **Organize by Category**: Group tests by category in subdirectories
2. **Use Tags**: Tag tests for easy filtering (smoke, regression, etc.)
3. **Set Priorities**: Mark critical tests as `priority: critical`
4. **Add Descriptions**: Document test purpose and expected behavior
5. **Use Assertions**: Multiple assertions per turn catch more issues
6. **Test Edge Cases**: Include empty inputs, special characters, long text
7. **Version Control**: Keep test files in version control

## Troubleshooting

### Common Issues

**Test file not found:**
```bash
# Check path exists
ls tests/conversations/

# Run validate to check syntax
convtest validate tests/conversations/
```

**Configuration not loading:**
```bash
# Show current config
convtest config --show

# Validate config file
convtest config --validate -c convtest.yaml
```

**Quality gates failing:**
```bash
# Check detailed results
convtest check-gates results.json -v

# Lower thresholds temporarily (not recommended for production)
CONVTEST_MIN_PASS_RATE=80 convtest run tests/
```

## Further Reading

- [API Reference](api-reference.md) - Detailed API documentation
- [Test Case Library](../../tests/conversations/README.md) - Pre-built test cases
- [Phase 6 Plan](../PHASE6_CONVERSATIONAL_TESTING_PLAN.md) - Architecture details
