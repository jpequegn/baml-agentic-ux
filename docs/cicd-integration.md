# CI/CD Integration for Conversational Testing

## Overview

This document describes the CI/CD integration for the Conversational Testing Framework, implemented as part of Task 6.8 (Issue #96).

## GitHub Actions Workflow

The workflow is defined in `.github/workflows/conversational-tests.yml` and runs automatically on:
- Push to `main` branch
- Pull requests to `main` branch
- Manual trigger via `workflow_dispatch`

### Workflow Jobs

#### 1. Test Execution Job (`test`)

Runs the conversation tests and collects metrics:

```yaml
jobs:
  test:
    name: Run Conversation Tests
    runs-on: ubuntu-latest
    timeout-minutes: 30
```

**Steps:**
1. Checkout repository
2. Set up Python 3.12
3. Install uv package manager
4. Cache dependencies
5. Install project dependencies
6. Run pytest with coverage

**Outputs:**
- `test_status`: passed/failed
- `pass_rate`: Percentage of tests passed
- `intent_accuracy`: Intent extraction accuracy
- `coherence_score`: Average coherence score
- `naturalness_score`: Average naturalness score
- `coverage`: Code coverage percentage

#### 2. Quality Gates Job (`quality-gates`)

Evaluates test results against configurable thresholds:

| Metric | Threshold | Type |
|--------|-----------|------|
| Test Pass Rate | ≥95% | BLOCKING |
| Intent Accuracy | ≥95% | BLOCKING |
| Coherence Score | ≥0.85 | WARNING |
| Naturalness Score | ≥0.80 | WARNING |
| Coverage | ≥70% | WARNING |

**BLOCKING** failures will prevent merging.
**WARNING** failures will be noted but won't block.

#### 3. PR Comment Job (`pr-comment`)

Automatically posts/updates a comment on PRs with:
- Test summary table
- Quality gate status
- Links to artifacts

## CLI Usage

The `convtest` CLI provides local testing capabilities:

```bash
# Run all tests
uv run convtest run tests/

# Run with specific output format
uv run convtest run tests/ --output json
uv run convtest run tests/ --output junit
uv run convtest run tests/ --output html

# Run with quality gates
uv run convtest run tests/ --quality-gates --min-pass-rate 95

# Filter tests by pattern
uv run convtest run tests/ --filter "intent"

# Check quality gates against results file
uv run convtest check-gates results.json

# Verbose output
uv run convtest run tests/ --verbose

# Get version
uv run convtest version

# Get framework info
uv run convtest info
```

### CLI Commands

#### `run`
Run conversation tests with optional quality gate evaluation.

```
Options:
  --output, -o      Output format (text, json, junit, html, markdown)
  --report-dir, -r  Directory to save reports
  --parallel, -p    Enable parallel test execution
  --timeout, -t     Default timeout per test in seconds
  --strict          Enable strict quality mode
  --filter, -k      Filter tests by pattern
  --quality-gates   Enable quality gate checks (default: true)
  --min-pass-rate   Minimum pass rate percentage (default: 95.0)
  --min-coherence   Minimum coherence score (default: 0.85)
  --verbose, -v     Verbose output
```

#### `check-gates`
Check quality gates against a results file.

```
Arguments:
  results_file      Path to JSON results file

Options:
  --min-pass-rate       Minimum pass rate percentage (default: 95.0)
  --min-intent-accuracy Minimum intent accuracy percentage (default: 95.0)
  --min-coherence       Minimum coherence score (default: 0.85)
  --min-naturalness     Minimum naturalness score (default: 0.80)
  --min-coverage        Minimum coverage percentage (default: 70.0)
  --output, -o          Output format (text, json)
```

## Manual Workflow Dispatch

You can manually trigger the workflow with custom parameters:

1. Go to Actions tab in GitHub
2. Select "Conversational Tests" workflow
3. Click "Run workflow"
4. Configure options:
   - `test_filter`: Pattern to filter tests (e.g., `test_intent*`)
   - `quality_strict`: Enable strict quality mode (true/false)

## Artifacts

The workflow generates and stores:

1. **test-results** (30-day retention)
   - `test-results.xml`: JUnit XML format
   - `test-output.log`: Full test output

2. **coverage-report** (30-day retention)
   - `coverage.xml`: Coverage data in XML
   - `coverage-html/`: Interactive HTML coverage report

## Local Development

### Running Tests Locally

```bash
# Install dependencies
uv sync --dev

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test file
uv run pytest tests/test_drift_detection/test_drift_pipeline.py -v
```

### Testing the Workflow Locally

You can use [act](https://github.com/nektos/act) to test the workflow locally:

```bash
# Install act
brew install act

# Run the workflow
act push
```

## Troubleshooting

### Quality Gate Failures

If quality gates fail:

1. Check the PR comment for specific failures
2. Review the test output in artifacts
3. Fix failing tests or improve quality metrics
4. Re-run the workflow

### Common Issues

**Tests timing out:**
- Increase the `timeout` parameter
- Check for infinite loops in conversation flows

**Low coherence scores:**
- Review conversation flow structure
- Ensure proper context is maintained

**Intent accuracy below threshold:**
- Add more training examples
- Review ambiguous intents
