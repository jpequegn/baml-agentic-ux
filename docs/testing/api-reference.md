# Conversational Testing Framework - API Reference

This document provides detailed API documentation for the Conversational Testing Framework.

## Table of Contents

1. [CLI Commands](#cli-commands)
2. [Core Classes](#core-classes)
3. [Types and Enums](#types-and-enums)
4. [Configuration](#configuration)

## CLI Commands

### `convtest run`

Execute conversation tests.

```bash
convtest run [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - Path to test file or directory (default: `tests/`)

**Options:**
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | text/json/junit/html/markdown | text | Output format |
| `--report-dir` | `-r` | TEXT | - | Directory to save reports |
| `--parallel` | `-p` | FLAG | false | Enable parallel execution |
| `--timeout` | `-t` | INTEGER | 30 | Timeout per test (seconds) |
| `--strict` | - | FLAG | false | Enable strict quality mode |
| `--filter` | `-k` | TEXT | - | Filter tests by pattern |
| `--quality-gates` | - | FLAG | true | Enable quality gate checks |
| `--min-pass-rate` | - | FLOAT | 95.0 | Minimum pass rate (%) |
| `--min-coherence` | - | FLOAT | 0.85 | Minimum coherence score |
| `--verbose` | `-v` | FLAG | false | Verbose output |

### `convtest validate`

Validate test files without running.

```bash
convtest validate [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - Path to test file or directory

**Options:**
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--strict` | `-s` | FLAG | false | Strict validation mode |
| `--output` | `-o` | text/json | text | Output format |
| `--verbose` | `-v` | FLAG | false | Verbose output |
| `--quiet` | `-q` | FLAG | false | Suppress non-essential output |

### `convtest coverage`

Analyze test coverage statistics.

```bash
convtest coverage [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - Path to test directory

**Options:**
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--by-category` | `-c` | FLAG | false | Show category breakdown |
| `--by-priority` | `-p` | FLAG | false | Show priority breakdown |
| `--show-gaps` | `-g` | FLAG | false | Show coverage gaps |
| `--output` | `-o` | text/json | text | Output format |
| `--verbose` | `-v` | FLAG | false | Verbose output |

### `convtest list-tests`

List available tests with filtering.

```bash
convtest list-tests [PATH] [OPTIONS]
```

**Arguments:**
- `PATH` - Path to test directory (default: `tests/conversations`)

**Options:**
| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--tags` | `-t` | TEXT | Filter by tags (comma-separated) |
| `--category` | `-c` | TEXT | Filter by category |
| `--priority` | `-p` | TEXT | Filter by priority |
| `--pattern` | `-k` | TEXT | Filter by name/ID pattern |
| `--output` | `-o` | text/json | Output format |

### `convtest check-gates`

Check quality gates against test results.

```bash
convtest check-gates [RESULTS_FILE] [OPTIONS]
```

**Arguments:**
- `RESULTS_FILE` - Path to JSON results file

**Options:**
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--config` | `-c` | TEXT | - | Path to config file |
| `--output` | `-o` | text/json | text | Output format |

**Exit Codes:**
- `0` - All quality gates passed
- `1` - One or more blocking gates failed

### `convtest generate`

Generate configuration files or templates.

```bash
convtest generate [TYPE] [OPTIONS]
```

**Arguments:**
- `TYPE` - Type to generate: `config` or `template`

**Options:**
| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--output` | `-o` | TEXT | varies | Output file path |
| `--force` | `-f` | FLAG | false | Overwrite existing file |

### `convtest config`

Manage configuration settings.

```bash
convtest config [OPTIONS]
```

**Options:**
| Option | Short | Type | Description |
|--------|-------|------|-------------|
| `--show` | `-s` | FLAG | Show current configuration |
| `--config` | `-c` | TEXT | Path to config file |
| `--validate` | - | FLAG | Validate configuration file |

### `convtest info`

Display framework information.

```bash
convtest info
```

### `convtest version`

Display version information.

```bash
convtest version
```

## Core Classes

### ConversationTestRunner

Main class for executing conversation tests.

```python
from src.testing import ConversationTestRunner, MockResponseHandler, RunnerConfig

# Create with mock handler
handler = MockResponseHandler(
    responses={1: "Hello!", 2: "How can I help?"},
    default_response="I understand."
)

# Configure runner
config = RunnerConfig(
    default_timeout_seconds=30,
    stop_on_first_failure=False,
    collect_quality_metrics=True
)

# Create runner
runner = ConversationTestRunner(handler, config)

# Run single test
result = runner.run_test(test)

# Run test suite
suite_result = runner.run_suite(suite)
```

**Constructor:**
```python
ConversationTestRunner(
    response_handler: ResponseHandler,
    config: Optional[RunnerConfig] = None
)
```

**Methods:**

| Method | Arguments | Returns | Description |
|--------|-----------|---------|-------------|
| `run_test` | `test: ConversationTest` | `TestExecutionResult` | Execute a single test |
| `run_suite` | `suite: TestSuite` | `TestSuiteResult` | Execute a test suite |

### ResponseHandler

Abstract base class for response generation.

```python
from abc import ABC, abstractmethod

class ResponseHandler(ABC):
    @abstractmethod
    def generate_response(
        self,
        user_input: str,
        context: dict[str, Any],
        turn_number: int,
    ) -> ResponseResult:
        pass
```

### MockResponseHandler

Mock implementation for testing.

```python
from src.testing import MockResponseHandler

handler = MockResponseHandler(
    responses={
        1: "Welcome!",
        2: "How can I help?",
        3: "Task created."
    },
    default_response="I understand."
)
```

### AssertionEvaluator

Evaluates assertions against test results.

```python
from src.testing import AssertionEvaluator

evaluator = AssertionEvaluator()
result = evaluator.evaluate(
    assertion=assertion,
    turn_result=turn_result,
    context=context,
    quality_scores=quality_scores
)
```

### ConversationTestLoader

Loads and validates test files.

```python
from src.testing import ConversationTestLoader, LoaderConfig

config = LoaderConfig(
    strict_validation=True,
    allow_unknown_fields=False
)

loader = ConversationTestLoader(config)

# Load single test
test = loader.load_test("tests/test.yaml")

# Load and validate
result = loader.load_and_validate("tests/test.yaml")

# Load suite
suite = loader.load_suite("tests/suite.yaml")
```

### ConfigLoader

Loads configuration from files and environment.

```python
from src.testing.config import ConfigLoader, load_config

# Load default config
config = load_config()

# Load from specific file
loader = ConfigLoader("custom-config.yaml")
config = loader.load()

# Export to YAML
yaml_str = loader.to_yaml(config)
```

## Types and Enums

### ConversationTest

Test definition dataclass.

```python
@dataclass
class ConversationTest:
    test_id: str
    name: str
    turns: list[TestTurn]
    expected_outcome: ExpectedOutcome
    description: str = ""
    category: TestCategory = TestCategory.QUALITY_ASSURANCE
    priority: TestPriority = TestPriority.MEDIUM
    tags: list[str] = field(default_factory=list)
    setup: Optional[TestSetup] = None
    timeout_seconds: Optional[int] = None
    quality_thresholds: Optional[QualityThresholds] = None
```

### TestTurn

Conversation turn definition.

```python
@dataclass
class TestTurn:
    turn_number: int
    role: TurnRole
    input: str
    expected_intent: Optional[str] = None
    expected_entities: list[ExpectedEntity] = field(default_factory=list)
    assertions: list[ConversationAssertion] = field(default_factory=list)
    delay_ms: Optional[int] = None
```

### ConversationAssertion

Assertion definition.

```python
@dataclass
class ConversationAssertion:
    assertion_id: str
    assertion_type: AssertionType
    target: AssertionTarget
    operator: AssertionOperator
    expected_value: Optional[str] = None
    threshold: Optional[float] = None
    tolerance: Optional[float] = None
    severity: AssertionSeverity = AssertionSeverity.ERROR
    message: Optional[str] = None
```

### TestExecutionResult

Result of test execution.

```python
@dataclass
class TestExecutionResult:
    test_id: str
    test_name: str
    status: TestStatus
    started_at: str
    completed_at: str
    duration_ms: int
    quality_scores: QualityScores
    turn_results: list[TurnResult]
    assertion_results: list[AssertionResult]
    failure_summary: Optional[FailureSummary] = None
    logs: list[str] = field(default_factory=list)
```

### Enumerations

**TestCategory:**
- `INTENT_RECOGNITION`
- `ENTITY_EXTRACTION`
- `DIALOGUE_FLOW`
- `EDGE_CASES`
- `ERROR_HANDLING`
- `SECURITY`
- `QUALITY_ASSURANCE`

**TestPriority:**
- `CRITICAL`
- `HIGH`
- `MEDIUM`
- `LOW`
- `EXPLORATORY`

**TestStatus:**
- `PASSED`
- `FAILED`
- `ERROR`
- `TIMEOUT`
- `SKIPPED`
- `PARTIAL`

**AssertionType:**
- `INTENT_MATCH`
- `ENTITY_PRESENT`
- `ENTITY_VALUE`
- `RESPONSE_CONTAINS`
- `RESPONSE_NOT_CONTAINS`
- `RESPONSE_PATTERN`
- `CONTEXT_VALUE`
- `LATENCY`
- `QUALITY_SCORE`

**AssertionOperator:**
- `EQUALS`
- `NOT_EQUALS`
- `CONTAINS`
- `NOT_CONTAINS`
- `MATCHES`
- `NOT_MATCHES`
- `GREATER_THAN`
- `GREATER_OR_EQUAL`
- `LESS_THAN`
- `LESS_OR_EQUAL`
- `IN_SET`
- `NOT_IN_SET`
- `SEMANTIC_SIMILAR`

**AssertionTarget:**
- `INTENT`
- `RESPONSE`
- `ENTITIES`
- `CONTEXT`
- `LATENCY`
- `COHERENCE`
- `NATURALNESS`
- `ACCURACY`
- `CONFIDENCE`

**AssertionSeverity:**
- `CRITICAL`
- `ERROR`
- `WARNING`
- `INFO`

**TurnRole:**
- `USER`
- `ASSISTANT`
- `SYSTEM`

**ExecutionOrder:**
- `SEQUENTIAL`
- `PRIORITY`
- `RANDOM`

**SuccessCondition:**
- `ALL_PASS`
- `REQUIRED_ONLY`
- `THRESHOLD`

## Configuration

### ConvTestConfig

Main configuration dataclass.

```python
@dataclass
class ConvTestConfig:
    quality_gates: QualityGatesConfig
    execution: ExecutionConfig
    reporting: ReportingConfig
    filter: FilterConfig
    paths: PathsConfig
    logging: LoggingConfig
    strict_mode: bool = False
    version: str = "1.0.0"
```

### QualityGatesConfig

Quality threshold configuration.

```python
@dataclass
class QualityGatesConfig:
    min_pass_rate: float = 95.0       # Blocking
    min_intent_accuracy: float = 95.0  # Blocking
    min_coherence: float = 0.85        # Warning
    min_naturalness: float = 0.80      # Warning
    min_coverage: float = 70.0         # Warning
    blocking_metrics: list[str]
    warning_metrics: list[str]
```

### ExecutionConfig

Execution settings.

```python
@dataclass
class ExecutionConfig:
    parallel: bool = False
    max_workers: int = 4
    timeout_seconds: int = 30
    retry_count: int = 0
    retry_delay_ms: int = 1000
    stop_on_failure: bool = False
```

### ReportingConfig

Report generation settings.

```python
@dataclass
class ReportingConfig:
    output_dir: str = "test-reports"
    formats: list[str] = ["html", "json", "junit"]
    include_logs: bool = True
    include_metrics: bool = True
    include_screenshots: bool = False
```

### Environment Variable Mapping

```python
ENV_VAR_MAPPING = {
    "CONVTEST_MIN_PASS_RATE": ("quality_gates", "min_pass_rate", float),
    "CONVTEST_MIN_INTENT_ACCURACY": ("quality_gates", "min_intent_accuracy", float),
    "CONVTEST_MIN_COHERENCE": ("quality_gates", "min_coherence", float),
    "CONVTEST_MIN_NATURALNESS": ("quality_gates", "min_naturalness", float),
    "CONVTEST_MIN_COVERAGE": ("quality_gates", "min_coverage", float),
    "CONVTEST_PARALLEL": ("execution", "parallel", bool),
    "CONVTEST_MAX_WORKERS": ("execution", "max_workers", int),
    "CONVTEST_TIMEOUT": ("execution", "timeout_seconds", int),
    "CONVTEST_OUTPUT_DIR": ("reporting", "output_dir", str),
    "CONVTEST_LOG_LEVEL": ("logging", "level", str),
    "CONVTEST_VERBOSE": ("logging", "verbose", bool),
    "CONVTEST_QUIET": ("logging", "quiet", bool),
    "CONVTEST_STRICT_MODE": ("strict_mode", None, bool),
}
```

## Python API Usage

### Running Tests Programmatically

```python
from src.testing import (
    ConversationTestRunner,
    MockResponseHandler,
    ConversationTestLoader,
    RunnerConfig,
)

# Load tests
loader = ConversationTestLoader()
suite = loader.load_suite("tests/my-suite.yaml")

# Create mock handler
handler = MockResponseHandler(
    responses={
        1: "Hello! How can I help?",
        2: "I've created that task for you.",
    }
)

# Configure and run
config = RunnerConfig(
    collect_quality_metrics=True,
    stop_on_first_failure=False,
)
runner = ConversationTestRunner(handler, config)

# Execute suite
result = runner.run_suite(suite)

# Check results
print(f"Status: {result.status.value}")
print(f"Passed: {result.summary.passed}/{result.summary.total_tests}")
print(f"Pass rate: {result.summary.pass_rate:.1%}")
```

### Custom Response Handler

```python
from src.testing import ResponseHandler, ResponseResult, ExtractedEntity

class MyLLMHandler(ResponseHandler):
    def __init__(self, client):
        self.client = client

    def generate_response(
        self,
        user_input: str,
        context: dict,
        turn_number: int,
    ) -> ResponseResult:
        # Call your LLM
        response = self.client.generate(user_input, context)

        return ResponseResult(
            response=response.text,
            detected_intent=response.intent,
            extracted_entities=[
                ExtractedEntity(e.type, e.value, e.confidence)
                for e in response.entities
            ],
            confidence=response.confidence,
            latency_ms=response.latency,
        )
```

### Evaluating Custom Assertions

```python
from src.testing import (
    AssertionEvaluator,
    ConversationAssertion,
    AssertionType,
    AssertionTarget,
    AssertionOperator,
    TurnResult,
)

evaluator = AssertionEvaluator()

turn_result = TurnResult(
    turn_number=1,
    input="Create a task",
    passed=True,
    latency_ms=150,
    actual_response="Task created successfully!",
    detected_intent="task_create",
)

assertion = ConversationAssertion(
    assertion_id="response-check",
    assertion_type=AssertionType.RESPONSE_CONTAINS,
    target=AssertionTarget.RESPONSE,
    operator=AssertionOperator.CONTAINS,
    expected_value="created",
)

result = evaluator.evaluate(assertion, turn_result, {})
print(f"Passed: {result.passed}")
```
