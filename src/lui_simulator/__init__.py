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
from .transitions import (
    TransitionManager,
    TransitionPolicy,
    TransitionDecision,
    TransitionResult,
    TransitionRecord,
    TransitionDirection,
    RollbackResult,
    ExpertiseLevel,
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
    # Level transitions
    "TransitionManager",
    "TransitionPolicy",
    "TransitionDecision",
    "TransitionResult",
    "TransitionRecord",
    "TransitionDirection",
    "RollbackResult",
    "ExpertiseLevel",
]
