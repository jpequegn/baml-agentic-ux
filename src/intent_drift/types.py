"""Intent drift detection type definitions.

This module defines Python types for intent drift detection and classification,
mirroring the BAML type definitions in baml_src/drift_types.baml.

Issue #78 - Task 5.1: Drift Analysis Types
Part of #28 - Phase 5: Intent Drift Detection
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


# ============================================
# Core Drift Enums
# ============================================


class DriftType(Enum):
    """Types of intent drift that can be detected."""

    NONE = "none"
    """Within capability - no drift detected."""

    SCOPE_EXPANSION = "scope_expansion"
    """Related but unsupported feature request."""

    DOMAIN_SHIFT = "domain_shift"
    """Different domain entirely from capabilities."""

    ABSTRACTION_CLIMB = "abstraction_climb"
    """Too abstract or philosophical for practical handling."""

    PERSONALIZATION = "personalization"
    """Requires user-specific data not available."""

    TEMPORAL_DRIFT = "temporal_drift"
    """Past/future beyond knowledge cutoff."""

    AMBIGUOUS = "ambiguous"
    """Multiple intents detected, needs clarification."""


class AbstractionLevel(Enum):
    """How abstract or concrete a request is."""

    CONCRETE = "concrete"
    """Specific, actionable request."""

    MODERATE = "moderate"
    """Somewhat abstract but handleable."""

    ABSTRACT = "abstract"
    """High-level, may need grounding."""

    PHILOSOPHICAL = "philosophical"
    """Too abstract for practical action."""


class TemporalReferenceType(Enum):
    """Types of temporal references in user input."""

    PAST_ABSOLUTE = "past_absolute"
    """Specific past date."""

    PAST_RELATIVE = "past_relative"
    """Relative past reference (yesterday, last week)."""

    PRESENT = "present"
    """Current time reference."""

    FUTURE_RELATIVE = "future_relative"
    """Relative future reference (tomorrow, next week)."""

    FUTURE_ABSOLUTE = "future_absolute"
    """Specific future date."""

    HYPOTHETICAL = "hypothetical"
    """Hypothetical time scenario."""


class ConfidenceTier(Enum):
    """Tiered confidence levels for drift detection."""

    VERY_HIGH = "very_high"
    """95%+ confidence - proceed normally."""

    HIGH = "high"
    """80-94% confidence - proceed with minor caveats."""

    MEDIUM = "medium"
    """60-79% confidence - may need clarification."""

    LOW = "low"
    """40-59% confidence - clarification recommended."""

    VERY_LOW = "very_low"
    """Below 40% - should not proceed without clarification."""


class RecommendedAction(Enum):
    """Recommended action based on confidence assessment."""

    PROCEED = "proceed"
    """Proceed with detected intent."""

    PROCEED_WITH_CAVEAT = "proceed_with_caveat"
    """Proceed but mention uncertainty."""

    CLARIFY = "clarify"
    """Ask for clarification before proceeding."""

    REDIRECT = "redirect"
    """Suggest alternative capabilities."""

    ESCALATE = "escalate"
    """Escalate to human or higher authority."""

    DECLINE = "decline"
    """Politely decline the request."""


class GracefulResponseType(Enum):
    """Types of graceful responses to drift."""

    CLARIFICATION = "clarification"
    """Asking for more information."""

    PARTIAL_HELP = "partial_help"
    """Can help with part of the request."""

    REDIRECT = "redirect"
    """Suggesting alternative capabilities."""

    BOUNDARY_STATEMENT = "boundary_statement"
    """Explaining capability boundaries."""

    ESCALATION = "escalation"
    """Offering to escalate."""

    ACKNOWLEDGMENT = "acknowledgment"
    """Acknowledging but cannot help."""


class DriftResponseTone(Enum):
    """Tone for drift response delivery."""

    EMPATHETIC = "empathetic"
    """Understanding and supportive."""

    HELPFUL = "helpful"
    """Focused on finding solutions."""

    PROFESSIONAL = "professional"
    """Neutral and business-like."""

    APOLOGETIC = "apologetic"
    """Expressing regret for limitations."""

    ENCOURAGING = "encouraging"
    """Positive about alternatives."""


class CoherenceTrend(Enum):
    """Trend in conversation coherence."""

    IMPROVING = "improving"
    """Conversation getting more focused."""

    STABLE = "stable"
    """Coherence relatively constant."""

    DEGRADING = "degrading"
    """Conversation losing focus."""

    VOLATILE = "volatile"
    """Coherence varying significantly."""


# ============================================
# Core Drift Data Classes
# ============================================


@dataclass
class RedirectSuggestion:
    """Alternative capability suggestion.

    Attributes:
        target_intent: The suggested alternative intent
        similarity_score: How similar to original request (0-1)
        redirect_reason: Why this is suggested as alternative
        transition_phrase: Natural language to transition to this
        confidence: Confidence in this suggestion
    """

    target_intent: str
    similarity_score: float
    redirect_reason: str
    transition_phrase: str
    confidence: float

    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.similarity_score <= 1.0:
            raise ValueError("similarity_score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")


@dataclass
class DriftAnalysis:
    """Main drift detection result.

    Attributes:
        current_input: The current user input being analyzed
        drift_score: 0.0 = on topic, 1.0 = completely off topic
        drift_type: Classification of the type of drift
        confidence: Confidence in the drift detection (0-1)
        semantic_distance: Semantic distance from supported intents
        graceful_response: Suggested response handling the drift
        original_intent: The original user intent if known
        last_supported_intent: Last intent that was within capability
        suggested_redirects: Suggested alternative capabilities
    """

    current_input: str
    drift_score: float
    drift_type: DriftType
    confidence: float
    semantic_distance: float
    graceful_response: str
    original_intent: Optional[str] = None
    last_supported_intent: Optional[str] = None
    suggested_redirects: list[RedirectSuggestion] = field(default_factory=list)

    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.drift_score <= 1.0:
            raise ValueError("drift_score must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")

    @property
    def has_drift(self) -> bool:
        """Check if drift was detected."""
        return self.drift_type != DriftType.NONE

    @property
    def needs_clarification(self) -> bool:
        """Check if clarification is recommended."""
        return self.drift_type == DriftType.AMBIGUOUS or self.confidence < 0.6

    @property
    def has_redirects(self) -> bool:
        """Check if redirect suggestions are available."""
        return len(self.suggested_redirects) > 0


# ============================================
# Semantic Analysis Types
# ============================================


@dataclass
class NearestIntent:
    """A supported intent close to the user's request.

    Attributes:
        intent_name: Name of the supported intent
        similarity: Cosine similarity or other distance metric
        capability_id: Associated capability ID
        requires_clarification: Whether clarification is needed
    """

    intent_name: str
    similarity: float
    capability_id: Optional[str] = None
    requires_clarification: bool = False

    def __post_init__(self):
        """Validate similarity is in valid range."""
        if not 0.0 <= self.similarity <= 1.0:
            raise ValueError("similarity must be between 0.0 and 1.0")


@dataclass
class TemporalReference:
    """Time expression analysis.

    Attributes:
        expression: The temporal expression found
        reference_type: Type of temporal reference
        is_within_knowledge: Whether within knowledge cutoff
        drift_risk: Risk this causes temporal drift (0-1)
        resolved_date: ISO 8601 date if resolvable
    """

    expression: str
    reference_type: TemporalReferenceType
    is_within_knowledge: bool
    drift_risk: float
    resolved_date: Optional[str] = None

    def __post_init__(self):
        """Validate drift_risk is in valid range."""
        if not 0.0 <= self.drift_risk <= 1.0:
            raise ValueError("drift_risk must be between 0.0 and 1.0")


@dataclass
class EntityMention:
    """Entity mentioned in user input.

    Attributes:
        text: The entity text
        entity_type: Type of entity (person, org, location, etc.)
        start_offset: Character offset start
        end_offset: Character offset end
        requires_personalization: Whether entity requires user data
    """

    text: str
    entity_type: str
    start_offset: int
    end_offset: int
    requires_personalization: bool = False


@dataclass
class SemanticAnalysis:
    """Semantic analysis of user input.

    Attributes:
        input_text: The analyzed input text
        abstraction_level: How abstract the request is
        nearest_intents: Closest matching supported intents
        domain_classification: Detected domains in input
        temporal_references: Time expressions found
        entity_mentions: Named entities detected
        embedding_vector: Semantic embedding if computed
    """

    input_text: str
    abstraction_level: AbstractionLevel
    nearest_intents: list[NearestIntent] = field(default_factory=list)
    domain_classification: list[str] = field(default_factory=list)
    temporal_references: list[TemporalReference] = field(default_factory=list)
    entity_mentions: list[EntityMention] = field(default_factory=list)
    embedding_vector: Optional[list[float]] = None

    @property
    def has_temporal_drift_risk(self) -> bool:
        """Check if any temporal reference poses drift risk."""
        return any(t.drift_risk > 0.5 for t in self.temporal_references)

    @property
    def requires_personalization(self) -> bool:
        """Check if any entity requires personalization."""
        return any(e.requires_personalization for e in self.entity_mentions)


# ============================================
# Confidence Assessment Types
# ============================================


@dataclass
class ConfidenceFactorScore:
    """Individual confidence factor score.

    Attributes:
        factor_name: Name of the confidence factor
        score: Score for this factor (0-1)
        weight: Weight of this factor in overall score
        explanation: Why this score was assigned
    """

    factor_name: str
    score: float
    weight: float
    explanation: Optional[str] = None

    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.score <= 1.0:
            raise ValueError("score must be between 0.0 and 1.0")
        if not 0.0 <= self.weight <= 1.0:
            raise ValueError("weight must be between 0.0 and 1.0")

    @property
    def weighted_score(self) -> float:
        """Get the weighted score."""
        return self.score * self.weight


@dataclass
class ConfidenceAssessment:
    """Multi-factor confidence assessment.

    Attributes:
        overall_confidence: Overall confidence score (0-1)
        confidence_tier: Tiered confidence level
        recommended_action: Suggested action based on confidence
        explanation: Human-readable confidence explanation
        factor_scores: Individual factor scores
    """

    overall_confidence: float
    confidence_tier: ConfidenceTier
    recommended_action: RecommendedAction
    explanation: str
    factor_scores: list[ConfidenceFactorScore] = field(default_factory=list)

    def __post_init__(self):
        """Validate overall_confidence is in valid range."""
        if not 0.0 <= self.overall_confidence <= 1.0:
            raise ValueError("overall_confidence must be between 0.0 and 1.0")

    @classmethod
    def from_score(cls, score: float, explanation: str = "") -> ConfidenceAssessment:
        """Create a ConfidenceAssessment from a raw score.

        Args:
            score: Confidence score (0-1)
            explanation: Optional explanation

        Returns:
            ConfidenceAssessment with appropriate tier and action
        """
        if score >= 0.95:
            tier = ConfidenceTier.VERY_HIGH
            action = RecommendedAction.PROCEED
        elif score >= 0.80:
            tier = ConfidenceTier.HIGH
            action = RecommendedAction.PROCEED_WITH_CAVEAT
        elif score >= 0.60:
            tier = ConfidenceTier.MEDIUM
            action = RecommendedAction.CLARIFY
        elif score >= 0.40:
            tier = ConfidenceTier.LOW
            action = RecommendedAction.REDIRECT
        else:
            tier = ConfidenceTier.VERY_LOW
            action = RecommendedAction.DECLINE

        return cls(
            overall_confidence=score,
            confidence_tier=tier,
            recommended_action=action,
            explanation=explanation or f"Confidence score: {score:.0%}",
        )


# ============================================
# Graceful Response Types
# ============================================


@dataclass
class Redirect:
    """Redirect to alternative capability.

    Attributes:
        capability_name: Name of alternative capability
        description: What this capability can do
        relevance_score: How relevant to original request
        action_phrase: Phrase to invoke this capability
    """

    capability_name: str
    description: str
    relevance_score: float
    action_phrase: str

    def __post_init__(self):
        """Validate relevance_score is in valid range."""
        if not 0.0 <= self.relevance_score <= 1.0:
            raise ValueError("relevance_score must be between 0.0 and 1.0")


@dataclass
class GracefulResponse:
    """Structure for handling drift gracefully.

    Attributes:
        response_type: Type of graceful response
        primary_message: Main response message
        tone: Tone of the response
        acknowledgment: Acknowledgment of user's request
        explanation: Why we can't fully help
        alternatives: Alternative actions offered
        follow_up_prompt: Prompt to continue conversation
    """

    response_type: GracefulResponseType
    primary_message: str
    tone: DriftResponseTone
    acknowledgment: Optional[str] = None
    explanation: Optional[str] = None
    alternatives: list[Redirect] = field(default_factory=list)
    follow_up_prompt: Optional[str] = None

    def to_message(self) -> str:
        """Generate the complete response message.

        Returns:
            Formatted response string
        """
        parts = []

        if self.acknowledgment:
            parts.append(self.acknowledgment)

        parts.append(self.primary_message)

        if self.explanation:
            parts.append(self.explanation)

        if self.alternatives:
            alt_text = "Here are some things I can help with: "
            alt_text += ", ".join(a.description for a in self.alternatives[:3])
            parts.append(alt_text)

        if self.follow_up_prompt:
            parts.append(self.follow_up_prompt)

        return " ".join(parts)


@dataclass
class DriftResponseTemplate:
    """Template for drift responses.

    Attributes:
        template_id: Unique template identifier
        drift_types: Applicable drift types
        template_text: Template with {placeholders}
        required_variables: Variables that must be filled
        tone: Intended tone
        example_output: Example of filled template
    """

    template_id: str
    drift_types: list[DriftType]
    template_text: str
    required_variables: list[str]
    tone: DriftResponseTone
    example_output: Optional[str] = None

    def render(self, variables: dict[str, str]) -> str:
        """Render the template with variables.

        Args:
            variables: Variable name to value mapping

        Returns:
            Rendered template string

        Raises:
            ValueError: If required variables are missing
        """
        missing = set(self.required_variables) - set(variables.keys())
        if missing:
            raise ValueError(f"Missing required variables: {missing}")

        result = self.template_text
        for key, value in variables.items():
            result = result.replace(f"{{{key}}}", value)
        return result


# ============================================
# Conversation Context Types
# ============================================


@dataclass
class DriftEvent:
    """A recorded drift event.

    Attributes:
        turn_id: Turn where drift occurred
        drift_type: Type of drift detected
        drift_score: Severity of drift
        recovery_attempted: Whether recovery was attempted
        recovery_successful: Whether recovery succeeded
        notes: Additional notes
    """

    turn_id: str
    drift_type: DriftType
    drift_score: float
    recovery_attempted: bool = False
    recovery_successful: bool = False
    notes: Optional[str] = None


@dataclass
class DriftConversationTurn:
    """Single conversation turn for drift tracking.

    Attributes:
        turn_id: Unique turn identifier
        turn_number: Sequential turn number
        user_input: User's input text
        timestamp: ISO 8601 timestamp
        detected_intent: Detected intent for this turn
        drift_analysis: Drift analysis if performed
        response: System response
    """

    turn_id: str
    turn_number: int
    user_input: str
    timestamp: str
    detected_intent: Optional[str] = None
    drift_analysis: Optional[DriftAnalysis] = None
    response: Optional[str] = None

    @property
    def had_drift(self) -> bool:
        """Check if this turn had drift."""
        return self.drift_analysis is not None and self.drift_analysis.has_drift


@dataclass
class CoherenceAnalysis:
    """Conversation coherence analysis.

    Attributes:
        coherence_score: Overall coherence (0-1)
        topic_consistency: How consistent topics are
        intent_stability: How stable intents are across turns
        coherence_trend: Whether coherence is improving
        turn_relevance_scores: Relevance score for each turn
        warnings: Coherence warnings if any
    """

    coherence_score: float
    topic_consistency: float
    intent_stability: float
    coherence_trend: CoherenceTrend
    turn_relevance_scores: list[float] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate scores are in valid range."""
        if not 0.0 <= self.coherence_score <= 1.0:
            raise ValueError("coherence_score must be between 0.0 and 1.0")
        if not 0.0 <= self.topic_consistency <= 1.0:
            raise ValueError("topic_consistency must be between 0.0 and 1.0")
        if not 0.0 <= self.intent_stability <= 1.0:
            raise ValueError("intent_stability must be between 0.0 and 1.0")

    @property
    def is_healthy(self) -> bool:
        """Check if conversation coherence is healthy."""
        return (
            self.coherence_score >= 0.6
            and self.coherence_trend != CoherenceTrend.DEGRADING
        )


@dataclass
class ConversationDriftContext:
    """Multi-turn conversation tracking.

    Attributes:
        session_id: Unique session identifier
        turns: Conversation turns
        drift_history: History of drift events
        coherence: Overall conversation coherence
        initial_intent: First detected intent in session
        current_topic: Current conversation topic
    """

    session_id: str
    turns: list[DriftConversationTurn] = field(default_factory=list)
    drift_history: list[DriftEvent] = field(default_factory=list)
    coherence: Optional[CoherenceAnalysis] = None
    initial_intent: Optional[str] = None
    current_topic: Optional[str] = None

    @property
    def turn_count(self) -> int:
        """Get number of turns in conversation."""
        return len(self.turns)

    @property
    def drift_count(self) -> int:
        """Get number of drift events."""
        return len(self.drift_history)

    @property
    def drift_rate(self) -> float:
        """Get percentage of turns with drift."""
        if not self.turns:
            return 0.0
        drift_turns = sum(1 for t in self.turns if t.had_drift)
        return drift_turns / len(self.turns)

    def add_turn(self, turn: DriftConversationTurn) -> None:
        """Add a turn to the conversation.

        Args:
            turn: The turn to add
        """
        self.turns.append(turn)

    def record_drift(self, event: DriftEvent) -> None:
        """Record a drift event.

        Args:
            event: The drift event to record
        """
        self.drift_history.append(event)


# ============================================
# Configuration Types
# ============================================


@dataclass
class DriftDetectionConfig:
    """Configuration for drift detection.

    Attributes:
        drift_threshold: Score above which drift is detected (default 0.5)
        confidence_threshold: Minimum confidence for detection
        max_semantic_distance: Maximum acceptable semantic distance
        supported_domains: Domains considered in-scope
        abstraction_tolerance: Max abstraction tolerated
        enable_personalization_detection: Detect personalization requests
        temporal_cutoff_date: Knowledge cutoff date
    """

    drift_threshold: float = 0.5
    confidence_threshold: float = 0.6
    max_semantic_distance: float = 0.7
    supported_domains: list[str] = field(default_factory=list)
    abstraction_tolerance: AbstractionLevel = AbstractionLevel.MODERATE
    enable_personalization_detection: bool = True
    temporal_cutoff_date: Optional[str] = None

    def __post_init__(self):
        """Validate thresholds are in valid range."""
        if not 0.0 <= self.drift_threshold <= 1.0:
            raise ValueError("drift_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0.0 and 1.0")
        if not 0.0 <= self.max_semantic_distance <= 1.0:
            raise ValueError("max_semantic_distance must be between 0.0 and 1.0")


@dataclass
class DriftDetectionResult:
    """Result of applying drift detection.

    Attributes:
        input: The analyzed input
        config: Configuration used
        analysis: The drift analysis result
        confidence_assessment: Confidence details
        semantic_analysis: Semantic analysis details
        processing_time_ms: Processing time in milliseconds
        suggested_response: Suggested response if drifted
    """

    input: str
    config: DriftDetectionConfig
    analysis: DriftAnalysis
    confidence_assessment: ConfidenceAssessment
    semantic_analysis: SemanticAnalysis
    processing_time_ms: int
    suggested_response: Optional[GracefulResponse] = None

    @property
    def needs_intervention(self) -> bool:
        """Check if drift requires intervention."""
        return (
            self.analysis.has_drift
            and self.confidence_assessment.recommended_action != RecommendedAction.PROCEED
        )


# ============================================
# Request/Response Types
# ============================================


@dataclass
class DriftAnalysisRequest:
    """Request for drift analysis.

    Attributes:
        input: User input to analyze
        include_semantic_analysis: Whether to include semantic analysis
        include_suggestions: Whether to include redirect suggestions
        context: Optional conversation context
        config: Optional custom configuration
    """

    input: str
    include_semantic_analysis: bool = True
    include_suggestions: bool = True
    context: Optional[ConversationDriftContext] = None
    config: Optional[DriftDetectionConfig] = None


@dataclass
class DriftAggregateStats:
    """Aggregate statistics for batch analysis.

    Attributes:
        total_inputs: Total inputs analyzed
        drift_count: Number with drift detected
        drift_rate: Percentage with drift
        avg_drift_score: Average drift score
        avg_confidence: Average confidence score
        drift_type_counts: Count by drift type
    """

    total_inputs: int
    drift_count: int
    drift_rate: float
    avg_drift_score: float
    avg_confidence: float
    drift_type_counts: dict[str, int] = field(default_factory=dict)


@dataclass
class BatchDriftAnalysis:
    """Batch drift analysis for multiple inputs.

    Attributes:
        requests: Inputs to analyze
        results: Results for each input
        aggregate_stats: Aggregate statistics
    """

    requests: list[DriftAnalysisRequest]
    results: list[DriftDetectionResult]
    aggregate_stats: DriftAggregateStats
