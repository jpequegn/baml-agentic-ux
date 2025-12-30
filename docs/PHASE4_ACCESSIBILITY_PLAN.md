# Phase 4: LUI Accessibility Standards - Implementation Plan

## Executive Summary

This plan defines accessibility standards for Language User Interfaces (LUI) - the conversational equivalent of WCAG. Based on comprehensive research into WCAG 2.2 adaptations, cognitive accessibility, screen reader patterns, and disability-specific needs, this phase establishes testable criteria for making conversational AI accessible to all users.

**Total Estimated Effort**: 38-48 hours
**Primary Standard**: LUIAG (Language User Interface Accessibility Guidelines)
**Compliance Levels**: Level A (Minimum), Level AA (Standard), Level AAA (Enhanced)

---

## Research Summary

### Key Standards Analyzed

| Standard | Scope | Application to LUI |
|----------|-------|-------------------|
| **WCAG 2.2** | Web content | Response structure, timing, navigation |
| **EN 301 549** | EU ICT products | Hardware + software requirements |
| **Section 508** | US Federal | Functional performance criteria |
| **ISO 9241-171** | Software accessibility | Ergonomic principles |
| **AAG v0.1** | AI interfaces (proposed) | Dynamic content, pace control |

### Cognitive Load Thresholds

| Metric | Target | Standard |
|--------|--------|----------|
| Working memory items | ≤4 chunks | Modern cognitive research |
| Menu options | 5-7 items | Miller's Law |
| Quick reply buttons | 3-5 options | Progressive disclosure |
| Reading grade level | 6th-8th grade | Plain language |
| Sentence length (average) | 15-20 words | Plain Language guidelines |
| Sentence length (maximum) | 25 words | UK Government |
| Response latency | <1 second | User engagement |

### Disability-Specific Requirements

| Disability | Key Requirement | Success Metric |
|------------|-----------------|----------------|
| **Visual** | Audio-first feedback | 100% audio confirmation |
| **Hearing** | Text alternatives | 99% caption accuracy |
| **Motor** | Extended timeouts | ≥5x standard duration |
| **Speech** | Text input alternatives | 100% text fallback |
| **Cognitive** | Simple language | Grade 6-8 reading level |
| **Epilepsy** | Seizure-safe design | Zero flashes >3Hz |

---

## LUIAG Framework

### Compliance Levels

#### Level A - Minimum Accessibility
Essential requirements for basic usability by people with disabilities.

| Criterion | Requirement | Testable |
|-----------|-------------|----------|
| A.1.1 | All responses have text equivalent | Automated |
| A.1.2 | Screen reader compatible (ARIA live regions) | Automated |
| A.1.3 | Keyboard navigable conversation history | Automated |
| A.2.1 | Timeout adjustable (≥20s warning) | Automated |
| A.2.2 | Pause/stop for auto-updating content | Manual |
| A.3.1 | Consistent help access | Automated |
| A.3.2 | Error identification with suggestions | Manual |
| A.4.1 | Works with assistive technology | Manual |

#### Level AA - Standard Accessibility
Enhanced usability meeting most legal requirements.

| Criterion | Requirement | Testable |
|-----------|-------------|----------|
| AA.1.1 | 4.5:1 color contrast (text) | Automated |
| AA.1.2 | Touch targets ≥44×44px | Automated |
| AA.2.1 | Multiple input methods supported | Manual |
| AA.2.2 | No timing-essential interactions | Manual |
| AA.3.1 | Reading level ≤ grade 8 | Automated |
| AA.3.2 | Jargon defined on first use | Manual |
| AA.3.3 | Consistent vocabulary | Manual |
| AA.4.1 | Status messages announced | Automated |

#### Level AAA - Enhanced Accessibility
Maximum inclusivity for diverse needs.

| Criterion | Requirement | Testable |
|-----------|-------------|----------|
| AAA.1.1 | 7:1 color contrast | Automated |
| AAA.1.2 | Sign language for audio/video | Manual |
| AAA.2.1 | No timing constraints | Manual |
| AAA.2.2 | Extended timeout (10x default) | Automated |
| AAA.3.1 | Reading level ≤ grade 6 | Automated |
| AAA.3.2 | Sentence length ≤ 20 words | Automated |
| AAA.3.3 | One concept per response | Manual |
| AAA.4.1 | Multi-modal output (text + audio + visual) | Manual |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                  LUI Accessibility Layer                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │ Accessibility │  │  Response    │  │   Interaction        │  │
│  │    Config     │  │  Analyzer    │  │   Accommodations     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
│         └─────────────────┼──────────────────────┘              │
│                           │                                      │
│                    ┌──────▼───────┐                             │
│                    │  Compliance   │                             │
│                    │   Checker     │                             │
│                    └──────┬───────┘                             │
│                           │                                      │
├───────────────────────────┼─────────────────────────────────────┤
│                           │                                      │
│  ┌────────────────────────▼────────────────────────────────┐   │
│  │              Existing LUI Framework                      │   │
│  │  (InterfaceSchema, Components, Intent, Response)        │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## BAML Type Definitions

### Core Accessibility Configuration

```baml
// Accessibility configuration for LUI schemas
class AccessibilityConfig {
  compliance_level ComplianceLevel
  response_constraints ResponseConstraints
  interaction_constraints InteractionConstraints
  cognitive_constraints CognitiveConstraints
  disability_accommodations DisabilityAccommodations
}

enum ComplianceLevel {
  LEVEL_A       // Minimum accessibility
  LEVEL_AA      // Standard (recommended)
  LEVEL_AAA     // Enhanced accessibility
}

class ResponseConstraints {
  max_sentence_length int @description("Maximum words per sentence")
  max_sentences_per_response int @description("Maximum sentences per response")
  max_reading_level ReadingLevel
  require_audio_equivalent bool
  require_text_equivalent bool
}

enum ReadingLevel {
  GRADE_5       // Simple (Flesch-Kincaid 90-100)
  GRADE_6       // Easy (Flesch-Kincaid 80-90)
  GRADE_8       // Standard (Flesch-Kincaid 60-70)
  GRADE_10      // Moderate (Flesch-Kincaid 50-60)
  GRADE_12      // Advanced (Flesch-Kincaid 30-50)
  UNRESTRICTED  // No limit
}

class InteractionConstraints {
  min_timeout_seconds int @description("Minimum before timeout warning")
  timeout_extension_factor float @description("Multiplier for extending timeout")
  supports_undo bool
  supports_repeat bool
  supports_pace_control bool
  supports_restart bool
  max_choices_at_once int @description("Maximum quick reply options")
}

class CognitiveConstraints {
  max_concepts_per_response int @description("Cognitive load limit")
  require_progressive_disclosure bool
  require_consistent_vocabulary bool
  require_jargon_definitions bool
  max_working_memory_items int @description("Miller's Law: 4±1")
}

class DisabilityAccommodations {
  visual VisualAccommodations
  hearing HearingAccommodations
  motor MotorAccommodations
  speech SpeechAccommodations
  cognitive CognitiveAccommodations
  neurological NeurologicalAccommodations
}
```

### Disability-Specific Accommodations

```baml
class VisualAccommodations {
  audio_first_design bool @description("All actions have audio feedback")
  screen_reader_optimized bool @description("ARIA live regions configured")
  high_contrast_support bool
  no_visual_only_information bool @description("No dead-end prompts")
}

class HearingAccommodations {
  text_alternatives_required bool @description("All audio has text")
  real_time_captions bool
  visual_alerts_for_audio bool @description("Visual equivalent for sounds")
  sign_language_available bool
}

class MotorAccommodations {
  extended_timeouts bool @description("5x or greater timeout")
  single_action_interactions bool @description("No multi-touch required")
  large_touch_targets bool @description("≥44×44px minimum")
  voice_input_support bool
  switch_access_compatible bool
  eye_tracking_compatible bool
}

class SpeechAccommodations {
  text_input_alternative bool @description("100% text fallback")
  custom_voice_profile_support bool
  gesture_input_support bool
  aac_device_compatible bool @description("AAC device support")
}

class CognitiveAccommodations {
  simple_language bool @description("Grade 6-8 reading level")
  consistent_navigation bool @description("Same actions in same places")
  clear_error_messages bool
  progress_indicators bool @description("Multi-step progress shown")
  undo_support bool @description("All actions reversible")
  auto_save bool @description("Never lose user input")
}

class NeurologicalAccommodations {
  seizure_safe bool @description("No flashes >3Hz")
  no_auto_play_media bool
  animation_controls bool @description("Pause/stop all motion")
  reduced_motion_support bool
  dark_mode_available bool
}
```

### Response Accessibility Analysis

```baml
class ResponseAccessibilityAnalysis {
  response_text string
  compliance_level ComplianceLevel
  passes bool
  violations AccessibilityViolation[]
  metrics ResponseMetrics
  suggestions AccessibilitySuggestion[]
}

class AccessibilityViolation {
  criterion string @description("e.g., AA.3.1")
  severity ViolationSeverity
  description string
  location string? @description("Where in response")
  remediation string
}

enum ViolationSeverity {
  CRITICAL    // Blocks accessibility
  MAJOR       // Significantly impacts usability
  MINOR       // Reduces usability
  ADVISORY    // Improvement suggestion
}

class ResponseMetrics {
  word_count int
  sentence_count int
  average_sentence_length float
  max_sentence_length int
  flesch_kincaid_grade float
  flesch_reading_ease float
  smog_grade float?
  concepts_count int
  jargon_terms string[]
  has_text_equivalent bool
  has_audio_equivalent bool
}

class AccessibilitySuggestion {
  criterion string
  current_value string
  suggested_value string
  impact string
  effort EffortLevel
}

enum EffortLevel {
  LOW
  MEDIUM
  HIGH
}
```

### Interaction Accessibility

```baml
class InteractionAccessibilityConfig {
  component_id string
  timing TimeoutConfig
  input_methods InputMethodConfig
  feedback FeedbackConfig
  error_handling ErrorHandlingConfig
}

class TimeoutConfig {
  initial_timeout_seconds int
  warning_before_seconds int @description("Show warning this many seconds before")
  extension_allowed bool
  extension_seconds int
  max_extensions int
}

class InputMethodConfig {
  keyboard_accessible bool
  voice_input bool
  touch_input bool
  switch_access bool
  eye_tracking bool
  mouse_input bool
}

class FeedbackConfig {
  visual_feedback bool
  audio_feedback bool
  haptic_feedback bool
  confirmation_required_for string[] @description("Action types requiring confirmation")
}

class ErrorHandlingConfig {
  clear_error_messages bool
  error_suggestions bool
  undo_available bool
  restart_available bool
  human_handoff_available bool
}
```

---

## BAML Functions

### Response Accessibility Analysis

```baml
function AnalyzeResponseAccessibility(
  response: string,
  config: AccessibilityConfig
) -> ResponseAccessibilityAnalysis {
  client GPT4o
  prompt #"
    Analyze the accessibility of this LUI response.

    Response Text:
    {{ response }}

    Accessibility Configuration:
    {{ config }}

    Evaluate against LUIAG criteria for compliance level {{ config.compliance_level }}:

    1. **Reading Level Analysis**
       - Calculate Flesch-Kincaid grade level
       - Check against max_reading_level threshold
       - Identify complex sentences

    2. **Cognitive Load Assessment**
       - Count distinct concepts
       - Check against max_concepts_per_response
       - Identify jargon terms

    3. **Sentence Structure**
       - Measure sentence lengths
       - Check against limits
       - Identify run-on sentences

    4. **Consistency Check**
       - Verify vocabulary consistency
       - Check for undefined jargon
       - Assess predictability

    For each violation found:
    - Cite the specific criterion
    - Assess severity
    - Provide remediation guidance

    {{ ctx.output_format }}
  "#
}

function SimplifyResponse(
  response: string,
  target_level: ReadingLevel,
  max_sentence_length: int
) -> SimplifiedResponse {
  client GPT4o
  prompt #"
    Simplify this response to meet accessibility requirements.

    Original Response:
    {{ response }}

    Target Reading Level: {{ target_level }}
    Maximum Sentence Length: {{ max_sentence_length }} words

    Guidelines:
    1. Use plain language (no jargon, or define it)
    2. One idea per sentence
    3. Active voice preferred
    4. Concrete rather than abstract language
    5. Break complex concepts into steps

    Preserve the meaning while making it accessible.

    {{ ctx.output_format }}
  "#
}

class SimplifiedResponse {
  original_text string
  simplified_text string
  changes_made string[]
  original_metrics ResponseMetrics
  new_metrics ResponseMetrics
  improvement_summary string
}
```

### Schema Accessibility Evaluation

```baml
function EvaluateLUIAccessibility(
  schema: InterfaceSchema,
  target_level: ComplianceLevel
) -> LUIAccessibilityEvaluation {
  client GPT4o
  prompt #"
    Evaluate this LUI schema for accessibility compliance.

    Schema:
    {{ schema }}

    Target Compliance Level: {{ target_level }}

    Evaluate each component against LUIAG criteria:

    **Level A Requirements:**
    - Text equivalents for all content
    - Screen reader compatibility
    - Keyboard navigation
    - Adjustable timing
    - Consistent help access
    - Error identification

    **Level AA Requirements (if applicable):**
    - Color contrast 4.5:1
    - Touch targets 44×44px
    - Multiple input methods
    - Reading level ≤ grade 8
    - Defined jargon
    - Status message announcements

    **Level AAA Requirements (if applicable):**
    - Color contrast 7:1
    - Sign language availability
    - No timing constraints
    - Reading level ≤ grade 6
    - One concept per response

    For each component:
    1. List passing criteria
    2. List violations with severity
    3. Provide remediation suggestions

    {{ ctx.output_format }}
  "#
}

class LUIAccessibilityEvaluation {
  schema_name string
  target_level ComplianceLevel
  achieved_level ComplianceLevel
  overall_score float @description("0.0-1.0")
  component_evaluations ComponentAccessibilityEval[]
  summary AccessibilitySummary
}

class ComponentAccessibilityEval {
  component_id string
  component_type string
  passes_target bool
  achieved_level ComplianceLevel
  violations AccessibilityViolation[]
  passing_criteria string[]
}

class AccessibilitySummary {
  total_components int
  passing_components int
  critical_violations int
  major_violations int
  minor_violations int
  top_issues string[]
  remediation_priority string[]
}
```

### Disability-Specific Evaluation

```baml
function EvaluateForDisability(
  schema: InterfaceSchema,
  disability_type: DisabilityType
) -> DisabilityEvaluation {
  client GPT4o
  prompt #"
    Evaluate this LUI schema for users with {{ disability_type }}.

    Schema:
    {{ schema }}

    Evaluate based on disability-specific needs:

    {% if disability_type == "VISUAL" %}
    - Audio-first design: Do all actions have audio feedback?
    - No dead-end prompts: Are there any visual-only responses?
    - Screen reader optimization: Are ARIA live regions configured?
    - High contrast support: Is there a high contrast mode?
    {% endif %}

    {% if disability_type == "HEARING" %}
    - Text alternatives: Does all audio have text equivalents?
    - Visual alerts: Are there visual alternatives for audio cues?
    - Real-time captions: Are captions available for live content?
    {% endif %}

    {% if disability_type == "MOTOR" %}
    - Extended timeouts: Are timeouts ≥5x standard?
    - Single-action interactions: Are there no multi-touch requirements?
    - Large touch targets: Are targets ≥44×44px?
    - Voice input: Is voice input supported?
    {% endif %}

    {% if disability_type == "COGNITIVE" %}
    - Simple language: Is reading level ≤ grade 8?
    - Consistent navigation: Are actions in predictable locations?
    - Progress indicators: Is progress shown for multi-step tasks?
    - Undo support: Are all actions reversible?
    {% endif %}

    {{ ctx.output_format }}
  "#
}

enum DisabilityType {
  VISUAL
  HEARING
  MOTOR
  SPEECH
  COGNITIVE
  NEUROLOGICAL
}

class DisabilityEvaluation {
  disability_type DisabilityType
  accommodation_score float @description("0.0-1.0")
  barriers BarrierAnalysis[]
  accommodations_present string[]
  accommodations_missing string[]
  recommendations string[]
}

class BarrierAnalysis {
  barrier_type string
  severity ViolationSeverity
  affected_components string[]
  description string
  impact_on_user string
  remediation string
}
```

---

## Python Implementation

### Readability Calculator

```python
# src/accessibility/readability.py

import re
import math
from dataclasses import dataclass
from typing import Optional

@dataclass
class ReadabilityMetrics:
    word_count: int
    sentence_count: int
    syllable_count: int
    average_sentence_length: float
    average_syllables_per_word: float
    flesch_reading_ease: float
    flesch_kincaid_grade: float
    smog_grade: Optional[float]

    @property
    def reading_level(self) -> str:
        """Convert Flesch-Kincaid grade to ReadingLevel enum."""
        if self.flesch_kincaid_grade <= 5:
            return "GRADE_5"
        elif self.flesch_kincaid_grade <= 6:
            return "GRADE_6"
        elif self.flesch_kincaid_grade <= 8:
            return "GRADE_8"
        elif self.flesch_kincaid_grade <= 10:
            return "GRADE_10"
        elif self.flesch_kincaid_grade <= 12:
            return "GRADE_12"
        else:
            return "UNRESTRICTED"


class ReadabilityAnalyzer:
    """
    Analyzes text readability using standard formulas.
    """

    # Common syllable patterns
    VOWELS = "aeiouy"
    SILENT_E_PATTERN = re.compile(r"[aeiou]e$", re.IGNORECASE)

    def analyze(self, text: str) -> ReadabilityMetrics:
        """Calculate readability metrics for text."""
        sentences = self._count_sentences(text)
        words = self._count_words(text)
        syllables = self._count_syllables(text)

        if sentences == 0 or words == 0:
            return ReadabilityMetrics(
                word_count=0,
                sentence_count=0,
                syllable_count=0,
                average_sentence_length=0.0,
                average_syllables_per_word=0.0,
                flesch_reading_ease=100.0,
                flesch_kincaid_grade=0.0,
                smog_grade=None
            )

        asl = words / sentences  # Average sentence length
        asw = syllables / words  # Average syllables per word

        # Flesch Reading Ease: 206.835 - 1.015(ASL) - 84.6(ASW)
        flesch_ease = 206.835 - (1.015 * asl) - (84.6 * asw)
        flesch_ease = max(0, min(100, flesch_ease))  # Clamp to 0-100

        # Flesch-Kincaid Grade: 0.39(ASL) + 11.8(ASW) - 15.59
        flesch_grade = (0.39 * asl) + (11.8 * asw) - 15.59
        flesch_grade = max(0, flesch_grade)  # No negative grades

        # SMOG Grade (requires 30+ sentences for accuracy)
        smog = None
        if sentences >= 30:
            polysyllables = self._count_polysyllables(text)
            smog = 1.0430 * math.sqrt(polysyllables * (30 / sentences)) + 3.1291

        return ReadabilityMetrics(
            word_count=words,
            sentence_count=sentences,
            syllable_count=syllables,
            average_sentence_length=asl,
            average_syllables_per_word=asw,
            flesch_reading_ease=round(flesch_ease, 2),
            flesch_kincaid_grade=round(flesch_grade, 2),
            smog_grade=round(smog, 2) if smog else None
        )

    def _count_sentences(self, text: str) -> int:
        """Count sentences using terminal punctuation."""
        # Match sentence-ending punctuation
        pattern = r'[.!?]+(?:\s|$)'
        matches = re.findall(pattern, text)
        return max(1, len(matches))  # At least 1 sentence

    def _count_words(self, text: str) -> int:
        """Count words (alphabetic sequences)."""
        words = re.findall(r'\b[a-zA-Z]+\b', text)
        return len(words)

    def _count_syllables(self, text: str) -> int:
        """Count syllables using vowel groups."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        total = 0
        for word in words:
            total += self._syllables_in_word(word)
        return total

    def _syllables_in_word(self, word: str) -> int:
        """Count syllables in a single word."""
        word = word.lower()

        # Handle special cases
        if len(word) <= 2:
            return 1

        # Count vowel groups
        count = 0
        prev_vowel = False

        for char in word:
            is_vowel = char in self.VOWELS
            if is_vowel and not prev_vowel:
                count += 1
            prev_vowel = is_vowel

        # Subtract silent e
        if word.endswith('e') and count > 1:
            if not self.SILENT_E_PATTERN.search(word):
                count -= 1

        # Words like "le" at end add syllable
        if word.endswith('le') and len(word) > 2 and word[-3] not in self.VOWELS:
            count += 1

        return max(1, count)

    def _count_polysyllables(self, text: str) -> int:
        """Count words with 3+ syllables (for SMOG)."""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return sum(1 for word in words if self._syllables_in_word(word) >= 3)


class SentenceAnalyzer:
    """
    Analyzes sentence structure for accessibility.
    """

    def analyze_sentences(self, text: str) -> list[dict]:
        """Analyze each sentence in the text."""
        sentences = self._split_sentences(text)
        results = []

        for i, sentence in enumerate(sentences):
            words = len(re.findall(r'\b\w+\b', sentence))
            results.append({
                'index': i,
                'text': sentence.strip(),
                'word_count': words,
                'exceeds_limit': words > 25,  # UK Government limit
                'recommendation': self._recommend(words)
            })

        return results

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Simple sentence splitting
        pattern = r'(?<=[.!?])\s+'
        return re.split(pattern, text)

    def _recommend(self, word_count: int) -> str:
        """Provide recommendation based on sentence length."""
        if word_count <= 15:
            return "Excellent - easy to read"
        elif word_count <= 20:
            return "Good - accessible"
        elif word_count <= 25:
            return "Acceptable - at limit"
        elif word_count <= 35:
            return "Split recommended - difficult to process"
        else:
            return "Must split - inaccessible"
```

### Accessibility Checker

```python
# src/accessibility/checker.py

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class ComplianceLevel(Enum):
    LEVEL_A = "A"
    LEVEL_AA = "AA"
    LEVEL_AAA = "AAA"

class ViolationSeverity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    ADVISORY = "advisory"

@dataclass
class AccessibilityViolation:
    criterion: str
    severity: ViolationSeverity
    description: str
    location: Optional[str] = None
    remediation: str = ""

@dataclass
class AccessibilityCheckResult:
    passes: bool
    level: ComplianceLevel
    achieved_level: Optional[ComplianceLevel]
    violations: list[AccessibilityViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: float = 0.0


class LUIAccessibilityChecker:
    """
    Checks LUI responses and schemas against LUIAG criteria.
    """

    # Threshold configurations by level
    THRESHOLDS = {
        ComplianceLevel.LEVEL_A: {
            'max_reading_grade': 12.0,
            'max_sentence_length': 35,
            'min_timeout_seconds': 20,
            'require_text_equivalent': True,
        },
        ComplianceLevel.LEVEL_AA: {
            'max_reading_grade': 8.0,
            'max_sentence_length': 25,
            'min_timeout_seconds': 30,
            'require_text_equivalent': True,
            'require_consistent_vocabulary': True,
        },
        ComplianceLevel.LEVEL_AAA: {
            'max_reading_grade': 6.0,
            'max_sentence_length': 20,
            'min_timeout_seconds': 60,
            'require_text_equivalent': True,
            'require_audio_equivalent': True,
            'max_concepts_per_response': 1,
        }
    }

    def __init__(self):
        self.readability = ReadabilityAnalyzer()
        self.sentence_analyzer = SentenceAnalyzer()

    def check_response(
        self,
        response: str,
        target_level: ComplianceLevel = ComplianceLevel.LEVEL_AA
    ) -> AccessibilityCheckResult:
        """Check a response against accessibility criteria."""
        violations = []
        thresholds = self.THRESHOLDS[target_level]

        # Readability check
        metrics = self.readability.analyze(response)

        if metrics.flesch_kincaid_grade > thresholds['max_reading_grade']:
            violations.append(AccessibilityViolation(
                criterion=f"{target_level.value}.3.1",
                severity=ViolationSeverity.MAJOR,
                description=f"Reading level {metrics.flesch_kincaid_grade:.1f} exceeds maximum {thresholds['max_reading_grade']}",
                remediation="Simplify vocabulary and sentence structure"
            ))

        # Sentence length check
        sentences = self.sentence_analyzer.analyze_sentences(response)
        max_len = thresholds['max_sentence_length']

        for sent in sentences:
            if sent['word_count'] > max_len:
                violations.append(AccessibilityViolation(
                    criterion=f"{target_level.value}.3.2",
                    severity=ViolationSeverity.MINOR,
                    description=f"Sentence {sent['index']+1} has {sent['word_count']} words (max: {max_len})",
                    location=sent['text'][:50] + "...",
                    remediation="Split into shorter sentences"
                ))

        # Determine achieved level
        achieved = self._determine_achieved_level(violations)

        # Calculate score
        score = self._calculate_score(violations, target_level)

        passes = len([v for v in violations
                     if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]]) == 0

        return AccessibilityCheckResult(
            passes=passes,
            level=target_level,
            achieved_level=achieved,
            violations=violations,
            score=score
        )

    def _determine_achieved_level(
        self,
        violations: list[AccessibilityViolation]
    ) -> Optional[ComplianceLevel]:
        """Determine what level is actually achieved."""
        critical_major = [v for v in violations
                        if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]]

        if len(critical_major) == 0:
            return ComplianceLevel.LEVEL_AAA

        # Check which level's criteria are violated
        aaa_violations = [v for v in critical_major if v.criterion.startswith("AAA")]
        aa_violations = [v for v in critical_major if v.criterion.startswith("AA")]
        a_violations = [v for v in critical_major if v.criterion.startswith("A.")]

        if a_violations:
            return None  # Doesn't meet minimum
        if aa_violations:
            return ComplianceLevel.LEVEL_A
        if aaa_violations:
            return ComplianceLevel.LEVEL_AA

        return ComplianceLevel.LEVEL_AAA

    def _calculate_score(
        self,
        violations: list[AccessibilityViolation],
        level: ComplianceLevel
    ) -> float:
        """Calculate accessibility score 0.0-1.0."""
        if not violations:
            return 1.0

        # Weight by severity
        weights = {
            ViolationSeverity.CRITICAL: 0.25,
            ViolationSeverity.MAJOR: 0.15,
            ViolationSeverity.MINOR: 0.05,
            ViolationSeverity.ADVISORY: 0.02,
        }

        total_penalty = sum(weights[v.severity] for v in violations)
        return max(0.0, 1.0 - total_penalty)


class SchemaAccessibilityChecker:
    """
    Checks LUI schemas for accessibility compliance.
    """

    def check_schema(
        self,
        schema: dict,
        target_level: ComplianceLevel
    ) -> AccessibilityCheckResult:
        """Check schema structure for accessibility."""
        violations = []

        # Check for required accessibility config
        if 'accessibility_config' not in schema:
            violations.append(AccessibilityViolation(
                criterion="A.1.1",
                severity=ViolationSeverity.MAJOR,
                description="Schema missing accessibility configuration",
                remediation="Add AccessibilityConfig to schema"
            ))

        # Check each component
        for component in schema.get('components', []):
            component_violations = self._check_component(component, target_level)
            violations.extend(component_violations)

        # Check feedback templates
        for component in schema.get('components', []):
            if 'feedback' in component:
                feedback_violations = self._check_feedback(
                    component['feedback'],
                    component.get('component_id', 'unknown'),
                    target_level
                )
                violations.extend(feedback_violations)

        achieved = self._determine_achieved_level(violations)
        passes = len([v for v in violations
                     if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]]) == 0

        return AccessibilityCheckResult(
            passes=passes,
            level=target_level,
            achieved_level=achieved,
            violations=violations,
            score=self._calculate_score(violations)
        )

    def _check_component(
        self,
        component: dict,
        level: ComplianceLevel
    ) -> list[AccessibilityViolation]:
        """Check a single component for accessibility."""
        violations = []
        component_id = component.get('component_id', 'unknown')

        # Check for confirmation on destructive actions
        if component.get('component_type') == 'ACTION':
            feedback = component.get('feedback', {})
            if not feedback.get('confirmation_required'):
                violations.append(AccessibilityViolation(
                    criterion="A.3.2",
                    severity=ViolationSeverity.ADVISORY,
                    description=f"Component {component_id}: Consider confirmation for actions",
                    remediation="Add confirmation_required for destructive actions"
                ))

        return violations

    def _check_feedback(
        self,
        feedback: dict,
        component_id: str,
        level: ComplianceLevel
    ) -> list[AccessibilityViolation]:
        """Check feedback templates for accessibility."""
        violations = []
        response_checker = LUIAccessibilityChecker()

        # Check success template
        if 'success_template' in feedback:
            result = response_checker.check_response(
                feedback['success_template'],
                level
            )
            for v in result.violations:
                v.location = f"{component_id}.feedback.success_template"
                violations.append(v)

        # Check error template
        if 'error_template' in feedback:
            result = response_checker.check_response(
                feedback['error_template'],
                level
            )
            for v in result.violations:
                v.location = f"{component_id}.feedback.error_template"
                violations.append(v)

        return violations
```

### Jargon Detector

```python
# src/accessibility/jargon.py

from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class JargonTerm:
    term: str
    context: str
    definition: Optional[str] = None
    simple_alternative: Optional[str] = None

class JargonDetector:
    """
    Detects technical jargon and suggests plain language alternatives.
    """

    # Common technical jargon with alternatives
    JARGON_DATABASE = {
        'authenticate': ('verify your identity', 'log in'),
        'authorization': ('permission', 'approval'),
        'bandwidth': ('capacity', 'speed'),
        'deprecated': ('outdated', 'old'),
        'endpoint': ('connection point', 'address'),
        'instantiate': ('create', 'make'),
        'leverage': ('use', 'apply'),
        'optimize': ('improve', 'make better'),
        'parameter': ('setting', 'option'),
        'parse': ('read', 'process'),
        'payload': ('data', 'content'),
        'propagate': ('spread', 'send'),
        'protocol': ('rules', 'method'),
        'query': ('search', 'question'),
        'schema': ('structure', 'format'),
        'synchronize': ('match', 'update'),
        'utilize': ('use', 'apply'),
        'validate': ('check', 'verify'),
    }

    def detect(self, text: str) -> list[JargonTerm]:
        """Find jargon terms in text."""
        found = []
        words = re.findall(r'\b\w+\b', text.lower())

        for word in words:
            if word in self.JARGON_DATABASE:
                alternatives = self.JARGON_DATABASE[word]
                found.append(JargonTerm(
                    term=word,
                    context=self._get_context(text, word),
                    simple_alternative=alternatives[0]
                ))

        return found

    def _get_context(self, text: str, word: str) -> str:
        """Get surrounding context for a word."""
        pattern = rf'\b(\w+\s+)?{word}(\s+\w+)?\b'
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0)
        return word

    def suggest_replacements(self, text: str) -> str:
        """Return text with jargon replaced by plain language."""
        result = text
        for term, alternatives in self.JARGON_DATABASE.items():
            pattern = rf'\b{term}\b'
            result = re.sub(pattern, alternatives[0], result, flags=re.IGNORECASE)
        return result
```

---

## Task Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 4.1 | Accessibility Config Types | 3-4h | None |
| 4.2 | Readability Analysis Engine | 4-5h | 4.1 |
| 4.3 | Response Accessibility Checker | 4-5h | 4.2 |
| 4.4 | Schema Accessibility Evaluator | 4-5h | 4.3 |
| 4.5 | Jargon Detection & Simplification | 3-4h | 4.2 |
| 4.6 | Disability-Specific Evaluators | 5-6h | 4.4 |
| 4.7 | Interaction Timing Validator | 3-4h | 4.1 |
| 4.8 | Seizure Safety Checker | 2-3h | None |
| 4.9 | ARIA Live Region Generator | 3-4h | 4.1 |
| 4.10 | Accessibility Report Generator | 4-5h | All |
| 4.11 | Testing & Documentation | 4-5h | All |

**Total Estimated Effort**: 38-48 hours

---

## Success Criteria

- [ ] LUIAG compliance levels defined (A/AA/AAA)
- [ ] Automated readability scoring (Flesch-Kincaid)
- [ ] Jargon detection with plain language suggestions
- [ ] Response accessibility checker functional
- [ ] Schema-level accessibility evaluation
- [ ] Disability-specific evaluation for all categories
- [ ] Seizure safety validation
- [ ] ≥80% automated testing coverage
- [ ] Documentation includes all criteria definitions

---

## Testing Strategy

### Automated Tests

```python
# tests/test_accessibility/

# Readability tests
def test_flesch_kincaid_simple_text():
    """Simple text should score grade 5 or below."""

def test_flesch_kincaid_complex_text():
    """Complex text should score appropriately."""

def test_sentence_length_detection():
    """Long sentences should be flagged."""

# Compliance tests
def test_level_a_compliance():
    """Test Level A requirements."""

def test_level_aa_compliance():
    """Test Level AA requirements."""

def test_level_aaa_compliance():
    """Test Level AAA requirements."""

# Jargon tests
def test_jargon_detection():
    """Technical terms should be identified."""

def test_jargon_replacement():
    """Jargon should be replaceable with plain language."""

# Disability-specific tests
def test_visual_accessibility():
    """Test audio-first design requirements."""

def test_hearing_accessibility():
    """Test text alternative requirements."""

def test_motor_accessibility():
    """Test timeout and target size requirements."""

def test_cognitive_accessibility():
    """Test reading level and consistency requirements."""
```

### Manual Testing Protocol

1. **Screen Reader Testing**
   - JAWS + Chrome (Windows)
   - NVDA + Firefox (Windows)
   - VoiceOver + Safari (macOS/iOS)
   - TalkBack (Android)

2. **Voice Control Testing**
   - Dragon NaturallySpeaking
   - Windows Speech Recognition
   - macOS Voice Control

3. **User Testing**
   - Recruit participants with diverse disabilities
   - Task completion scenarios
   - Satisfaction surveys

---

## References

- [WCAG 2.2 Specification](https://www.w3.org/TR/WCAG22/)
- [EN 301 549](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/)
- [Section 508 Standards](https://www.access-board.gov/)
- [Plain Language Guidelines](https://plainlanguage.gov/)
- [UK GOV.UK Content Design](https://www.gov.uk/guidance/content-design)
- [Flesch-Kincaid Formula](https://en.wikipedia.org/wiki/Flesch–Kincaid_readability_tests)
- [PEAT (Photosensitive Epilepsy Analysis Tool)](https://trace.umd.edu/peat)

---

*Generated as part of the baml-agentic-ux research project, December 2024*
