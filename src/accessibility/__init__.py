"""Accessibility analysis module for LUI applications.

This module provides tools for analyzing readability and accessibility
compliance of text content following WCAG and plain language guidelines.
"""

from .readability import (
    ReadabilityAnalyzer,
    ReadabilityMetrics,
    SentenceAnalyzer,
    SentenceAnalysis,
)

from .checker import (
    AccessibilityCheckResult,
    AccessibilityViolation,
    ComplianceLevel,
    LUIAccessibilityChecker,
    ViolationSeverity,
)

from .schema_checker import (
    ComponentAccessibilityEval,
    SchemaAccessibilityChecker,
    SchemaAccessibilityResult,
    SchemaViolation,
)

from .jargon import (
    JargonCategory,
    JargonDetector,
    JargonTerm,
    SimplificationResult,
)

__all__ = [
    # Readability
    "ReadabilityAnalyzer",
    "ReadabilityMetrics",
    "SentenceAnalyzer",
    "SentenceAnalysis",
    # Checker
    "AccessibilityCheckResult",
    "AccessibilityViolation",
    "ComplianceLevel",
    "LUIAccessibilityChecker",
    "ViolationSeverity",
    # Schema Checker
    "ComponentAccessibilityEval",
    "SchemaAccessibilityChecker",
    "SchemaAccessibilityResult",
    "SchemaViolation",
    # Jargon Detection
    "JargonCategory",
    "JargonDetector",
    "JargonTerm",
    "SimplificationResult",
]
