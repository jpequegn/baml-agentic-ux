# Drift Types Reference

This document provides a comprehensive reference for all drift types detected by the Intent Drift Detection system.

## Table of Contents

- [Overview](#overview)
- [DriftType.NONE](#drifttypenone)
- [DriftType.SCOPE_EXPANSION](#drifttypescope_expansion)
- [DriftType.DOMAIN_SHIFT](#drifttypedomain_shift)
- [DriftType.ABSTRACTION_CLIMB](#drifttypeabstraction_climb)
- [DriftType.PERSONALIZATION](#drifttypepersonalization)
- [DriftType.TEMPORAL_DRIFT](#drifttypetemporal_drift)
- [DriftType.AMBIGUOUS](#drifttypeambiguous)
- [Detection Patterns](#detection-patterns)
- [Handling Strategies](#handling-strategies)

---

## Overview

Drift types classify how user requests deviate from an application's supported capabilities. Understanding each type helps you:

1. Respond appropriately to out-of-scope requests
2. Identify patterns in user needs
3. Guide feature development
4. Maintain coherent conversations

```python
from src.intent_drift import DriftType

class DriftType(Enum):
    NONE = "none"
    SCOPE_EXPANSION = "scope_expansion"
    DOMAIN_SHIFT = "domain_shift"
    ABSTRACTION_CLIMB = "abstraction_climb"
    PERSONALIZATION = "personalization"
    TEMPORAL_DRIFT = "temporal_drift"
    AMBIGUOUS = "ambiguous"
```

---

## DriftType.NONE

**Definition:** The request is within the application's supported capabilities.

### Characteristics

- High semantic similarity to supported intents
- Clear, actionable request
- Matches known examples or patterns
- Low drift score (typically < 0.3)

### Examples

For a task management application:

| User Input | Why It's NONE |
|------------|---------------|
| "Create a task" | Direct intent match |
| "Show my todos" | Matches list-tasks intent |
| "Mark meeting prep as done" | Matches complete-task intent |
| "Add a reminder for 3pm" | Matches set-reminder intent |

### Recommended Action

```python
if result.drift_type == DriftType.NONE:
    # Proceed with intent handling
    return PipelineAction.PROCEED
```

### Response Pattern

No special response needed - proceed with normal intent handling.

---

## DriftType.SCOPE_EXPANSION

**Definition:** The request is related to the application's domain but asks for functionality that isn't currently supported.

### Characteristics

- Related to core domain
- References concepts the system understands
- Requests unsupported features or extensions
- Medium drift score (typically 0.4-0.7)

### Examples

For a task management application:

| User Input | Why It's SCOPE_EXPANSION |
|------------|--------------------------|
| "Can you also send email reminders?" | Email not supported |
| "Integrate with my calendar" | Calendar integration not available |
| "Share this task with my team" | Collaboration not supported |
| "Set recurring tasks" | Recurrence not implemented |
| "Export my tasks to Excel" | Export not available |

### Detection Patterns

```python
# Common scope expansion indicators
patterns = [
    r"can you also",
    r"what about",
    r"add .* feature",
    r"integrate with",
    r"connect to",
    r"share .* with",
    r"export to",
    r"sync with",
]
```

### Recommended Action

```python
if result.drift_type == DriftType.SCOPE_EXPANSION:
    # Log feature request
    log_feature_request(result.user_input)

    # Acknowledge and offer alternatives
    return PipelineAction.REDIRECT
```

### Response Pattern

> "That's a great idea! Currently, I can help with [current capabilities]. I've noted your interest in [requested feature] for future development. In the meantime, would you like to [alternative action]?"

---

## DriftType.DOMAIN_SHIFT

**Definition:** The request is about a completely different domain than the application supports.

### Characteristics

- Low semantic similarity to any supported intent
- Different vocabulary and concepts
- Completely unrelated subject matter
- High drift score (typically > 0.7)

### Examples

For a task management application:

| User Input | Why It's DOMAIN_SHIFT |
|------------|----------------------|
| "What's the weather forecast?" | Weather is unrelated |
| "Play some music" | Media playback unrelated |
| "Book a flight to Paris" | Travel booking unrelated |
| "What's the stock price of Apple?" | Finance unrelated |
| "Translate this to Spanish" | Translation unrelated |

### Detection Patterns

```python
# Domain shift is detected by low similarity to all supported intents
# No specific patterns - relies on semantic distance

def detect_domain_shift(semantic_analysis):
    # If best match similarity is very low, it's a domain shift
    if semantic_analysis.best_match_score < 0.3:
        return DriftType.DOMAIN_SHIFT
```

### Recommended Action

```python
if result.drift_type == DriftType.DOMAIN_SHIFT:
    # Clear boundary statement
    return PipelineAction.DECLINE  # or REDIRECT if alternatives exist
```

### Response Pattern

> "I'm focused on [application domain] and can't help with [user request]. Here's what I can help you with: [capability list]. Would any of these be helpful?"

---

## DriftType.ABSTRACTION_CLIMB

**Definition:** The request moves from practical/actionable to philosophical, theoretical, or overly abstract.

### Characteristics

- Uses abstract or philosophical language
- Asks "why" questions about concepts
- Seeks meaning, purpose, or explanation
- Moves from doing to understanding
- Medium-high drift score (typically 0.5-0.8)

### Examples

For a task management application:

| User Input | Why It's ABSTRACTION_CLIMB |
|------------|---------------------------|
| "Why do humans procrastinate?" | Philosophical question |
| "What is the meaning of productivity?" | Abstract concept |
| "How can I find purpose in my work?" | Existential question |
| "Explain the psychology of motivation" | Theoretical request |
| "What makes a task truly important?" | Philosophical inquiry |

### Detection Patterns

```python
abstraction_patterns = [
    r"why do (humans|people|we)",
    r"what is the meaning of",
    r"what is the purpose of",
    r"philosophy of",
    r"theory of",
    r"psychology of",
    r"what makes .* (truly|really|fundamentally)",
    r"how can (I|we) find (meaning|purpose|happiness)",
    r"what is consciousness",
    r"explain (the concept|the nature) of",
]
```

### Recommended Action

```python
if result.drift_type == DriftType.ABSTRACTION_CLIMB:
    # Ground the user back to actionable tasks
    return PipelineAction.REDIRECT
```

### Response Pattern

> "That's a thought-provoking question! While I focus on practical task management, I can help you [concrete action]. Would you like to [specific suggestion]?"

---

## DriftType.PERSONALIZATION

**Definition:** The request asks the system to remember, learn, or adapt based on user preferences.

### Characteristics

- Requests persistent memory
- Asks for preference storage
- Expects personalized behavior
- References past interactions
- Medium drift score (typically 0.4-0.6)

### Examples

For a task management application:

| User Input | Why It's PERSONALIZATION |
|------------|-------------------------|
| "Remember my preference for morning reminders" | Preference storage |
| "Learn my task patterns" | Learning request |
| "Always use blue for work tasks" | Persistent customization |
| "You should know I prefer lists" | Expected memory |
| "Personalize the interface for me" | Customization request |

### Detection Patterns

```python
personalization_patterns = [
    r"remember (my|that|this)",
    r"learn (my|about me|from)",
    r"always use",
    r"my preference",
    r"personalize",
    r"customize for me",
    r"you should know",
    r"don't forget",
    r"keep track of my",
    r"adapt to my",
]
```

### Recommended Action

```python
if result.drift_type == DriftType.PERSONALIZATION:
    # Explain limitations, offer alternatives
    return PipelineAction.REDIRECT
```

### Response Pattern

> "I don't store personal preferences between sessions, but you can [workaround]. Would you like me to help you set that up for this session?"

---

## DriftType.TEMPORAL_DRIFT

**Definition:** The request asks about past data, historical information, or future predictions that the system cannot provide.

### Characteristics

- References specific past time periods
- Asks about historical data
- Requests future predictions
- Expects data persistence across time
- Medium drift score (typically 0.4-0.7)

### Examples

For a task management application:

| User Input | Why It's TEMPORAL_DRIFT |
|------------|------------------------|
| "What tasks did I have last year?" | Historical data request |
| "Show my productivity trends" | Historical analysis |
| "What will I be doing next month?" | Future prediction |
| "Compare my tasks from 2020 vs now" | Historical comparison |
| "How many tasks did I complete in Q1?" | Historical metrics |

### Detection Patterns

```python
temporal_patterns = [
    r"\d+ (years?|months?|weeks?) ago",
    r"last (year|month|week)",
    r"in \d{4}",
    r"back in",
    r"historically",
    r"over time",
    r"trend",
    r"compare .* from",
    r"(next|in) \d+ (years?|months?)",
    r"prediction",
    r"forecast",
]
```

### Recommended Action

```python
if result.drift_type == DriftType.TEMPORAL_DRIFT:
    # Explain data limitations
    return PipelineAction.DECLINE  # or REDIRECT to current data
```

### Response Pattern

> "I can only help with current and upcoming tasks. Historical data from [time period] isn't available. Would you like to see your current tasks or create new ones?"

---

## DriftType.AMBIGUOUS

**Definition:** The request is unclear, vague, or could match multiple intents.

### Characteristics

- Vague or generic language
- Missing key information
- Uses pronouns without clear references
- Could apply to multiple actions
- Low confidence across all intents

### Examples

For a task management application:

| User Input | Why It's AMBIGUOUS |
|------------|-------------------|
| "Do the thing" | Completely unclear |
| "Handle that" | Missing reference |
| "It" | No context |
| "Maybe something with tasks" | Very vague |
| "You know what I mean" | Assumes context |

### Detection Patterns

```python
ambiguous_patterns = [
    r"^(do|handle|fix) (it|that|this|the thing)$",
    r"^(it|that|this)$",
    r"you know what",
    r"the usual",
    r"like before",
    r"that thing",
    r"^maybe",
    r"^something",
]

# Also detected by:
# - Low confidence scores across all intents
# - Multiple intents with similar scores
# - Missing required entities
```

### Recommended Action

```python
if result.drift_type == DriftType.AMBIGUOUS:
    # Ask for clarification
    return PipelineAction.CLARIFY
```

### Response Pattern

> "I want to help, but I'm not sure what you need. Could you tell me more about:
> - What you'd like to do (create, view, complete)?
> - Which task or reminder you're referring to?"

---

## Detection Patterns

### Pattern Matching Configuration

```python
from src.intent_drift import DriftClassifierConfig

config = DriftClassifierConfig(
    drift_threshold=0.5,

    abstraction_patterns=[
        r"why do (humans|people|we)",
        r"what is the meaning",
        r"philosophy of",
        r"psychology of",
    ],

    temporal_patterns=[
        r"\d+ years ago",
        r"last (year|month)",
        r"in \d{4}",
        r"trend",
    ],

    personalization_patterns=[
        r"remember my",
        r"learn (my|about)",
        r"my preference",
        r"personalize",
    ],
)
```

### Priority Order

When multiple drift types could apply, they're prioritized:

1. **AMBIGUOUS** - If we can't understand, we can't classify further
2. **DOMAIN_SHIFT** - If completely unrelated, other types don't apply
3. **ABSTRACTION_CLIMB** - Check for philosophical drift
4. **TEMPORAL_DRIFT** - Check for time-based issues
5. **PERSONALIZATION** - Check for preference requests
6. **SCOPE_EXPANSION** - If related but unsupported

---

## Handling Strategies

### Decision Matrix

| Drift Type | Confidence | Recommended Action |
|------------|------------|-------------------|
| NONE | High | PROCEED |
| NONE | Low | PROCEED_WITH_CAVEAT |
| SCOPE_EXPANSION | Any | REDIRECT |
| DOMAIN_SHIFT | Any | DECLINE or REDIRECT |
| ABSTRACTION_CLIMB | Any | REDIRECT |
| PERSONALIZATION | Any | REDIRECT |
| TEMPORAL_DRIFT | Any | DECLINE or REDIRECT |
| AMBIGUOUS | Any | CLARIFY |

### Code Example

```python
def get_action(result: IntentExtractionWithDrift) -> PipelineAction:
    match result.drift_type:
        case DriftType.NONE:
            if result.confidence >= 0.8:
                return PipelineAction.PROCEED
            elif result.confidence >= 0.5:
                return PipelineAction.PROCEED_WITH_CAVEAT
            else:
                return PipelineAction.CLARIFY

        case DriftType.AMBIGUOUS:
            return PipelineAction.CLARIFY

        case DriftType.DOMAIN_SHIFT:
            if result.redirects:
                return PipelineAction.REDIRECT
            return PipelineAction.DECLINE

        case DriftType.SCOPE_EXPANSION:
            log_feature_request(result.user_input)
            return PipelineAction.REDIRECT

        case DriftType.ABSTRACTION_CLIMB:
            return PipelineAction.REDIRECT

        case DriftType.PERSONALIZATION:
            return PipelineAction.REDIRECT

        case DriftType.TEMPORAL_DRIFT:
            return PipelineAction.DECLINE
```

### Severity Classification

```python
class DriftSeverity(Enum):
    LOW = "low"           # Minor drift, easily recoverable
    MEDIUM = "medium"     # Moderate drift, may need guidance
    HIGH = "high"         # Significant drift, clear boundary needed
    CRITICAL = "critical" # Complete domain shift, decline

def get_severity(drift_type: DriftType, score: float) -> DriftSeverity:
    if drift_type == DriftType.NONE:
        return DriftSeverity.LOW

    if drift_type == DriftType.DOMAIN_SHIFT and score > 0.8:
        return DriftSeverity.CRITICAL

    if drift_type in [DriftType.DOMAIN_SHIFT, DriftType.ABSTRACTION_CLIMB]:
        return DriftSeverity.HIGH if score > 0.6 else DriftSeverity.MEDIUM

    if drift_type in [DriftType.SCOPE_EXPANSION, DriftType.PERSONALIZATION]:
        return DriftSeverity.MEDIUM

    return DriftSeverity.LOW
```

---

## Quick Reference

| Drift Type | Description | Typical Score | Action |
|------------|-------------|---------------|--------|
| NONE | Within capabilities | < 0.3 | PROCEED |
| SCOPE_EXPANSION | Related but unsupported | 0.4-0.7 | REDIRECT |
| DOMAIN_SHIFT | Different domain | > 0.7 | DECLINE |
| ABSTRACTION_CLIMB | Too philosophical | 0.5-0.8 | REDIRECT |
| PERSONALIZATION | Preference storage | 0.4-0.6 | REDIRECT |
| TEMPORAL_DRIFT | Past/future data | 0.4-0.7 | DECLINE |
| AMBIGUOUS | Unclear intent | Any | CLARIFY |
