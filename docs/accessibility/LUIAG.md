# LUIAG - Language User Interface Accessibility Guidelines

LUIAG (Language User Interface Accessibility Guidelines) is an accessibility framework specifically designed for conversational and LLM-based interfaces. It extends WCAG principles to address the unique challenges of language-based user experiences.

## Table of Contents

- [Overview](#overview)
- [Compliance Levels](#compliance-levels)
- [Principles](#principles)
- [Guidelines by Category](#guidelines-by-category)
  - [Perceivable](#perceivable)
  - [Operable](#operable)
  - [Understandable](#understandable)
  - [Robust](#robust)
- [Success Criteria](#success-criteria)
- [Disability-Specific Requirements](#disability-specific-requirements)
- [Implementation Mapping](#implementation-mapping)

---

## Overview

### What is LUIAG?

LUIAG provides accessibility guidelines specifically for Language User Interfaces (LUIs) - conversational agents, chatbots, voice assistants, and other LLM-powered interfaces. While WCAG addresses traditional visual interfaces, LUIAG addresses the unique challenges of:

- **Conversational Interfaces**: Turn-based dialogue, context maintenance
- **Natural Language Processing**: Understanding varied user input
- **AI-Generated Content**: Ensuring accessible LLM outputs
- **Multimodal Interaction**: Voice, text, and hybrid interfaces

### Relationship to WCAG

| WCAG Principle | LUIAG Adaptation |
|----------------|------------------|
| Perceivable | Content understandable across modalities |
| Operable | Multiple input methods, flexible timing |
| Understandable | Plain language, predictable behavior |
| Robust | Compatible with assistive technologies |

---

## Compliance Levels

### Level A - Minimum

Essential accessibility features that must be present for basic usability.

| Requirement | Description |
|-------------|-------------|
| Text Alternatives | All non-text content has text alternatives |
| Time Limits | 20+ second timeouts with warning |
| Keyboard Access | All functionality accessible via keyboard |
| Reading Level | Grade 12 or lower |
| Error Identification | Errors are clearly identified |

### Level AA - Standard (Recommended)

Standard accessibility that should be met for most applications.

| Requirement | Description |
|-------------|-------------|
| All Level A | All Level A requirements |
| Enhanced Timing | 30+ seconds with extensions |
| Plain Language | Grade 8 reading level |
| Multiple Input | Voice input support |
| Error Prevention | Prevention for important actions |
| Consistent Navigation | Predictable interaction patterns |

### Level AAA - Maximum

Maximum accessibility for specialized high-accessibility contexts.

| Requirement | Description |
|-------------|-------------|
| All Level AA | All Level AA requirements |
| Extended Timing | 60+ seconds, unlimited extensions |
| Simple Language | Grade 6 reading level |
| Full Input Support | All input methods including switch |
| Sign Language | Sign language support available |
| Full Error Prevention | Prevention, suggestions, and undo |

---

## Principles

### 1. Perceivable

Information must be presentable in ways all users can perceive.

**For LUIs:**
- Text responses readable by screen readers
- Audio content has text alternatives
- Visual cues have non-visual equivalents
- Information not dependent on single sensory channel

### 2. Operable

Users must be able to operate the interface.

**For LUIs:**
- Multiple input methods (text, voice, keyboard)
- Sufficient time to respond
- No time-sensitive interactions without alternatives
- Navigation and interaction via assistive technologies

### 3. Understandable

Information and operation must be understandable.

**For LUIs:**
- Plain language appropriate to audience
- Predictable behavior and responses
- Clear error messages with guidance
- Consistent interaction patterns

### 4. Robust

Content must be robust enough to work with assistive technologies.

**For LUIs:**
- ARIA live regions for dynamic content
- Compatible with screen readers
- Graceful degradation
- Standard protocols and formats

---

## Guidelines by Category

### Perceivable

#### P1: Text Alternatives

All non-text content must have text alternatives.

```python
# Check: Text content is available
from src.accessibility import LUIAccessibilityChecker

checker = LUIAccessibilityChecker()
result = checker.check_response(response, ComplianceLevel.LEVEL_A)
```

| Level | Requirement |
|-------|-------------|
| A | Text alternatives for all media |
| AA | Captions for audio content |
| AAA | Sign language interpretation |

#### P2: Adaptable Content

Content must be presentable in different ways.

| Level | Requirement |
|-------|-------------|
| A | Meaningful sequence preserved |
| AA | Multiple presentation formats |
| AAA | User-configurable presentation |

#### P3: Distinguishable

Content must be easy to perceive.

| Level | Requirement |
|-------|-------------|
| A | Information not conveyed by color alone |
| AA | Audio control available |
| AAA | Low or no background audio |

---

### Operable

#### O1: Keyboard Accessible

All functionality accessible via keyboard.

```python
from src.accessibility import InputMethodConfig

# Level A: Basic keyboard
config_a = InputMethodConfig(keyboard_accessible=True)

# Level AA: Keyboard + voice
config_aa = InputMethodConfig(
    keyboard_accessible=True,
    voice_input=True,
)

# Level AAA: All methods
config_aaa = InputMethodConfig(
    keyboard_accessible=True,
    voice_input=True,
    switch_access=True,
    eye_tracking=True,
)
```

#### O2: Enough Time

Users must have enough time to read and use content.

```python
from src.accessibility import TimeoutConfig, TIMING_THRESHOLDS

# Level A: 20 seconds minimum
TIMING_THRESHOLDS[ComplianceLevel.LEVEL_A].min_timeout_seconds  # 20

# Level AA: 30 seconds with extension
TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AA].min_timeout_seconds  # 30
TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AA].extension_required  # True

# Level AAA: 60 seconds with unlimited extensions
TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AAA].min_timeout_seconds  # 60
TIMING_THRESHOLDS[ComplianceLevel.LEVEL_AAA].unlimited_extensions  # True
```

#### O3: Seizure Safe

Content must not cause seizures.

```python
from src.accessibility import SeizureSafetyChecker

checker = SeizureSafetyChecker()

# Critical thresholds
# - Flash frequency: < 3 Hz
# - Red flash: Never
# - Flash area: < 25% viewport
```

#### O4: Navigable

Users must be able to navigate and find content.

| Level | Requirement |
|-------|-------------|
| A | Purpose of each interaction clear |
| AA | Multiple ways to access functions |
| AAA | Location in conversation context clear |

---

### Understandable

#### U1: Readable

Text content must be readable and understandable.

```python
from src.accessibility import ReadabilityAnalyzer

analyzer = ReadabilityAnalyzer()
metrics = analyzer.analyze(text)

# Level A: Grade 12 or lower
assert metrics.flesch_kincaid_grade <= 12

# Level AA: Grade 8 or lower
assert metrics.flesch_kincaid_grade <= 8

# Level AAA: Grade 6 or lower
assert metrics.flesch_kincaid_grade <= 6
```

**Plain Language Guidelines:**

| Aspect | Level A | Level AA | Level AAA |
|--------|---------|----------|-----------|
| Reading Grade | ≤ 12 | ≤ 8 | ≤ 6 |
| Sentence Length | ≤ 30 words | ≤ 20 words | ≤ 15 words |
| Complex Words | ≤ 20% | ≤ 15% | ≤ 10% |
| Jargon | Defined | Minimized | Avoided |
| Passive Voice | Allowed | Minimized | Avoided |

#### U2: Predictable

Interfaces must operate predictably.

| Level | Requirement |
|-------|-------------|
| A | No unexpected context changes |
| AA | Consistent navigation patterns |
| AAA | User-controlled all changes |

#### U3: Input Assistance

Help users avoid and correct mistakes.

```python
from src.accessibility import ErrorHandlingConfig

# Level A: Error identification
config_a = ErrorHandlingConfig(
    error_identification=True,
)

# Level AA: Error prevention and suggestions
config_aa = ErrorHandlingConfig(
    error_identification=True,
    error_prevention=True,
    error_suggestions=True,
)

# Level AAA: Full error support
config_aaa = ErrorHandlingConfig(
    error_identification=True,
    error_prevention=True,
    error_suggestions=True,
    undo_available=True,
    auto_save=True,
    recovery_options=True,
)
```

---

### Robust

#### R1: Compatible

Content must be compatible with assistive technologies.

```python
from src.accessibility import ARIALiveRegionGenerator

generator = ARIALiveRegionGenerator()

# All dynamic content must use ARIA live regions
html = generator.generate_live_region(
    response,
    politeness=ARIAPoliteness.POLITE,
)
```

#### R2: Screen Reader Support

Major screen readers must be supported.

| Screen Reader | Platform | Support Required |
|---------------|----------|-----------------|
| JAWS | Windows | Level A |
| NVDA | Windows | Level A |
| VoiceOver | macOS/iOS | Level A |
| TalkBack | Android | Level AA |
| Narrator | Windows | Level AA |
| Orca | Linux | Level AAA |

---

## Success Criteria

### Quick Reference

| Criterion | Level | Description |
|-----------|-------|-------------|
| 1.1.1 | A | Non-text alternatives |
| 1.2.1 | A | Audio-only alternatives |
| 1.3.1 | A | Information and relationships |
| 1.4.1 | A | Use of color |
| 2.1.1 | A | Keyboard accessible |
| 2.2.1 | A | Timing adjustable |
| 2.3.1 | A | Seizure safe |
| 2.4.1 | A | Skip to content |
| 3.1.1 | A | Language of content |
| 3.2.1 | A | On focus behavior |
| 3.3.1 | A | Error identification |
| 4.1.1 | A | ARIA compatibility |
| 1.2.4 | AA | Captions (live) |
| 1.4.3 | AA | Contrast minimum |
| 2.2.2 | AA | Pause, stop, hide |
| 2.4.5 | AA | Multiple ways |
| 3.1.2 | AA | Language of parts |
| 3.2.3 | AA | Consistent navigation |
| 3.3.3 | AA | Error suggestion |
| 1.2.6 | AAA | Sign language |
| 2.2.3 | AAA | No timing |
| 2.4.8 | AAA | Location |
| 3.1.5 | AAA | Reading level |
| 3.2.5 | AAA | Change on request |
| 3.3.6 | AAA | Error prevention (all) |

---

## Disability-Specific Requirements

### Visual Disabilities

```python
from src.accessibility import VisualAccessibilityEvaluator

evaluator = VisualAccessibilityEvaluator()
result = evaluator.evaluate(schema)

# Requirements:
# - Screen reader compatible
# - Text alternatives for all media
# - No information conveyed by color alone
# - Sufficient contrast ratios
```

### Hearing Disabilities

```python
from src.accessibility import HearingAccessibilityEvaluator

evaluator = HearingAccessibilityEvaluator()
result = evaluator.evaluate(schema)

# Requirements:
# - Captions for audio content
# - Transcripts available
# - Visual alternatives to audio cues
# - Sign language support (Level AAA)
```

### Motor Disabilities

```python
from src.accessibility import MotorAccessibilityEvaluator

evaluator = MotorAccessibilityEvaluator()
result = evaluator.evaluate(schema)

# Requirements:
# - Keyboard navigation
# - Sufficient time for input
# - Large click/touch targets
# - Switch access support
# - Voice input support
```

### Speech Disabilities

```python
from src.accessibility import SpeechAccessibilityEvaluator

evaluator = SpeechAccessibilityEvaluator()
result = evaluator.evaluate(schema)

# Requirements:
# - Text-based input alternatives
# - No voice-only functions
# - Multiple communication channels
```

### Cognitive Disabilities

```python
from src.accessibility import CognitiveAccessibilityEvaluator

evaluator = CognitiveAccessibilityEvaluator()
result = evaluator.evaluate(schema)

# Requirements:
# - Plain language
# - Clear structure
# - Consistent patterns
# - Error prevention
# - Memory aids
```

### Neurological Disabilities

```python
from src.accessibility import NeurologicalAccessibilityEvaluator

evaluator = NeurologicalAccessibilityEvaluator()
result = evaluator.evaluate(schema)

# Requirements:
# - No flashing content
# - Animation controls
# - Reduced motion support
# - No auto-play media
```

---

## Implementation Mapping

### Module to LUIAG Mapping

| LUIAG Area | Module | Primary Classes |
|------------|--------|-----------------|
| Readability | `readability` | `ReadabilityAnalyzer`, `SentenceAnalyzer` |
| Response Checking | `checker` | `LUIAccessibilityChecker` |
| Schema Validation | `schema_checker` | `SchemaAccessibilityChecker` |
| Plain Language | `jargon` | `JargonDetector` |
| Disability Coverage | `disability_evaluators` | `CombinedDisabilityEvaluator` |
| Timing | `timing` | `InteractionTimingValidator` |
| Seizure Safety | `seizure_safety` | `SeizureSafetyChecker` |
| Screen Readers | `aria` | `ARIALiveRegionGenerator` |
| Reporting | `report` | `AccessibilityReportGenerator` |

### Validation Workflow

```python
from src.accessibility import (
    SchemaAccessibilityChecker,
    CombinedDisabilityEvaluator,
    InteractionTimingValidator,
    SeizureSafetyChecker,
    AccessibilityReportGenerator,
    ComplianceLevel,
)

def validate_luiag_compliance(schema: dict, level: ComplianceLevel) -> bool:
    """Validate full LUIAG compliance."""

    # 1. Check schema structure and content
    schema_checker = SchemaAccessibilityChecker()
    schema_result = schema_checker.check_schema(schema, level)

    if not schema_result.passes:
        return False

    # 2. Check all disability types
    disability_evaluator = CombinedDisabilityEvaluator()
    disability_results = disability_evaluator.evaluate(schema)

    min_score = {
        ComplianceLevel.LEVEL_A: 0.5,
        ComplianceLevel.LEVEL_AA: 0.7,
        ComplianceLevel.LEVEL_AAA: 0.9,
    }

    for dtype, result in disability_results.items():
        if result.accommodation_score < min_score[level]:
            return False

    # 3. Check timing configuration
    if "timing" in schema:
        timing_validator = InteractionTimingValidator()
        # ... validate timing

    # 4. Check seizure safety
    if schema.get("has_animations") or schema.get("has_media"):
        safety_checker = SeizureSafetyChecker()
        # ... validate safety

    return True
```

---

## See Also

- [API.md](./API.md) - Complete API reference
- [GUIDE.md](./GUIDE.md) - Usage guide and examples
- [CHECKLIST.md](./CHECKLIST.md) - Implementation checklist
- [WCAG 2.1](https://www.w3.org/TR/WCAG21/) - Web Content Accessibility Guidelines
