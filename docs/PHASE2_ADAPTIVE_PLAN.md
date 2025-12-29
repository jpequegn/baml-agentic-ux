# Phase 2: Adaptive Interface Personalization Implementation Plan

## Research Summary

Based on comprehensive research into adaptive UI patterns, expertise detection, user profiling, and consistency principles, this document outlines the implementation plan for adding adaptive personalization to the BAML Agentic UX framework.

### Key Research Findings

#### 1. Expertise Detection Signals

| Signal Category | Metrics | Detection Method |
|-----------------|---------|------------------|
| **Command Fluency** | Completion speed, shortcut usage | Keystroke dynamics analysis |
| **Error Patterns** | Error rate, recovery speed | Sequential behavior analysis |
| **Help-Seeking** | Documentation access, tooltip engagement | Event tracking |
| **Parameter Provision** | Completeness, defaults usage | Input pattern analysis |
| **Navigation** | Path efficiency, backtracking | Mouse/click dynamics |

**Key Algorithm**: Exponential Moving Average for expertise scoring
```
expertise(t) = α * current_performance + (1-α) * expertise(t-1)
α = 0.3 for gradual adaptation
```

#### 2. Level Transition Thresholds

| Transition | Trigger Conditions |
|------------|-------------------|
| **Level Up** | 5 consecutive successes, <10% error rate, shortcut usage detected |
| **Level Down** | 3 consecutive errors, >40% help requests, completion time >90th percentile |
| **Stable** | Consistent performance over 5-10 sessions |

**Cold Start**: Start conservative (novice mode), enable fast-track progression, high sensitivity to positive signals.

#### 3. Consistency Principles

**Must Stay Constant**:
- Brand voice and terminology
- Core personality traits
- Fundamental interaction patterns
- Security and safety behaviors

**Can Safely Change**:
- Response verbosity level
- Confirmation frequency
- Suggestion proactivity
- Detail depth
- Feature visibility

#### 4. Privacy Considerations (GDPR/CCPA)

- **Data Minimization**: Only collect metrics necessary for adaptation
- **On-Device Processing**: Prefer local expertise calculation
- **Consent**: Explicit opt-in for profiling features
- **Right to Reset**: Users can clear their profile anytime
- **Transparency**: Explain why adaptation occurs

#### 5. Industry Patterns

**Duolingo's BirdBrain**:
- Adapts lesson difficulty based on performance
- Inserts extra practice for struggling concepts
- Personalizes learning path based on goals and knowledge

**Grammarly**:
- Adjusts suggestions based on writing style
- Context-aware correction intensity
- Learns user vocabulary over time

---

## Implementation Architecture

### Phase 2 Structure

```
Phase 2: Adaptive Interface Personalization
├── Task 2.1: User Profile Type System
│   └── Define BAML types for user profiles and metrics
├── Task 2.2: Interaction Metrics Collection
│   └── Track behavioral signals for expertise detection
├── Task 2.3: Expertise Detection Algorithm
│   └── Calculate expertise level from metrics
├── Task 2.4: Level Transition Logic
│   └── Manage level-up/down with smooth transitions
├── Task 2.5: Adaptive Response Templates
│   └── Verbosity and detail templates per level
├── Task 2.6: Profile-Aware Response Generation
│   └── Modify response generation for profiles
├── Task 2.7: Privacy and Consent Management
│   └── GDPR-compliant profile handling
├── Task 2.8: User Control Interface
│   └── Override, reset, and preference settings
└── Task 2.9: Testing and Documentation
    └── Tests, examples, and docs
```

---

## Task Breakdown

### Task 2.1: User Profile Type System

**Objective**: Define BAML types for representing user profiles, expertise levels, and interaction history.

**Deliverables**:
- `baml_src/user_profile_types.baml` - Core profile type definitions

**Types to Implement**:

```baml
// Expertise Levels
enum ExpertiseLevel {
  NOVICE       @description("Full explanations, confirmation prompts, tutorials")
  BEGINNER     @description("Guided with examples, some confirmations")
  INTERMEDIATE @description("Standard responses, occasional hints")
  ADVANCED     @description("Concise responses, power-user shortcuts visible")
  EXPERT       @description("Minimal, assume domain knowledge, no hand-holding")
}

// Verbosity Preferences
enum VerbosityLevel {
  MINIMAL      @description("Just the facts, <20 words")
  STANDARD     @description("Balanced detail, 20-50 words")
  DETAILED     @description("Full explanations, 50-100 words")
  TUTORIAL     @description("Teaching mode, step-by-step, examples")
}

// Interaction Style
enum InteractionStyle {
  CONVERSATIONAL  @description("Natural, chatty, friendly")
  PROFESSIONAL    @description("Formal, business-like")
  TERSE           @description("Minimal, command-like")
  EDUCATIONAL     @description("Explanatory, teaching")
}

// Main User Profile
class UserProfile {
  user_id string
  created_at DateTime
  updated_at DateTime

  // Expertise
  expertise_level ExpertiseLevel
  expertise_score float         @description("0.0-1.0, granular score")
  expertise_confidence float    @description("0.0-1.0, confidence in estimate")

  // Preferences
  preferred_verbosity VerbosityLevel
  preferred_style InteractionStyle
  domain_familiarity float      @description("0.0-1.0, domain knowledge")

  // Metrics
  interaction_metrics InteractionMetrics

  // Consent
  profiling_consent bool
  last_consent_update DateTime?
}

// Interaction Metrics
class InteractionMetrics {
  // Volume
  total_interactions int
  session_count int

  // Success Metrics
  successful_intents int
  failed_intents int
  success_rate float            @description("Calculated: successful/total")

  // Efficiency Metrics
  avg_completion_time_ms float
  avg_parameters_provided float @description("How many params user provides vs defaults")
  shortcut_usage_rate float     @description("0.0-1.0, use of power features")

  // Help Metrics
  help_requests int
  disambiguation_requests int
  error_recovery_count int

  // Engagement
  avg_session_duration_ms float
  feature_exploration_rate float
}

// Session State (transient)
class SessionMetrics {
  session_id string
  started_at DateTime

  // Current session tracking
  interactions_this_session int
  successes_this_session int
  errors_this_session int
  help_requests_this_session int

  // Frustration indicators
  consecutive_errors int
  rapid_repeated_attempts int

  // Learning indicators
  new_features_used string[]
  shortcuts_discovered string[]
}

// Expertise Change Event
class ExpertiseTransition {
  previous_level ExpertiseLevel
  new_level ExpertiseLevel
  trigger TransitionTrigger
  timestamp DateTime
  metrics_snapshot InteractionMetrics
}

enum TransitionTrigger {
  CONSECUTIVE_SUCCESS
  SHORTCUT_ADOPTION
  REDUCED_HELP_SEEKING
  CONSECUTIVE_ERRORS
  HIGH_HELP_RATE
  USER_REQUEST
  TIMEOUT_DECAY
}
```

**Success Criteria**:
- [ ] All types compile without errors
- [ ] Types documented with `@description` annotations
- [ ] Support for both persistent and session-level data
- [ ] Privacy-conscious design (minimal required fields)

**Estimated Effort**: 3-4 hours
**Dependencies**: None

---

### Task 2.2: Interaction Metrics Collection

**Objective**: Implement tracking of behavioral signals for expertise detection.

**Deliverables**:
- `baml_src/metrics_collection.baml` - Metric types and collection logic
- `src/lui_simulator/metrics.py` - Python metrics collector

**Types**:

```baml
// Individual interaction record
class InteractionRecord {
  interaction_id string
  timestamp DateTime
  session_id string

  // What happened
  intent_detected string
  intent_confidence float
  parameters_provided int
  parameters_required int

  // How it went
  outcome InteractionOutcome
  completion_time_ms int
  error_count int
  help_requested bool
  disambiguation_needed bool

  // User behavior signals
  used_shortcut bool
  used_natural_language bool
  input_length int
  correction_count int
}

enum InteractionOutcome {
  SUCCESS
  PARTIAL_SUCCESS
  FAILURE
  ABANDONED
  HELP_ESCALATION
}

// Aggregated metrics for analysis
class MetricsWindow {
  window_start DateTime
  window_end DateTime
  interaction_count int

  // Aggregates
  success_rate float
  avg_completion_time float
  help_rate float
  shortcut_rate float
  error_rate float

  // Trends
  success_trend TrendDirection
  efficiency_trend TrendDirection
}

enum TrendDirection {
  IMPROVING
  STABLE
  DECLINING
}
```

**Python Implementation**:

```python
class MetricsCollector:
    """Collects and aggregates interaction metrics."""

    def __init__(self, user_id: str, privacy_mode: bool = True):
        self.user_id = user_id
        self.privacy_mode = privacy_mode
        self.session_metrics = SessionMetrics()

    def record_interaction(
        self,
        intent: str,
        outcome: InteractionOutcome,
        completion_time_ms: int,
        parameters_provided: int,
        parameters_required: int,
        used_shortcut: bool = False,
        help_requested: bool = False,
        disambiguation_needed: bool = False
    ) -> InteractionRecord:
        """Record a single interaction."""

    def get_windowed_metrics(
        self,
        window_size: int = 20  # Last N interactions
    ) -> MetricsWindow:
        """Get aggregated metrics over recent interactions."""

    def detect_frustration_signals(self) -> FrustrationSignals:
        """Detect if user is frustrated based on patterns."""

    def detect_mastery_signals(self) -> MasterySignals:
        """Detect if user is ready to level up."""
```

**Frustration Detection**:

```python
class FrustrationSignals:
    """Signals that user may be frustrated."""

    is_frustrated: bool
    confidence: float
    signals: List[str]

    @classmethod
    def detect(cls, session: SessionMetrics, window: MetricsWindow):
        signals = []

        # Consecutive errors
        if session.consecutive_errors >= 3:
            signals.append("3+ consecutive errors")

        # Rapid repeated attempts
        if session.rapid_repeated_attempts >= 2:
            signals.append("Rapid retry pattern")

        # Declining success rate
        if window.success_trend == TrendDirection.DECLINING:
            signals.append("Declining success rate")

        # High help rate
        if window.help_rate > 0.4:
            signals.append("High help-seeking (>40%)")

        return cls(
            is_frustrated=len(signals) >= 2,
            confidence=min(len(signals) / 4, 1.0),
            signals=signals
        )
```

**Success Criteria**:
- [ ] Track all key behavioral signals
- [ ] Support privacy mode (anonymized/local-only)
- [ ] Efficient storage (aggregate, don't store every detail)
- [ ] Frustration/mastery detection working

**Estimated Effort**: 4-5 hours
**Dependencies**: Task 2.1

---

### Task 2.3: Expertise Detection Algorithm

**Objective**: Calculate expertise level from collected metrics using proven algorithms.

**Deliverables**:
- `baml_src/expertise_detection.baml` - Detection function
- `src/lui_simulator/expertise.py` - Algorithm implementation

**Algorithm Design**:

```baml
class ExpertiseEstimate {
  level ExpertiseLevel
  score float              @description("0.0-1.0 granular score")
  confidence float         @description("0.0-1.0 confidence in estimate")
  contributing_factors ExpertiseFactor[]
  suggested_adjustments string[]
}

class ExpertiseFactor {
  factor_name string
  weight float
  score float
  evidence string
}

function EstimateExpertise(
  current_profile: UserProfile,
  recent_metrics: MetricsWindow,
  session_metrics: SessionMetrics
) -> ExpertiseEstimate {
  client GPT4o
  prompt #"
    Estimate user expertise level based on interaction patterns.

    ## Current Profile
    {{ current_profile }}

    ## Recent Metrics (last 20 interactions)
    {{ recent_metrics }}

    ## Current Session
    {{ session_metrics }}

    ## Expertise Scoring Model

    Calculate weighted score:
    - Command Fluency (30%): shortcut_rate, completion_time
    - Success Rate (25%): success_rate, error_recovery
    - Self-Sufficiency (25%): 1 - help_rate, parameters_provided
    - Engagement (20%): feature_exploration, session_duration

    ## Level Mapping
    - NOVICE: score < 0.2
    - BEGINNER: 0.2 <= score < 0.4
    - INTERMEDIATE: 0.4 <= score < 0.6
    - ADVANCED: 0.6 <= score < 0.8
    - EXPERT: score >= 0.8

    ## Confidence Calculation
    - Low confidence (<0.5): <15 interactions
    - Medium confidence (0.5-0.8): 15-50 interactions
    - High confidence (>0.8): >50 interactions with consistent patterns

    {{ ctx.output_format }}
  "#
}
```

**Python Implementation**:

```python
class ExpertiseDetector:
    """Detects user expertise level from behavioral patterns."""

    # Scoring weights
    WEIGHTS = {
        'command_fluency': 0.30,
        'success_rate': 0.25,
        'self_sufficiency': 0.25,
        'engagement': 0.20
    }

    # Level thresholds
    THRESHOLDS = {
        ExpertiseLevel.NOVICE: 0.0,
        ExpertiseLevel.BEGINNER: 0.2,
        ExpertiseLevel.INTERMEDIATE: 0.4,
        ExpertiseLevel.ADVANCED: 0.6,
        ExpertiseLevel.EXPERT: 0.8
    }

    def calculate_expertise_score(
        self,
        metrics: MetricsWindow,
        profile: UserProfile
    ) -> float:
        """Calculate weighted expertise score."""

        # Command fluency
        fluency = (
            metrics.shortcut_rate * 0.6 +
            self._normalize_completion_time(metrics.avg_completion_time) * 0.4
        )

        # Success rate (already 0-1)
        success = metrics.success_rate

        # Self-sufficiency
        self_sufficiency = (
            (1 - metrics.help_rate) * 0.5 +
            self._normalize_params(metrics) * 0.5
        )

        # Engagement
        engagement = metrics.feature_exploration_rate

        # Weighted sum
        score = (
            self.WEIGHTS['command_fluency'] * fluency +
            self.WEIGHTS['success_rate'] * success +
            self.WEIGHTS['self_sufficiency'] * self_sufficiency +
            self.WEIGHTS['engagement'] * engagement
        )

        return score

    def score_to_level(self, score: float) -> ExpertiseLevel:
        """Convert score to discrete level."""
        for level in reversed(ExpertiseLevel):
            if score >= self.THRESHOLDS[level]:
                return level
        return ExpertiseLevel.NOVICE

    def calculate_confidence(
        self,
        interaction_count: int,
        score_variance: float
    ) -> float:
        """Calculate confidence in expertise estimate."""

        # Volume-based confidence
        volume_conf = min(interaction_count / 50, 1.0)

        # Consistency-based confidence
        consistency_conf = 1 - min(score_variance * 2, 1.0)

        return (volume_conf * 0.6 + consistency_conf * 0.4)
```

**Success Criteria**:
- [ ] Score calculation matches research-based weights
- [ ] Level mapping is smooth (no jarring jumps)
- [ ] Confidence reflects data quality
- [ ] Works with cold-start (low data) scenarios

**Estimated Effort**: 4-5 hours
**Dependencies**: Tasks 2.1, 2.2

---

### Task 2.4: Level Transition Logic

**Objective**: Manage level-up and level-down transitions with smooth, non-jarring changes.

**Deliverables**:
- `baml_src/level_transition.baml` - Transition logic
- `src/lui_simulator/transitions.py` - Transition manager

**Types**:

```baml
class TransitionDecision {
  should_transition bool
  direction TransitionDirection?
  from_level ExpertiseLevel
  to_level ExpertiseLevel?
  rationale string
  user_notification string?
  rollback_available bool
}

enum TransitionDirection {
  LEVEL_UP
  LEVEL_DOWN
  LATERAL   @description("Same level, different style")
}

class TransitionPolicy {
  // Level-up requirements
  min_consecutive_successes int     @description("Default: 5")
  min_success_rate float            @description("Default: 0.8")
  min_interactions_at_level int     @description("Default: 10")

  // Level-down triggers
  max_consecutive_errors int        @description("Default: 3")
  max_help_rate float               @description("Default: 0.4")
  frustration_threshold float       @description("Default: 0.7")

  // Smoothing
  require_confirmation bool         @description("Ask user before changing")
  transition_cooldown_hours int     @description("Default: 24, min time between changes")
  gradual_transition bool           @description("Show both UI versions temporarily")
}

function DecideTransition(
  current_profile: UserProfile,
  recent_metrics: MetricsWindow,
  session_metrics: SessionMetrics,
  policy: TransitionPolicy
) -> TransitionDecision {
  client GPT4o
  prompt #"
    Decide if user should transition expertise levels.

    ## Current State
    Profile: {{ current_profile }}
    Recent Metrics: {{ recent_metrics }}
    Session: {{ session_metrics }}

    ## Policy
    {{ policy }}

    ## Decision Guidelines

    ### Level Up Triggers
    - {{ policy.min_consecutive_successes }}+ consecutive successes
    - Success rate > {{ policy.min_success_rate }}
    - Low help-seeking (<10%)
    - Shortcut usage emerging
    - At least {{ policy.min_interactions_at_level }} interactions at current level

    ### Level Down Triggers
    - {{ policy.max_consecutive_errors }}+ consecutive errors
    - Help rate > {{ policy.max_help_rate }}
    - Frustration signals detected
    - User explicitly requests more help

    ### Stay Stable
    - Mixed signals
    - Recent level change (cooldown)
    - User preference override active

    If transitioning, provide:
    - Brief, encouraging user notification
    - Rationale for logs
    - Rollback flag

    {{ ctx.output_format }}
  "#
}
```

**Python Implementation**:

```python
class TransitionManager:
    """Manages expertise level transitions."""

    DEFAULT_POLICY = TransitionPolicy(
        min_consecutive_successes=5,
        min_success_rate=0.8,
        min_interactions_at_level=10,
        max_consecutive_errors=3,
        max_help_rate=0.4,
        frustration_threshold=0.7,
        require_confirmation=False,
        transition_cooldown_hours=24,
        gradual_transition=True
    )

    def __init__(self, policy: TransitionPolicy = None):
        self.policy = policy or self.DEFAULT_POLICY
        self.transition_history: List[ExpertiseTransition] = []

    def check_level_up(
        self,
        profile: UserProfile,
        metrics: MetricsWindow,
        session: SessionMetrics
    ) -> Optional[TransitionDecision]:
        """Check if user qualifies for level up."""

        # Consecutive successes
        if session.successes_this_session < self.policy.min_consecutive_successes:
            return None

        # Success rate
        if metrics.success_rate < self.policy.min_success_rate:
            return None

        # Minimum interactions
        if profile.interaction_metrics.total_interactions < self.policy.min_interactions_at_level:
            return None

        # Cooldown check
        if self._in_cooldown(profile):
            return None

        # All checks passed
        new_level = self._next_level(profile.expertise_level)
        if new_level == profile.expertise_level:
            return None  # Already at max

        return TransitionDecision(
            should_transition=True,
            direction=TransitionDirection.LEVEL_UP,
            from_level=profile.expertise_level,
            to_level=new_level,
            rationale=f"Consistent success (>{self.policy.min_success_rate:.0%}), low help-seeking",
            user_notification=self._generate_level_up_message(new_level),
            rollback_available=True
        )

    def check_level_down(
        self,
        profile: UserProfile,
        session: SessionMetrics,
        frustration: FrustrationSignals
    ) -> Optional[TransitionDecision]:
        """Check if user needs more help (level down)."""

        if frustration.is_frustrated and frustration.confidence > self.policy.frustration_threshold:
            new_level = self._previous_level(profile.expertise_level)

            return TransitionDecision(
                should_transition=True,
                direction=TransitionDirection.LEVEL_DOWN,
                from_level=profile.expertise_level,
                to_level=new_level,
                rationale=f"Frustration detected: {', '.join(frustration.signals)}",
                user_notification="I'll provide more guidance to help you out.",
                rollback_available=True
            )

        return None

    def _generate_level_up_message(self, new_level: ExpertiseLevel) -> str:
        """Generate encouraging level-up message."""
        messages = {
            ExpertiseLevel.BEGINNER: "You're getting the hang of this! I'll show you some shortcuts.",
            ExpertiseLevel.INTERMEDIATE: "Nice progress! I'll be more concise now.",
            ExpertiseLevel.ADVANCED: "You're a pro! Enabling power-user features.",
            ExpertiseLevel.EXPERT: "Expert mode unlocked! Minimal prompts, maximum efficiency."
        }
        return messages.get(new_level, "You've leveled up!")
```

**User Notification Examples**:

| Transition | Message |
|------------|---------|
| Novice → Beginner | "You're getting the hang of this! I'll show you some shortcuts." |
| Beginner → Intermediate | "Nice progress! I'll be more concise now." |
| Intermediate → Advanced | "You're a pro! Enabling power-user features." |
| Any → Lower | "I'll provide more guidance to help you out." |
| User requests more help | "No problem! I'll explain things in more detail." |

**Success Criteria**:
- [ ] Smooth, non-jarring transitions
- [ ] Encouraging, non-condescending messages
- [ ] Rollback capability
- [ ] Cooldown prevents oscillation
- [ ] Works with user preference overrides

**Estimated Effort**: 4-5 hours
**Dependencies**: Tasks 2.1-2.3

---

### Task 2.5: Adaptive Response Templates

**Objective**: Create response templates that vary by expertise level.

**Deliverables**:
- `baml_src/adaptive_templates.baml` - Template definitions

**Types**:

```baml
class AdaptiveTemplate {
  template_id string
  purpose TemplatePurpose
  variants TemplateVariant[]
}

enum TemplatePurpose {
  SUCCESS_CONFIRMATION
  ERROR_MESSAGE
  DISAMBIGUATION
  HELP_OFFER
  FEATURE_SUGGESTION
  ACTION_CONFIRMATION
}

class TemplateVariant {
  expertise_level ExpertiseLevel
  verbosity VerbosityLevel
  template string
  show_examples bool
  show_shortcuts bool
  require_confirmation bool
}

// Example template set for task creation
class TaskCreationTemplates {
  // NOVICE: Full explanation
  novice_template string @description("
    I'll create a new task for you. Here's what I understood:

    - Title: {title}
    - Priority: {priority}
    - Due: {due_date}

    Does this look right? Say 'yes' to confirm or tell me what to change.
  ")

  // BEGINNER: Brief confirmation
  beginner_template string @description("
    Creating task: '{title}' (Priority: {priority}, Due: {due_date})

    Confirm? [Yes/Edit]
  ")

  // INTERMEDIATE: Inline confirmation
  intermediate_template string @description("
    Created: '{title}' - {priority} priority, due {due_date}
    [Undo]
  ")

  // ADVANCED: Minimal
  advanced_template string @description("
    ✓ {title} ({priority}, {due_date})
  ")

  // EXPERT: Ultra-minimal
  expert_template string @description("
    ✓ {title}
  ")
}
```

**Template Variations by Type**:

```baml
// Error messages by level
class ErrorTemplates {
  novice string @description("
    I couldn't find a task called '{query}'.

    Here's what you can try:
    1. Check the spelling
    2. Use a different name
    3. Say 'show my tasks' to see all tasks

    Would you like me to search for similar tasks?
  ")

  beginner string @description("
    No task found: '{query}'

    Try: 'show my tasks' or use a different name
  ")

  intermediate string @description("
    Task not found: '{query}'. Show all tasks?
  ")

  advanced string @description("
    Not found: '{query}' [Show all]
  ")

  expert string @description("
    ✗ {query} not found
  ")
}

// Feature suggestions by level
class FeatureSuggestionTemplates {
  novice string @description("
    Did you know? You can also {feature_description}.

    For example: {example}

    Would you like to try it now?
  ")

  beginner string @description("
    Tip: {feature_description}
    Example: {example}
  ")

  intermediate string @description("
    Tip: {short_description}
  ")

  advanced string @description("
    → {shortcut}: {feature_name}
  ")

  expert string @description("")  // No suggestions for experts
}
```

**Template Selection Logic**:

```baml
function SelectTemplate(
  purpose: TemplatePurpose,
  user_profile: UserProfile,
  context: ConversationContext
) -> TemplateVariant {
  client GPT4o
  prompt #"
    Select the appropriate template variant.

    Purpose: {{ purpose }}
    User Expertise: {{ user_profile.expertise_level }}
    User Verbosity Preference: {{ user_profile.preferred_verbosity }}
    Interaction Style: {{ user_profile.preferred_style }}

    ## Selection Rules

    1. Match expertise level first
    2. Respect verbosity preference (may override expertise)
    3. If user explicitly asked for more/less detail, adjust
    4. Error messages should be slightly MORE verbose than normal
    5. Success messages should be slightly LESS verbose than normal

    {{ ctx.output_format }}
  "#
}
```

**Success Criteria**:
- [ ] Templates for all common purposes
- [ ] Clear progression from verbose to minimal
- [ ] Maintains personality across levels
- [ ] Respects user preferences
- [ ] Easy to add new template sets

**Estimated Effort**: 3-4 hours
**Dependencies**: Task 2.1

---

### Task 2.6: Profile-Aware Response Generation

**Objective**: Modify response generation to incorporate user profile.

**Deliverables**:
- `baml_src/adaptive_response.baml` - Profile-aware generation function

**Function**:

```baml
function GenerateAdaptiveResponse(
  intent: IntentExtraction,
  action_result: ActionResult?,
  conversation_context: ConversationContext,
  user_profile: UserProfile,
  session_metrics: SessionMetrics
) -> AdaptiveResponse {
  client GPT4o
  prompt #"
    Generate a response adapted to the user's expertise level.

    ## Intent & Result
    Intent: {{ intent }}
    Result: {{ action_result }}

    ## User Profile
    Expertise: {{ user_profile.expertise_level }}
    Verbosity: {{ user_profile.preferred_verbosity }}
    Style: {{ user_profile.preferred_style }}
    Domain Familiarity: {{ user_profile.domain_familiarity }}

    ## Session Context
    {{ session_metrics }}

    ## Adaptation Guidelines

    ### By Expertise Level

    **NOVICE**:
    - Full explanations with examples
    - Confirm before actions
    - Offer help proactively
    - Define domain terms
    - Show step-by-step

    **BEGINNER**:
    - Brief explanations
    - Confirm destructive actions only
    - Mention shortcuts exist
    - Assume basic familiarity

    **INTERMEDIATE**:
    - Standard responses
    - No unsolicited explanations
    - Suggest efficiency tips occasionally
    - Assume competence

    **ADVANCED**:
    - Concise responses
    - No confirmations except critical
    - Surface power features
    - Technical language OK

    **EXPERT**:
    - Minimal responses
    - No hand-holding
    - Assume full knowledge
    - Support command-line style

    ### Frustration Detection
    If session shows frustration signals:
    - Increase helpfulness
    - Offer alternatives
    - Don't apologize excessively

    {{ ctx.output_format }}
  "#
}

class AdaptiveResponse {
  content string
  verbosity_used VerbosityLevel
  adaptations_applied string[]
  shortcuts_mentioned string[]
  follow_up_suggestions string[]

  // For gradual transition
  alternative_content string?     @description("More/less verbose alternative")
  show_toggle bool                @description("Show verbosity toggle to user")
}
```

**Success Criteria**:
- [ ] Response verbosity matches expertise level
- [ ] Consistency principles maintained (see research)
- [ ] Frustration detection triggers more help
- [ ] Works with multi-modal responses (Phase 1)
- [ ] Graceful when profile is incomplete

**Estimated Effort**: 4-5 hours
**Dependencies**: Tasks 2.1-2.5, Phase 1 (optional)

---

### Task 2.7: Privacy and Consent Management

**Objective**: GDPR/CCPA compliant profile handling.

**Deliverables**:
- `baml_src/privacy_types.baml` - Privacy-related types
- `src/lui_simulator/privacy.py` - Privacy manager

**Types**:

```baml
class PrivacySettings {
  profiling_enabled bool
  data_retention_days int         @description("How long to keep data, 0=session only")
  on_device_only bool             @description("Never sync to server")
  share_anonymous_stats bool      @description("Contribute to aggregate improvements")
}

class ConsentRecord {
  user_id string
  consent_type ConsentType
  granted bool
  timestamp DateTime
  version string                  @description("Policy version consented to")
  withdrawal_timestamp DateTime?
}

enum ConsentType {
  PROFILING                       @description("Track interaction patterns")
  PERSONALIZATION                 @description("Adapt responses to profile")
  ANALYTICS                       @description("Anonymous usage statistics")
  DATA_EXPORT                     @description("Allow profile export")
}

class DataSubjectRequest {
  request_type DSRType
  user_id string
  timestamp DateTime
  status DSRStatus
  completed_at DateTime?
}

enum DSRType {
  ACCESS        @description("GDPR Article 15 - Right of access")
  RECTIFICATION @description("GDPR Article 16 - Right to rectification")
  ERASURE       @description("GDPR Article 17 - Right to erasure")
  PORTABILITY   @description("GDPR Article 20 - Right to data portability")
  OBJECTION     @description("GDPR Article 21 - Right to object")
}

enum DSRStatus {
  PENDING
  IN_PROGRESS
  COMPLETED
  REJECTED
}
```

**Python Implementation**:

```python
class PrivacyManager:
    """Manages user privacy preferences and data subject requests."""

    def __init__(self, storage_backend):
        self.storage = storage_backend

    def check_consent(
        self,
        user_id: str,
        consent_type: ConsentType
    ) -> bool:
        """Check if user has granted specific consent."""

    def request_consent(
        self,
        user_id: str,
        consent_types: List[ConsentType],
        policy_version: str
    ) -> ConsentRequest:
        """Create consent request for user."""

    def withdraw_consent(
        self,
        user_id: str,
        consent_types: List[ConsentType]
    ) -> None:
        """Withdraw consent and trigger data handling."""

    def handle_dsr(
        self,
        request: DataSubjectRequest
    ) -> DSRResponse:
        """Handle data subject request."""

    def export_user_data(
        self,
        user_id: str,
        format: str = "json"
    ) -> bytes:
        """Export all user data in portable format."""

    def delete_user_data(
        self,
        user_id: str,
        retain_consent_records: bool = True
    ) -> DeletionResult:
        """Delete user data (right to erasure)."""

    def anonymize_for_analytics(
        self,
        profile: UserProfile
    ) -> AnonymizedMetrics:
        """Create anonymized version for aggregate analytics."""
```

**Consent Flow**:

```
New User → Show consent request → If accepted: enable profiling
                                → If declined: session-only mode (no persistence)

Existing User → Check consent valid → If valid: continue
                                    → If expired: re-request
                                    → If withdrawn: session-only mode
```

**Success Criteria**:
- [ ] GDPR Article 22 (profiling) compliant
- [ ] Right to erasure working
- [ ] Data portability working
- [ ] Consent withdrawal stops profiling
- [ ] On-device mode available
- [ ] Clear privacy explanations

**Estimated Effort**: 4-5 hours
**Dependencies**: Task 2.1

---

### Task 2.8: User Control Interface

**Objective**: Allow users to override, reset, and control adaptation.

**Deliverables**:
- `baml_src/user_controls.baml` - Control types and actions

**Types**:

```baml
class UserControlPanel {
  current_level ExpertiseLevel
  available_levels ExpertiseLevel[]
  current_verbosity VerbosityLevel
  current_style InteractionStyle

  // Toggles
  auto_adapt bool
  show_shortcuts bool
  confirm_actions bool

  // Privacy
  privacy_settings PrivacySettings
}

class UserOverride {
  override_type OverrideType
  value string
  duration OverrideDuration
  reason string?
}

enum OverrideType {
  EXPERTISE_LEVEL
  VERBOSITY
  STYLE
  FEATURE_VISIBILITY
}

enum OverrideDuration {
  THIS_SESSION
  UNTIL_CHANGED
  TEMPORARY_5_MIN
}

// User commands for control
class ControlCommand {
  command_type ControlCommandType
  parameters string[]
}

enum ControlCommandType {
  MORE_HELP          @description("User: 'I need more help' → increase verbosity")
  LESS_DETAIL        @description("User: 'Be more concise' → decrease verbosity")
  RESET_PROFILE      @description("User: 'Start fresh' → reset to novice")
  SHOW_SHORTCUTS     @description("User: 'Show shortcuts' → enable shortcut hints")
  HIDE_TIPS          @description("User: 'Stop showing tips' → disable suggestions")
  EXPLAIN_ADAPTATION @description("User: 'Why did you change?' → explain adaptation")
}
```

**Natural Language Control Patterns**:

| User Says | Action |
|-----------|--------|
| "I need more help" | Temporarily increase verbosity |
| "Be more concise" | Decrease verbosity |
| "I'm an expert" | Fast-track to advanced level |
| "Start over" / "Reset" | Reset profile to novice |
| "Why are you being so brief?" | Explain adaptation + offer change |
| "Show me shortcuts" | Enable shortcut visibility |
| "Stop showing tips" | Disable proactive suggestions |
| "Go back to how it was" | Rollback last change |

**Control Function**:

```baml
function HandleUserControl(
  user_input: string,
  current_profile: UserProfile,
  available_controls: ControlCommand[]
) -> ControlResponse {
  client GPT4o
  prompt #"
    Detect if user is requesting a profile/adaptation control.

    User Input: {{ user_input }}
    Current Profile: {{ current_profile }}
    Available Controls: {{ available_controls }}

    ## Detection Patterns

    ### More Help
    - "help me more"
    - "I don't understand"
    - "explain more"
    - "slow down"

    ### Less Detail
    - "be concise"
    - "shorter please"
    - "I know this"
    - "skip the explanation"

    ### Reset
    - "start fresh"
    - "reset everything"
    - "forget what you know about me"

    ### Explain
    - "why are you..."
    - "you changed"
    - "different than before"

    If control detected, return the action.
    If not a control request, return null.

    {{ ctx.output_format }}
  "#
}

class ControlResponse {
  is_control_request bool
  control_type ControlCommandType?
  action_taken string?
  user_message string?
}
```

**Success Criteria**:
- [ ] Natural language control detection
- [ ] Manual override capability
- [ ] Clear explanation when asked
- [ ] Rollback available
- [ ] Settings persist correctly

**Estimated Effort**: 3-4 hours
**Dependencies**: Tasks 2.1, 2.4

---

### Task 2.9: Testing and Documentation

**Objective**: Comprehensive testing and documentation for adaptive personalization.

**Deliverables**:
- `tests/test_adaptive.py` - Unit and integration tests
- `examples/adaptive_demo.py` - Demo script
- `docs/ADAPTIVE_GUIDE.md` - User documentation

**Test Cases**:

```python
class TestUserProfile:
    """Test profile creation and management."""

    def test_profile_creation(self): ...
    def test_profile_update(self): ...
    def test_metrics_aggregation(self): ...
    def test_privacy_compliance(self): ...

class TestExpertiseDetection:
    """Test expertise level detection."""

    def test_novice_detection(self): ...
    def test_expert_detection(self): ...
    def test_cold_start_handling(self): ...
    def test_gradual_progression(self): ...
    def test_frustration_detection(self): ...
    def test_mastery_detection(self): ...

class TestLevelTransitions:
    """Test level up/down logic."""

    def test_level_up_triggers(self): ...
    def test_level_down_triggers(self): ...
    def test_cooldown_enforcement(self): ...
    def test_rollback_capability(self): ...
    def test_user_notification(self): ...

class TestAdaptiveResponses:
    """Test response adaptation."""

    def test_novice_verbose_response(self): ...
    def test_expert_minimal_response(self): ...
    def test_template_selection(self): ...
    def test_consistency_maintained(self): ...
    def test_frustration_increases_help(self): ...

class TestUserControls:
    """Test user control mechanisms."""

    def test_more_help_command(self): ...
    def test_less_detail_command(self): ...
    def test_reset_profile(self): ...
    def test_manual_override(self): ...
    def test_rollback(self): ...

class TestPrivacy:
    """Test privacy compliance."""

    def test_consent_required(self): ...
    def test_data_export(self): ...
    def test_data_deletion(self): ...
    def test_on_device_mode(self): ...
```

**Documentation Sections**:

1. **Quick Start** - Enable adaptive personalization
2. **How It Works** - Expertise detection explained
3. **Privacy** - What data is collected, how to control
4. **User Controls** - Commands and settings
5. **Customization** - Configure thresholds and policies
6. **Integration** - Use with existing LUI schemas

**Success Criteria**:
- [ ] >90% code coverage
- [ ] All edge cases tested
- [ ] Privacy scenarios tested
- [ ] Documentation complete
- [ ] Demo script working

**Estimated Effort**: 4-5 hours
**Dependencies**: Tasks 2.1-2.8

---

## Implementation Timeline

| Task | Estimated Effort | Dependencies |
|------|------------------|--------------|
| 2.1 User Profile Types | 3-4 hours | None |
| 2.2 Metrics Collection | 4-5 hours | 2.1 |
| 2.3 Expertise Detection | 4-5 hours | 2.1, 2.2 |
| 2.4 Level Transition | 4-5 hours | 2.1-2.3 |
| 2.5 Adaptive Templates | 3-4 hours | 2.1 |
| 2.6 Profile-Aware Response | 4-5 hours | 2.1-2.5 |
| 2.7 Privacy Management | 4-5 hours | 2.1 |
| 2.8 User Controls | 3-4 hours | 2.1, 2.4 |
| 2.9 Testing & Docs | 4-5 hours | 2.1-2.8 |

**Total Estimated Effort**: 34-43 hours

---

## Success Metrics

### Functional
- [ ] Expertise detection accuracy >80%
- [ ] Level transitions feel smooth (user testing)
- [ ] Response verbosity matches expertise
- [ ] User controls work reliably
- [ ] Privacy compliance verified

### Quality
- [ ] >90% test coverage
- [ ] GDPR/CCPA compliance
- [ ] No jarring transitions (user testing)
- [ ] Documentation complete

### Integration
- [ ] Works with Phase 1 (Multi-Modal)
- [ ] Integrates with existing response generation
- [ ] Compatible with usability analysis

---

## Research Sources

### Expertise Detection
- [Mouse Behavioral Patterns Study](https://www.sciencedirect.com/science/article/abs/pii/S0747563218300700)
- [Keystroke Dynamics Research](https://arxiv.org/html/2303.04605v2)
- [MIT Media Lab Frustration Detection](https://www.media.mit.edu/publications/the-bayes-point-machine-for-computer-user-frustration-detection-via-pressure-mouse/)
- [Adaptive User Interfaces](https://www.researchgate.net/publication/2824884_User_Modeling_in_Adaptive_Interface)

### Adaptive UI Patterns
- [AI Adaptive User Interfaces 2025](https://yenra.com/ai20/adaptive-user-interfaces/)
- [Duolingo UX Analysis](https://userguiding.com/blog/duolingo-onboarding-ux)
- [Progressive Disclosure (NN/g)](https://www.nngroup.com/articles/progressive-disclosure/)
- [Grammarly Personalization](https://fuselabcreative.com/hyper-personalized-interface-design-with-ai/)

### Privacy & Compliance
- [GDPR and AI Best Practices](https://www.dpo-consulting.com/blog/gdpr-and-ai-best-practices)
- [ICO AI and Data Minimisation](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/artificial-intelligence/guidance-on-ai-and-data-protection/how-should-we-assess-security-and-data-minimisation-in-ai/)
- [EDPB AI Models Opinion 2024](https://www.edpb.europa.eu/system/files/2024-12/edpb_opinion_202428_ai-models_en.pdf)

### Consistency & Transitions
- [AI Personality Consistency](https://ideausher.com/blog/ai-personality-consistency-in-companion-apps/)
- [Conversational AI Design 2025](https://botpress.com/blog/conversation-design)
- [How Adaptive Systems Fail](https://resilienceroundup.com/issues/how-adaptive-systems-fail/)
