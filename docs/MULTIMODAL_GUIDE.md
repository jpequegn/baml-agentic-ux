# Multi-Modal LUI User Guide

A comprehensive guide to building multi-modal Language User Interfaces with the BAML Agentic UX framework. This guide covers voice, visual, and text modalities with full accessibility support.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Type Reference](#type-reference)
4. [Modality Selection](#modality-selection)
5. [SSML Voice Guide](#ssml-voice-guide)
6. [Visual Elements](#visual-elements)
7. [Accessibility](#accessibility)
8. [Graceful Degradation](#graceful-degradation)
9. [Examples](#examples)

---

## Quick Start

### Basic Multi-Modal Response

Create a response that works across text, voice, and visual modalities:

```python
from baml_client import b
from baml_client.types import (
    Modality,
    MultiModalResponse,
    TextResponse,
    VoiceResponse,
    AccessibilityMeta,
    TextFormat,
    AriaLive,
    ReadingLevel,
    CognitiveLoad,
)

# Create a simple multi-modal response
response = MultiModalResponse(
    response_id="greeting-001",
    primary_modality=Modality.HYBRID,
    text=TextResponse(
        content="Hello! Welcome to our service.",
        format=TextFormat.PLAIN,
    ),
    voice=VoiceResponse(
        ssml="<speak>Hello! <break strength='weak'/> Welcome to our service.</speak>",
        plain_text="Hello! Welcome to our service.",
        voice_id="friendly-assistant",
    ),
    accessibility=AccessibilityMeta(
        aria_label="Welcome greeting",
        aria_live=AriaLive.POLITE,
        reading_level=ReadingLevel.BASIC,
        cognitive_load=CognitiveLoad.LOW,
    ),
)
```

### Using AI Generation

Use BAML functions to generate multi-modal responses:

```python
from baml_client import b

# Generate a multi-modal response using AI
result = b.GenerateMultiModalResponse(
    prompt="Welcome the user to a weather app",
    modalities=[Modality.TEXT, Modality.VOICE, Modality.VISUAL],
    user_preferences=UserPreferences(
        preferred_modality=Modality.HYBRID,
        accessibility_needs=[],
    ),
)
```

---

## Core Concepts

### Modalities

The framework supports four modality types:

| Modality | Use Case | Best For |
|----------|----------|----------|
| `TEXT` | Written content | Detailed information, editing, precise data |
| `VOICE` | Spoken content | Hands-free, quick responses, accessibility |
| `VISUAL` | Rich visual elements | Data visualization, choices, complex info |
| `HYBRID` | Combined modalities | Full experience, adaptive scenarios |

### When to Use Each Modality

**TEXT is best for:**
- Detailed procedures and documentation
- Precise values and data entry
- Content that users may want to copy/paste
- Reference information

**VOICE is best for:**
- Hands-free scenarios (driving, cooking)
- Quick acknowledgments and confirmations
- Users with visual impairments
- Sequential, guided instructions

**VISUAL is best for:**
- Data comparisons and charts
- Selection from multiple options
- Spatial relationships
- Complex forms and inputs

**HYBRID is recommended for:**
- Rich, complete user experiences
- Maximum accessibility coverage
- Adaptive interfaces that adjust to context

---

## Type Reference

### Core Types

#### MultiModalResponse

The main response type combining all modalities:

```python
class MultiModalResponse:
    response_id: str           # Unique identifier
    primary_modality: Modality # Preferred output modality
    text: TextResponse | None  # Text content
    voice: VoiceResponse | None # Voice content with SSML
    visuals: List[MultiModalVisualElement] | None  # Visual elements
    actions: List[MultiModalAction] | None  # User actions
    accessibility: AccessibilityMeta  # Accessibility metadata
    timing: ResponseTiming | None  # Timing hints
    context_hints: ContextHints | None  # Context for adapting
```

#### TextResponse

Text content with formatting:

```python
class TextResponse:
    content: str         # The text content
    format: TextFormat   # PLAIN, MARKDOWN, HTML, RICH
    highlights: List[TextHighlight] | None  # Important sections
    metadata: Dict[str, str] | None
```

#### VoiceResponse

Voice content with SSML support:

```python
class VoiceResponse:
    ssml: str           # SSML-formatted speech
    plain_text: str     # Fallback plain text
    voice_id: str | None  # Voice identifier
    language: str | None  # Language code (e.g., "en-US")
    emotion: str | None   # Emotional tone
    speaking_style: VoiceSpeakingStyle | None
```

### Enums

#### Modality

```python
class Modality(Enum):
    TEXT = "TEXT"
    VOICE = "VOICE"
    VISUAL = "VISUAL"
    HYBRID = "HYBRID"
```

#### TextFormat

```python
class TextFormat(Enum):
    PLAIN = "PLAIN"
    MARKDOWN = "MARKDOWN"
    HTML = "HTML"
    RICH = "RICH"
```

#### VoiceSpeakingStyle

```python
class VoiceSpeakingStyle(Enum):
    NEUTRAL = "NEUTRAL"
    CONVERSATIONAL = "CONVERSATIONAL"
    PROFESSIONAL = "PROFESSIONAL"
    FRIENDLY = "FRIENDLY"
    EMPATHETIC = "EMPATHETIC"
    EXCITED = "EXCITED"
```

---

## Modality Selection

### Automatic Selection

The framework can automatically select the best modality based on context:

```python
from baml_client.types import (
    DeviceCapabilities,
    EnvironmentContext,
    ContentMetadata,
    ModalityRecommendation,
    ScreenSize,
    NoiseLevel,
    PrivacyLevel,
)

# Define device capabilities
device = DeviceCapabilities(
    has_screen=True,
    has_speaker=True,
    has_microphone=True,
    screen_size=ScreenSize.MEDIUM,
    supports_touch=True,
)

# Define environment context
environment = EnvironmentContext(
    noise_level=NoiseLevel.MODERATE,
    privacy_level=PrivacyLevel.PRIVATE,
    lighting=None,
    mobility=None,
)

# Get modality recommendation
result = b.RecommendModality(
    device=device,
    environment=environment,
    content=ContentMetadata(
        content_type=ContentType.INFORMATIONAL,
        message_length=MessageLength.MEDIUM,
        priority=MessagePriority.NORMAL,
    ),
)

# Result contains recommended modality and reasoning
print(f"Recommended: {result.recommended_modality}")
print(f"Reason: {result.reasoning}")
```

### Selection Rules

| Context | Recommended Modality | Reason |
|---------|---------------------|--------|
| No screen | VOICE | Cannot display visual content |
| No speaker | TEXT or VISUAL | Cannot play audio |
| High noise | VISUAL or TEXT | Voice may not be heard |
| Private environment | Any | All modalities suitable |
| Public environment | TEXT or VISUAL | Voice may disturb others |
| Driving/hands-free | VOICE | Eyes and hands occupied |
| Blind user | VOICE | Screen reader or audio output |
| Deaf user | TEXT or VISUAL | Cannot hear audio |

### User Preferences

Always respect user preferences when selecting modalities:

```python
from baml_client.types import UserPreferences, AccessibilityNeed

preferences = UserPreferences(
    preferred_modality=Modality.TEXT,
    accessibility_needs=[AccessibilityNeed.DEAF],
    language="en-US",
)

# The system will prioritize TEXT/VISUAL for this user
```

---

## SSML Voice Guide

### SSML Basics

SSML (Speech Synthesis Markup Language) provides fine-grained control over voice output:

```xml
<speak>
    Hello! <break strength="weak"/>
    Welcome to our <emphasis level="moderate">amazing</emphasis> service.
</speak>
```

### Supported Elements

#### Break (Pauses)

```xml
<break strength="none"/>      <!-- No pause -->
<break strength="x-weak"/>    <!-- Very brief pause -->
<break strength="weak"/>      <!-- Brief pause (comma) -->
<break strength="medium"/>    <!-- Medium pause (sentence) -->
<break strength="strong"/>    <!-- Long pause (paragraph) -->
<break strength="x-strong"/>  <!-- Very long pause -->
<break time="500ms"/>         <!-- Specific duration -->
```

#### Emphasis

```xml
<emphasis level="reduced">less important</emphasis>
<emphasis level="moderate">important</emphasis>
<emphasis level="strong">very important</emphasis>
```

#### Prosody (Rate, Pitch, Volume)

```xml
<!-- Rate -->
<prosody rate="x-slow">Very slow speech</prosody>
<prosody rate="slow">Slow speech</prosody>
<prosody rate="medium">Normal speech</prosody>
<prosody rate="fast">Fast speech</prosody>
<prosody rate="x-fast">Very fast speech</prosody>

<!-- Pitch -->
<prosody pitch="x-low">Very low pitch</prosody>
<prosody pitch="low">Low pitch</prosody>
<prosody pitch="medium">Normal pitch</prosody>
<prosody pitch="high">High pitch</prosody>
<prosody pitch="x-high">Very high pitch</prosody>

<!-- Volume -->
<prosody volume="silent">Silent</prosody>
<prosody volume="x-soft">Whisper</prosody>
<prosody volume="soft">Soft</prosody>
<prosody volume="medium">Normal volume</prosody>
<prosody volume="loud">Loud</prosody>
<prosody volume="x-loud">Very loud</prosody>

<!-- Combined -->
<prosody rate="slow" pitch="low" volume="soft">
    Speaking slowly, quietly, with low pitch
</prosody>
```

#### Say-As (Interpretation)

```xml
<say-as interpret-as="number">12345</say-as>
<say-as interpret-as="cardinal">42</say-as>
<say-as interpret-as="ordinal">1</say-as>  <!-- "first" -->
<say-as interpret-as="characters">API</say-as>  <!-- "A P I" -->
<say-as interpret-as="date" format="mdy">12/25/2024</say-as>
<say-as interpret-as="time">2:30pm</say-as>
<say-as interpret-as="telephone">+1-555-1234</say-as>
<say-as interpret-as="currency">$49.99</say-as>
<say-as interpret-as="unit">5 kilometers</say-as>
```

#### Audio

```xml
<audio src="https://example.com/sound.mp3">
    Fallback text if audio fails
</audio>
```

### SSML Types in Code

```python
from baml_client.types import (
    SSMLElement,
    SSMLElementType,
    SSMLBreakStrength,
    SSMLProsodyRate,
    SSMLProsodyPitch,
    SSMLProsodyVolume,
    SSMLEmphasisLevel,
)

# Create SSML elements programmatically
break_element = SSMLElement(
    element_type=SSMLElementType.BREAK,
    break_strength=SSMLBreakStrength.MEDIUM,
)

prosody_element = SSMLElement(
    element_type=SSMLElementType.PROSODY,
    prosody_rate=SSMLProsodyRate.SLOW,
    prosody_pitch=SSMLProsodyPitch.LOW,
    prosody_volume=SSMLProsodyVolume.SOFT,
    content="Important announcement",
)
```

---

## Visual Elements

### Adaptive Cards

Adaptive Cards provide rich, cross-platform visual elements:

```python
from baml_client.types import (
    AdaptiveCard,
    CardElement,
    CardElementType,
    CardAction,
    CardActionType,
)

# Create a simple card
card = AdaptiveCard(
    card_type="AdaptiveCard",
    version="1.5",
    body=[
        CardElement(
            element_type=CardElementType.TEXT_BLOCK,
            text="Welcome!",
            size="Large",
            weight="Bolder",
        ),
        CardElement(
            element_type=CardElementType.TEXT_BLOCK,
            text="This is adaptive card content.",
            wrap=True,
        ),
    ],
    actions=[
        CardAction(
            action_type=CardActionType.SUBMIT,
            title="Get Started",
            data={"action": "start"},
        ),
    ],
)
```

### Visual Element Types

```python
class MultiModalVisualType(Enum):
    TEXT_BLOCK = "TEXT_BLOCK"   # Text content
    IMAGE = "IMAGE"             # Images
    TABLE = "TABLE"             # Data tables
    CHART = "CHART"             # Charts and graphs
    CARD = "CARD"               # Adaptive cards
    BUTTON_GROUP = "BUTTON_GROUP"  # Action buttons
    INPUT_FORM = "INPUT_FORM"   # Form inputs
    LIST = "LIST"               # Lists
    PROGRESS = "PROGRESS"       # Progress indicators
    NOTIFICATION = "NOTIFICATION"  # Notifications
```

### Card Element Types

```python
class CardElementType(Enum):
    TEXT_BLOCK = "TEXT_BLOCK"
    IMAGE = "IMAGE"
    COLUMN_SET = "COLUMN_SET"
    COLUMN = "COLUMN"
    CONTAINER = "CONTAINER"
    FACT_SET = "FACT_SET"
    IMAGE_SET = "IMAGE_SET"
    INPUT_TEXT = "INPUT_TEXT"
    INPUT_NUMBER = "INPUT_NUMBER"
    INPUT_DATE = "INPUT_DATE"
    INPUT_TIME = "INPUT_TIME"
    INPUT_TOGGLE = "INPUT_TOGGLE"
    INPUT_CHOICE_SET = "INPUT_CHOICE_SET"
    ACTION_SET = "ACTION_SET"
    RICH_TEXT_BLOCK = "RICH_TEXT_BLOCK"
    MEDIA = "MEDIA"
    TABLE = "TABLE"
```

---

## Accessibility

### WCAG Compliance

The framework supports WCAG 2.2 compliance at AA level:

```python
from baml_client.types import (
    AccessibilityMeta,
    WCAGLevel,
    WCAGCategory,
    AriaLive,
    ReadingLevel,
    CognitiveLoad,
)

accessibility = AccessibilityMeta(
    aria_label="Weather information display",
    aria_live=AriaLive.POLITE,
    screen_reader_text="Current temperature is 72 degrees Fahrenheit",
    reading_level=ReadingLevel.BASIC,
    cognitive_load=CognitiveLoad.LOW,
    wcag_level=WCAGLevel.AA,
)
```

### ARIA Live Regions

Control how screen readers announce updates:

| Value | Use Case |
|-------|----------|
| `OFF` | No announcements |
| `POLITE` | Announce when user is idle (recommended default) |
| `ASSERTIVE` | Announce immediately (urgent notifications only) |

### Reading Levels

Match content complexity to user needs:

```python
class ReadingLevel(Enum):
    BASIC = "BASIC"           # Simple vocabulary, short sentences
    INTERMEDIATE = "INTERMEDIATE"  # Standard complexity
    ADVANCED = "ADVANCED"     # Technical/specialized content
    TECHNICAL = "TECHNICAL"   # Expert-level content
```

### Cognitive Load

Consider cognitive impact of responses:

```python
class CognitiveLoad(Enum):
    MINIMAL = "MINIMAL"   # Single piece of information
    LOW = "LOW"           # Few related items
    MODERATE = "MODERATE" # Multiple items requiring attention
    HIGH = "HIGH"         # Complex decisions/many options
```

### Accessibility Needs

Support different accessibility requirements:

```python
class AccessibilityNeed(Enum):
    BLIND = "BLIND"
    LOW_VISION = "LOW_VISION"
    DEAF = "DEAF"
    HARD_OF_HEARING = "HARD_OF_HEARING"
    MOTOR_IMPAIRED = "MOTOR_IMPAIRED"
    COGNITIVE = "COGNITIVE"
```

### Best Practices

1. **Always provide alt text** for visual elements
2. **Use semantic structure** (headings, lists, landmarks)
3. **Ensure keyboard navigation** for all interactive elements
4. **Test with screen readers** (VoiceOver, NVDA, JAWS)
5. **Provide text alternatives** for audio content
6. **Use sufficient color contrast** (4.5:1 for normal text)
7. **Avoid timing-dependent interactions** where possible
8. **Keep cognitive load appropriate** for the audience

---

## Graceful Degradation

### Fallback Chains

Define what happens when a modality is unavailable:

```python
from baml_client.types import (
    FallbackChain,
    FallbackStep,
    FallbackTrigger,
    ModalityErrorType,
)

fallback = FallbackChain(
    original_modality=Modality.VOICE,
    fallback_steps=[
        FallbackStep(
            from_modality=Modality.VOICE,
            to_modality=Modality.TEXT,
            trigger=FallbackTrigger.MODALITY_UNAVAILABLE,
            transformation_hint="Convert SSML to plain text",
        ),
        FallbackStep(
            from_modality=Modality.TEXT,
            to_modality=Modality.VISUAL,
            trigger=FallbackTrigger.USER_PREFERENCE,
            transformation_hint="Display as card",
        ),
    ],
    final_fallback=Modality.TEXT,
)
```

### Error Types

```python
class ModalityErrorType(Enum):
    UNAVAILABLE = "UNAVAILABLE"      # Hardware/software unavailable
    TIMEOUT = "TIMEOUT"              # Operation timed out
    PERMISSION_DENIED = "PERMISSION_DENIED"  # User denied permission
    RATE_LIMITED = "RATE_LIMITED"    # Too many requests
    CONTENT_ERROR = "CONTENT_ERROR"  # Content generation failed
    NETWORK_ERROR = "NETWORK_ERROR"  # Network issue
```

### Recovery Tiers

```python
class RecoveryTier(Enum):
    SELF_REPAIR = "SELF_REPAIR"      # Automatic retry/fallback
    GUIDED_REPAIR = "GUIDED_REPAIR"  # User guidance provided
    ESCALATION = "ESCALATION"        # Requires human intervention
```

### Notification Styles

```python
class NotificationStyle(Enum):
    SUBTLE = "SUBTLE"           # Minimal, non-intrusive
    INFORMATIVE = "INFORMATIVE" # Clear explanation
    PROMINENT = "PROMINENT"     # Cannot be missed
    URGENT = "URGENT"           # Immediate attention required
```

---

## Examples

### Weather Response (Multi-Modal)

```python
weather_response = MultiModalResponse(
    response_id="weather-001",
    primary_modality=Modality.HYBRID,
    text=TextResponse(
        content="Currently 72°F and sunny in San Francisco.",
        format=TextFormat.PLAIN,
    ),
    voice=VoiceResponse(
        ssml="""
        <speak>
            <prosody rate="medium">
                Currently <say-as interpret-as="unit">72 degrees Fahrenheit</say-as>
                and sunny in San Francisco.
            </prosody>
        </speak>
        """,
        plain_text="Currently 72 degrees and sunny in San Francisco.",
        voice_id="weather-voice",
    ),
    visuals=[
        MultiModalVisualElement(
            element_type=MultiModalVisualType.CARD,
            content='{"type": "AdaptiveCard", "version": "1.5", "body": [...]}',
            alt_text="Weather card showing 72°F sunny conditions",
            priority=1,
            interactive=False,
        ),
    ],
    accessibility=AccessibilityMeta(
        aria_label="Weather information for San Francisco",
        aria_live=AriaLive.POLITE,
        screen_reader_text="The current weather in San Francisco is 72 degrees Fahrenheit and sunny",
        reading_level=ReadingLevel.BASIC,
        cognitive_load=CognitiveLoad.LOW,
    ),
)
```

### Error Notification (Accessible)

```python
error_response = MultiModalResponse(
    response_id="error-001",
    primary_modality=Modality.HYBRID,
    text=TextResponse(
        content="Unable to complete your request. Please try again.",
        format=TextFormat.PLAIN,
        highlights=[
            TextHighlight(
                start_index=0,
                end_index=31,
                highlight_type=HighlightType.IMPORTANT,
            ),
        ],
    ),
    voice=VoiceResponse(
        ssml="""
        <speak>
            <prosody rate="slow" pitch="low">
                Sorry, <break strength="weak"/>
                I was unable to complete your request.
                <break strength="medium"/>
                Please try again.
            </prosody>
        </speak>
        """,
        plain_text="Sorry, I was unable to complete your request. Please try again.",
    ),
    accessibility=AccessibilityMeta(
        aria_label="Error notification",
        aria_live=AriaLive.ASSERTIVE,  # Immediate announcement for errors
        reading_level=ReadingLevel.BASIC,
        cognitive_load=CognitiveLoad.LOW,
    ),
)
```

### Form Input (Visual with Fallback)

```python
form_response = MultiModalResponse(
    response_id="form-001",
    primary_modality=Modality.VISUAL,
    text=TextResponse(
        content="Please enter your name and email address.",
        format=TextFormat.PLAIN,
    ),
    voice=VoiceResponse(
        ssml="""
        <speak>
            Please tell me your name.
            <break strength="strong"/>
            Then spell your email address.
        </speak>
        """,
        plain_text="Please tell me your name, then spell your email address.",
    ),
    visuals=[
        MultiModalVisualElement(
            element_type=MultiModalVisualType.INPUT_FORM,
            content='{"fields": [{"id": "name", "label": "Name"}, {"id": "email", "label": "Email"}]}',
            alt_text="Registration form with name and email fields",
            priority=1,
            interactive=True,
        ),
    ],
    accessibility=AccessibilityMeta(
        aria_label="Registration form",
        aria_live=AriaLive.POLITE,
        reading_level=ReadingLevel.BASIC,
        cognitive_load=CognitiveLoad.LOW,
    ),
)
```

---

## Further Resources

- [Adaptive Cards Documentation](https://adaptivecards.io/)
- [SSML W3C Specification](https://www.w3.org/TR/speech-synthesis11/)
- [WCAG 2.2 Guidelines](https://www.w3.org/WAI/WCAG22/quickref/)
- [BAML Documentation](https://docs.boundaryml.com/)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Phase 1 | Initial multi-modal support |
