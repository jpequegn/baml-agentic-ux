"""Intent Pipeline Integration with Drift Detection.

This module integrates drift detection into the intent extraction pipeline,
providing seamless detection and handling of intent drift.

Issue #85 - Task 5.8: Intent Pipeline Integration
Part of #28 - Phase 5: Intent Drift Detection
Dependencies: All previous tasks (5.1-5.7)
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional, Protocol

from .coherence_tracker import ConversationCoherenceTracker, CoherenceTrackerConfig
from .confidence_assessor import ConfidenceAssessor, ConfidenceAssessorConfig
from .drift_classifier import DriftClassification, DriftClassifier, DriftClassifierConfig
from .redirect_engine import RedirectContext, RedirectEngineConfig, RedirectSuggestionEngine
from .response_generator import GracefulResponseGenerator, ResponseGeneratorConfig
from .semantic_analyzer import IntentDefinition, SemanticAnalyzer, SemanticAnalyzerConfig
from .types import (
    AbstractionLevel,
    ConfidenceAssessment,
    ConfidenceTier,
    ConversationDriftContext,
    DriftAnalysis,
    DriftDetectionConfig,
    DriftDetectionResult,
    DriftType,
    GracefulResponse,
    RecommendedAction,
    RedirectSuggestion,
    SemanticAnalysis,
)


# ============================================
# Pipeline Action Enum
# ============================================


class PipelineAction(Enum):
    """Action determined by the pipeline."""

    EXECUTE = "execute"
    """Proceed with executing the detected intent."""

    CLARIFY = "clarify"
    """Ask for clarification before proceeding."""

    REDIRECT = "redirect"
    """Suggest alternative capabilities."""

    REJECT = "reject"
    """Politely decline the request."""

    ESCALATE = "escalate"
    """Escalate to human or higher authority."""


# ============================================
# Intent Extraction Protocol
# ============================================


class IntentExtractionResult(Protocol):
    """Protocol for intent extraction results.

    This allows integration with various intent extraction implementations.
    """

    @property
    def intent_name(self) -> str:
        """Name of the detected intent."""
        ...

    @property
    def confidence(self) -> float:
        """Confidence in the extraction (0-1)."""
        ...

    @property
    def target_component(self) -> Optional[str]:
        """Target component ID for routing."""
        ...


# ============================================
# Pipeline Configuration
# ============================================


@dataclass
class PipelineDriftConfig:
    """Configuration for drift detection in the pipeline.

    Attributes:
        enable_drift_detection: Whether to enable drift detection
        enable_coherence_tracking: Whether to track conversation coherence
        confidence_thresholds: Tier thresholds for confidence levels
        max_redirect_suggestions: Maximum number of redirect suggestions
        fallback_to_clarification: Whether to ask for clarification on low confidence
        parallel_analysis: Whether to run analyses in parallel
        include_semantic_details: Whether to include full semantic analysis
        include_graceful_response: Whether to generate graceful responses
    """

    enable_drift_detection: bool = True
    enable_coherence_tracking: bool = True
    confidence_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "very_high": 0.95,
            "high": 0.80,
            "medium": 0.60,
            "low": 0.40,
        }
    )
    max_redirect_suggestions: int = 3
    fallback_to_clarification: bool = True
    parallel_analysis: bool = True
    include_semantic_details: bool = True
    include_graceful_response: bool = True

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_redirect_suggestions < 0:
            raise ValueError("max_redirect_suggestions must be non-negative")
        for tier, threshold in self.confidence_thresholds.items():
            if not 0.0 <= threshold <= 1.0:
                raise ValueError(f"Threshold for {tier} must be between 0.0 and 1.0")


# ============================================
# Simple Intent Extraction Result
# ============================================


@dataclass
class SimpleIntentExtraction:
    """Simple intent extraction result for internal use.

    Attributes:
        intent_name: Name of the detected intent
        intent_category: Category of the intent
        target_component: Target component ID
        confidence: Confidence in the extraction
        extracted_parameters: Extracted parameters
        is_ambiguous: Whether the intent is ambiguous
        suggested_clarification: Suggested clarification if ambiguous
    """

    intent_name: str
    intent_category: str
    target_component: Optional[str]
    confidence: float
    extracted_parameters: dict[str, Any] = field(default_factory=dict)
    is_ambiguous: bool = False
    suggested_clarification: Optional[str] = None


# ============================================
# Intent Extraction With Drift Result
# ============================================


@dataclass
class IntentExtractionWithDrift:
    """Complete result of intent extraction with drift analysis.

    Attributes:
        intent_extraction: The base intent extraction result
        drift_analysis: Drift analysis results
        confidence_assessment: Confidence assessment
        recommended_action: Recommended action based on analysis
        response: Generated response (standard or graceful)
        semantic_analysis: Optional semantic analysis details
        redirect_suggestions: Optional redirect suggestions
        processing_time_ms: Total processing time
    """

    intent_extraction: SimpleIntentExtraction
    drift_analysis: DriftAnalysis
    confidence_assessment: ConfidenceAssessment
    recommended_action: PipelineAction
    response: str
    semantic_analysis: Optional[SemanticAnalysis] = None
    redirect_suggestions: list[RedirectSuggestion] = field(default_factory=list)
    processing_time_ms: int = 0

    @property
    def has_drift(self) -> bool:
        """Check if drift was detected."""
        return self.drift_analysis.has_drift

    @property
    def should_proceed(self) -> bool:
        """Check if the pipeline should proceed with execution."""
        return self.recommended_action == PipelineAction.EXECUTE

    @property
    def needs_clarification(self) -> bool:
        """Check if clarification is needed."""
        return self.recommended_action == PipelineAction.CLARIFY

    @property
    def needs_redirect(self) -> bool:
        """Check if redirect is recommended."""
        return self.recommended_action == PipelineAction.REDIRECT


# ============================================
# Conversation Context for Pipeline
# ============================================


@dataclass
class PipelineConversationContext:
    """Conversation context for the pipeline.

    Attributes:
        session_id: Unique session identifier
        recent_messages: Recent conversation history
        current_state: Current application state
        active_entity: Currently focused entity ID
        user_preferences: Known user preferences
    """

    session_id: str
    recent_messages: list[dict[str, Any]] = field(default_factory=list)
    current_state: Optional[str] = None
    active_entity: Optional[str] = None
    user_preferences: Optional[dict[str, Any]] = None

    def to_drift_context(self) -> ConversationDriftContext:
        """Convert to drift-specific context.

        Returns:
            ConversationDriftContext for drift analysis
        """
        return ConversationDriftContext(
            session_id=self.session_id,
            current_topic=self.current_state,
        )


# ============================================
# Available Component Definition
# ============================================


@dataclass
class AvailableComponent:
    """Represents an available LUI component for routing.

    Attributes:
        component_id: Unique component identifier
        component_type: Type of component (ACTION, QUERY, etc.)
        intent: Description of what the component does
        invocation_phrases: Phrases that trigger this component
        parameters: Available parameters
        domain: Domain the component belongs to
    """

    component_id: str
    component_type: str
    intent: str
    invocation_phrases: list[str] = field(default_factory=list)
    parameters: list[dict[str, Any]] = field(default_factory=list)
    domain: Optional[str] = None

    def to_intent_definition(self) -> IntentDefinition:
        """Convert to IntentDefinition for semantic analysis.

        Returns:
            IntentDefinition for this component
        """
        return IntentDefinition(
            name=self.component_id,
            description=self.intent,
            keywords=self.invocation_phrases[:5] if self.invocation_phrases else [],
            examples=self.invocation_phrases[5:10] if len(self.invocation_phrases) > 5 else [],
            capability_id=self.component_id,
            domain=self.domain,
        )


# ============================================
# Main Intent Pipeline With Drift
# ============================================


class IntentPipelineWithDrift:
    """Enhanced intent pipeline with drift detection.

    This class integrates drift detection into the intent extraction pipeline,
    providing seamless detection and graceful handling of intent drift.

    The pipeline flow is:
    1. User Input
    2. Semantic Analysis (parallel with intent classification)
    3. Intent Classification ←→ Drift Detection
    4. Confidence Assessment
    5. Route: Execute | Clarify | Redirect | Reject
    6. Response Generation

    Attributes:
        config: Pipeline configuration
        drift_config: Drift detection configuration
        semantic_analyzer: Semantic analysis component
        drift_classifier: Drift classification component
        confidence_assessor: Confidence assessment component
        response_generator: Response generation component
        redirect_engine: Redirect suggestion component
        coherence_tracker: Conversation coherence tracking

    Example:
        >>> pipeline = IntentPipelineWithDrift(
        ...     available_components=components,
        ...     core_capabilities=["search", "create"],
        ... )
        >>> result = pipeline.extract_intent_with_drift(
        ...     user_input="Can you help me invest in stocks?",
        ...     conversation_context=context,
        ... )
        >>> if result.should_proceed:
        ...     execute_intent(result.intent_extraction)
        ... else:
        ...     show_response(result.response)
    """

    def __init__(
        self,
        config: Optional[PipelineDriftConfig] = None,
        drift_config: Optional[DriftDetectionConfig] = None,
        available_components: Optional[list[AvailableComponent]] = None,
        core_capabilities: Optional[list[str]] = None,
        supported_domains: Optional[list[str]] = None,
        # Sub-component configs
        semantic_config: Optional[SemanticAnalyzerConfig] = None,
        classifier_config: Optional[DriftClassifierConfig] = None,
        assessor_config: Optional[ConfidenceAssessorConfig] = None,
        response_config: Optional[ResponseGeneratorConfig] = None,
        redirect_config: Optional[RedirectEngineConfig] = None,
        coherence_config: Optional[CoherenceTrackerConfig] = None,
    ):
        """Initialize the intent pipeline with drift detection.

        Args:
            config: Pipeline configuration
            drift_config: Drift detection configuration
            available_components: Available LUI components
            core_capabilities: Names of core capabilities
            supported_domains: Supported domains
            semantic_config: Semantic analyzer configuration
            classifier_config: Drift classifier configuration
            assessor_config: Confidence assessor configuration
            response_config: Response generator configuration
            redirect_config: Redirect engine configuration
            coherence_config: Coherence tracker configuration
        """
        self.config = config or PipelineDriftConfig()
        self.drift_config = drift_config or DriftDetectionConfig(
            supported_domains=supported_domains or []
        )

        # Convert components to intent definitions
        self._available_components = available_components or []
        intent_definitions = [c.to_intent_definition() for c in self._available_components]

        # Initialize sub-components
        self.semantic_analyzer = SemanticAnalyzer(
            config=semantic_config,
            domain_keywords=supported_domains or [],
        )

        self.drift_classifier = DriftClassifier(
            config=classifier_config,
        )

        self.confidence_assessor = ConfidenceAssessor(
            config=assessor_config,
        )

        self.response_generator = GracefulResponseGenerator(
            config=response_config,
        )

        self.redirect_engine = RedirectSuggestionEngine(
            config=redirect_config,
            available_intents=intent_definitions,
            core_capability_names=core_capabilities or [],
        )

        self.coherence_tracker = ConversationCoherenceTracker(
            config=coherence_config,
        )

        self._core_capabilities = set(core_capabilities or [])

    def set_available_components(self, components: list[AvailableComponent]) -> None:
        """Set the available components.

        Args:
            components: List of available components
        """
        self._available_components = components
        intent_definitions = [c.to_intent_definition() for c in components]
        self.redirect_engine.set_available_intents(intent_definitions)

    def set_core_capabilities(self, names: list[str]) -> None:
        """Set the core capability names.

        Args:
            names: List of core capability names
        """
        self._core_capabilities = set(names)
        self.redirect_engine.set_core_capabilities(names)

    def extract_intent_with_drift(
        self,
        user_input: str,
        conversation_context: Optional[PipelineConversationContext] = None,
        available_components: Optional[list[AvailableComponent]] = None,
        intent_extraction_result: Optional[IntentExtractionResult] = None,
    ) -> IntentExtractionWithDrift:
        """Extract intent with integrated drift detection.

        This is the main entry point for the pipeline. It performs:
        1. Semantic analysis of the input
        2. Intent classification (or uses provided result)
        3. Drift detection and classification
        4. Confidence assessment
        5. Action determination
        6. Response generation

        Args:
            user_input: The user's input text
            conversation_context: Optional conversation context
            available_components: Optional override for available components
            intent_extraction_result: Optional pre-computed intent extraction

        Returns:
            IntentExtractionWithDrift with full analysis and response
        """
        start_time = time.time()

        # Use provided components or fall back to configured ones
        components = available_components or self._available_components
        intent_definitions = [c.to_intent_definition() for c in components]

        # Update redirect engine with current intents
        if available_components:
            self.redirect_engine.set_available_intents(intent_definitions)

        # Get drift context from conversation context
        drift_context = None
        if conversation_context:
            drift_context = conversation_context.to_drift_context()

        # Step 1: Semantic Analysis
        semantic_result = self._perform_semantic_analysis(
            user_input, intent_definitions
        )

        # Step 2: Intent Classification (use provided or extract)
        intent_extraction = self._get_or_extract_intent(
            user_input, semantic_result, intent_extraction_result
        )

        # Step 3: Drift Detection
        drift_analysis = self._perform_drift_analysis(
            user_input, semantic_result, intent_extraction
        )

        # Step 4: Confidence Assessment
        confidence_assessment = self._assess_confidence(
            intent_extraction, drift_analysis, semantic_result
        )

        # Step 5: Determine Action
        recommended_action = self._determine_action(
            drift_analysis, confidence_assessment, intent_extraction
        )

        # Step 6: Get Redirect Suggestions (if needed)
        redirect_suggestions: list[RedirectSuggestion] = []
        if recommended_action in (PipelineAction.REDIRECT, PipelineAction.CLARIFY):
            redirect_context = self._build_redirect_context(
                conversation_context, intent_extraction
            )
            redirect_suggestions = self.redirect_engine.suggest_redirects(
                semantic_result=semantic_result,
                drift_type=drift_analysis.drift_type,
                max_suggestions=self.config.max_redirect_suggestions,
                context=redirect_context,
            )

        # Step 7: Generate Response
        response = self._generate_response(
            user_input=user_input,
            intent_extraction=intent_extraction,
            drift_analysis=drift_analysis,
            recommended_action=recommended_action,
            redirect_suggestions=redirect_suggestions,
        )

        # Step 8: Update Coherence Tracker (if enabled)
        if self.config.enable_coherence_tracking:
            self.coherence_tracker.add_turn(
                user_input=user_input,
                detected_intent=intent_extraction.intent_name,
                drift_score=drift_analysis.drift_score,
            )

        processing_time_ms = int((time.time() - start_time) * 1000)

        return IntentExtractionWithDrift(
            intent_extraction=intent_extraction,
            drift_analysis=drift_analysis,
            confidence_assessment=confidence_assessment,
            recommended_action=recommended_action,
            response=response,
            semantic_analysis=semantic_result if self.config.include_semantic_details else None,
            redirect_suggestions=redirect_suggestions,
            processing_time_ms=processing_time_ms,
        )

    def _perform_semantic_analysis(
        self,
        user_input: str,
        intent_definitions: list[IntentDefinition],
    ) -> SemanticAnalysis:
        """Perform semantic analysis on the input.

        Args:
            user_input: User's input text
            intent_definitions: Available intent definitions

        Returns:
            SemanticAnalysis result
        """
        # Convert intent definitions to dict format for analyzer
        intent_dicts = [
            {
                "name": intent.name,
                "description": intent.description,
                "keywords": intent.keywords,
                "examples": intent.examples,
                "capability_id": intent.capability_id,
                "domain": intent.domain,
            }
            for intent in intent_definitions
        ]

        return self.semantic_analyzer.analyze(
            user_input=user_input,
            available_intents=intent_dicts,
            domain_keywords=self.drift_config.supported_domains,
        )

    def _get_or_extract_intent(
        self,
        user_input: str,
        semantic_result: SemanticAnalysis,
        provided_extraction: Optional[IntentExtractionResult],
    ) -> SimpleIntentExtraction:
        """Get or extract intent from input.

        Args:
            user_input: User's input text
            semantic_result: Semantic analysis result
            provided_extraction: Optional pre-computed extraction

        Returns:
            SimpleIntentExtraction result
        """
        if provided_extraction:
            # Convert protocol to our internal type
            return SimpleIntentExtraction(
                intent_name=provided_extraction.intent_name,
                intent_category="unknown",
                target_component=provided_extraction.target_component,
                confidence=provided_extraction.confidence,
            )

        # Use semantic analysis to determine best intent
        if semantic_result.nearest_intents:
            best_intent = semantic_result.nearest_intents[0]
            return SimpleIntentExtraction(
                intent_name=best_intent.intent_name,
                intent_category="inferred",
                target_component=best_intent.capability_id,
                confidence=best_intent.similarity,
                is_ambiguous=len(semantic_result.nearest_intents) > 1
                and semantic_result.nearest_intents[0].similarity
                - semantic_result.nearest_intents[1].similarity
                < 0.1,
            )

        # No intent found
        return SimpleIntentExtraction(
            intent_name="unknown",
            intent_category="none",
            target_component=None,
            confidence=0.0,
            is_ambiguous=True,
            suggested_clarification="Could you please clarify what you'd like to do?",
        )

    def _perform_drift_analysis(
        self,
        user_input: str,
        semantic_result: SemanticAnalysis,
        intent_extraction: SimpleIntentExtraction,
    ) -> DriftAnalysis:
        """Perform drift analysis.

        Args:
            user_input: User's input text
            semantic_result: Semantic analysis result
            intent_extraction: Intent extraction result

        Returns:
            DriftAnalysis result
        """
        if not self.config.enable_drift_detection:
            # Return no-drift result if detection is disabled
            return DriftAnalysis(
                current_input=user_input,
                drift_score=0.0,
                drift_type=DriftType.NONE,
                confidence=1.0,
                semantic_distance=0.0,
                graceful_response="",
            )

        # Classify drift using the classifier
        classification = self.drift_classifier.classify(
            user_input=user_input,
            semantic_analysis=semantic_result,
        )

        # Calculate semantic distance from nearest intent
        semantic_distance = 1.0 - intent_extraction.confidence
        if semantic_result.nearest_intents:
            semantic_distance = 1.0 - semantic_result.nearest_intents[0].similarity

        # Generate graceful response if needed
        graceful_response = ""
        if classification.drift_type != DriftType.NONE:
            response = self.response_generator.generate_simple(
                drift_type=classification.drift_type,
                user_input=user_input,
            )
            graceful_response = response.primary_message

        return DriftAnalysis(
            current_input=user_input,
            drift_score=classification.drift_score,
            drift_type=classification.drift_type,
            confidence=classification.confidence,
            semantic_distance=semantic_distance,
            graceful_response=graceful_response,
            original_intent=intent_extraction.intent_name if intent_extraction.confidence > 0 else None,
        )

    def _assess_confidence(
        self,
        intent_extraction: SimpleIntentExtraction,
        drift_analysis: DriftAnalysis,
        semantic_result: SemanticAnalysis,
    ) -> ConfidenceAssessment:
        """Assess confidence in the extraction.

        Args:
            intent_extraction: Intent extraction result
            drift_analysis: Drift analysis result
            semantic_result: Semantic analysis result

        Returns:
            ConfidenceAssessment result
        """
        # Calculate individual factor scores

        # Intent confidence (40% weight)
        intent_confidence = intent_extraction.confidence

        # Entity confidence - use inverse of ambiguity (20% weight)
        entity_confidence = 0.5 if intent_extraction.is_ambiguous else 1.0

        # Context coherence - based on drift score (20% weight)
        context_coherence = 1.0 - drift_analysis.drift_score

        # Semantic similarity - based on abstraction level and nearest intent (20% weight)
        semantic_similarity = 1.0
        if semantic_result.abstraction_level == AbstractionLevel.ABSTRACT:
            semantic_similarity = 0.6
        elif semantic_result.abstraction_level == AbstractionLevel.PHILOSOPHICAL:
            semantic_similarity = 0.3
        if semantic_result.nearest_intents:
            # Blend with nearest intent similarity
            semantic_similarity = (
                semantic_similarity + semantic_result.nearest_intents[0].similarity
            ) / 2

        # Use confidence assessor with raw scores
        assessment_result = self.confidence_assessor.assess_with_scores(
            intent_confidence=intent_confidence,
            entity_confidence=entity_confidence,
            context_coherence=context_coherence,
            semantic_similarity=semantic_similarity,
        )

        # Convert to ConfidenceAssessment type
        return assessment_result.to_confidence_assessment()

    def _determine_action(
        self,
        drift_analysis: DriftAnalysis,
        confidence_assessment: ConfidenceAssessment,
        intent_extraction: SimpleIntentExtraction,
    ) -> PipelineAction:
        """Determine the recommended pipeline action.

        Args:
            drift_analysis: Drift analysis result
            confidence_assessment: Confidence assessment
            intent_extraction: Intent extraction result

        Returns:
            Recommended PipelineAction
        """
        # Map recommended action from confidence assessor
        action_map = {
            RecommendedAction.PROCEED: PipelineAction.EXECUTE,
            RecommendedAction.PROCEED_WITH_CAVEAT: PipelineAction.EXECUTE,
            RecommendedAction.CLARIFY: PipelineAction.CLARIFY,
            RecommendedAction.REDIRECT: PipelineAction.REDIRECT,
            RecommendedAction.ESCALATE: PipelineAction.ESCALATE,
            RecommendedAction.DECLINE: PipelineAction.REJECT,
        }

        base_action = action_map.get(
            confidence_assessment.recommended_action, PipelineAction.CLARIFY
        )

        # Override based on drift analysis
        if drift_analysis.drift_type == DriftType.DOMAIN_SHIFT:
            return PipelineAction.REDIRECT

        if drift_analysis.drift_type in (
            DriftType.ABSTRACTION_CLIMB,
            DriftType.PERSONALIZATION,
        ):
            if self.config.fallback_to_clarification:
                return PipelineAction.CLARIFY
            return PipelineAction.REJECT

        if drift_analysis.drift_type == DriftType.AMBIGUOUS:
            return PipelineAction.CLARIFY

        # Check for low confidence
        if confidence_assessment.confidence_tier in (
            ConfidenceTier.LOW,
            ConfidenceTier.VERY_LOW,
        ):
            if self.config.fallback_to_clarification:
                return PipelineAction.CLARIFY
            return PipelineAction.REDIRECT

        # Check intent ambiguity
        if intent_extraction.is_ambiguous:
            return PipelineAction.CLARIFY

        return base_action

    def _build_redirect_context(
        self,
        conversation_context: Optional[PipelineConversationContext],
        intent_extraction: SimpleIntentExtraction,
    ) -> RedirectContext:
        """Build redirect context from conversation context.

        Args:
            conversation_context: Optional conversation context
            intent_extraction: Intent extraction result

        Returns:
            RedirectContext for redirect suggestions
        """
        failed_intents: list[str] = []
        successful_intents: list[str] = []
        current_domain: Optional[str] = None
        turn_count = 0

        if conversation_context:
            turn_count = len(conversation_context.recent_messages)
            current_domain = conversation_context.current_state

            # Extract intents from recent messages
            for msg in conversation_context.recent_messages:
                if msg.get("role") == "user" and msg.get("intent"):
                    intent_name = msg["intent"]
                    if msg.get("success", True):
                        successful_intents.append(intent_name)
                    else:
                        failed_intents.append(intent_name)

        return RedirectContext(
            failed_intents=failed_intents,
            successful_intents=successful_intents,
            current_domain=current_domain,
            turn_count=turn_count,
        )

    def _generate_response(
        self,
        user_input: str,
        intent_extraction: SimpleIntentExtraction,
        drift_analysis: DriftAnalysis,
        recommended_action: PipelineAction,
        redirect_suggestions: list[RedirectSuggestion],
    ) -> str:
        """Generate appropriate response based on analysis.

        Args:
            user_input: User's input text
            intent_extraction: Intent extraction result
            drift_analysis: Drift analysis result
            recommended_action: Recommended action
            redirect_suggestions: Redirect suggestions

        Returns:
            Response string
        """
        if recommended_action == PipelineAction.EXECUTE:
            # Standard execution response
            return f"I'll help you with {intent_extraction.intent_name}."

        if recommended_action == PipelineAction.CLARIFY:
            if intent_extraction.suggested_clarification:
                return intent_extraction.suggested_clarification
            # Generate clarification using generate_simple
            response = self.response_generator.generate_simple(
                drift_type=drift_analysis.drift_type,
                user_input=user_input,
            )
            if response.follow_up_prompt:
                return response.follow_up_prompt
            return response.primary_message

        if recommended_action == PipelineAction.REDIRECT:
            # Build redirect message with suggestions
            alternatives = [s.transition_phrase for s in redirect_suggestions[:3]]
            response = self.response_generator.generate_simple(
                drift_type=drift_analysis.drift_type,
                user_input=user_input,
                alternatives=alternatives if alternatives else None,
            )
            return response.primary_message

        if recommended_action == PipelineAction.REJECT:
            response = self.response_generator.generate_simple(
                drift_type=drift_analysis.drift_type,
                user_input=user_input,
            )
            return response.primary_message

        if recommended_action == PipelineAction.ESCALATE:
            response = self.response_generator.generate_simple(
                drift_type=DriftType.SCOPE_EXPANSION,  # Use scope expansion for escalation
                user_input=user_input,
            )
            return response.primary_message

        return drift_analysis.graceful_response or "I'm not sure how to help with that."

    def get_drift_detection_result(
        self,
        user_input: str,
        conversation_context: Optional[PipelineConversationContext] = None,
    ) -> DriftDetectionResult:
        """Get a detailed drift detection result.

        This method provides the full DriftDetectionResult format
        for compatibility with other drift detection consumers.

        Args:
            user_input: User's input text
            conversation_context: Optional conversation context

        Returns:
            DriftDetectionResult with full details
        """
        start_time = time.time()

        # Get the full extraction result
        result = self.extract_intent_with_drift(
            user_input=user_input,
            conversation_context=conversation_context,
        )

        processing_time_ms = int((time.time() - start_time) * 1000)

        # Generate graceful response if needed
        graceful_response: Optional[GracefulResponse] = None
        if result.has_drift and self.config.include_graceful_response:
            # Create a DriftClassification from DriftAnalysis
            classification = DriftClassification(
                drift_type=result.drift_analysis.drift_type,
                drift_score=result.drift_analysis.drift_score,
                confidence=result.drift_analysis.confidence,
            )
            graceful_response = self.response_generator.generate(
                drift_classification=classification,
                redirect_suggestions=result.redirect_suggestions,
                user_input=user_input,
            )

        return DriftDetectionResult(
            input=user_input,
            config=self.drift_config,
            analysis=result.drift_analysis,
            confidence_assessment=result.confidence_assessment,
            semantic_analysis=result.semantic_analysis
            or SemanticAnalysis(
                input_text=user_input,
                abstraction_level=AbstractionLevel.CONCRETE,
            ),
            processing_time_ms=processing_time_ms,
            suggested_response=graceful_response,
        )

    def get_coherence_metrics(self) -> dict[str, Any]:
        """Get current coherence metrics.

        Returns:
            Dictionary with coherence metrics
        """
        metrics = self.coherence_tracker.get_metrics()
        return {
            "average_coherence": metrics.average_coherence,
            "turn_count": metrics.turn_count,
            "drift_rate": metrics.drift_rate,
            "trend": metrics.trend.value if metrics.trend else None,
            "recovery_rate": metrics.recovery_rate,
        }

    def reset_coherence_tracker(self) -> None:
        """Reset the coherence tracker for a new conversation."""
        self.coherence_tracker.reset()

    def should_reset_context(self) -> tuple[bool, Optional[str]]:
        """Check if context should be reset based on coherence.

        Returns:
            Tuple of (should_reset, reason)
        """
        trigger = self.coherence_tracker.should_reset_context()
        if trigger:
            return True, trigger.reason.value
        return False, None
