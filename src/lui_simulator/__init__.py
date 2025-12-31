"""LUI Simulator - Interactive Language User Interface testing tool."""

from .simulator import LUISimulator
from .context import SimulatorContext, SimulatorConfig
from .logger import ConversationLogger, ConversationEntry
from .metrics import (
    MetricsCollector,
    MetricsStoreConfig,
    InteractionRecord,
    MetricsWindow,
    FrustrationSignals,
    MasterySignals,
    InteractionOutcome,
    TrendDirection,
    SignalSeverity,
    PrivacyMode,
)
from .expertise import (
    ExpertiseDetector,
    ExpertiseDetectionConfig,
    ExpertiseEstimate,
    ExpertiseFactor,
    ExpertiseFactorBreakdown,
    ExpertiseLevel,
    LevelThreshold,
    ColdStartConfig,
)
from .transitions import (
    TransitionManager,
    TransitionPolicy,
    TransitionDecision,
    TransitionResult,
    TransitionRecord,
    TransitionDirection,
    RollbackResult,
)
from .templates import (
    TemplateManager,
    TemplatePurpose,
    TemplateVariant,
    AdaptiveTemplate,
    TemplateSelectionContext,
    RenderedTemplate,
    TemplateLibrary,
    VerbosityMapping,
    TemplateCustomization,
    ErrorTemplateDetails,
)
from .adaptive_response import (
    AdaptiveResponseGenerator,
    AdaptiveResponse,
    AdaptationSettings,
    FrustrationIndicators,
    FrustrationResponse,
    ResponseModifier,
)

__all__ = [
    "LUISimulator",
    "SimulatorContext",
    "SimulatorConfig",
    "ConversationLogger",
    "ConversationEntry",
    # Metrics collection
    "MetricsCollector",
    "MetricsStoreConfig",
    "InteractionRecord",
    "MetricsWindow",
    "FrustrationSignals",
    "MasterySignals",
    "InteractionOutcome",
    "TrendDirection",
    "SignalSeverity",
    "PrivacyMode",
    # Expertise detection
    "ExpertiseDetector",
    "ExpertiseDetectionConfig",
    "ExpertiseEstimate",
    "ExpertiseFactor",
    "ExpertiseFactorBreakdown",
    "ExpertiseLevel",
    "LevelThreshold",
    "ColdStartConfig",
    # Level transitions
    "TransitionManager",
    "TransitionPolicy",
    "TransitionDecision",
    "TransitionResult",
    "TransitionRecord",
    "TransitionDirection",
    "RollbackResult",
    # Adaptive templates
    "TemplateManager",
    "TemplatePurpose",
    "TemplateVariant",
    "AdaptiveTemplate",
    "TemplateSelectionContext",
    "RenderedTemplate",
    "TemplateLibrary",
    "VerbosityMapping",
    "TemplateCustomization",
    "ErrorTemplateDetails",
    # Adaptive response generation
    "AdaptiveResponseGenerator",
    "AdaptiveResponse",
    "AdaptationSettings",
    "FrustrationIndicators",
    "FrustrationResponse",
    "ResponseModifier",
]
