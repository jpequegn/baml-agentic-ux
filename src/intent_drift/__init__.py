"""Intent drift detection module.

This module provides tools for detecting and handling intent drift in
conversational AI applications. Intent drift occurs when user requests
move outside the supported capabilities of the system.

Issue #78 - Task 5.1: Drift Analysis Types
Part of #28 - Phase 5: Intent Drift Detection
"""

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
