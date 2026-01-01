# Adaptive Personalization User Guide

This guide explains how the adaptive personalization system works and how to manage your experience.

## How Personalization Works

### Overview

The adaptive personalization system automatically adjusts the interface to match your expertise level. As you use the system, it learns from your interactions and adapts responses accordingly.

### Expertise Levels

The system recognizes five expertise levels:

| Level | Description | What You'll See |
|-------|-------------|-----------------|
| **Novice** | New to the system | Detailed explanations, step-by-step guides, many examples |
| **Beginner** | Some familiarity | Clear instructions, helpful tips, relevant examples |
| **Intermediate** | Regular user | Standard responses, optional details available |
| **Advanced** | Power user | Concise responses, shortcuts mentioned |
| **Expert** | Deep system knowledge | Minimal responses, shortcuts assumed |

### How Levels Are Determined

Your expertise level is calculated from four factors:

1. **Command Fluency (30%)** - How efficiently you formulate requests
2. **Success Rate (25%)** - How often your tasks complete successfully
3. **Self-Sufficiency (25%)** - How often you need help or clarification
4. **Engagement (20%)** - How frequently you use advanced features

### Level Transitions

The system includes safeguards to prevent jarring changes:

- **Gradual changes**: Your level changes smoothly, not abruptly
- **Cooldown periods**: A minimum time between transitions prevents rapid switching
- **Hysteresis**: You need to consistently perform at a new level before transitioning

## Managing Your Preferences

### Override Your Level

You can temporarily override your detected level:

```python
from src.lui_simulator.preferences import PreferencesManager

manager = PreferencesManager()

# Override to a specific level
manager.set_level_override(
    user_id="your-id",
    target_level=ExpertiseLevel.ADVANCED,
    duration=OverrideDuration.SESSION  # or DAY, WEEK, PERMANENT
)

# Clear the override
manager.clear_level_override(user_id="your-id")
```

**Override durations:**
- `SESSION` - Until you log out
- `DAY` - 24 hours
- `WEEK` - 7 days
- `PERMANENT` - Until manually cleared

### Adjust Verbosity

Control how detailed responses are, independent of your expertise level:

```python
# Set verbosity preference
manager.set_verbosity_preference(
    user_id="your-id",
    verbosity=VerbosityLevel.CONCISE
)

# Preview what responses will look like
preview = manager.get_verbosity_preview(
    user_id="your-id",
    sample_context="How do I reset my password?"
)
```

**Verbosity levels:**
- `MINIMAL` - Essential information only
- `CONCISE` - Brief but complete
- `STANDARD` - Balanced detail (default)
- `DETAILED` - Comprehensive with examples
- `VERBOSE` - Maximum detail and explanation

### Accessibility Settings

Configure accessibility features:

```python
# Update accessibility settings
manager.update_accessibility_settings(
    user_id="your-id",
    high_contrast=True,
    large_text=True,
    screen_reader_mode=True
)

# Get current settings
settings = manager.get_accessibility_settings(user_id="your-id")
```

## Privacy Controls

### Understanding Data Collection

The system collects interaction data to personalize your experience. This includes:

- **Interaction patterns** - What features you use and how
- **Success metrics** - Whether your tasks complete successfully
- **Timing data** - How quickly you perform actions

### Managing Consent

You control what data is collected:

```python
from src.lui_simulator.privacy import PrivacyManager, ConsentType

privacy = PrivacyManager()

# Check your current consent
has_consent = privacy.check_consent("your-id", ConsentType.PROFILING)

# Withdraw consent
privacy.withdraw_consent(
    user_id="your-id",
    consent_types=[ConsentType.PROFILING],
    reason="No longer want personalization"
)
```

**Consent types:**
- `PROFILING` - Track interaction patterns
- `PERSONALIZATION` - Adapt responses based on behavior
- `ANALYTICS` - Include in anonymous statistics
- `DATA_EXPORT` - Allow profile data export
- `RETENTION` - Allow data retention beyond session

### Viewing Your Data

See what data has been collected about you:

```python
# Get data transparency panel
transparency = manager.get_data_transparency(user_id="your-id")

# View collected data summary
print(f"Interactions recorded: {transparency.data_collected}")
print(f"Current level: {transparency.current_level}")
```

### Exporting Your Data

Export all your data in standard formats:

```python
# Export as JSON
result = privacy.export_user_data(
    user_id="your-id",
    format=ExportFormat.JSON
)

# Export as CSV
result = privacy.export_user_data(
    user_id="your-id",
    format=ExportFormat.CSV
)
```

### Deleting Your Data

Request complete deletion of your data:

```python
# Delete all data (irreversible)
result = privacy.delete_user_data(user_id="your-id")
```

## Tips for Better Personalization

### Help the System Learn

- **Be consistent** - Regular usage patterns help accurate level detection
- **Use shortcuts** - Using shortcuts signals expertise
- **Complete tasks** - Successful completions improve your metrics

### When Personalization Feels Wrong

If responses don't match your expertise:

1. **Check your current level** via the data transparency panel
2. **Use a level override** to immediately change behavior
3. **Adjust verbosity** for fine-grained control
4. **Wait for adjustment** - the system will adapt over time

### Privacy-First Options

If you prefer minimal data collection:

1. **Withdraw profiling consent** - Disables behavior tracking
2. **Use session-only mode** - Data deleted when you log out
3. **Set a permanent level** - Use override instead of detection

## Troubleshooting

### "My level seems stuck"

This is by design. The system uses hysteresis to prevent oscillation. If you believe your level should change:

1. Perform consistently at your desired level
2. Wait for the cooldown period to expire
3. Use a level override for immediate change

### "Responses are too detailed/brief"

Use verbosity settings to adjust independently of expertise level:

1. Open preferences
2. Set your preferred verbosity level
3. Preview to confirm the change

### "I want to start fresh"

To reset your profile:

1. Delete your user data via privacy controls
2. This removes all interaction history
3. You'll start as a new user (Intermediate default)

### "The system isn't adapting"

Check that:

1. Profiling consent is granted
2. Personalization consent is granted
3. You have enough interactions (minimum 10)
4. No permanent level override is set

## Integration with Applications

### Basic Integration

```python
from src.lui_simulator.metrics import MetricsCollector, InteractionRecord
from src.lui_simulator.expertise import ExpertiseDetector
from src.lui_simulator.templates import AdaptiveTemplateEngine, TemplateContext

# 1. Record interactions
collector = MetricsCollector(user_id="user-123")
collector.record_interaction(InteractionRecord(...))

# 2. Estimate expertise
detector = ExpertiseDetector()
window = collector.get_metrics_window()
estimate = detector.estimate_expertise(window, list(collector._interactions))

# 3. Adapt responses
engine = AdaptiveTemplateEngine()
context = TemplateContext(
    expertise_level=estimate.estimated_level,
    interaction_count=window.interaction_count,
    success_rate=window.aggregate_metrics.success_rate,
    uses_shortcuts=True
)
params = engine.get_template_parameters(context)

# 4. Generate response using params
```

### With Privacy Checks

```python
from src.lui_simulator.privacy import PrivacyManager, ConsentType, PrivacyMode

privacy = PrivacyManager()

# Determine collection mode based on consent
if privacy.check_consent(user_id, ConsentType.PROFILING):
    mode = PrivacyMode.FULL
elif privacy.check_consent(user_id, ConsentType.ANALYTICS):
    mode = PrivacyMode.AGGREGATE_ONLY
else:
    mode = PrivacyMode.DISABLED

collector = MetricsCollector(user_id=user_id, privacy_mode=mode)
```

## Glossary

| Term | Definition |
|------|------------|
| **Cold Start** | Period when a new user has insufficient data for reliable expertise estimation |
| **EMA Smoothing** | Exponential Moving Average - technique to smooth score changes over time |
| **Hysteresis** | Buffer zone around level thresholds preventing rapid oscillation |
| **Cooldown** | Minimum time between expertise level transitions |
| **DSR** | Data Subject Request - GDPR right to access, modify, or delete data |
| **Consent** | User permission for specific types of data processing |
