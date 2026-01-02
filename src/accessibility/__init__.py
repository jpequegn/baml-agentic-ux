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

from .disability_evaluators import (
    Barrier,
    BarrierAnalysis,
    BarrierCategory,
    CognitiveAccessibilityEvaluator,
    CombinedDisabilityEvaluator,
    DisabilityEvaluation,
    DisabilityEvaluator,
    DisabilityType,
    HearingAccessibilityEvaluator,
    MotorAccessibilityEvaluator,
    NeurologicalAccessibilityEvaluator,
    SpeechAccessibilityEvaluator,
    VisualAccessibilityEvaluator,
)

from .timing import (
    AutoUpdateConfig,
    ErrorHandlingConfig,
    FeedbackConfig,
    INPUT_REQUIREMENTS,
    InputMethodConfig,
    InputValidationResult,
    InteractionTimingValidator,
    InteractionValidationResult,
    TIMING_THRESHOLDS,
    TimeoutConfig,
    TimingThreshold,
    TimingValidationResult,
    TimingViolation,
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
    # Disability Evaluators
    "Barrier",
    "BarrierAnalysis",
    "BarrierCategory",
    "CognitiveAccessibilityEvaluator",
    "CombinedDisabilityEvaluator",
    "DisabilityEvaluation",
    "DisabilityEvaluator",
    "DisabilityType",
    "HearingAccessibilityEvaluator",
    "MotorAccessibilityEvaluator",
    "NeurologicalAccessibilityEvaluator",
    "SpeechAccessibilityEvaluator",
    "VisualAccessibilityEvaluator",
    # Interaction Timing
    "AutoUpdateConfig",
    "ErrorHandlingConfig",
    "FeedbackConfig",
    "INPUT_REQUIREMENTS",
    "InputMethodConfig",
    "InputValidationResult",
    "InteractionTimingValidator",
    "InteractionValidationResult",
    "TIMING_THRESHOLDS",
    "TimeoutConfig",
    "TimingThreshold",
    "TimingValidationResult",
    "TimingViolation",
]
