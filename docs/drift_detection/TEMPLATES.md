# Response Templates Guide

This guide documents the response template system for handling drift detection scenarios gracefully.

## Table of Contents

- [Overview](#overview)
- [Template Categories](#template-categories)
- [Built-in Templates](#built-in-templates)
- [Custom Templates](#custom-templates)
- [Template Variables](#template-variables)
- [Tone Configuration](#tone-configuration)
- [Best Practices](#best-practices)

---

## Overview

The template system provides consistent, helpful responses when user requests drift outside your application's capabilities. Templates are organized by:

1. **Drift Type** - The type of drift detected
2. **Category** - The template's purpose (boundary, redirect, clarification)
3. **Tone** - The response style (helpful, professional, casual)

### Basic Usage

```python
from src.intent_drift import (
    TemplateLibrary,
    get_default_library,
    DriftType,
    TemplateCategory,
)

# Get the default template library
library = get_default_library()

# Get a template for a specific drift type
template = library.get_template(
    drift_type=DriftType.DOMAIN_SHIFT,
    category=TemplateCategory.BOUNDARY,
)

# Render with variables
response = library.render(
    template_id=template.id,
    variables={
        "user_request": "check my email",
        "capability_description": "task management",
        "alternatives": "creating tasks, listing tasks, or setting reminders",
    },
)
```

---

## Template Categories

### Boundary Templates

Set clear boundaries about what the system can and cannot do.

```python
TemplateCategory.BOUNDARY
```

**Purpose:** Clearly communicate system limitations without being dismissive.

**Example:**
> "I'm focused on task management and can't help with email. Would you like to create a task instead?"

### Redirect Templates

Guide users toward supported capabilities.

```python
TemplateCategory.REDIRECT
```

**Purpose:** Acknowledge the user's intent while suggesting alternatives.

**Example:**
> "While I can't check weather forecasts, I can help you create a reminder for when to check the weather. Would that be helpful?"

### Clarification Templates

Request additional information for ambiguous inputs.

```python
TemplateCategory.CLARIFICATION
```

**Purpose:** Gather more context to better understand user intent.

**Example:**
> "I want to make sure I help you correctly. Could you tell me more about what you'd like to do with your tasks?"

### Acknowledgment Templates

Acknowledge the request before redirecting or declining.

```python
TemplateCategory.ACKNOWLEDGMENT
```

**Purpose:** Show the user they've been heard before explaining limitations.

**Example:**
> "I understand you're interested in productivity tips. While I can't provide general advice, I can help you manage your tasks more effectively."

---

## Built-in Templates

### Domain Shift Templates

For requests in completely different domains.

```python
# Template: domain_shift_boundary
"""
I'm designed to help with {capability_description}.
While I can't assist with {user_request}, I can help you with {alternatives}.
"""

# Template: domain_shift_redirect
"""
That's outside my area, but here's what I can do:
{redirect_list}
Would any of these help?
"""
```

### Scope Expansion Templates

For requests that extend beyond current capabilities.

```python
# Template: scope_expansion_boundary
"""
That's a great idea! Currently, I can help with {current_capabilities}.
I've noted your interest in {requested_capability} for future development.
"""

# Template: scope_expansion_redirect
"""
While {requested_feature} isn't available yet, you might find these helpful:
{available_features}
"""
```

### Abstraction Climb Templates

For philosophical or overly abstract requests.

```python
# Template: abstraction_climb_redirect
"""
That's a thought-provoking question! While I focus on practical task management,
I can help you {concrete_action}. Would you like to try that?
"""

# Template: abstraction_climb_ground
"""
Let's bring this back to something actionable.
What specific task or reminder would help you right now?
"""
```

### Personalization Templates

For requests requiring persistent user data.

```python
# Template: personalization_boundary
"""
I don't store personal preferences between sessions, but I can help you
{available_action} right now. What would you like to do?
"""

# Template: personalization_alternative
"""
While I can't remember preferences, you can {workaround}.
Would you like me to help with that?
"""
```

### Temporal Drift Templates

For past/future data requests.

```python
# Template: temporal_drift_boundary
"""
I can only help with current and upcoming tasks.
Historical data from {time_period} isn't available.
Would you like to see your current tasks instead?
"""

# Template: temporal_drift_redirect
"""
While I don't have access to {historical_data}, I can help you:
- View current tasks
- Create new tasks
- Set reminders for the future
"""
```

### Ambiguous Request Templates

For unclear or multi-intent requests.

```python
# Template: ambiguous_clarify
"""
I want to help, but I'm not sure what you need. Could you tell me:
- What you'd like to do (create, view, complete)?
- Which item you're referring to?
"""

# Template: ambiguous_options
"""
I can help with several things. Did you mean:
{option_list}
Just let me know which one!
"""
```

---

## Custom Templates

### Creating Custom Templates

```python
from src.intent_drift import ResponseTemplate, TemplateCategory, DriftType

# Create a custom template
custom_template = ResponseTemplate(
    id="my_custom_template",
    drift_type=DriftType.DOMAIN_SHIFT,
    category=TemplateCategory.BOUNDARY,
    template="Sorry, I'm a {app_name} assistant and can't help with {user_request}. "
             "Try asking me about {main_capability}!",
    variables=["app_name", "user_request", "main_capability"],
    tone=DriftResponseTone.CASUAL,
)

# Add to library
library = get_default_library()
library.add_template(custom_template)
```

### Template Structure

```python
@dataclass
class ResponseTemplate:
    id: str                          # Unique identifier
    drift_type: DriftType            # Which drift type this handles
    category: TemplateCategory       # Template category
    template: str                    # Template string with {variables}
    variables: list[str]             # Required variables
    tone: DriftResponseTone          # Response tone
    priority: int = 0                # Higher = preferred when multiple match
    conditions: dict = None          # Optional conditions for selection
```

### Conditional Templates

```python
# Template that only applies in certain conditions
conditional_template = ResponseTemplate(
    id="first_time_drift",
    drift_type=DriftType.DOMAIN_SHIFT,
    category=TemplateCategory.BOUNDARY,
    template="Welcome! I'm here to help with tasks. "
             "I noticed you asked about {topic} - that's not my specialty, "
             "but I'd love to show you what I can do!",
    variables=["topic"],
    conditions={"is_first_interaction": True},
)
```

---

## Template Variables

### Common Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{user_request}` | Original user input | "check my email" |
| `{capability_description}` | What the system does | "task management" |
| `{alternatives}` | Comma-separated alternatives | "creating tasks, reminders" |
| `{redirect_list}` | Formatted list of redirects | "- Create task\n- Set reminder" |
| `{app_name}` | Application name | "TaskMaster" |

### Drift-Specific Variables

| Drift Type | Variable | Description |
|------------|----------|-------------|
| Scope Expansion | `{requested_capability}` | Feature user asked for |
| Scope Expansion | `{current_capabilities}` | What's available now |
| Temporal | `{time_period}` | Requested time frame |
| Temporal | `{historical_data}` | Type of historical data |
| Abstraction | `{concrete_action}` | Practical alternative |
| Personalization | `{workaround}` | Alternative approach |

### Variable Rendering

```python
# Automatic variable substitution
response = library.render(
    template_id="domain_shift_boundary",
    variables={
        "capability_description": "task and reminder management",
        "user_request": "checking the weather",
        "alternatives": "creating tasks, listing your todos, or setting reminders",
    },
)
# Result: "I'm designed to help with task and reminder management.
#          While I can't assist with checking the weather,
#          I can help you with creating tasks, listing your todos, or setting reminders."
```

---

## Tone Configuration

### Available Tones

```python
class DriftResponseTone(Enum):
    HELPFUL = "helpful"       # Warm, supportive
    PROFESSIONAL = "professional"  # Formal, business-like
    CASUAL = "casual"         # Friendly, conversational
    CONCISE = "concise"       # Brief, to-the-point
```

### Tone Examples

**Helpful:**
> "I'd love to help with that! While checking emails isn't something I can do, I'm great at helping you manage tasks. Would you like to create a task for checking your emails later?"

**Professional:**
> "That request falls outside my current capabilities. I am designed to assist with task management. Please let me know if you would like help with creating or managing tasks."

**Casual:**
> "Ha, I wish I could check your email! But that's not my thing. I'm all about tasks and reminders though - want me to help with those instead?"

**Concise:**
> "I can't help with email. I handle tasks and reminders. Need either of those?"

### Setting Default Tone

```python
from src.intent_drift import ResponseGeneratorConfig, DriftResponseTone

config = ResponseGeneratorConfig(
    default_tone=DriftResponseTone.HELPFUL,  # Default for all responses
)

generator = GracefulResponseGenerator(config=config)
```

### Per-Request Tone Override

```python
response = generator.generate(
    drift_type=DriftType.DOMAIN_SHIFT,
    user_input="Check my email",
    tone=DriftResponseTone.CASUAL,  # Override default
)
```

---

## Best Practices

### 1. Always Acknowledge First

```python
# Good: Acknowledges before redirecting
"""
I understand you're looking for weather information.
While that's not something I can help with,
I'd be happy to help you create a task or reminder.
"""

# Bad: Jumps straight to "no"
"""
I can't help with weather. Try tasks instead.
"""
```

### 2. Offer Concrete Alternatives

```python
# Good: Specific alternatives
"""
Instead of email, I can help you:
- Create a task to check email at a specific time
- Set a reminder to follow up on emails
- Make a todo list for email-related actions
"""

# Bad: Vague suggestion
"""
I can't do email. Maybe try something else?
"""
```

### 3. Match User's Energy Level

```python
# User is casual
user_input = "yo can you check my email"
tone = DriftResponseTone.CASUAL

# User is formal
user_input = "Would you please check my email messages?"
tone = DriftResponseTone.PROFESSIONAL
```

### 4. Keep Templates Short and Scannable

```python
# Good: Brief and clear
"""
I'm focused on tasks. Would you like to:
• Create a task
• View your tasks
• Set a reminder
"""

# Bad: Wall of text
"""
Thank you for your interest in using our system. Unfortunately,
the functionality you have requested is not currently within our
supported feature set. Our system is primarily designed for task
management and related activities. We would be more than happy to
assist you with any task-related needs you may have...
"""
```

### 5. Use Variables for Personalization

```python
# Good: Dynamic and relevant
template = """
I can't help with {user_topic}, but since you mentioned {keyword},
would you like to {suggested_action}?
"""

# Bad: Generic and impersonal
template = """
That's not supported. Would you like to do something else?
"""
```

### 6. A/B Test Templates

Track which templates lead to better outcomes:

```python
# Log template usage
analytics.log_event(
    template_id=template.id,
    user_accepted_redirect=user_clicked_alternative,
    user_left_session=user_abandoned,
)

# Analyze effectiveness
report = analytics.template_effectiveness_report()
```

---

## Template Library Reference

### Getting Templates

```python
# Get single template
template = library.get_template(
    drift_type=DriftType.DOMAIN_SHIFT,
    category=TemplateCategory.BOUNDARY,
)

# Get all templates for a drift type
templates = library.get_all_templates(drift_type=DriftType.DOMAIN_SHIFT)

# Get all boundary templates
boundaries = library.get_all_templates(category=TemplateCategory.BOUNDARY)
```

### Rendering Templates

```python
# Render with variables
response = library.render(
    template_id="domain_shift_boundary",
    variables={"user_request": "email", "alternatives": "tasks"},
)

# Render with fallback
response = library.render(
    template_id="custom_template",
    variables=variables,
    fallback="I can't help with that. Would you like to try something else?",
)
```

### Template Validation

```python
# Check if template has all required variables
template = library.get_template(drift_type, category)
missing = set(template.variables) - set(my_variables.keys())
if missing:
    raise ValueError(f"Missing variables: {missing}")
```
