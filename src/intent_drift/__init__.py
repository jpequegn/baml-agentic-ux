"""Intent drift detection module.

This module provides tools for detecting and handling intent drift in
conversational AI applications. Intent drift occurs when user requests
move outside the supported capabilities of the system.

Issue #78 - Task 5.1: Drift Analysis Types
Issue #79 - Task 5.2: Semantic Analyzer
Issue #80 - Task 5.3: Drift Classifier
Issue #81 - Task 5.4: Confidence Assessor
Issue #82 - Task 5.5: Graceful Response Generator
Issue #83 - Task 5.6: Conversation Coherence Tracker
Issue #84 - Task 5.7: Redirect Suggestion Engine
Issue #85 - Task 5.8: Intent Pipeline Integration
Issue #86 - Task 5.9: Response Template Library
Part of #28 - Phase 5: Intent Drift Detection
"""

from .coherence_tracker import (
    # Enums
    ContextResetReason,
    DriftTrend,
    # Data Classes
    CoherenceMetrics,
    CoherenceTrackerConfig,
    ContextResetTrigger,
    TurnCoherence,
    # Main Class
    ConversationCoherenceTracker,
)
from .confidence_assessor import (
    # Thresholds
    ConfidenceThresholds,
    # Enums
    AssessmentAction,
    # Data Classes
    AssessmentResult,
    CalibrationResult,
    ConfidenceAssessorConfig,
    IntentResult,
    # Main Class
    ConfidenceAssessor,
)
from .drift_classifier import (
    # Pattern definitions
    ABSTRACTION_PATTERNS,
    META_PATTERNS,
    PII_PATTERNS,
    TEMPORAL_FUTURE_PATTERNS,
    TEMPORAL_PAST_PATTERNS,
    # Classes
    DriftClassification,
    DriftClassifier,
    DriftClassifierConfig,
    DriftScoreRange,
    PatternMatch,
)
from .response_generator import (
    # Templates
    DRIFT_TEMPLATES,
    TEMPLATE_ABSTRACTION_CLIMB,
    TEMPLATE_AMBIGUOUS,
    TEMPLATE_DOMAIN_SHIFT,
    TEMPLATE_ESCALATION,
    TEMPLATE_NONE,
    TEMPLATE_PERSONALIZATION,
    TEMPLATE_SCOPE_EXPANSION,
    TEMPLATE_TEMPORAL_DRIFT,
    # Configuration
    ResponseGeneratorConfig,
    # Main Class
    GracefulResponseGenerator,
)
from .semantic_analyzer import (
    # Thresholds
    DOMAIN_SHIFT_THRESHOLD,
    IN_SCOPE_THRESHOLD,
    SCOPE_EXPANSION_MIN,
    # Classes
    IntentDefinition,
    SemanticAnalyzer,
    SemanticAnalyzerConfig,
    SimilarityResult,
)
from .redirect_engine import (
    # Enums
    RedirectStrategy,
    # Configuration
    RedirectEngineConfig,
    # Data Classes
    RedirectContext,
    ScoredSuggestion,
    # Templates
    REDIRECT_PHRASE_TEMPLATES,
    REDIRECT_REASON_TEMPLATES,
    # Main Class
    RedirectSuggestionEngine,
)
from .templates import (
    # Enums
    TemplateCategory,
    # Configuration
    TemplateConfig,
    # Core Classes
    ResponseTemplate,
    TemplateLibrary,
    # Template Collections
    ALL_TEMPLATES,
    CAPABILITY_TEMPLATES,
    CLARIFICATION_TEMPLATES,
    ESCALATION_TEMPLATES,
    IN_SCOPE_TEMPLATES,
    REDIRECT_TEMPLATES as LIBRARY_REDIRECT_TEMPLATES,
    UNCERTAINTY_TEMPLATES,
    # Factory Functions
    get_default_library,
    reset_default_library,
)
from .types import (
    # Core Enums
    AbstractionLevel,
    CoherenceTrend,
    ConfidenceTier,
    DriftResponseTone,
    DriftType,
    GracefulResponseType,
    RecommendedAction,
    TemporalReferenceType,
    # Core Data Classes
    DriftAnalysis,
    RedirectSuggestion,
    # Semantic Analysis
    EntityMention,
    NearestIntent,
    SemanticAnalysis,
    TemporalReference,
    # Confidence Assessment
    ConfidenceAssessment,
    ConfidenceFactorScore,
    # Graceful Response
    DriftResponseTemplate,
    GracefulResponse,
    Redirect,
    # Conversation Context
    CoherenceAnalysis,
    ConversationDriftContext,
    DriftConversationTurn,
    DriftEvent,
    # Configuration
    DriftDetectionConfig,
    DriftDetectionResult,
    # Request/Response
    BatchDriftAnalysis,
    DriftAggregateStats,
    DriftAnalysisRequest,
)

__all__ = [
    # Coherence Tracker
    "ContextResetReason",
    "DriftTrend",
    "CoherenceMetrics",
    "CoherenceTrackerConfig",
    "ContextResetTrigger",
    "TurnCoherence",
    "ConversationCoherenceTracker",
    # Confidence Assessor
    "ConfidenceThresholds",
    "AssessmentAction",
    "AssessmentResult",
    "CalibrationResult",
    "ConfidenceAssessorConfig",
    "IntentResult",
    "ConfidenceAssessor",
    # Response Generator
    "DRIFT_TEMPLATES",
    "TEMPLATE_ABSTRACTION_CLIMB",
    "TEMPLATE_AMBIGUOUS",
    "TEMPLATE_DOMAIN_SHIFT",
    "TEMPLATE_ESCALATION",
    "TEMPLATE_NONE",
    "TEMPLATE_PERSONALIZATION",
    "TEMPLATE_SCOPE_EXPANSION",
    "TEMPLATE_TEMPORAL_DRIFT",
    "ResponseGeneratorConfig",
    "GracefulResponseGenerator",
    # Drift Classifier
    "ABSTRACTION_PATTERNS",
    "META_PATTERNS",
    "PII_PATTERNS",
    "TEMPORAL_FUTURE_PATTERNS",
    "TEMPORAL_PAST_PATTERNS",
    "DriftClassification",
    "DriftClassifier",
    "DriftClassifierConfig",
    "DriftScoreRange",
    "PatternMatch",
    # Semantic Analyzer
    "DOMAIN_SHIFT_THRESHOLD",
    "IN_SCOPE_THRESHOLD",
    "SCOPE_EXPANSION_MIN",
    "IntentDefinition",
    "SemanticAnalyzer",
    "SemanticAnalyzerConfig",
    "SimilarityResult",
    # Redirect Engine
    "RedirectStrategy",
    "RedirectEngineConfig",
    "RedirectContext",
    "ScoredSuggestion",
    "REDIRECT_PHRASE_TEMPLATES",
    "REDIRECT_REASON_TEMPLATES",
    "RedirectSuggestionEngine",
    # Template Library
    "TemplateCategory",
    "TemplateConfig",
    "ResponseTemplate",
    "TemplateLibrary",
    "ALL_TEMPLATES",
    "CAPABILITY_TEMPLATES",
    "CLARIFICATION_TEMPLATES",
    "ESCALATION_TEMPLATES",
    "IN_SCOPE_TEMPLATES",
    "LIBRARY_REDIRECT_TEMPLATES",
    "UNCERTAINTY_TEMPLATES",
    "get_default_library",
    "reset_default_library",
    # Core Enums
    "AbstractionLevel",
    "CoherenceTrend",
    "ConfidenceTier",
    "DriftResponseTone",
    "DriftType",
    "GracefulResponseType",
    "RecommendedAction",
    "TemporalReferenceType",
    # Core Data Classes
    "DriftAnalysis",
    "RedirectSuggestion",
    # Semantic Analysis
    "EntityMention",
    "NearestIntent",
    "SemanticAnalysis",
    "TemporalReference",
    # Confidence Assessment
    "ConfidenceAssessment",
    "ConfidenceFactorScore",
    # Graceful Response
    "DriftResponseTemplate",
    "GracefulResponse",
    "Redirect",
    # Conversation Context
    "CoherenceAnalysis",
    "ConversationDriftContext",
    "DriftConversationTurn",
    "DriftEvent",
    # Configuration
    "DriftDetectionConfig",
    "DriftDetectionResult",
    # Request/Response
    "BatchDriftAnalysis",
    "DriftAggregateStats",
    "DriftAnalysisRequest",
]
