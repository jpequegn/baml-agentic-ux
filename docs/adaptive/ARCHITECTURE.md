# Adaptive Personalization Architecture

This document describes the architecture of the adaptive interface personalization system implemented in Phase 2.

## Overview

The adaptive personalization system automatically adjusts interface behavior based on user expertise, providing an experience tailored to each user's skill level and preferences.

```
┌─────────────────────────────────────────────────────────────────┐
│                     User Interaction                             │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Metrics Collector                              │
│  - Records interactions                                          │
│  - Tracks success/failure                                        │
│  - Calculates aggregate metrics                                  │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Expertise  │  │  Privacy    │  │ Transition  │
│  Detector   │  │  Manager    │  │  Manager    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                  Template Engine                                 │
│  - Selects response templates                                    │
│  - Adapts verbosity and detail                                   │
│  - Personalizes output format                                    │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Metrics Collector (`metrics.py`)

**Purpose**: Captures and aggregates user interaction data.

**Key Features**:
- Records individual interactions with timestamps
- Calculates success rates, completion times
- Generates metrics windows for analysis
- Supports privacy modes (FULL, AGGREGATE_ONLY, SESSION_ONLY, DISABLED)

**Data Flow**:
```
Interaction → Record → Aggregate → MetricsWindow
```

### 2. Expertise Detector (`expertise.py`)

**Purpose**: Estimates user expertise level from behavioral metrics.

**Key Features**:
- Weighted scoring model with 4 factors
- EMA smoothing for stability
- Cold start handling for new users
- Level threshold mapping

**Algorithm**:
```
Score = 0.30 × CommandFluency +
        0.25 × SuccessRate +
        0.25 × SelfSufficiency +
        0.20 × Engagement
```

### 3. Transition Manager (`transitions.py`)

**Purpose**: Manages expertise level changes with safety controls.

**Key Features**:
- Hysteresis zones to prevent oscillation
- Cooldown periods between transitions
- Rollback capability for false positives
- User confirmation for significant changes

**State Machine**:
```
NOVICE ←→ BEGINNER ←→ INTERMEDIATE ←→ ADVANCED ←→ EXPERT
```

### 4. Privacy Manager (`privacy.py`)

**Purpose**: GDPR/CCPA compliant consent and data management.

**Key Features**:
- Consent lifecycle management
- Data Subject Request (DSR) handling
- Data export in JSON/CSV formats
- Complete data deletion
- Anonymization for analytics

**Consent Types**:
- PROFILING
- PERSONALIZATION
- ANALYTICS
- DATA_EXPORT
- RETENTION

### 5. Template Engine (`templates.py`)

**Purpose**: Adapts response format based on expertise level.

**Key Features**:
- Level-specific template selection
- Verbosity control
- Example inclusion logic
- Tip and guidance insertion

**Template Parameters by Level**:

| Level        | Verbosity | Examples | Tips | Shortcuts |
|--------------|-----------|----------|------|-----------|
| NOVICE       | Detailed  | Yes      | Yes  | No        |
| BEGINNER     | Standard  | Yes      | Yes  | No        |
| INTERMEDIATE | Standard  | Optional | No   | Mention   |
| ADVANCED     | Concise   | No       | No   | Use       |
| EXPERT       | Minimal   | No       | No   | Assume    |

## Data Flow

### Interaction Processing

```
1. User performs action
   ↓
2. Interaction recorded with metadata
   ↓
3. Metrics window updated
   ↓
4. Expertise estimated (if enough data)
   ↓
5. Transition evaluated (if score changed)
   ↓
6. Response adapted to current level
```

### Consent Flow

```
1. User prompted for consent
   ↓
2. Consent choices recorded
   ↓
3. Settings applied to collectors
   ↓
4. Data collected per consent
   ↓
5. DSR requests honored
```

## Integration Points

### BAML Schema Integration

The system uses BAML types defined in:
- `user_profile_types.baml` - User profiles and preferences
- `expertise_detection.baml` - Expertise estimation types
- `level_transition.baml` - Transition logic types
- `privacy_types.baml` - Privacy and consent types
- `adaptive_templates.baml` - Response template types
- `adaptive_response.baml` - Response generation types

### External Dependencies

- **MetricsCollector** depends on **PrivacyManager** for consent checks
- **ExpertiseDetector** depends on **MetricsCollector** for data
- **TransitionManager** depends on **ExpertiseDetector** for scores
- **TemplateEngine** depends on **TransitionManager** for levels

## Performance Characteristics

| Operation | Target | Typical |
|-----------|--------|---------|
| Expertise calculation | <10ms | ~5ms |
| Metrics window generation | <20ms | ~10ms |
| Template parameter generation | <10ms | ~3ms |
| Consent check | <5ms | ~1ms |
| Full response adaptation | <100ms | ~50ms |

## Scalability Considerations

### Per-User Data

- Interaction history: Limited to last N interactions (configurable)
- Profile data: Lightweight, <10KB per user
- Consent records: Append-only audit log

### Computation

- EMA smoothing is O(1) per update
- Metrics aggregation is O(n) where n = window size
- All operations are single-threaded safe

## Security Model

### Data Protection

- User IDs are internal identifiers, not PII
- IP addresses are hashed before storage
- Consent changes are audit logged
- Data deletion is complete and verifiable

### Privacy Modes

```python
class PrivacyMode(Enum):
    FULL = "FULL"              # All data collected
    AGGREGATE_ONLY = "AGGREGATE_ONLY"  # Only aggregates
    SESSION_ONLY = "SESSION_ONLY"      # Data expires with session
    DISABLED = "DISABLED"      # No collection
```

## Future Extensibility

### Planned Enhancements

1. **Multi-domain expertise**: Track expertise per feature area
2. **Collaborative filtering**: Learn from similar users
3. **A/B testing integration**: Experiment with thresholds
4. **Real-time dashboards**: Monitor adaptation effectiveness

### Extension Points

- Custom expertise factors via configuration
- Pluggable template engines
- External consent management integration
- Metrics export to analytics platforms
