# Adaptive Personalization Algorithms

This document describes the algorithms used in the adaptive personalization system.

## Expertise Detection Algorithm

### Overview

The expertise detection algorithm estimates a user's skill level based on their interaction patterns. It uses a weighted multi-factor scoring model with EMA smoothing.

### Factor Breakdown

#### 1. Command Fluency (Weight: 0.30)

Measures how efficiently users formulate commands.

**Inputs**:
- `input_length`: Characters in user input
- `completion_time_ms`: Time to complete interaction
- `parameters_provided` / `parameters_required`: Parameter completeness
- `used_shortcut`: Whether shortcuts were used

**Calculation**:
```python
# Conciseness score (shorter is better, up to a point)
conciseness = 1.0 - min(input_length / 100, 1.0) * 0.5

# Speed score (faster is better, capped)
speed = 1.0 - min(completion_time_ms / 5000, 1.0) * 0.3

# Parameter completeness
completeness = parameters_provided / parameters_required

# Shortcut bonus
shortcut_bonus = 0.2 if used_shortcut else 0.0

command_fluency = (conciseness * 0.3 + speed * 0.3 +
                   completeness * 0.3 + shortcut_bonus * 0.1)
```

#### 2. Success Rate (Weight: 0.25)

Measures task completion effectiveness.

**Inputs**:
- `outcome`: SUCCESS, PARTIAL_SUCCESS, FAILED, ABANDONED
- `error_count`: Number of errors in interaction

**Calculation**:
```python
outcome_scores = {
    SUCCESS: 1.0,
    PARTIAL_SUCCESS: 0.7,
    FAILED: 0.3,
    ABANDONED: 0.0
}

base_score = outcome_scores[outcome]
error_penalty = min(error_count * 0.1, 0.3)

success_rate = max(0, base_score - error_penalty)
```

#### 3. Self-Sufficiency (Weight: 0.25)

Measures independence from assistance.

**Inputs**:
- `help_requested`: Whether user asked for help
- `disambiguation_needed`: Whether clarification was needed

**Calculation**:
```python
help_penalty = 0.4 if help_requested else 0.0
disambig_penalty = 0.3 if disambiguation_needed else 0.0

self_sufficiency = max(0, 1.0 - help_penalty - disambig_penalty)
```

#### 4. Engagement (Weight: 0.20)

Measures consistent interaction patterns.

**Inputs**:
- `interaction_count`: Total interactions
- `shortcut_usage_rate`: Proportion using shortcuts
- `session_count`: Number of sessions

**Calculation**:
```python
# Frequency factor (more interactions = higher)
frequency = min(interaction_count / 100, 1.0)

# Feature exploration
exploration = shortcut_usage_rate * 0.5

# Consistency (regular sessions)
consistency = min(session_count / 10, 1.0) * 0.3

engagement = frequency * 0.4 + exploration * 0.3 + consistency * 0.3
```

### Total Score Calculation

```python
total_score = (
    command_fluency * 0.30 +
    success_rate * 0.25 +
    self_sufficiency * 0.25 +
    engagement * 0.20
)
```

### Level Thresholds

| Level        | Min Score | Max Score |
|--------------|-----------|-----------|
| NOVICE       | 0.00      | 0.20      |
| BEGINNER     | 0.20      | 0.40      |
| INTERMEDIATE | 0.40      | 0.60      |
| ADVANCED     | 0.60      | 0.80      |
| EXPERT       | 0.80      | 1.00      |

## EMA Smoothing

### Purpose

Exponential Moving Average (EMA) smoothing prevents rapid score oscillation due to short-term performance variations.

### Algorithm

```python
def apply_ema(current_score: float,
              previous_score: float,
              alpha: float = 0.3) -> float:
    """
    Apply EMA smoothing to expertise score.

    Alpha controls responsiveness:
    - Higher alpha (0.5+) = More responsive to changes
    - Lower alpha (0.1-0.3) = More stable, slower to change

    Default alpha=0.3 provides balance between stability and responsiveness.
    """
    return alpha * current_score + (1 - alpha) * previous_score
```

### Behavior

With alpha = 0.3:
- After 1 update: 30% new, 70% old
- After 3 updates: ~66% new influence
- After 7 updates: ~90% new influence

This means sudden changes take 5-7 interactions to fully reflect in the score.

## Cold Start Handling

### Problem

New users have insufficient data for reliable expertise estimation.

### Solution

```python
class ColdStartConfig:
    min_interactions: int = 10      # Minimum for estimation
    default_level: ExpertiseLevel = INTERMEDIATE
    default_score: float = 0.5
    default_confidence: float = 0.3
    ramp_up_interactions: int = 50  # Full confidence threshold

def handle_cold_start(interaction_count: int,
                      config: ColdStartConfig) -> tuple[bool, float]:
    """
    Determine cold start status and confidence factor.

    Returns:
        is_cold_start: Whether user is in cold start phase
        confidence: Confidence factor for estimates (0.0-1.0)
    """
    if interaction_count < config.min_interactions:
        return True, config.default_confidence

    # Ramp up confidence linearly
    progress = (interaction_count - config.min_interactions) / \
               (config.ramp_up_interactions - config.min_interactions)
    confidence = min(1.0, config.default_confidence + progress * 0.7)

    return False, confidence
```

## Level Transition Algorithm

### Hysteresis

Hysteresis prevents oscillation at level boundaries.

```python
class HysteresisConfig:
    upgrade_buffer: float = 0.05   # Score above threshold to upgrade
    downgrade_buffer: float = 0.05 # Score below threshold to downgrade

def should_transition(current_score: float,
                      current_level: ExpertiseLevel,
                      thresholds: dict,
                      config: HysteresisConfig) -> Optional[ExpertiseLevel]:
    """
    Determine if level transition should occur.

    User must exceed threshold by buffer amount to trigger transition.
    """
    current_max = thresholds[current_level].max_score
    current_min = thresholds[current_level].min_score

    # Check for upgrade
    if current_score > current_max + config.upgrade_buffer:
        next_level = get_next_level(current_level)
        if next_level:
            return next_level

    # Check for downgrade
    if current_score < current_min - config.downgrade_buffer:
        prev_level = get_previous_level(current_level)
        if prev_level:
            return prev_level

    return None  # No transition
```

### Cooldown

Cooldown prevents rapid consecutive transitions.

```python
def can_transition(user_id: str,
                   last_transition_time: datetime,
                   cooldown_seconds: int = 3600) -> bool:
    """
    Check if enough time has passed since last transition.

    Default: 1 hour cooldown between transitions.
    """
    if last_transition_time is None:
        return True

    elapsed = (datetime.now(timezone.utc) - last_transition_time).total_seconds()
    return elapsed >= cooldown_seconds
```

### Rollback

Rollback allows reverting false-positive transitions.

```python
def evaluate_rollback(user_id: str,
                      recent_interactions: list[InteractionRecord],
                      transition_record: TransitionRecord,
                      rollback_threshold: int = 3) -> bool:
    """
    Determine if recent performance warrants rollback.

    If user has rollback_threshold consecutive errors after upgrade,
    revert to previous level.
    """
    if transition_record.direction != TransitionDirection.UPGRADE:
        return False

    # Count consecutive errors since transition
    consecutive_errors = 0
    for interaction in recent_interactions:
        if interaction.outcome in [InteractionOutcome.FAILED,
                                   InteractionOutcome.ABANDONED]:
            consecutive_errors += 1
        else:
            break

    return consecutive_errors >= rollback_threshold
```

## Threshold Calibration

### Default Thresholds

```python
DEFAULT_THRESHOLDS = {
    ExpertiseLevel.NOVICE: LevelThreshold(
        min_score=0.0, max_score=0.2,
        description="New to the system, needs extensive guidance"
    ),
    ExpertiseLevel.BEGINNER: LevelThreshold(
        min_score=0.2, max_score=0.4,
        description="Some familiarity, still learning"
    ),
    ExpertiseLevel.INTERMEDIATE: LevelThreshold(
        min_score=0.4, max_score=0.6,
        description="Regular user, comfortable with basics"
    ),
    ExpertiseLevel.ADVANCED: LevelThreshold(
        min_score=0.6, max_score=0.8,
        description="Power user, uses advanced features"
    ),
    ExpertiseLevel.EXPERT: LevelThreshold(
        min_score=0.8, max_score=1.0,
        description="Deep system knowledge, optimal efficiency"
    ),
}
```

### Calibration Guidelines

1. **Collect baseline data**: Gather interaction data from known user segments
2. **Analyze distributions**: Plot score distributions by user type
3. **Adjust thresholds**: Move boundaries to minimize misclassification
4. **Validate with A/B test**: Compare adaptive vs fixed experience

## Performance Optimization

### Incremental Updates

Instead of recalculating all metrics, update incrementally:

```python
class IncrementalMetrics:
    def __init__(self):
        self.total_interactions = 0
        self.success_count = 0
        self.total_time_ms = 0

    def update(self, interaction: InteractionRecord):
        self.total_interactions += 1
        if interaction.outcome == InteractionOutcome.SUCCESS:
            self.success_count += 1
        self.total_time_ms += interaction.completion_time_ms

    @property
    def success_rate(self) -> float:
        if self.total_interactions == 0:
            return 0.0
        return self.success_count / self.total_interactions

    @property
    def avg_time_ms(self) -> float:
        if self.total_interactions == 0:
            return 0.0
        return self.total_time_ms / self.total_interactions
```

### Windowed Metrics

Use sliding window for recent behavior emphasis:

```python
def get_windowed_metrics(interactions: list[InteractionRecord],
                         window_size: int = 30) -> MetricsWindow:
    """
    Calculate metrics from most recent interactions.

    Larger windows = more stable, less responsive
    Smaller windows = more responsive, less stable

    Default: 30 interactions provides good balance
    """
    recent = interactions[-window_size:]
    return calculate_metrics(recent)
```
