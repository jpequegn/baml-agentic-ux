# Intent Drift Detection API Reference

This document provides a complete API reference for the Intent Drift Detection module.

## Table of Contents

- [Core Types](#core-types)
- [Semantic Analyzer](#semantic-analyzer)
- [Drift Classifier](#drift-classifier)
- [Confidence Assessor](#confidence-assessor)
- [Response Generator](#response-generator)
- [Coherence Tracker](#coherence-tracker)
- [Redirect Engine](#redirect-engine)
- [Intent Pipeline](#intent-pipeline)
- [Analytics](#analytics)
- [Template Library](#template-library)

---

## Core Types

### DriftType

Enumeration of drift types that can be detected.

```python
from src.intent_drift import DriftType

class DriftType(Enum):
    NONE = "none"                       # Within capability
    SCOPE_EXPANSION = "scope_expansion" # Related but unsupported
    DOMAIN_SHIFT = "domain_shift"       # Different domain entirely
    ABSTRACTION_CLIMB = "abstraction_climb"  # Too abstract
    PERSONALIZATION = "personalization" # Requires user data
    TEMPORAL_DRIFT = "temporal_drift"   # Past/future issues
    AMBIGUOUS = "ambiguous"             # Multiple intents
```

### DriftAnalysis

Main drift detection result.

```python
@dataclass
class DriftAnalysis:
    current_input: str           # User input analyzed
    drift_score: float           # 0.0 = on topic, 1.0 = off topic
    drift_type: DriftType        # Classification
    confidence: float            # Detection confidence (0-1)
    semantic_distance: float     # Distance from supported intents
    graceful_response: str       # Suggested response
    original_intent: Optional[str]
    last_supported_intent: Optional[str]
    suggested_redirects: list[RedirectSuggestion]

    @property
    def has_drift(self) -> bool: ...
    @property
    def needs_clarification(self) -> bool: ...
    @property
    def has_redirects(self) -> bool: ...
```

### ConfidenceAssessment

Multi-factor confidence assessment.

```python
@dataclass
class ConfidenceAssessment:
    overall_confidence: float           # 0-1 score
    confidence_tier: ConfidenceTier     # Categorical tier
    recommended_action: RecommendedAction
    explanation: str
    factor_scores: list[ConfidenceFactorScore]

    @classmethod
    def from_score(cls, score: float, explanation: str = "") -> ConfidenceAssessment
```

### ConfidenceTier

```python
class ConfidenceTier(Enum):
    VERY_HIGH = "very_high"  # 95%+
    HIGH = "high"            # 80-94%
    MEDIUM = "medium"        # 60-79%
    LOW = "low"              # 40-59%
    VERY_LOW = "very_low"    # <40%
```

### RecommendedAction

```python
class RecommendedAction(Enum):
    PROCEED = "proceed"
    PROCEED_WITH_CAVEAT = "proceed_with_caveat"
    CLARIFY = "clarify"
    REDIRECT = "redirect"
    ESCALATE = "escalate"
    DECLINE = "decline"
```

---

## Semantic Analyzer

Analyzes semantic similarity between user input and supported intents.

### SemanticAnalyzer

```python
from src.intent_drift import SemanticAnalyzer, SemanticAnalyzerConfig, IntentDefinition

class SemanticAnalyzer:
    def __init__(
        self,
        config: SemanticAnalyzerConfig = None,
        supported_intents: list[IntentDefinition] = None,
    ): ...

    def analyze(self, user_input: str) -> SemanticAnalysis:
        """Analyze user input for semantic similarity to supported intents."""

    def get_nearest_intents(
        self,
        user_input: str,
        limit: int = 5,
    ) -> list[NearestIntent]:
        """Get the closest matching supported intents."""

    def calculate_similarity(
        self,
        text1: str,
        text2: str,
    ) -> float:
        """Calculate similarity between two texts."""
```

### SemanticAnalyzerConfig

```python
@dataclass
class SemanticAnalyzerConfig:
    similarity_threshold: float = 0.6      # Min similarity for match
    use_embeddings: bool = False           # Use embedding-based similarity
    max_cached_embeddings: int = 1000      # Embedding cache size
```

### IntentDefinition

```python
@dataclass
class IntentDefinition:
    name: str                              # Intent identifier
    description: str                       # What this intent does
    examples: list[str]                    # Example utterances
    capability_id: Optional[str] = None    # Associated capability
    keywords: list[str] = field(default_factory=list)
```

---

## Drift Classifier

Classifies user input into drift types.

### DriftClassifier

```python
from src.intent_drift import DriftClassifier, DriftClassifierConfig

class DriftClassifier:
    def __init__(self, config: DriftClassifierConfig = None): ...

    def classify(
        self,
        user_input: str,
        semantic_analysis: SemanticAnalysis = None,
    ) -> DriftClassification:
        """Classify drift type for user input."""

    def get_drift_score(
        self,
        user_input: str,
        semantic_analysis: SemanticAnalysis = None,
    ) -> float:
        """Get numeric drift score (0-1)."""
```

### DriftClassifierConfig

```python
@dataclass
class DriftClassifierConfig:
    drift_threshold: float = 0.5          # Score threshold for drift
    abstraction_patterns: list[str] = ... # Patterns for abstraction
    temporal_patterns: list[str] = ...    # Patterns for temporal
    personalization_patterns: list[str] = ...
```

### DriftClassification

```python
@dataclass
class DriftClassification:
    drift_type: DriftType
    drift_score: float
    confidence: float
    detected_intent: Optional[str]
    pattern_matches: list[PatternMatch]
    explanation: str
```

---

## Confidence Assessor

Assesses confidence in intent detection results.

### ConfidenceAssessor

```python
from src.intent_drift import ConfidenceAssessor, ConfidenceAssessorConfig

class ConfidenceAssessor:
    def __init__(self, config: ConfidenceAssessorConfig = None): ...

    def assess(
        self,
        classification: DriftClassification,
        semantic_analysis: SemanticAnalysis = None,
    ) -> ConfidenceAssessment:
        """Assess confidence in classification result."""

    def get_recommended_action(
        self,
        confidence: float,
        drift_type: DriftType,
    ) -> RecommendedAction:
        """Get recommended action based on confidence."""
```

### ConfidenceAssessorConfig

```python
@dataclass
class ConfidenceAssessorConfig:
    very_high_threshold: float = 0.95
    high_threshold: float = 0.80
    medium_threshold: float = 0.60
    low_threshold: float = 0.40
```

---

## Response Generator

Generates graceful responses for drift scenarios.

### GracefulResponseGenerator

```python
from src.intent_drift import GracefulResponseGenerator, ResponseGeneratorConfig

class GracefulResponseGenerator:
    def __init__(self, config: ResponseGeneratorConfig = None): ...

    def generate(
        self,
        drift_type: DriftType,
        user_input: str,
        confidence: float = 0.5,
        alternatives: list[str] = None,
        tone: DriftResponseTone = None,
    ) -> str:
        """Generate graceful response for drift."""

    def get_template(self, drift_type: DriftType) -> DriftResponseTemplate:
        """Get response template for drift type."""
```

### ResponseGeneratorConfig

```python
@dataclass
class ResponseGeneratorConfig:
    default_tone: DriftResponseTone = DriftResponseTone.HELPFUL
    include_alternatives: bool = True
    max_alternatives: int = 3
```

---

## Coherence Tracker

Tracks conversation coherence across multiple turns.

### ConversationCoherenceTracker

```python
from src.intent_drift import ConversationCoherenceTracker, CoherenceTrackerConfig

class ConversationCoherenceTracker:
    def __init__(self, config: CoherenceTrackerConfig = None): ...

    def add_turn(
        self,
        session_id: str,
        user_input: str,
        detected_intent: str = None,
        drift_type: DriftType = None,
        drift_score: float = 0.0,
    ) -> TurnCoherence:
        """Add a conversation turn and calculate coherence."""

    def get_coherence(self, session_id: str) -> CoherenceMetrics:
        """Get coherence metrics for a session."""

    def should_reset_context(self, session_id: str) -> ContextResetTrigger:
        """Check if context should be reset."""

    def clear_session(self, session_id: str) -> None:
        """Clear session history."""
```

### CoherenceTrackerConfig

```python
@dataclass
class CoherenceTrackerConfig:
    max_turns: int = 20
    coherence_threshold: float = 0.6
    drift_decay_factor: float = 0.9
```

### CoherenceMetrics

```python
@dataclass
class CoherenceMetrics:
    session_id: str
    turn_count: int
    coherence_score: float
    topic_consistency: float
    intent_stability: float
    drift_trend: DriftTrend
    recent_drift_count: int
```

---

## Redirect Engine

Suggests alternative capabilities when drift is detected.

### RedirectSuggestionEngine

```python
from src.intent_drift import RedirectSuggestionEngine, RedirectEngineConfig

class RedirectSuggestionEngine:
    def __init__(
        self,
        config: RedirectEngineConfig = None,
        supported_intents: list[IntentDefinition] = None,
    ): ...

    def get_suggestions(
        self,
        user_input: str,
        drift_type: DriftType,
        limit: int = 3,
    ) -> list[ScoredSuggestion]:
        """Get redirect suggestions for drifted request."""

    def get_best_suggestion(
        self,
        user_input: str,
        drift_type: DriftType,
    ) -> Optional[ScoredSuggestion]:
        """Get single best redirect suggestion."""
```

### RedirectEngineConfig

```python
@dataclass
class RedirectEngineConfig:
    min_similarity: float = 0.3
    max_suggestions: int = 5
    enable_phrase_generation: bool = True
```

### ScoredSuggestion

```python
@dataclass
class ScoredSuggestion:
    target_intent: str
    similarity_score: float
    redirect_reason: str
    transition_phrase: str
    confidence: float
```

---

## Intent Pipeline

Unified pipeline combining all drift detection components.

### IntentPipelineWithDrift

```python
from src.intent_drift import IntentPipelineWithDrift, PipelineDriftConfig

class IntentPipelineWithDrift:
    def __init__(
        self,
        config: PipelineDriftConfig = None,
        available_components: list[AvailableComponent] = None,
    ): ...

    def process(
        self,
        user_input: str,
        context: PipelineConversationContext = None,
    ) -> IntentExtractionWithDrift:
        """Process user input through full drift-aware pipeline."""
```

### PipelineDriftConfig

```python
@dataclass
class PipelineDriftConfig:
    drift_threshold: float = 0.5
    confidence_threshold: float = 0.6
    enable_redirects: bool = True
    max_redirects: int = 3
    enable_coherence_tracking: bool = True
```

### IntentExtractionWithDrift

```python
@dataclass
class IntentExtractionWithDrift:
    intent: Optional[str]
    component_id: Optional[str]
    confidence: float
    drift_type: DriftType
    drift_score: float
    action: PipelineAction
    graceful_response: Optional[str]
    redirects: list[ScoredSuggestion]
```

---

## Analytics

Track and analyze drift events.

### DriftAnalytics

```python
from src.intent_drift import DriftAnalytics, create_drift_analytics

class DriftAnalytics:
    def __init__(
        self,
        store: DriftEventStore = None,
        total_interactions: Callable[[], int] = None,
    ): ...

    def log_event(
        self,
        session_id: str,
        turn_id: str,
        drift_type: DriftType,
        drift_score: float,
        user_input: str,
        **kwargs,
    ) -> DriftAnalyticsEvent:
        """Log a drift event."""

    def get_events(
        self,
        time_range: TimeRange = None,
        session_id: str = None,
        drift_type: DriftType = None,
        severity: DriftSeverity = None,
        limit: int = None,
    ) -> list[DriftAnalyticsEvent]:
        """Query drift events."""

    def calculate_metrics(
        self,
        time_range: TimeRange = None,
        total_interactions: int = None,
    ) -> DriftMetrics:
        """Calculate drift metrics."""

    def analyze_patterns(
        self,
        time_range: TimeRange = None,
        min_frequency: int = 3,
        min_confidence: float = 0.6,
    ) -> list[DriftPattern]:
        """Detect drift patterns."""

    def get_summary(
        self,
        time_range: TimeRange = None,
    ) -> DriftSummary:
        """Generate comprehensive drift summary."""

    def export_json(
        self,
        time_range: TimeRange = None,
        include_summary: bool = True,
    ) -> str:
        """Export events to JSON."""

    def export_csv(
        self,
        time_range: TimeRange = None,
    ) -> str:
        """Export events to CSV."""
```

### DriftMetrics

```python
@dataclass
class DriftMetrics:
    total_events: int
    total_sessions: int
    drift_rate: float
    recovery_rate: float
    avg_drift_score: float
    median_drift_score: float
    avg_response_time_ms: Optional[float]
    severity_distribution: dict[str, int]
    drift_type_distribution: dict[str, int]
    recovery_method_distribution: dict[str, int]
    channel_distribution: dict[str, int]
    hourly_distribution: dict[int, int]
```

---

## Template Library

Manage response templates.

### TemplateLibrary

```python
from src.intent_drift import TemplateLibrary, ResponseTemplate, get_default_library

class TemplateLibrary:
    def __init__(self, templates: list[ResponseTemplate] = None): ...

    def get_template(
        self,
        drift_type: DriftType,
        category: TemplateCategory = None,
    ) -> Optional[ResponseTemplate]:
        """Get template for drift type."""

    def get_all_templates(
        self,
        drift_type: DriftType = None,
        category: TemplateCategory = None,
    ) -> list[ResponseTemplate]:
        """Get all matching templates."""

    def add_template(self, template: ResponseTemplate) -> None:
        """Add custom template."""

    def render(
        self,
        template_id: str,
        variables: dict[str, str],
    ) -> str:
        """Render template with variables."""

# Factory function
def get_default_library() -> TemplateLibrary:
    """Get library with all default templates."""
```

---

## Quick Start

```python
from src.intent_drift import (
    SemanticAnalyzer,
    DriftClassifier,
    ConfidenceAssessor,
    GracefulResponseGenerator,
    IntentDefinition,
)

# Define supported intents
intents = [
    IntentDefinition(
        name="create-task",
        description="Create a new task",
        examples=["Create task", "Add todo"],
    ),
]

# Create components
analyzer = SemanticAnalyzer(supported_intents=intents)
classifier = DriftClassifier()
assessor = ConfidenceAssessor()
generator = GracefulResponseGenerator()

# Process user input
user_input = "What's the weather?"

semantic = analyzer.analyze(user_input)
classification = classifier.classify(user_input, semantic)
confidence = assessor.assess(classification, semantic)

if classification.drift_type != DriftType.NONE:
    response = generator.generate(
        drift_type=classification.drift_type,
        user_input=user_input,
    )
    print(response)
```
