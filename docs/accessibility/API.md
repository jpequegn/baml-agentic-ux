# Accessibility Module API Reference

This document provides a comprehensive API reference for the LUI Accessibility module, implementing LUIAG (Language User Interface Accessibility Guidelines).

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Modules](#core-modules)
  - [Readability Analysis](#readability-analysis)
  - [LUI Accessibility Checker](#lui-accessibility-checker)
  - [Schema Accessibility Checker](#schema-accessibility-checker)
  - [Jargon Detection](#jargon-detection)
  - [Disability Evaluators](#disability-evaluators)
  - [Interaction Timing](#interaction-timing)
  - [Seizure Safety](#seizure-safety)
  - [ARIA Live Regions](#aria-live-regions)
  - [Report Generation](#report-generation)
- [Enums and Constants](#enums-and-constants)
- [Configuration Classes](#configuration-classes)

## Installation

The accessibility module is part of the baml-agentic-ux package:

```python
from src.accessibility import (
    ReadabilityAnalyzer,
    LUIAccessibilityChecker,
    SchemaAccessibilityChecker,
    ComplianceLevel,
)
```

## Quick Start

```python
from src.accessibility import (
    LUIAccessibilityChecker,
    ComplianceLevel,
    AccessibilityReportGenerator,
)

# Check a response for accessibility
checker = LUIAccessibilityChecker()
result = checker.check_response(
    "Hello! How can I help you today?",
    ComplianceLevel.LEVEL_AA
)

print(f"Score: {result.score:.0%}")
print(f"Violations: {len(result.violations)}")

# Generate a full report
generator = AccessibilityReportGenerator()
report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)
print(generator.export_markdown(report))
```

---

## Core Modules

### Readability Analysis

Analyzes text for readability metrics following plain language guidelines.

#### `ReadabilityAnalyzer`

```python
class ReadabilityAnalyzer:
    def analyze(self, text: str) -> ReadabilityMetrics:
        """Analyze text and return comprehensive readability metrics."""
```

**Example:**
```python
from src.accessibility import ReadabilityAnalyzer, ReadabilityMetrics

analyzer = ReadabilityAnalyzer()
metrics = analyzer.analyze("The quick brown fox jumps over the lazy dog.")

print(f"Flesch-Kincaid Grade: {metrics.flesch_kincaid_grade}")
print(f"Flesch Reading Ease: {metrics.flesch_reading_ease}")
print(f"Average Sentence Length: {metrics.avg_sentence_length}")
print(f"Average Word Length: {metrics.avg_word_length}")
```

#### `ReadabilityMetrics`

```python
@dataclass
class ReadabilityMetrics:
    flesch_kincaid_grade: float      # Grade level (lower is easier)
    flesch_reading_ease: float       # Score 0-100 (higher is easier)
    avg_sentence_length: float       # Average words per sentence
    avg_word_length: float           # Average characters per word
    avg_syllables_per_word: float    # Average syllables per word
    word_count: int                  # Total word count
    sentence_count: int              # Total sentence count
    complex_word_count: int          # Words with 3+ syllables
    complex_word_percentage: float   # Percentage of complex words
```

#### `SentenceAnalyzer`

```python
class SentenceAnalyzer:
    def analyze(self, text: str) -> SentenceAnalysis:
        """Analyze individual sentences for accessibility issues."""
```

---

### LUI Accessibility Checker

Main checker for response-level accessibility compliance.

#### `LUIAccessibilityChecker`

```python
class LUIAccessibilityChecker:
    def check_response(
        self,
        response: str,
        target_level: ComplianceLevel,
    ) -> AccessibilityCheckResult:
        """Check a response for accessibility compliance."""
```

**Example:**
```python
from src.accessibility import LUIAccessibilityChecker, ComplianceLevel

checker = LUIAccessibilityChecker()
result = checker.check_response(
    "Your task has been completed successfully.",
    ComplianceLevel.LEVEL_AA
)

if result.passes:
    print("Response meets accessibility requirements!")
else:
    for violation in result.violations:
        print(f"Violation: {violation.code} - {violation.description}")
```

#### `AccessibilityCheckResult`

```python
@dataclass
class AccessibilityCheckResult:
    text: str                           # Original text checked
    target_level: ComplianceLevel       # Target compliance level
    score: float                        # Score 0.0-1.0
    passes: bool                        # Whether target level achieved
    achieved_level: ComplianceLevel     # Highest level achieved
    violations: list[AccessibilityViolation]
    recommendations: list[str]          # Improvement suggestions
    readability: ReadabilityMetrics     # Readability analysis
```

#### `AccessibilityViolation`

```python
@dataclass
class AccessibilityViolation:
    code: str                    # Violation code (e.g., "READABILITY_TOO_COMPLEX")
    severity: ViolationSeverity  # CRITICAL, MAJOR, MINOR, ADVISORY
    description: str             # Human-readable description
    location: str                # Where the violation occurs
    remediation: str             # Suggested fix
```

---

### Schema Accessibility Checker

Validates entire LUI schemas for accessibility compliance.

#### `SchemaAccessibilityChecker`

```python
class SchemaAccessibilityChecker:
    def check_schema(
        self,
        schema: dict,
        target_level: ComplianceLevel,
    ) -> SchemaAccessibilityResult:
        """Check a schema for accessibility compliance."""
```

**Example:**
```python
from src.accessibility import SchemaAccessibilityChecker, ComplianceLevel

schema = {
    "name": "Task Manager",
    "components": [
        {
            "id": "greeting",
            "type": "message",
            "feedback": {"success_template": "Hello! How can I help?"}
        }
    ]
}

checker = SchemaAccessibilityChecker()
result = checker.check_schema(schema, ComplianceLevel.LEVEL_AA)

print(f"Overall Score: {result.overall_score:.0%}")
print(f"Components Evaluated: {result.total_components}")
```

#### `SchemaAccessibilityResult`

```python
@dataclass
class SchemaAccessibilityResult:
    schema_name: str
    target_level: ComplianceLevel
    achieved_level: Optional[ComplianceLevel]
    overall_score: float
    passes: bool
    total_components: int
    component_evaluations: list[ComponentAccessibilityEval]
    violations: list[SchemaViolation]
    recommendations: list[str]
    summary: str
```

---

### Jargon Detection

Detects and suggests replacements for jargon and complex terminology.

#### `JargonDetector`

```python
class JargonDetector:
    def detect(self, text: str) -> list[JargonTerm]:
        """Detect jargon terms in text."""

    def simplify(self, text: str) -> SimplificationResult:
        """Detect and suggest simplifications for jargon."""
```

**Example:**
```python
from src.accessibility import JargonDetector

detector = JargonDetector()

# Detect jargon
terms = detector.detect("Let's leverage our synergies to optimize bandwidth.")
for term in terms:
    print(f"Jargon: '{term.term}' -> Suggest: '{term.suggestion}'")

# Get simplified version
result = detector.simplify("The API endpoint requires authentication.")
print(f"Simplified: {result.simplified_text}")
```

#### `JargonTerm`

```python
@dataclass
class JargonTerm:
    term: str                    # The jargon term found
    category: JargonCategory     # Category (BUSINESS, TECHNICAL, etc.)
    suggestion: str              # Plain language replacement
    context: str                 # Surrounding context
    confidence: float            # Detection confidence 0.0-1.0
```

#### `JargonCategory`

```python
class JargonCategory(Enum):
    BUSINESS = "business"        # Corporate jargon
    TECHNICAL = "technical"      # Technical terms
    LEGAL = "legal"              # Legal terminology
    MEDICAL = "medical"          # Medical terminology
    ACADEMIC = "academic"        # Academic language
    SLANG = "slang"              # Informal slang
```

---

### Disability Evaluators

Evaluates accessibility for specific disability types.

#### `CombinedDisabilityEvaluator`

```python
class CombinedDisabilityEvaluator:
    def evaluate(
        self,
        schema: dict,
    ) -> dict[DisabilityType, DisabilityEvaluation]:
        """Evaluate schema for all disability types."""
```

**Example:**
```python
from src.accessibility import CombinedDisabilityEvaluator, DisabilityType

evaluator = CombinedDisabilityEvaluator()
results = evaluator.evaluate(schema)

for disability_type, evaluation in results.items():
    print(f"{disability_type.value}: {evaluation.accommodation_score:.0%}")
    for barrier in evaluation.barriers:
        print(f"  - Barrier: {barrier.description}")
```

#### Individual Evaluators

```python
class VisualAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluates visual accessibility (screen readers, contrast, etc.)"""

class HearingAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluates hearing accessibility (captions, transcripts, etc.)"""

class MotorAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluates motor accessibility (keyboard nav, timing, etc.)"""

class SpeechAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluates speech accessibility (voice input alternatives)"""

class CognitiveAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluates cognitive accessibility (plain language, memory load)"""

class NeurologicalAccessibilityEvaluator(DisabilityEvaluator):
    """Evaluates neurological accessibility (seizure safety, etc.)"""
```

#### `DisabilityType`

```python
class DisabilityType(Enum):
    VISUAL = "visual"
    HEARING = "hearing"
    MOTOR = "motor"
    SPEECH = "speech"
    COGNITIVE = "cognitive"
    NEUROLOGICAL = "neurological"
```

#### `DisabilityEvaluation`

```python
@dataclass
class DisabilityEvaluation:
    disability_type: DisabilityType
    accommodation_score: float        # Score 0.0-1.0
    barriers: list[Barrier]           # Identified barriers
    accommodations_present: list[str] # Present accommodations
    accommodations_missing: list[str] # Missing accommodations
    recommendations: list[str]        # Improvement suggestions
    total_barriers: int               # Total barrier count
```

---

### Interaction Timing

Validates timeout and timing configurations for motor/cognitive accessibility.

#### `InteractionTimingValidator`

```python
class InteractionTimingValidator:
    def validate_timeout(
        self,
        config: TimeoutConfig,
        target_level: ComplianceLevel,
    ) -> TimingValidationResult:
        """Validate timeout configuration."""

    def validate_input_methods(
        self,
        config: InputMethodConfig,
        target_level: ComplianceLevel,
    ) -> InputValidationResult:
        """Validate input method support."""

    def validate_all(
        self,
        component_id: str,
        target_level: ComplianceLevel,
        timeout_config: TimeoutConfig = None,
        input_config: InputMethodConfig = None,
        feedback_config: FeedbackConfig = None,
        error_config: ErrorHandlingConfig = None,
        auto_update_config: AutoUpdateConfig = None,
    ) -> InteractionValidationResult:
        """Validate all interaction timing aspects."""
```

**Example:**
```python
from src.accessibility import (
    InteractionTimingValidator,
    TimeoutConfig,
    ComplianceLevel,
)

validator = InteractionTimingValidator()

config = TimeoutConfig(
    initial_timeout_seconds=30,
    warning_before_seconds=10,
    extension_allowed=True,
    extension_seconds=30,
)

result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AA)

if result.passes:
    print("Timing configuration meets requirements!")
else:
    for violation in result.violations:
        print(f"Issue: {violation.description}")
```

#### `TimeoutConfig`

```python
@dataclass
class TimeoutConfig:
    initial_timeout_seconds: int     # Base timeout duration
    warning_before_seconds: int = 0  # Warning time before timeout
    extension_allowed: bool = False  # Whether extension is available
    extension_seconds: int = 0       # Duration of each extension
    max_extensions: int = 0          # Max extensions (-1 for unlimited)
```

#### Timing Thresholds

```python
TIMING_THRESHOLDS: dict[ComplianceLevel, TimingThreshold]
# Level A: 20s minimum, no extension required
# Level AA: 30s minimum, extension required
# Level AAA: 60s minimum, unlimited extensions required
```

---

### Seizure Safety

Validates content for photosensitive seizure safety.

#### `SeizureSafetyChecker`

```python
class SeizureSafetyChecker:
    def check_content(
        self,
        content: dict,
    ) -> SeizureSafetyResult:
        """Check content for seizure safety."""

    def check_animation(
        self,
        config: AnimationConfig,
    ) -> AnimationSafetyResult:
        """Check animation configuration for safety."""
```

**Example:**
```python
from src.accessibility import SeizureSafetyChecker

checker = SeizureSafetyChecker()

result = checker.check_content({
    "has_animations": True,
    "has_flashing": False,
    "animation_duration_ms": 300,
})

if result.passes:
    print("Content is safe for photosensitive users")
else:
    for violation in result.violations:
        print(f"Warning: {violation.description}")
```

#### Convenience Functions

```python
def check_flash_safety(flash_config: dict) -> FlashAnalysis:
    """Quick check for flash safety."""

def check_animation_safety(animation_config: AnimationConfig) -> AnimationSafetyResult:
    """Quick check for animation safety."""
```

---

### ARIA Live Regions

Generates ARIA markup for screen reader compatibility.

#### `ARIALiveRegionGenerator`

```python
class ARIALiveRegionGenerator:
    def generate_live_region(
        self,
        response: str,
        politeness: ARIAPoliteness = None,
        content_type: ContentType = None,
        config: ARIAConfig = None,
    ) -> str:
        """Generate ARIA live region HTML."""

    def generate_live_region_full(
        self,
        response: str,
        politeness: ARIAPoliteness = None,
        content_type: ContentType = None,
        config: ARIAConfig = None,
        include_hints: bool = True,
    ) -> LiveRegionResult:
        """Generate ARIA live region with full result details."""

    def generate_error_region(self, message: str) -> str:
        """Generate error alert region."""

    def generate_status_region(self, message: str) -> str:
        """Generate status update region."""
```

**Example:**
```python
from src.accessibility import (
    ARIALiveRegionGenerator,
    ARIAPoliteness,
    ContentType,
)

generator = ARIALiveRegionGenerator()

# Simple usage
html = generator.generate_live_region(
    "Task completed successfully",
    politeness=ARIAPoliteness.POLITE,
)
print(html)
# <div aria-live="polite" role="status">Task completed successfully</div>

# With full details
result = generator.generate_live_region_full(
    "New message received",
    content_type=ContentType.NOTIFICATION,
)
print(f"HTML: {result.html}")
for hint in result.screen_reader_hints:
    print(f"Hint for {hint.screen_reader.value}: {hint.hint}")
```

#### `ARIAPoliteness`

```python
class ARIAPoliteness(Enum):
    OFF = "off"              # No announcements
    POLITE = "polite"        # Wait for user idle (default)
    ASSERTIVE = "assertive"  # Interrupt immediately
```

#### `ARIARole`

```python
class ARIARole(Enum):
    LOG = "log"              # Sequential log (chat history)
    STATUS = "status"        # Status information
    ALERT = "alert"          # Important messages
    ALERTDIALOG = "alertdialog"
    PROGRESSBAR = "progressbar"
    TIMER = "timer"
    MARQUEE = "marquee"
    REGION = "region"
```

#### Convenience Functions

```python
def generate_live_region(response: str, ...) -> str:
    """Quick live region generation."""

def generate_error_alert(message: str) -> str:
    """Quick error alert generation."""

def generate_status_update(message: str) -> str:
    """Quick status update generation."""
```

---

### Report Generation

Generates comprehensive accessibility reports.

#### `AccessibilityReportGenerator`

```python
class AccessibilityReportGenerator:
    def generate_report(
        self,
        schema: dict,
        target_level: ComplianceLevel,
    ) -> AccessibilityReport:
        """Generate a comprehensive accessibility report."""

    def export_markdown(self, report: AccessibilityReport) -> str:
        """Export report as Markdown."""

    def export_json(self, report: AccessibilityReport) -> str:
        """Export report as JSON."""

    def export_html(self, report: AccessibilityReport) -> str:
        """Export report as HTML."""
```

**Example:**
```python
from src.accessibility import (
    AccessibilityReportGenerator,
    ComplianceLevel,
)

generator = AccessibilityReportGenerator()
report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)

# Export in different formats
md = generator.export_markdown(report)
json_str = generator.export_json(report)
html = generator.export_html(report)

# Access report details
print(f"Schema: {report.schema_name}")
print(f"Score: {report.summary.overall_score:.0%}")
print(f"Achieved Level: {report.summary.achieved_level}")
```

#### `AccessibilityReport`

```python
@dataclass
class AccessibilityReport:
    schema_name: str
    target_level: ComplianceLevel
    generated_at: datetime
    summary: ReportSummary
    component_details: list[ComponentReport]
    disability_coverage: list[DisabilityReport]
    violations: list[AccessibilityViolation]
    recommendations: list[Recommendation]
```

#### `Recommendation`

```python
@dataclass
class Recommendation:
    priority: str          # "high", "medium", "low"
    category: str          # Category of recommendation
    description: str       # What to improve
    impact: str            # Expected impact
    effort: str            # Implementation effort
```

---

## Enums and Constants

### `ComplianceLevel`

```python
class ComplianceLevel(Enum):
    LEVEL_A = "A"      # Minimum accessibility
    LEVEL_AA = "AA"    # Standard accessibility (recommended)
    LEVEL_AAA = "AAA"  # Maximum accessibility
```

### `ViolationSeverity`

```python
class ViolationSeverity(Enum):
    CRITICAL = "critical"  # Blocks access completely
    MAJOR = "major"        # Significantly impacts access
    MINOR = "minor"        # Causes inconvenience
    ADVISORY = "advisory"  # Best practice suggestion
```

---

## Configuration Classes

### Input Methods

```python
@dataclass
class InputMethodConfig:
    keyboard_accessible: bool = True
    voice_input: bool = False
    touch_input: bool = True
    switch_access: bool = False
    eye_tracking: bool = False
    gesture_alternatives: bool = False
    pointer_adjustable: bool = False
```

### Feedback

```python
@dataclass
class FeedbackConfig:
    immediate_confirmation: bool = True
    error_messages_clear: bool = True
    success_indicators: bool = True
    progress_indicators: bool = False
    status_updates: bool = False
```

### Error Handling

```python
@dataclass
class ErrorHandlingConfig:
    error_prevention: bool = True
    error_identification: bool = True
    error_suggestions: bool = False
    undo_available: bool = False
    auto_save: bool = False
    recovery_options: bool = False
```

### Auto-Update

```python
@dataclass
class AutoUpdateConfig:
    has_auto_update: bool = False
    can_pause: bool = False
    can_stop: bool = False
    can_adjust_frequency: bool = False
    update_frequency_seconds: int = 0
```

### Animation

```python
@dataclass
class AnimationConfig:
    has_animation: bool = False
    flash_frequency_hz: float = 0.0
    duration_seconds: float = 0.0
    can_pause: bool = False
    can_disable: bool = False
    reduced_motion_supported: bool = False
```

### ARIA

```python
@dataclass
class ARIAConfig:
    role: ARIARole
    aria_live: ARIAPoliteness
    aria_atomic: bool = False
    aria_relevant: ARIARelevant = ARIARelevant.ADDITIONS_TEXT
    aria_busy: bool = False
```

---

## See Also

- [GUIDE.md](./GUIDE.md) - Usage guide and best practices
- [LUIAG.md](./LUIAG.md) - LUIAG compliance reference
- [CHECKLIST.md](./CHECKLIST.md) - Implementation checklist
