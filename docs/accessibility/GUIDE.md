# LUI Accessibility Module Usage Guide

This guide provides practical instructions for using the LUI Accessibility module to build accessible Language User Interfaces. For API details, see [API.md](./API.md).

## Table of Contents

- [Getting Started](#getting-started)
- [Response Accessibility](#response-accessibility)
- [Schema Validation](#schema-validation)
- [Readability Analysis](#readability-analysis)
- [Jargon Detection](#jargon-detection)
- [Disability-Specific Evaluation](#disability-specific-evaluation)
- [Timing and Interaction](#timing-and-interaction)
- [Seizure Safety](#seizure-safety)
- [Screen Reader Support](#screen-reader-support)
- [Generating Reports](#generating-reports)
- [Best Practices](#best-practices)
- [Common Patterns](#common-patterns)

---

## Getting Started

### Basic Setup

```python
from src.accessibility import (
    LUIAccessibilityChecker,
    ComplianceLevel,
)

# Create a checker with default settings
checker = LUIAccessibilityChecker()

# Check a simple response
result = checker.check_response(
    "Hello! I'm here to help you with your tasks.",
    ComplianceLevel.LEVEL_AA  # Standard compliance level
)

# Check if it passes
if result.passes:
    print("Response is accessible!")
else:
    print(f"Issues found: {len(result.violations)}")
    for v in result.violations:
        print(f"  - {v.description}")
```

### Understanding Compliance Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| **Level A** | Minimum accessibility | Basic compliance, essential features |
| **Level AA** | Standard accessibility | Recommended for most applications |
| **Level AAA** | Maximum accessibility | High-accessibility contexts |

```python
# Level A - Minimum requirements
result_a = checker.check_response(text, ComplianceLevel.LEVEL_A)

# Level AA - Recommended standard (default)
result_aa = checker.check_response(text, ComplianceLevel.LEVEL_AA)

# Level AAA - Maximum accessibility
result_aaa = checker.check_response(text, ComplianceLevel.LEVEL_AAA)
```

---

## Response Accessibility

### Checking Individual Responses

```python
from src.accessibility import LUIAccessibilityChecker, ComplianceLevel

checker = LUIAccessibilityChecker()

# Check a response
result = checker.check_response(
    "Your task has been completed successfully.",
    ComplianceLevel.LEVEL_AA
)

# Access the results
print(f"Score: {result.score:.0%}")           # e.g., "85%"
print(f"Passes: {result.passes}")              # True/False
print(f"Achieved Level: {result.achieved_level.value}")  # "A", "AA", or "AAA"

# Check violations
for violation in result.violations:
    print(f"[{violation.severity.value}] {violation.code}")
    print(f"  Description: {violation.description}")
    print(f"  Fix: {violation.remediation}")

# Get recommendations
for rec in result.recommendations:
    print(f"Suggestion: {rec}")
```

### Understanding Violation Severities

```python
from src.accessibility import ViolationSeverity

for violation in result.violations:
    if violation.severity == ViolationSeverity.CRITICAL:
        # Blocks access completely - must fix
        print(f"CRITICAL: {violation.description}")
    elif violation.severity == ViolationSeverity.MAJOR:
        # Significantly impacts access - should fix
        print(f"MAJOR: {violation.description}")
    elif violation.severity == ViolationSeverity.MINOR:
        # Causes inconvenience - consider fixing
        print(f"MINOR: {violation.description}")
    else:  # ADVISORY
        # Best practice - nice to have
        print(f"SUGGESTION: {violation.description}")
```

---

## Schema Validation

### Validating a Complete Schema

```python
from src.accessibility import SchemaAccessibilityChecker, ComplianceLevel

# Define your schema
schema = {
    "name": "Task Manager Assistant",
    "description": "Helps users manage their tasks",
    "accessibility": {
        "target_level": "AA",
        "language": "en",
        "plain_language": True,
    },
    "components": [
        {
            "id": "greeting",
            "type": "message",
            "feedback": {
                "success_template": "Hello! I can help you with tasks.",
                "aria_label": "Greeting message",
            },
        },
        {
            "id": "create_task",
            "type": "action",
            "feedback": {
                "success_template": "Task created!",
                "error_template": "Could not create task. Please try again.",
            },
        },
    ],
    "timing": {
        "response_timeout": 30000,
        "typing_indicator": True,
        "allow_extension": True,
    },
}

# Validate the schema
checker = SchemaAccessibilityChecker()
result = checker.check_schema(schema, ComplianceLevel.LEVEL_AA)

# Review results
print(f"Schema: {result.schema_name}")
print(f"Overall Score: {result.overall_score:.0%}")
print(f"Components Evaluated: {result.total_components}")

# Check each component
for comp_eval in result.component_evaluations:
    print(f"\n{comp_eval.component_id}:")
    print(f"  Score: {comp_eval.score:.0%}")
    print(f"  Issues: {len(comp_eval.violations)}")
```

---

## Readability Analysis

### Analyzing Text Readability

```python
from src.accessibility import ReadabilityAnalyzer

analyzer = ReadabilityAnalyzer()

# Analyze text
text = """
Your request has been processed. The system will now execute
the specified operations according to the predefined parameters.
"""

metrics = analyzer.analyze(text)

# Key metrics
print(f"Flesch-Kincaid Grade Level: {metrics.flesch_kincaid_grade:.1f}")
print(f"Flesch Reading Ease: {metrics.flesch_reading_ease:.1f}")
print(f"Average Sentence Length: {metrics.avg_sentence_length:.1f} words")
print(f"Complex Words: {metrics.complex_word_percentage:.0%}")
```

### Readability Guidelines

| Metric | Level A | Level AA | Level AAA |
|--------|---------|----------|-----------|
| Reading Grade | ≤ 12 | ≤ 8 | ≤ 6 |
| Sentence Length | ≤ 30 words | ≤ 20 words | ≤ 15 words |
| Complex Words | ≤ 20% | ≤ 15% | ≤ 10% |

```python
# Check if text meets guidelines
def check_readability_level(metrics, level):
    if level == ComplianceLevel.LEVEL_AAA:
        return metrics.flesch_kincaid_grade <= 6
    elif level == ComplianceLevel.LEVEL_AA:
        return metrics.flesch_kincaid_grade <= 8
    else:  # LEVEL_A
        return metrics.flesch_kincaid_grade <= 12
```

---

## Jargon Detection

### Finding and Replacing Jargon

```python
from src.accessibility import JargonDetector

detector = JargonDetector()

# Detect jargon terms
text = "Let's leverage our synergies to optimize bandwidth."
terms = detector.detect(text)

for term in terms:
    print(f"Found: '{term.term}'")
    print(f"  Category: {term.category.value}")
    print(f"  Suggestion: '{term.suggestion}'")
    print(f"  Confidence: {term.confidence:.0%}")
```

### Getting Simplified Text

```python
# Get full simplification
result = detector.simplify(
    "The API endpoint requires authentication via OAuth2."
)

print(f"Original: {result.original_text}")
print(f"Simplified: {result.simplified_text}")
print(f"Terms replaced: {len(result.terms_found)}")
```

### Jargon Categories

```python
from src.accessibility import JargonCategory

# Business jargon
# "leverage", "synergies", "bandwidth", "pivot"

# Technical jargon
# "API", "authentication", "backend", "cache"

# Legal jargon
# "aforementioned", "notwithstanding", "herein"

# Medical jargon
# "acute", "chronic", "contraindicated"
```

---

## Disability-Specific Evaluation

### Evaluating All Disability Types

```python
from src.accessibility import CombinedDisabilityEvaluator, DisabilityType

evaluator = CombinedDisabilityEvaluator()
results = evaluator.evaluate(schema)

# Check each disability type
for disability_type, evaluation in results.items():
    print(f"\n{disability_type.value.upper()}")
    print(f"  Score: {evaluation.accommodation_score:.0%}")
    print(f"  Barriers: {evaluation.total_barriers}")

    # List accommodations present
    for acc in evaluation.accommodations_present:
        print(f"  ✓ {acc}")

    # List missing accommodations
    for acc in evaluation.accommodations_missing:
        print(f"  ✗ {acc}")
```

### Individual Evaluators

```python
from src.accessibility import (
    VisualAccessibilityEvaluator,
    CognitiveAccessibilityEvaluator,
    MotorAccessibilityEvaluator,
)

# Focus on specific disability types
visual = VisualAccessibilityEvaluator()
visual_result = visual.evaluate(schema)

cognitive = CognitiveAccessibilityEvaluator()
cognitive_result = cognitive.evaluate(schema)

motor = MotorAccessibilityEvaluator()
motor_result = motor.evaluate(schema)
```

---

## Timing and Interaction

### Validating Timeout Configuration

```python
from src.accessibility import (
    InteractionTimingValidator,
    TimeoutConfig,
    ComplianceLevel,
)

validator = InteractionTimingValidator()

# Configure timeout
config = TimeoutConfig(
    initial_timeout_seconds=30,      # 30 second initial timeout
    warning_before_seconds=10,        # Warn 10 seconds before
    extension_allowed=True,           # Allow extending timeout
    extension_seconds=30,             # 30 second extensions
    max_extensions=-1,                # Unlimited extensions
)

# Validate against compliance level
result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AA)

if result.passes:
    print("Timeout configuration is accessible!")
else:
    for violation in result.violations:
        print(f"Issue: {violation.description}")
        print(f"Expected: {violation.threshold_expected}")
        print(f"Actual: {violation.threshold_actual}")
```

### Timing Requirements by Level

| Level | Min Timeout | Warning Required | Extension Required |
|-------|-------------|------------------|-------------------|
| A | 20 seconds | No | No |
| AA | 30 seconds | Yes | Yes |
| AAA | 60 seconds | Yes | Unlimited |

### Validating Input Methods

```python
from src.accessibility import InputMethodConfig

input_config = InputMethodConfig(
    keyboard_accessible=True,    # All keyboard accessible
    voice_input=True,            # Voice input supported
    touch_input=True,            # Touch supported
    switch_access=True,          # Switch device support
    gesture_alternatives=True,   # Alternatives to complex gestures
)

result = validator.validate_input_methods(
    input_config,
    ComplianceLevel.LEVEL_AA
)
```

---

## Seizure Safety

### Checking Content Safety

```python
from src.accessibility import SeizureSafetyChecker

checker = SeizureSafetyChecker()

# Check content configuration
result = checker.check_content({
    "has_animations": True,
    "has_flashing": False,
    "flash_frequency_hz": 0,
})

if result.passes:
    print("Content is safe for photosensitive users")
else:
    for violation in result.violations:
        print(f"⚠️ {violation.description}")
```

### Animation Safety

```python
from src.accessibility import AnimationConfig, check_animation_safety

config = AnimationConfig(
    has_animation=True,
    flash_frequency_hz=0,           # No flashing
    duration_seconds=0.3,           # 300ms animation
    can_pause=True,                 # Can pause
    can_disable=True,               # Can disable
    reduced_motion_supported=True,  # Respects prefers-reduced-motion
)

result = check_animation_safety(config)
print(f"Animation safe: {result.passes}")
```

### Critical Thresholds

| Risk Factor | Safe Threshold |
|-------------|----------------|
| Flash frequency | < 3 Hz |
| Red flash | Never allowed |
| Flash area | < 25% of viewport |
| Animation duration | Pauseable if > 5s |

---

## Screen Reader Support

### Generating ARIA Live Regions

```python
from src.accessibility import (
    ARIALiveRegionGenerator,
    ARIAPoliteness,
    ContentType,
)

generator = ARIALiveRegionGenerator()

# Generate a polite update (waits for user idle)
html = generator.generate_live_region(
    "Your task has been saved.",
    politeness=ARIAPoliteness.POLITE,
)
# Output: <div aria-live="polite" role="status">Your task has been saved.</div>

# Generate an assertive alert (interrupts immediately)
error_html = generator.generate_error_region("Error: Could not save task.")
# Output: <div aria-live="assertive" role="alert">Error: Could not save task.</div>

# Generate status update
status_html = generator.generate_status_region("3 tasks remaining")
```

### Content Type Auto-Configuration

```python
# Content type determines optimal ARIA configuration
result = generator.generate_live_region_full(
    "Task completed!",
    content_type=ContentType.SUCCESS,  # Uses polite + status role
)

result = generator.generate_live_region_full(
    "Error occurred",
    content_type=ContentType.ERROR,    # Uses assertive + alert role
)

result = generator.generate_live_region_full(
    "Processing...",
    content_type=ContentType.PROGRESS, # Uses polite + progressbar role
)
```

### Screen Reader Hints

```python
result = generator.generate_live_region_full(
    "New message from support",
    content_type=ContentType.NOTIFICATION,
)

# Get screen reader-specific hints
for hint in result.screen_reader_hints:
    print(f"{hint.screen_reader.value}: {hint.hint}")
# JAWS: Announced as notification
# NVDA: Announced as notification
# VoiceOver: Announced as notification
```

---

## Generating Reports

### Full Accessibility Report

```python
from src.accessibility import (
    AccessibilityReportGenerator,
    ComplianceLevel,
)

generator = AccessibilityReportGenerator()

# Generate report
report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)

# Summary
print(f"Schema: {report.schema_name}")
print(f"Target: {report.target_level.value}")
print(f"Score: {report.summary.overall_score:.0%}")
print(f"Achieved: {report.summary.achieved_level.value}")
print(f"Violations: {report.summary.violation_count}")
```

### Exporting Reports

```python
# Markdown format (for documentation)
markdown = generator.export_markdown(report)
with open("accessibility_report.md", "w") as f:
    f.write(markdown)

# JSON format (for tools/APIs)
json_data = generator.export_json(report)
with open("accessibility_report.json", "w") as f:
    f.write(json_data)

# HTML format (for web display)
html = generator.export_html(report)
with open("accessibility_report.html", "w") as f:
    f.write(html)
```

### Prioritized Recommendations

```python
# Get prioritized recommendations
for rec in report.recommendations:
    print(f"[{rec.priority.upper()}] {rec.description}")
    print(f"  Category: {rec.category}")
    print(f"  Impact: {rec.impact}")
    print(f"  Effort: {rec.effort}")
```

---

## Best Practices

### 1. Write Clear, Simple Responses

```python
# Good - Simple and clear
"Task created! It's now in your list."

# Bad - Complex and jargon-heavy
"The task instantiation process has completed successfully
and the item has been persisted to the database."
```

### 2. Provide Meaningful Feedback

```python
# Good - Specific and actionable
"Could not create task. The title is too long. Use 50 characters or less."

# Bad - Vague
"Error occurred."
```

### 3. Use Appropriate Timeouts

```python
# Level AA compliant timeout
config = TimeoutConfig(
    initial_timeout_seconds=30,
    warning_before_seconds=10,
    extension_allowed=True,
    extension_seconds=30,
)
```

### 4. Support Multiple Input Methods

```python
# Accessible input configuration
config = InputMethodConfig(
    keyboard_accessible=True,     # Required for all levels
    voice_input=True,             # Recommended
    touch_input=True,             # Common on mobile
    gesture_alternatives=True,    # For motor accessibility
)
```

### 5. Generate ARIA for Dynamic Content

```python
# Always wrap dynamic content in ARIA live regions
generator = ARIALiveRegionGenerator()

# Normal updates
html = generator.generate_live_region(message, ARIAPoliteness.POLITE)

# Important alerts
html = generator.generate_error_region(error_message)
```

---

## Common Patterns

### Pattern 1: Pre-Flight Accessibility Check

```python
def send_response(response_text: str) -> str:
    """Send response after accessibility check."""
    checker = LUIAccessibilityChecker()
    result = checker.check_response(response_text, ComplianceLevel.LEVEL_AA)

    if not result.passes:
        # Log violations for monitoring
        for v in result.violations:
            logger.warning(f"Accessibility issue: {v.code}")

    # Generate ARIA markup
    generator = ARIALiveRegionGenerator()
    return generator.generate_live_region(response_text)
```

### Pattern 2: Schema Validation Pipeline

```python
def validate_schema_accessibility(schema: dict) -> bool:
    """Validate schema before deployment."""
    # Check schema structure
    schema_checker = SchemaAccessibilityChecker()
    schema_result = schema_checker.check_schema(schema, ComplianceLevel.LEVEL_AA)

    if not schema_result.passes:
        return False

    # Check all disability types
    evaluator = CombinedDisabilityEvaluator()
    results = evaluator.evaluate(schema)

    # Ensure all disability types score above threshold
    return all(r.accommodation_score >= 0.7 for r in results.values())
```

### Pattern 3: Continuous Monitoring

```python
def monitor_accessibility_metrics(responses: list[str]) -> dict:
    """Monitor accessibility across responses."""
    checker = LUIAccessibilityChecker()
    analyzer = ReadabilityAnalyzer()

    metrics = {
        "total_responses": len(responses),
        "passing_count": 0,
        "avg_score": 0.0,
        "avg_reading_level": 0.0,
        "violations_by_type": {},
    }

    for response in responses:
        result = checker.check_response(response, ComplianceLevel.LEVEL_AA)
        readability = analyzer.analyze(response)

        if result.passes:
            metrics["passing_count"] += 1

        metrics["avg_score"] += result.score
        metrics["avg_reading_level"] += readability.flesch_kincaid_grade

        for v in result.violations:
            metrics["violations_by_type"][v.code] = (
                metrics["violations_by_type"].get(v.code, 0) + 1
            )

    n = len(responses)
    metrics["avg_score"] /= n
    metrics["avg_reading_level"] /= n
    metrics["pass_rate"] = metrics["passing_count"] / n

    return metrics
```

---

## See Also

- [API.md](./API.md) - Complete API reference
- [LUIAG.md](./LUIAG.md) - LUIAG compliance reference
- [CHECKLIST.md](./CHECKLIST.md) - Implementation checklist
