# Intent Drift Detection Usage Guide

This guide explains how to integrate and use the Intent Drift Detection module in your LUI applications.

## Table of Contents

- [Quick Start](#quick-start)
- [Integration Patterns](#integration-patterns)
- [Configuration](#configuration)
- [Handling Drift Events](#handling-drift-events)
- [Multi-turn Conversations](#multi-turn-conversations)
- [Analytics and Monitoring](#analytics-and-monitoring)
- [Best Practices](#best-practices)

---

## Quick Start

### Basic Integration

```python
from src.intent_drift import (
    IntentPipelineWithDrift,
    PipelineDriftConfig,
    AvailableComponent,
    DriftType,
    PipelineAction,
)

# 1. Define your available components
components = [
    AvailableComponent(
        component_id="task_manager",
        name="Task Manager",
        description="Create and manage tasks",
        intents=["create-task", "list-tasks", "complete-task"],
        examples=["Create a task", "Show my tasks", "Mark as done"],
    ),
    AvailableComponent(
        component_id="reminder",
        name="Reminder Service",
        description="Set and manage reminders",
        intents=["set-reminder", "list-reminders"],
        examples=["Remind me at 3pm", "What reminders do I have"],
    ),
]

# 2. Configure the pipeline
config = PipelineDriftConfig(
    drift_threshold=0.5,      # When to consider input as drifted
    confidence_threshold=0.6, # Minimum confidence for proceeding
    enable_redirects=True,    # Suggest alternatives for drifted requests
    max_redirects=3,          # Maximum number of redirect suggestions
)

# 3. Create the pipeline
pipeline = IntentPipelineWithDrift(
    config=config,
    available_components=components,
)

# 4. Process user input
result = pipeline.process("Show my tasks")

# 5. Handle the result
if result.action == PipelineAction.PROCEED:
    # Route to component
    component = get_component(result.component_id)
    component.handle(result.intent)
elif result.action == PipelineAction.REDIRECT:
    # Show graceful response with alternatives
    show_user(result.graceful_response)
elif result.action == PipelineAction.CLARIFY:
    # Ask for clarification
    ask_user_to_clarify(result.graceful_response)
```

---

## Integration Patterns

### Pattern 1: Middleware Integration

Use drift detection as middleware in your request pipeline:

```python
class DriftDetectionMiddleware:
    def __init__(self, pipeline: IntentPipelineWithDrift):
        self.pipeline = pipeline

    async def process(self, request: UserRequest) -> MiddlewareResult:
        result = self.pipeline.process(
            user_input=request.text,
            context=request.conversation_context,
        )

        if result.action == PipelineAction.PROCEED:
            return MiddlewareResult(
                should_continue=True,
                intent=result.intent,
                component_id=result.component_id,
            )
        else:
            return MiddlewareResult(
                should_continue=False,
                response=result.graceful_response,
                redirects=result.redirects,
            )
```

### Pattern 2: Component-Level Integration

Integrate at the component level for fine-grained control:

```python
from src.intent_drift import (
    SemanticAnalyzer,
    DriftClassifier,
    GracefulResponseGenerator,
    IntentDefinition,
)

class TaskManagerComponent:
    def __init__(self):
        self.intents = [
            IntentDefinition(
                name="create-task",
                description="Create a new task",
                examples=["Create task", "Add todo", "New task"],
            ),
            # ... more intents
        ]

        self.analyzer = SemanticAnalyzer(supported_intents=self.intents)
        self.classifier = DriftClassifier()
        self.generator = GracefulResponseGenerator()

    def can_handle(self, user_input: str) -> tuple[bool, str]:
        """Check if this component can handle the request."""
        analysis = self.analyzer.analyze(user_input)
        classification = self.classifier.classify(user_input, analysis)

        if classification.drift_type == DriftType.NONE:
            return True, classification.detected_intent

        response = self.generator.generate(
            drift_type=classification.drift_type,
            user_input=user_input,
        )
        return False, response
```

### Pattern 3: Event-Driven Integration

Use analytics events for monitoring:

```python
from src.intent_drift import DriftAnalytics, create_drift_analytics

class DriftEventHandler:
    def __init__(self):
        self.analytics = create_drift_analytics()

    def on_drift_detected(
        self,
        session_id: str,
        turn_id: str,
        drift_type: DriftType,
        drift_score: float,
        user_input: str,
    ):
        # Log the event
        event = self.analytics.log_event(
            session_id=session_id,
            turn_id=turn_id,
            drift_type=drift_type,
            drift_score=drift_score,
            user_input=user_input,
        )

        # Trigger alerts for high-severity drift
        if event.severity.value >= DriftSeverity.HIGH.value:
            self.send_alert(event)

        # Track patterns
        patterns = self.analytics.analyze_patterns()
        if patterns:
            self.log_patterns(patterns)
```

---

## Configuration

### Pipeline Configuration

```python
from src.intent_drift import PipelineDriftConfig

config = PipelineDriftConfig(
    # Drift Detection
    drift_threshold=0.5,        # 0.0-1.0, higher = more lenient
    confidence_threshold=0.6,   # Minimum confidence to proceed

    # Redirects
    enable_redirects=True,      # Suggest alternatives
    max_redirects=3,            # Limit suggestions

    # Coherence Tracking
    enable_coherence_tracking=True,  # Track multi-turn coherence
)
```

### Semantic Analyzer Configuration

```python
from src.intent_drift import SemanticAnalyzerConfig

config = SemanticAnalyzerConfig(
    similarity_threshold=0.6,   # Minimum similarity for intent match
    use_embeddings=False,       # Use embedding-based similarity
    max_cached_embeddings=1000, # Cache size for embeddings
)
```

### Drift Classifier Configuration

```python
from src.intent_drift import DriftClassifierConfig

config = DriftClassifierConfig(
    drift_threshold=0.5,        # Score threshold for drift detection

    # Pattern lists for specific drift types
    abstraction_patterns=[
        r"why do .*\?",
        r"what is the meaning",
        r"philosophy of",
    ],
    temporal_patterns=[
        r"\d+ years ago",
        r"in the past",
        r"historically",
    ],
    personalization_patterns=[
        r"remember my",
        r"my preference",
        r"personalize",
    ],
)
```

### Response Generator Configuration

```python
from src.intent_drift import ResponseGeneratorConfig, DriftResponseTone

config = ResponseGeneratorConfig(
    default_tone=DriftResponseTone.HELPFUL,  # HELPFUL, PROFESSIONAL, CASUAL
    include_alternatives=True,               # Include redirect suggestions
    max_alternatives=3,                      # Limit alternatives shown
)
```

### Coherence Tracker Configuration

```python
from src.intent_drift import CoherenceTrackerConfig

config = CoherenceTrackerConfig(
    max_turns=20,              # Maximum turns to track per session
    coherence_threshold=0.6,   # Threshold for coherence warnings
    drift_decay_factor=0.9,    # How quickly drift effects decay
)
```

---

## Handling Drift Events

### Action-Based Routing

```python
from src.intent_drift import PipelineAction

def handle_result(result: IntentExtractionWithDrift):
    match result.action:
        case PipelineAction.PROCEED:
            # Full confidence, route to component
            return route_to_component(result.component_id, result.intent)

        case PipelineAction.PROCEED_WITH_CAVEAT:
            # Can proceed but with lower confidence
            return route_with_confirmation(result.component_id, result.intent)

        case PipelineAction.CLARIFY:
            # Need more information from user
            return ask_clarification(result.graceful_response)

        case PipelineAction.REDIRECT:
            # Out of scope, suggest alternatives
            return show_redirect(result.graceful_response, result.redirects)

        case PipelineAction.ESCALATE:
            # Needs human intervention
            return escalate_to_human(result)

        case PipelineAction.DECLINE:
            # Cannot help with this request
            return decline_gracefully(result.graceful_response)
```

### Drift Type Specific Handling

```python
def handle_drift(result: IntentExtractionWithDrift):
    match result.drift_type:
        case DriftType.NONE:
            # No drift, proceed normally
            pass

        case DriftType.SCOPE_EXPANSION:
            # User wants more than we support
            # Acknowledge the request, offer what we can do
            log_feature_request(result.user_input)

        case DriftType.DOMAIN_SHIFT:
            # Completely different domain
            # Clear boundary, suggest alternatives if any

        case DriftType.ABSTRACTION_CLIMB:
            # Too philosophical/abstract
            # Bring back to concrete actions

        case DriftType.PERSONALIZATION:
            # Wants persistent preferences
            # Explain what personalization is available

        case DriftType.TEMPORAL_DRIFT:
            # Past/future issues
            # Explain data availability

        case DriftType.AMBIGUOUS:
            # Multiple possible intents
            # Ask for clarification
```

---

## Multi-turn Conversations

### Context Management

```python
from src.intent_drift import PipelineConversationContext

class ConversationManager:
    def __init__(self, pipeline: IntentPipelineWithDrift):
        self.pipeline = pipeline
        self.sessions: dict[str, list[str]] = {}

    def process_turn(
        self,
        session_id: str,
        user_input: str,
        last_intent: str = None,
        last_component: str = None,
    ) -> IntentExtractionWithDrift:
        # Track intents for this session
        if session_id not in self.sessions:
            self.sessions[session_id] = []

        context = PipelineConversationContext(
            session_id=session_id,
            recent_intents=self.sessions[session_id][-5:],  # Last 5 intents
            turn_count=len(self.sessions[session_id]) + 1,
            last_component=last_component,
        )

        result = self.pipeline.process(user_input, context)

        # Track successful intent
        if result.intent:
            self.sessions[session_id].append(result.intent)

        return result
```

### Coherence Monitoring

```python
from src.intent_drift import ConversationCoherenceTracker

tracker = ConversationCoherenceTracker()

# Add turns as conversation progresses
tracker.add_turn(
    session_id="user_123",
    user_input="Create a task",
    detected_intent="create-task",
    drift_type=DriftType.NONE,
    drift_score=0.1,
)

# Check coherence
coherence = tracker.get_coherence("user_123")
print(f"Coherence score: {coherence.coherence_score}")
print(f"Drift trend: {coherence.drift_trend}")

# Check if context reset is needed
reset_trigger = tracker.should_reset_context("user_123")
if reset_trigger.should_reset:
    print(f"Reset recommended: {reset_trigger.reason}")
```

---

## Analytics and Monitoring

### Basic Metrics

```python
from src.intent_drift import DriftAnalytics, create_drift_analytics, TimeRange
from datetime import datetime, timedelta, timezone

analytics = create_drift_analytics()

# Get metrics for the last 24 hours
time_range = TimeRange(
    start=datetime.now(timezone.utc) - timedelta(hours=24),
    end=datetime.now(timezone.utc),
)

metrics = analytics.calculate_metrics(time_range=time_range)

print(f"Total drift events: {metrics.total_events}")
print(f"Drift rate: {metrics.drift_rate:.1%}")
print(f"Recovery rate: {metrics.recovery_rate:.1%}")
print(f"Average drift score: {metrics.avg_drift_score:.2f}")
```

### Pattern Analysis

```python
# Detect recurring drift patterns
patterns = analytics.analyze_patterns(
    time_range=time_range,
    min_frequency=3,      # Must occur at least 3 times
    min_confidence=0.6,   # Pattern confidence threshold
)

for pattern in patterns:
    print(f"Pattern: {pattern.description}")
    print(f"  Frequency: {pattern.frequency}")
    print(f"  Common phrases: {pattern.common_phrases}")
```

### Export Data

```python
# Export to JSON
json_data = analytics.export_json(
    time_range=time_range,
    include_summary=True,
)

# Export to CSV
csv_data = analytics.export_csv(time_range=time_range)
```

---

## Best Practices

### 1. Define Clear Intent Boundaries

```python
# Good: Specific, actionable intents
IntentDefinition(
    name="create-task",
    description="Create a new task with a title",
    examples=[
        "Create a task called meeting prep",
        "Add a new task for groceries",
        "Make a todo item",
    ],
)

# Avoid: Vague or overlapping intents
IntentDefinition(
    name="do-something",  # Too vague
    description="Do something with tasks",
    examples=["do it", "handle that"],  # Ambiguous
)
```

### 2. Provide Rich Examples

```python
# More examples = better matching
IntentDefinition(
    name="complete-task",
    description="Mark a task as completed",
    examples=[
        "Complete the task",
        "Mark as done",
        "Finish the task",
        "I'm done with that task",
        "Task is finished",
        "Check off the meeting prep task",
        "Mark grocery shopping as complete",
    ],
)
```

### 3. Handle All Action Types

Always implement handlers for all possible pipeline actions:

```python
# Ensure all cases are handled
for action in PipelineAction:
    assert has_handler(action), f"Missing handler for {action}"
```

### 4. Log Drift Events for Improvement

```python
# Log all drift events for future analysis
def on_drift(result: IntentExtractionWithDrift):
    if result.drift_type != DriftType.NONE:
        analytics.log_event(
            session_id=current_session.id,
            turn_id=generate_turn_id(),
            drift_type=result.drift_type,
            drift_score=result.drift_score,
            user_input=result.user_input,
        )
```

### 5. Tune Thresholds Based on Your Domain

```python
# Stricter for critical applications
config = PipelineDriftConfig(
    drift_threshold=0.3,        # Catch more potential drift
    confidence_threshold=0.8,   # Require high confidence
)

# More lenient for exploratory interfaces
config = PipelineDriftConfig(
    drift_threshold=0.7,        # Allow some drift
    confidence_threshold=0.5,   # Accept lower confidence
)
```

### 6. Test with Real User Inputs

```python
# Collect and test with real user inputs
def test_real_user_scenarios():
    real_inputs = load_user_inputs_from_logs()

    for input_data in real_inputs:
        result = pipeline.process(input_data.text)

        # Verify expected behavior
        if input_data.was_handled_correctly:
            assert result.action == PipelineAction.PROCEED
        else:
            assert result.drift_type != DriftType.NONE
```

---

## Troubleshooting

### Low Detection Accuracy

1. **Add more examples** to intent definitions
2. **Adjust similarity threshold** in SemanticAnalyzerConfig
3. **Review pattern lists** in DriftClassifierConfig

### Too Many False Positives

1. **Raise drift_threshold** to be more lenient
2. **Add keywords** to intent definitions
3. **Tune abstraction/temporal/personalization patterns**

### Slow Performance

1. **Enable embedding caching** with `max_cached_embeddings`
2. **Reduce intent set size** by consolidating similar intents
3. **Use async processing** for multi-turn conversations
