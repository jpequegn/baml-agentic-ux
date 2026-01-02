"""Response-level accessibility checker for LUI applications.

This module implements the LUIAG (Language User Interface Accessibility Guidelines)
compliance checker that validates LUI responses against accessibility criteria.

Issue #69 - Task 4.3: Response Accessibility Checker
Part of #27 - Phase 4: LUI Accessibility Standards
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

from .readability import ReadabilityAnalyzer, ReadabilityMetrics, SentenceAnalyzer


# ============================================
# Enums
# ============================================


class ComplianceLevel(Enum):
    """LUIAG conformance levels (aligned with WCAG structure)."""

    LEVEL_A = "A"  # Minimum accessibility - essential requirements
    LEVEL_AA = "AA"  # Standard accessibility - recommended for most
    LEVEL_AAA = "AAA"  # Enhanced accessibility - highest conformance


class ViolationSeverity(Enum):
    """Severity levels for accessibility violations."""

    CRITICAL = "critical"  # Blocks accessibility (weight: 0.25)
    MAJOR = "major"  # Significant impact (weight: 0.15)
    MINOR = "minor"  # Reduces usability (weight: 0.05)
    ADVISORY = "advisory"  # Suggestions (weight: 0.02)


# ============================================
# Constants
# ============================================

# Severity weights for scoring
SEVERITY_WEIGHTS = {
    ViolationSeverity.CRITICAL: 0.25,
    ViolationSeverity.MAJOR: 0.15,
    ViolationSeverity.MINOR: 0.05,
    ViolationSeverity.ADVISORY: 0.02,
}

# Thresholds by compliance level
LEVEL_THRESHOLDS = {
    ComplianceLevel.LEVEL_A: {
        "max_grade": 12.0,
        "max_sentence_words": 35,
        "min_timeout_seconds": 20,
        "max_flesch_kincaid": 12.0,
        "min_flesch_reading_ease": 30.0,
    },
    ComplianceLevel.LEVEL_AA: {
        "max_grade": 8.0,
        "max_sentence_words": 25,
        "min_timeout_seconds": 30,
        "max_flesch_kincaid": 8.0,
        "min_flesch_reading_ease": 60.0,
    },
    ComplianceLevel.LEVEL_AAA: {
        "max_grade": 6.0,
        "max_sentence_words": 20,
        "min_timeout_seconds": 60,
        "max_flesch_kincaid": 6.0,
        "min_flesch_reading_ease": 70.0,
    },
}

# Common problematic patterns
COMPLEX_WORDS_PATTERNS = [
    r"\b(utilize|utilization)\b",
    r"\b(necessitate|necessitates|necessitated)\b",
    r"\b(implementation|implementations)\b",
    r"\b(functionality|functionalities)\b",
    r"\b(methodology|methodologies)\b",
    r"\b(authorization|authenticate|authentication)\b",
    r"\b(verification|verification)\b",
    r"\b(subsequently|consequently|furthermore|moreover)\b",
    r"\b(notwithstanding|aforementioned|hereinafter)\b",
    r"\b(prerequisite|prerequisites)\b",
]

SIMPLE_ALTERNATIVES = {
    "utilize": "use",
    "utilization": "use",
    "necessitate": "need",
    "necessitates": "needs",
    "implementation": "setup",
    "functionality": "feature",
    "methodology": "method",
    "authorization": "approval",
    "authentication": "login",
    "verification": "check",
    "subsequently": "then",
    "consequently": "so",
    "furthermore": "also",
    "moreover": "also",
    "notwithstanding": "despite",
    "aforementioned": "this",
    "prerequisite": "requirement",
}

# Passive voice patterns
PASSIVE_VOICE_PATTERNS = [
    r"\b(is|are|was|were|been|being)\s+\w+ed\b",
    r"\b(has|have|had)\s+been\s+\w+ed\b",
]

# Jargon and technical terms that may need definitions
TECHNICAL_JARGON = [
    r"\bAPI\b", r"\bSDK\b", r"\bUI\b", r"\bUX\b",
    r"\b(backend|front-end|frontend)\b",
    r"\b(cache|caching)\b",
    r"\b(async|asynchronous|synchronous)\b",
    r"\b(deprecated)\b",
    r"\b(endpoint|endpoints)\b",
    r"\b(token|tokens)\b",
]


# ============================================
# Data Classes
# ============================================


@dataclass
class AccessibilityViolation:
    """A single accessibility violation found in the response."""

    criterion: str  # e.g., "A.1.1", "AA.3.1"
    severity: ViolationSeverity
    description: str
    remediation: str
    element: Optional[str] = None  # Specific text that caused the violation
    line_number: Optional[int] = None  # If applicable

    @property
    def weight(self) -> float:
        """Get the scoring weight for this violation's severity."""
        return SEVERITY_WEIGHTS.get(self.severity, 0.05)


@dataclass
class AccessibilityCheckResult:
    """Complete result of an accessibility check."""

    passes: bool  # Overall pass/fail
    level: ComplianceLevel  # Target level
    achieved_level: Optional[ComplianceLevel]  # What was achieved
    violations: list[AccessibilityViolation]
    score: float  # 0.0-1.0 accessibility score
    readability_metrics: Optional[ReadabilityMetrics] = None
    summary: str = ""
    recommendations: list[str] = field(default_factory=list)

    @property
    def critical_count(self) -> int:
        """Count of critical violations."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.CRITICAL)

    @property
    def major_count(self) -> int:
        """Count of major violations."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.MAJOR)

    @property
    def minor_count(self) -> int:
        """Count of minor violations."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.MINOR)

    @property
    def advisory_count(self) -> int:
        """Count of advisory notices."""
        return sum(1 for v in self.violations if v.severity == ViolationSeverity.ADVISORY)


# ============================================
# Main Checker Class
# ============================================


class LUIAccessibilityChecker:
    """Checks LUI responses against LUIAG criteria.

    This checker validates text responses against accessibility requirements
    for different compliance levels (A, AA, AAA) based on:
    - Reading level (Flesch-Kincaid grade)
    - Sentence length
    - Vocabulary complexity
    - Use of passive voice
    - Technical jargon
    - And other LUIAG criteria
    """

    def __init__(self):
        """Initialize the checker with required analyzers."""
        self._readability_analyzer = ReadabilityAnalyzer()
        self._sentence_analyzer = SentenceAnalyzer()

    def check_response(
        self,
        response: str,
        target_level: ComplianceLevel = ComplianceLevel.LEVEL_AA,
    ) -> AccessibilityCheckResult:
        """Check a response against LUIAG criteria.

        Args:
            response: The text response to check
            target_level: Target compliance level (default: AA)

        Returns:
            AccessibilityCheckResult with violations and score
        """
        if not response or not response.strip():
            return AccessibilityCheckResult(
                passes=True,
                level=target_level,
                achieved_level=ComplianceLevel.LEVEL_AAA,
                violations=[],
                score=1.0,
                readability_metrics=None,
                summary="Empty response - no violations",
                recommendations=[],
            )

        violations: list[AccessibilityViolation] = []

        # Get readability metrics
        metrics = self._readability_analyzer.analyze(response)

        # Run all checks based on target level
        violations.extend(self._check_level_a(response, metrics))

        if target_level in [ComplianceLevel.LEVEL_AA, ComplianceLevel.LEVEL_AAA]:
            violations.extend(self._check_level_aa(response, metrics))

        if target_level == ComplianceLevel.LEVEL_AAA:
            violations.extend(self._check_level_aaa(response, metrics))

        # Calculate score
        score = self._calculate_score(violations)

        # Determine achieved level
        achieved_level = self._determine_achieved_level(response, metrics)

        # Check if passes target level
        passes = achieved_level is not None and self._level_value(achieved_level) >= self._level_value(target_level)

        # Generate summary and recommendations
        summary = self._generate_summary(violations, score, target_level, achieved_level)
        recommendations = self._generate_recommendations(violations, metrics)

        return AccessibilityCheckResult(
            passes=passes,
            level=target_level,
            achieved_level=achieved_level,
            violations=violations,
            score=score,
            readability_metrics=metrics,
            summary=summary,
            recommendations=recommendations,
        )

    def _check_level_a(
        self,
        response: str,
        metrics: ReadabilityMetrics,
    ) -> list[AccessibilityViolation]:
        """Check Level A (minimum) criteria."""
        violations = []
        thresholds = LEVEL_THRESHOLDS[ComplianceLevel.LEVEL_A]

        # A.1.1: Basic readability
        if metrics.flesch_kincaid_grade > thresholds["max_grade"]:
            violations.append(
                AccessibilityViolation(
                    criterion="A.1.1",
                    severity=ViolationSeverity.CRITICAL,
                    description=(
                        f"Reading level {metrics.flesch_kincaid_grade:.1f} "
                        f"exceeds maximum {thresholds['max_grade']:.1f} for Level A"
                    ),
                    remediation="Simplify vocabulary and sentence structure",
                )
            )

        # A.1.2: Sentence length
        sentences = self._sentence_analyzer.analyze_sentences(response)
        for i, sent in enumerate(sentences, 1):
            if sent.word_count > thresholds["max_sentence_words"]:
                violations.append(
                    AccessibilityViolation(
                        criterion="A.1.2",
                        severity=ViolationSeverity.MAJOR,
                        description=(
                            f"Sentence {i} has {sent.word_count} words, "
                            f"exceeds maximum {thresholds['max_sentence_words']}"
                        ),
                        remediation="Split long sentences into shorter ones",
                        element=sent.text[:100] + "..." if len(sent.text) > 100 else sent.text,
                        line_number=i,
                    )
                )

        # A.2.1: Text content exists
        if metrics.word_count < 3:
            violations.append(
                AccessibilityViolation(
                    criterion="A.2.1",
                    severity=ViolationSeverity.MAJOR,
                    description="Response is too brief to be meaningful",
                    remediation="Provide sufficient context and information",
                )
            )

        return violations

    def _check_level_aa(
        self,
        response: str,
        metrics: ReadabilityMetrics,
    ) -> list[AccessibilityViolation]:
        """Check Level AA (standard) criteria."""
        violations = []
        thresholds = LEVEL_THRESHOLDS[ComplianceLevel.LEVEL_AA]

        # AA.1.1: Stricter readability
        if metrics.flesch_kincaid_grade > thresholds["max_grade"]:
            violations.append(
                AccessibilityViolation(
                    criterion="AA.1.1",
                    severity=ViolationSeverity.MAJOR,
                    description=(
                        f"Reading level {metrics.flesch_kincaid_grade:.1f} "
                        f"exceeds maximum {thresholds['max_grade']:.1f} for Level AA"
                    ),
                    remediation="Use simpler words and shorter sentences",
                )
            )

        # AA.1.2: Flesch Reading Ease
        if metrics.flesch_reading_ease < thresholds["min_flesch_reading_ease"]:
            violations.append(
                AccessibilityViolation(
                    criterion="AA.1.2",
                    severity=ViolationSeverity.MAJOR,
                    description=(
                        f"Flesch Reading Ease {metrics.flesch_reading_ease:.1f} "
                        f"below minimum {thresholds['min_flesch_reading_ease']:.1f}"
                    ),
                    remediation="Simplify text to improve readability score",
                )
            )

        # AA.2.1: Complex vocabulary
        complex_words = self._find_complex_words(response)
        if len(complex_words) > 0:
            for word, alternative in complex_words[:3]:  # Report first 3
                violations.append(
                    AccessibilityViolation(
                        criterion="AA.2.1",
                        severity=ViolationSeverity.MINOR,
                        description=f"Complex word '{word}' found",
                        remediation=f"Consider using '{alternative}' instead",
                        element=word,
                    )
                )

        # AA.2.2: Stricter sentence length
        sentences = self._sentence_analyzer.analyze_sentences(response)
        for i, sent in enumerate(sentences, 1):
            if sent.word_count > thresholds["max_sentence_words"]:
                violations.append(
                    AccessibilityViolation(
                        criterion="AA.2.2",
                        severity=ViolationSeverity.MAJOR,
                        description=(
                            f"Sentence {i} has {sent.word_count} words, "
                            f"exceeds Level AA maximum {thresholds['max_sentence_words']}"
                        ),
                        remediation="Split into shorter sentences for better comprehension",
                        element=sent.text[:100] + "..." if len(sent.text) > 100 else sent.text,
                        line_number=i,
                    )
                )

        # AA.3.1: Passive voice (should be limited)
        passive_count = self._count_passive_voice(response)
        if passive_count > 2:
            violations.append(
                AccessibilityViolation(
                    criterion="AA.3.1",
                    severity=ViolationSeverity.MINOR,
                    description=f"Found {passive_count} instances of passive voice",
                    remediation="Use active voice for clearer communication",
                )
            )

        return violations

    def _check_level_aaa(
        self,
        response: str,
        metrics: ReadabilityMetrics,
    ) -> list[AccessibilityViolation]:
        """Check Level AAA (enhanced) criteria."""
        violations = []
        thresholds = LEVEL_THRESHOLDS[ComplianceLevel.LEVEL_AAA]

        # AAA.1.1: Strictest readability
        if metrics.flesch_kincaid_grade > thresholds["max_grade"]:
            violations.append(
                AccessibilityViolation(
                    criterion="AAA.1.1",
                    severity=ViolationSeverity.MAJOR,
                    description=(
                        f"Reading level {metrics.flesch_kincaid_grade:.1f} "
                        f"exceeds maximum {thresholds['max_grade']:.1f} for Level AAA"
                    ),
                    remediation="Use very simple language appropriate for 6th grade",
                )
            )

        # AAA.1.2: Highest reading ease
        if metrics.flesch_reading_ease < thresholds["min_flesch_reading_ease"]:
            violations.append(
                AccessibilityViolation(
                    criterion="AAA.1.2",
                    severity=ViolationSeverity.MAJOR,
                    description=(
                        f"Flesch Reading Ease {metrics.flesch_reading_ease:.1f} "
                        f"below Level AAA minimum {thresholds['min_flesch_reading_ease']:.1f}"
                    ),
                    remediation="Significantly simplify text for maximum accessibility",
                )
            )

        # AAA.2.1: Strictest sentence length
        sentences = self._sentence_analyzer.analyze_sentences(response)
        for i, sent in enumerate(sentences, 1):
            if sent.word_count > thresholds["max_sentence_words"]:
                violations.append(
                    AccessibilityViolation(
                        criterion="AAA.2.1",
                        severity=ViolationSeverity.MAJOR,
                        description=(
                            f"Sentence {i} has {sent.word_count} words, "
                            f"exceeds Level AAA maximum {thresholds['max_sentence_words']}"
                        ),
                        remediation="Keep all sentences under 20 words",
                        element=sent.text[:100] + "..." if len(sent.text) > 100 else sent.text,
                        line_number=i,
                    )
                )

        # AAA.2.2: No passive voice
        passive_count = self._count_passive_voice(response)
        if passive_count > 0:
            violations.append(
                AccessibilityViolation(
                    criterion="AAA.2.2",
                    severity=ViolationSeverity.MINOR,
                    description=f"Found {passive_count} instances of passive voice",
                    remediation="Eliminate all passive voice for Level AAA",
                )
            )

        # AAA.3.1: Technical jargon
        jargon_found = self._find_technical_jargon(response)
        if jargon_found:
            violations.append(
                AccessibilityViolation(
                    criterion="AAA.3.1",
                    severity=ViolationSeverity.MINOR,
                    description=f"Technical jargon found: {', '.join(jargon_found[:5])}",
                    remediation="Define or replace technical terms",
                )
            )

        # AAA.3.2: All complex words flagged
        complex_words = self._find_complex_words(response)
        if complex_words:
            violations.append(
                AccessibilityViolation(
                    criterion="AAA.3.2",
                    severity=ViolationSeverity.ADVISORY,
                    description=f"Found {len(complex_words)} complex words",
                    remediation="Replace with simpler alternatives where possible",
                )
            )

        # AAA.4.1: Polysyllable density
        if metrics.complex_word_percentage > 10:
            violations.append(
                AccessibilityViolation(
                    criterion="AAA.4.1",
                    severity=ViolationSeverity.MINOR,
                    description=(
                        f"Complex word percentage {metrics.complex_word_percentage:.1f}% "
                        f"exceeds 10% for Level AAA"
                    ),
                    remediation="Reduce use of words with 3+ syllables",
                )
            )

        return violations

    def _find_complex_words(self, text: str) -> list[tuple[str, str]]:
        """Find complex words and their simple alternatives."""
        found = []
        text_lower = text.lower()

        for pattern in COMPLEX_WORDS_PATTERNS:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                alternative = SIMPLE_ALTERNATIVES.get(match.lower(), "simpler word")
                found.append((match, alternative))

        return found

    def _count_passive_voice(self, text: str) -> int:
        """Count instances of passive voice."""
        count = 0
        for pattern in PASSIVE_VOICE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count

    def _find_technical_jargon(self, text: str) -> list[str]:
        """Find technical jargon that may need explanation."""
        found = []
        for pattern in TECHNICAL_JARGON:
            matches = re.findall(pattern, text, re.IGNORECASE)
            found.extend(matches)
        return list(set(found))

    def _calculate_score(self, violations: list[AccessibilityViolation]) -> float:
        """Calculate accessibility score from violations.

        Score starts at 1.0 and is reduced by violation weights.
        """
        if not violations:
            return 1.0

        total_weight = sum(v.weight for v in violations)
        score = max(0.0, 1.0 - total_weight)
        return round(score, 2)

    def _determine_achieved_level(
        self,
        response: str,
        metrics: ReadabilityMetrics,
    ) -> Optional[ComplianceLevel]:
        """Determine the highest compliance level achieved."""
        # Check AAA first
        aaa_violations = self._check_level_a(response, metrics)
        aaa_violations.extend(self._check_level_aa(response, metrics))
        aaa_violations.extend(self._check_level_aaa(response, metrics))

        critical_or_major_aaa = sum(
            1 for v in aaa_violations
            if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]
        )

        if critical_or_major_aaa == 0:
            return ComplianceLevel.LEVEL_AAA

        # Check AA
        aa_violations = self._check_level_a(response, metrics)
        aa_violations.extend(self._check_level_aa(response, metrics))

        critical_or_major_aa = sum(
            1 for v in aa_violations
            if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]
        )

        if critical_or_major_aa == 0:
            return ComplianceLevel.LEVEL_AA

        # Check A
        a_violations = self._check_level_a(response, metrics)

        critical_or_major_a = sum(
            1 for v in a_violations
            if v.severity in [ViolationSeverity.CRITICAL, ViolationSeverity.MAJOR]
        )

        if critical_or_major_a == 0:
            return ComplianceLevel.LEVEL_A

        return None

    def _level_value(self, level: ComplianceLevel) -> int:
        """Get numeric value for level comparison."""
        return {
            ComplianceLevel.LEVEL_A: 1,
            ComplianceLevel.LEVEL_AA: 2,
            ComplianceLevel.LEVEL_AAA: 3,
        }[level]

    def _generate_summary(
        self,
        violations: list[AccessibilityViolation],
        score: float,
        target_level: ComplianceLevel,
        achieved_level: Optional[ComplianceLevel],
    ) -> str:
        """Generate a human-readable summary."""
        if not violations:
            return f"Response meets {target_level.value} requirements with score {score:.0%}"

        achieved_str = achieved_level.value if achieved_level else "None"
        critical = sum(1 for v in violations if v.severity == ViolationSeverity.CRITICAL)
        major = sum(1 for v in violations if v.severity == ViolationSeverity.MAJOR)

        parts = [
            f"Accessibility score: {score:.0%}",
            f"Target: {target_level.value}, Achieved: {achieved_str}",
        ]

        if critical > 0:
            parts.append(f"{critical} critical violation(s)")
        if major > 0:
            parts.append(f"{major} major violation(s)")

        return ". ".join(parts)

    def _generate_recommendations(
        self,
        violations: list[AccessibilityViolation],
        metrics: ReadabilityMetrics,
    ) -> list[str]:
        """Generate prioritized recommendations."""
        recommendations = []

        # Get unique remediations, prioritized by severity
        seen_remediations = set()
        sorted_violations = sorted(
            violations,
            key=lambda v: [
                ViolationSeverity.CRITICAL,
                ViolationSeverity.MAJOR,
                ViolationSeverity.MINOR,
                ViolationSeverity.ADVISORY,
            ].index(v.severity),
        )

        for v in sorted_violations:
            if v.remediation not in seen_remediations:
                recommendations.append(v.remediation)
                seen_remediations.add(v.remediation)

        # Add general recommendations based on metrics
        if metrics.flesch_kincaid_grade > 8:
            if "Simplify vocabulary and sentence structure" not in recommendations:
                recommendations.append(
                    f"Reduce reading level from grade {metrics.flesch_kincaid_grade:.1f} to 8 or below"
                )

        if metrics.average_sentence_length > 20:
            recommendations.append(
                f"Shorten average sentence length from {metrics.average_sentence_length:.1f} words"
            )

        return recommendations[:10]  # Limit to top 10
