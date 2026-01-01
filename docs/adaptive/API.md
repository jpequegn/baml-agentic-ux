# Adaptive Personalization API Reference

This document provides the API reference for the adaptive personalization system.

## BAML Types

### Expertise Detection

#### ExpertiseLevel (enum)

```baml
enum ExpertiseLevel {
  NOVICE       // New to the system
  BEGINNER     // Some familiarity
  INTERMEDIATE // Regular user
  ADVANCED     // Power user
  EXPERT       // Deep system knowledge
}
```

#### ExpertiseFactor (class)

```baml
class ExpertiseFactor {
  factor_name string       // Name of the factor
  weight float             // Weight in overall score (0.0-1.0)
  raw_value float          // Raw measured value (0.0-1.0)
  weighted_value float     // Value after applying weight
  confidence float         // Confidence in measurement (0.0-1.0)
  evidence string[]        // Evidence supporting this value
}
```

#### ExpertiseEstimate (class)

```baml
class ExpertiseEstimate {
  estimated_level ExpertiseLevel
  expertise_score float
  previous_score float?
  score_delta float?
  factor_breakdown ExpertiseFactorBreakdown
  confidence float
  is_cold_start bool
  cold_start_reason string?
  interactions_analyzed int
  ema_alpha float
  ema_applied bool
  level_stable bool
  recommended_action string?
  action_rationale string?
}
```

### Metrics Collection

#### InteractionOutcome (enum)

```baml
enum InteractionOutcome {
  SUCCESS         // Completed successfully
  PARTIAL_SUCCESS // Completed with issues
  FAILED          // Did not complete
  ABANDONED       // User gave up
}
```

#### InteractionRecord (class)

```baml
class InteractionRecord {
  interaction_id string
  timestamp string           // ISO 8601 format
  intent_detected string
  outcome InteractionOutcome
  completion_time_ms int
  input_length int
  used_shortcut bool?
  help_requested bool?
  disambiguation_needed bool?
  error_count int?
  parameters_provided int?
  parameters_required int?
}
```

#### MetricsWindow (class)

```baml
class MetricsWindow {
  window_id string
  user_id string
  start_time string
  end_time string
  interaction_count int
  aggregate_metrics AggregateMetrics
  trend TrendDirection
}
```

### Level Transitions

#### TransitionDirection (enum)

```baml
enum TransitionDirection {
  UPGRADE   // Moving to higher level
  DOWNGRADE // Moving to lower level
}
```

#### TransitionDecision (class)

```baml
class TransitionDecision {
  should_transition bool
  direction TransitionDirection?
  from_level ExpertiseLevel
  to_level ExpertiseLevel?
  confidence float
  triggers TransitionTrigger[]
  blocked_by string?
  rationale string
}
```

### Privacy and Consent

#### ConsentType (enum)

```baml
enum ConsentType {
  PROFILING        // Track interaction patterns
  PERSONALIZATION  // Adapt responses based on behavior
  ANALYTICS        // Include in anonymous statistics
  DATA_EXPORT      // Allow profile data export
  RETENTION        // Allow data retention beyond session
}
```

#### ConsentStatus (enum)

```baml
enum ConsentStatus {
  PENDING   // Awaiting user response
  GRANTED   // User has granted consent
  DENIED    // User has denied consent
  WITHDRAWN // User has withdrawn consent
  EXPIRED   // Consent needs renewal
}
```

#### DSRType (enum)

```baml
enum DSRType {
  ACCESS       // GDPR Art. 15: Right to access
  RECTIFICATION // GDPR Art. 16: Right to correct
  ERASURE      // GDPR Art. 17: Right to be forgotten
  PORTABILITY  // GDPR Art. 20: Right to data portability
  OBJECTION    // GDPR Art. 21: Right to object
  RESTRICTION  // GDPR Art. 18: Right to restrict
}
```

### Adaptive Templates

#### TemplateParameters (class)

```baml
class TemplateParameters {
  includes_examples bool
  includes_tips bool
  includes_shortcuts bool
  explanation_depth string  // minimal, brief, standard, detailed, thorough
  show_advanced_options bool
  suggested_next_actions bool
  verbosity_level string
}
```

## Python API

### MetricsCollector

```python
class MetricsCollector:
    """Collects and aggregates user interaction metrics."""

    def __init__(self, user_id: str, privacy_mode: PrivacyMode = PrivacyMode.FULL):
        """Initialize collector for a user."""

    def record_interaction(self, interaction: InteractionRecord) -> None:
        """Record a single interaction."""

    def get_metrics_window(self, window_size: int = 30) -> MetricsWindow:
        """Get aggregated metrics for recent interactions."""

    def get_trend(self) -> TrendDirection:
        """Get trend direction based on recent performance."""

    def reset_session(self) -> None:
        """Reset session-specific metrics."""
```

### ExpertiseDetector

```python
class ExpertiseDetector:
    """Estimates user expertise from behavioral metrics."""

    def __init__(self, config: ExpertiseDetectionConfig = None):
        """Initialize detector with optional custom config."""

    def estimate_expertise(
        self,
        window: MetricsWindow,
        interactions: list[InteractionRecord],
        previous_estimate: ExpertiseEstimate = None
    ) -> ExpertiseEstimate:
        """
        Estimate expertise level.

        Args:
            window: Aggregated metrics window
            interactions: Recent interactions for detailed analysis
            previous_estimate: Previous estimate for EMA smoothing

        Returns:
            ExpertiseEstimate with level, score, and breakdown
        """

    def get_factor_breakdown(
        self,
        window: MetricsWindow,
        interactions: list[InteractionRecord]
    ) -> ExpertiseFactorBreakdown:
        """Get detailed factor breakdown without level estimation."""
```

### TransitionManager

```python
class TransitionManager:
    """Manages expertise level transitions."""

    def __init__(self, config: TransitionConfig = None):
        """Initialize with optional custom config."""

    def can_transition(
        self,
        user_id: str,
        from_level: ExpertiseLevel,
        to_level: ExpertiseLevel
    ) -> bool:
        """Check if transition is allowed (cooldown, etc.)."""

    def evaluate_transition(
        self,
        user_id: str,
        estimate: ExpertiseEstimate,
        current_level: ExpertiseLevel
    ) -> TransitionDecision:
        """
        Evaluate whether a transition should occur.

        Returns:
            TransitionDecision with recommendation and rationale
        """

    def record_transition(
        self,
        user_id: str,
        from_level: ExpertiseLevel,
        to_level: ExpertiseLevel,
        trigger: str
    ) -> TransitionRecord:
        """Record a completed transition."""

    def rollback_transition(
        self,
        user_id: str,
        transition_id: str
    ) -> bool:
        """Rollback a previous transition."""
```

### PrivacyManager

```python
class PrivacyManager:
    """Manages privacy consent and data subject requests."""

    def __init__(self):
        """Initialize privacy manager."""

    def check_consent(
        self,
        user_id: str,
        consent_type: ConsentType
    ) -> bool:
        """Check if user has granted specific consent."""

    def request_consent(
        self,
        user_id: str,
        consent_types: list[ConsentType],
        purpose: str = None
    ) -> ConsentRequest:
        """Create a consent request."""

    def process_consent_response(
        self,
        response: ConsentResponse,
        ip_address: str = None
    ) -> list[ConsentRecord]:
        """Process user's consent decisions."""

    def withdraw_consent(
        self,
        user_id: str,
        consent_types: list[ConsentType],
        reason: str = None
    ) -> list[ConsentRecord]:
        """Withdraw previously granted consent."""

    def handle_dsr(
        self,
        request: DataSubjectRequest
    ) -> DSRResponse:
        """Handle a GDPR data subject request."""

    def export_user_data(
        self,
        user_id: str,
        format: ExportFormat = ExportFormat.JSON
    ) -> ExportResult:
        """Export user's data for portability."""

    def delete_user_data(
        self,
        user_id: str
    ) -> DeletionResult:
        """Delete all user data (right to erasure)."""
```

### AdaptiveTemplateEngine

```python
class AdaptiveTemplateEngine:
    """Adapts response templates based on expertise level."""

    def __init__(self):
        """Initialize template engine."""

    def get_template_parameters(
        self,
        context: TemplateContext
    ) -> TemplateParameters:
        """
        Get template parameters for given context.

        Args:
            context: User context including expertise level

        Returns:
            TemplateParameters for response generation
        """

    def select_template(
        self,
        template_type: str,
        expertise_level: ExpertiseLevel
    ) -> str:
        """Select appropriate template for user level."""
```

## Error Handling

### Common Exceptions

```python
class AdaptivePersonalizationError(Exception):
    """Base exception for adaptive personalization."""
    pass

class ConsentRequiredError(AdaptivePersonalizationError):
    """Raised when operation requires consent not granted."""
    pass

class ColdStartError(AdaptivePersonalizationError):
    """Raised when insufficient data for reliable estimation."""
    pass

class TransitionBlockedError(AdaptivePersonalizationError):
    """Raised when transition blocked by cooldown or other constraint."""
    pass
```

### Error Handling Pattern

```python
try:
    estimate = detector.estimate_expertise(window, interactions)
except ColdStartError as e:
    # Use default level for new users
    estimate = ExpertiseEstimate(
        estimated_level=ExpertiseLevel.INTERMEDIATE,
        expertise_score=0.5,
        is_cold_start=True,
        cold_start_reason=str(e)
    )
```

## Usage Examples

### Basic Expertise Detection

```python
from src.lui_simulator.metrics import MetricsCollector, InteractionRecord
from src.lui_simulator.expertise import ExpertiseDetector

# Collect metrics
collector = MetricsCollector(user_id="user-123")
collector.record_interaction(InteractionRecord(
    interaction_id="int-1",
    timestamp="2024-01-01T12:00:00Z",
    intent_detected="search",
    outcome=InteractionOutcome.SUCCESS,
    completion_time_ms=1500,
    input_length=30,
    used_shortcut=True
))

# Estimate expertise
detector = ExpertiseDetector()
window = collector.get_metrics_window()
estimate = detector.estimate_expertise(window, list(collector._interactions))

print(f"Level: {estimate.estimated_level}")
print(f"Score: {estimate.expertise_score:.2f}")
```

### Privacy-Aware Collection

```python
from src.lui_simulator.privacy import PrivacyManager, ConsentType

# Check consent before collecting
privacy = PrivacyManager()
if privacy.check_consent("user-123", ConsentType.PROFILING):
    collector = MetricsCollector(user_id="user-123")
    # ... collect metrics
else:
    collector = MetricsCollector(
        user_id="user-123",
        privacy_mode=PrivacyMode.DISABLED
    )
```

### Adaptive Response

```python
from src.lui_simulator.templates import AdaptiveTemplateEngine, TemplateContext

# Create context from estimate
context = TemplateContext(
    expertise_level=estimate.estimated_level,
    interaction_count=window.interaction_count,
    success_rate=window.aggregate_metrics.success_rate,
    uses_shortcuts=True
)

# Get template parameters
engine = AdaptiveTemplateEngine()
params = engine.get_template_parameters(context)

# Use parameters in response generation
response = generate_response(
    content="Your request has been processed.",
    include_examples=params.includes_examples,
    verbosity=params.verbosity_level
)
```
