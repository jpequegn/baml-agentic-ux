# Phase 1: Multi-Modal LUI Implementation Plan

## Research Summary

Based on comprehensive research into multi-modal conversational AI frameworks, this document outlines the implementation plan for adding multi-modal support to the BAML Agentic UX framework.

### Key Research Findings

#### 1. Modality Types and Affordances

| Modality | Best For | Avoid For |
|----------|----------|-----------|
| **Voice** | Sequential info, higher-level commands, hands-free | Precise data entry, complex parameters |
| **Text** | Detailed procedures, exact values, editing | Long-form input on mobile |
| **Visual** | Spatial relationships, data comparison, choices | Users with visual impairments (need fallback) |

#### 2. Cognitive Load Considerations

- Modality switching carries **measurable cognitive costs** (23+ minutes to fully refocus after interruption)
- Multi-modal teaching reduces cognitive load by **34.9%** vs single-modality
- Users prefer to **stay in same modality** even when errors occur
- Compatible pairings (auditory-vocal, visual-manual) reduce switching costs

#### 3. Framework Patterns (Industry Standards)

- **Adaptive Cards** (Microsoft): JSON schema for cross-platform visual elements
- **SSML**: W3C standard for speech synthesis markup
- **LangGraph**: State machine for conversation flow
- **MCP**: Model Context Protocol for tool integration

#### 4. Accessibility Requirements (WCAG 2.2)

- `aria-live="polite"` for screen reader announcements
- `role="log"` for chat containers
- Sound notifications for message send/receive
- Fallback modalities when primary unavailable
- Timing: Avoid announcing updates too frequently

---

## Implementation Architecture

### Phase 1 Structure

```
Phase 1: Multi-Modal LUI Support
├── Task 1.1: Core Type System
│   └── Define BAML types for multi-modal responses
├── Task 1.2: SSML Integration
│   └── Speech synthesis markup support
├── Task 1.3: Visual Elements (Adaptive Cards)
│   └── Rich visual response components
├── Task 1.4: Modality Selection Logic
│   └── Automatic modality recommendation
├── Task 1.5: Graceful Degradation
│   └── Fallback when modality unavailable
├── Task 1.6: Multi-Modal Response Generation
│   └── BAML function for generating responses
├── Task 1.7: Accessibility Compliance
│   └── WCAG 2.2 validation and requirements
└── Task 1.8: Testing and Documentation
    └── Tests, examples, and docs
```

---

## Task Breakdown

### Task 1.1: Core Multi-Modal Type System

**Objective**: Define BAML types for representing multi-modal responses.

**Deliverables**:
- `baml_src/multimodal_types.baml` - Core type definitions

**Types to Implement**:

```baml
enum Modality {
  TEXT
  VOICE
  VISUAL
  HYBRID
}

enum VisualElementType {
  TEXT_BLOCK
  IMAGE
  TABLE
  CHART
  CARD
  BUTTON_GROUP
  INPUT_FORM
}

class VisualElement {
  element_type VisualElementType
  content string
  alt_text string?  // Accessibility: Required for images
  aria_label string?
  children VisualElement[]?
}

class VoiceResponse {
  plain_text string      // Fallback for non-SSML systems
  ssml string?           // Optional SSML markup
  voice_id string?       // Voice selection
  speed float?           // 0.5-2.0, default 1.0
  pitch string?          // "x-low", "low", "medium", "high", "x-high"
}

class TextResponse {
  content string
  formatting TextFormatting?
  suggestions string[]?  // Quick reply suggestions
}

class MultiModalResponse {
  primary_modality Modality
  text TextResponse?
  voice VoiceResponse?
  visual VisualElement[]?
  actions Action[]?
  suggested_modality Modality?  // System recommendation
  accessibility AccessibilityMeta
}

class Action {
  action_id string
  action_type ActionType
  label string
  data string?
  confirmation_required bool
}

enum ActionType {
  OPEN_URL
  SUBMIT
  SHOW_CARD
  SWITCH_MODALITY
  SPEAK
  NAVIGATE
}

class AccessibilityMeta {
  aria_live AriaLiveType?
  aria_label string?
  role string?
  reading_level ReadingLevel?
  cognitive_load CognitiveLoad?
}

enum AriaLiveType {
  OFF
  POLITE
  ASSERTIVE
}

enum ReadingLevel {
  SIMPLE      // Grade 5, Flesch-Kincaid ~80
  STANDARD    // Grade 8, Flesch-Kincaid ~60
  ADVANCED    // Grade 12, Flesch-Kincaid ~40
  TECHNICAL   // No limit
}

enum CognitiveLoad {
  MINIMAL     // 1 concept, <3 sentences
  LOW         // 2-3 concepts
  STANDARD    // Normal complexity
  HIGH        // Power user, dense info
}
```

**Success Criteria**:
- [ ] All types compile without errors
- [ ] Types are documented with `@description`
- [ ] Unit tests validate type construction
- [ ] Example schemas use new types

**Estimated Complexity**: Medium
**Dependencies**: None

---

### Task 1.2: SSML Integration

**Objective**: Add Speech Synthesis Markup Language support for voice output.

**Deliverables**:
- `baml_src/ssml_types.baml` - SSML-specific types
- `src/lui_schema_export/ssml.py` - SSML generation utilities

**Types to Implement**:

```baml
class SSMLDocument {
  content SSMLElement[]
  language string?  // e.g., "en-US"
}

class SSMLElement {
  element_type SSMLElementType
  text string?
  attributes SSMLAttributes?
  children SSMLElement[]?
}

enum SSMLElementType {
  SPEAK
  BREAK
  EMPHASIS
  PROSODY
  SAY_AS
  PHONEME
  SUB
  AUDIO
}

class SSMLAttributes {
  // Break
  time string?          // "500ms", "1s"
  strength string?      // "none", "x-weak", "weak", "medium", "strong", "x-strong"

  // Emphasis
  level string?         // "reduced", "none", "moderate", "strong"

  // Prosody
  rate string?          // "x-slow", "slow", "medium", "fast", "x-fast" or percentage
  pitch string?         // "x-low", "low", "medium", "high", "x-high" or percentage
  volume string?        // "silent", "x-soft", "soft", "medium", "loud", "x-loud"

  // Say-as
  interpret_as string?  // "date", "time", "telephone", "cardinal", "ordinal"
  format string?        // e.g., "mdy" for dates

  // Audio
  src string?           // Audio file URL
}
```

**Python Utilities**:

```python
def generate_ssml(voice_response: VoiceResponse) -> str:
    """Generate SSML from VoiceResponse type."""

def text_to_ssml(text: str, options: SSMLOptions = None) -> str:
    """Convert plain text to SSML with smart defaults."""

def validate_ssml(ssml: str) -> ValidationResult:
    """Validate SSML against W3C spec."""
```

**Success Criteria**:
- [ ] SSML types defined in BAML
- [ ] Python generator creates valid SSML
- [ ] Works with major TTS providers (Google, AWS, Azure)
- [ ] Fallback to plain text when SSML not supported

**Estimated Complexity**: Medium
**Dependencies**: Task 1.1

---

### Task 1.3: Visual Elements (Adaptive Cards)

**Objective**: Support rich visual responses using Adaptive Cards-compatible format.

**Deliverables**:
- `baml_src/visual_types.baml` - Visual element types
- `src/lui_schema_export/adaptive_cards.py` - Adaptive Cards exporter

**Extended Visual Types**:

```baml
class AdaptiveCard {
  schema_version string  // "1.5"
  body CardElement[]
  actions CardAction[]?
  fallback_text string   // Accessibility: Screen reader fallback
}

class CardElement {
  element_type CardElementType
  // Common properties
  id string?
  spacing Spacing?
  separator bool?

  // Type-specific (use appropriate based on element_type)
  text string?
  size TextSize?
  weight TextWeight?
  color TextColor?
  wrap bool?

  // Image
  url string?
  alt_text string?

  // FactSet
  facts Fact[]?

  // Container
  items CardElement[]?
}

enum CardElementType {
  TEXT_BLOCK
  IMAGE
  RICH_TEXT_BLOCK
  FACT_SET
  CONTAINER
  COLUMN_SET
  TABLE
  INPUT_TEXT
  INPUT_NUMBER
  INPUT_DATE
  INPUT_CHOICE_SET
}

class CardAction {
  action_type CardActionType
  title string
  url string?
  data string?
  card AdaptiveCard?  // For SHOW_CARD
}

enum CardActionType {
  OPEN_URL
  SUBMIT
  SHOW_CARD
  TOGGLE_VISIBILITY
}

class Fact {
  title string
  value string
}
```

**Success Criteria**:
- [ ] Visual types cover common UI patterns
- [ ] Exporter generates valid Adaptive Cards JSON
- [ ] Cards render in Microsoft Teams, Outlook (test manually)
- [ ] Fallback text always present for accessibility

**Estimated Complexity**: Medium-High
**Dependencies**: Task 1.1

---

### Task 1.4: Modality Selection Logic

**Objective**: Implement intelligent modality recommendation based on context.

**Deliverables**:
- `baml_src/modality_selection.baml` - Selection logic types and function

**Types and Function**:

```baml
class ModalityContext {
  available_modalities Modality[]
  user_preference Modality?
  device_capabilities DeviceCapabilities
  environment_context EnvironmentContext?
  content_type ContentType
  message_length MessageLength
  urgency UrgencyLevel
}

class DeviceCapabilities {
  has_screen bool
  has_speaker bool
  has_microphone bool
  has_keyboard bool
  screen_size ScreenSize?
}

enum ScreenSize {
  SMALL      // Phone
  MEDIUM     // Tablet
  LARGE      // Desktop
  NONE       // No screen
}

class EnvironmentContext {
  noise_level NoiseLevel?
  privacy_level PrivacyLevel?
  mobility bool?  // User is moving
}

enum NoiseLevel {
  QUIET
  MODERATE
  LOUD
}

enum PrivacyLevel {
  PRIVATE
  SEMI_PRIVATE
  PUBLIC
}

enum ContentType {
  CONFIRMATION
  ERROR
  DATA_TABLE
  LONG_TEXT
  SHORT_RESPONSE
  ACTION_REQUIRED
  DISAMBIGUATION
}

enum MessageLength {
  SHORT      // <20 words
  MEDIUM     // 20-100 words
  LONG       // >100 words
}

enum UrgencyLevel {
  LOW
  NORMAL
  HIGH
  CRITICAL
}

class ModalityRecommendation {
  primary Modality
  secondary Modality?
  rationale string
  confidence float
  fallback_chain Modality[]
}

function SelectModality(
  context: ModalityContext,
  user_accessibility_needs: AccessibilityNeed[]?
) -> ModalityRecommendation {
  client GPT4o
  prompt #"
    Given the context, recommend the optimal modality for this interaction.

    Context:
    - Available modalities: {{ context.available_modalities }}
    - Device: {{ context.device_capabilities }}
    - Content type: {{ context.content_type }}
    - Message length: {{ context.message_length }}
    - Urgency: {{ context.urgency }}

    Accessibility needs: {{ user_accessibility_needs }}

    Guidelines:
    - Voice: Best for short confirmations, hands-free, mobility
    - Text: Best for detailed info, precise data, searchable content
    - Visual: Best for comparisons, tables, spatial info
    - Hybrid: When content benefits from multiple channels

    Always provide a fallback chain for graceful degradation.

    {{ ctx.output_format }}
  "#
}
```

**Success Criteria**:
- [ ] Function recommends appropriate modality for various scenarios
- [ ] Fallback chain always provided
- [ ] Accessibility needs override other preferences
- [ ] Works without environment context (graceful defaults)

**Estimated Complexity**: Medium
**Dependencies**: Task 1.1

---

### Task 1.5: Graceful Degradation

**Objective**: Handle modality failures and provide seamless fallbacks.

**Deliverables**:
- `baml_src/modality_fallback.baml` - Fallback types and logic
- Tests for degradation scenarios

**Types**:

```baml
class ModalityStatus {
  modality Modality
  available bool
  error ModalityError?
  last_successful DateTime?
}

class ModalityError {
  error_type ModalityErrorType
  message string
  recoverable bool
  suggested_fallback Modality?
}

enum ModalityErrorType {
  UNAVAILABLE
  TIMEOUT
  PERMISSION_DENIED
  QUOTA_EXCEEDED
  NETWORK_ERROR
  SERVICE_ERROR
}

class DegradedResponse {
  original_modality Modality
  actual_modality Modality
  response MultiModalResponse
  degradation_notice string?
  recovery_action string?
}

function HandleModalityFailure(
  intended_response: MultiModalResponse,
  failed_modality: Modality,
  error: ModalityError,
  available_modalities: Modality[]
) -> DegradedResponse {
  client GPT4o
  prompt #"
    The {{ failed_modality }} modality failed with: {{ error.message }}

    Original response intended for {{ failed_modality }}:
    {{ intended_response }}

    Available fallback modalities: {{ available_modalities }}

    Transform the response for the best available fallback while:
    1. Preserving all essential information
    2. Adapting format for the new modality
    3. Notifying user of the modality change (briefly)
    4. Suggesting how to recover (if applicable)

    {{ ctx.output_format }}
  "#
}
```

**Fallback Hierarchy**:
```
Voice Failed:
  1. Text with enhanced formatting
  2. Visual with text elements
  3. Minimal text-only

Visual Failed:
  1. Text with structured formatting
  2. Voice with clear segmentation
  3. Plain text

Text Failed:
  1. Voice with natural language
  2. Visual cards
  3. Minimal voice-only
```

**Success Criteria**:
- [ ] All failure scenarios have defined fallbacks
- [ ] User is notified of modality switch (briefly, not intrusively)
- [ ] No information loss during degradation
- [ ] Recovery suggestions when applicable

**Estimated Complexity**: Medium
**Dependencies**: Tasks 1.1, 1.2, 1.3

---

### Task 1.6: Multi-Modal Response Generation

**Objective**: Create the main BAML function for generating multi-modal responses.

**Deliverables**:
- `baml_src/multimodal_generation.baml` - Response generation function

**Function**:

```baml
function GenerateMultiModalResponse(
  intent: IntentExtraction,
  action_result: ActionResult?,
  conversation_context: ConversationContext,
  modality_context: ModalityContext,
  persona: ResponsePersona?
) -> MultiModalResponse {
  client GPT4o
  prompt #"
    Generate a multi-modal response for this interaction.

    ## Intent
    {{ intent }}

    ## Action Result
    {{ action_result }}

    ## Conversation Context
    {{ conversation_context }}

    ## Modality Context
    Available: {{ modality_context.available_modalities }}
    Device: {{ modality_context.device_capabilities }}

    ## Persona
    {{ persona }}

    ## Guidelines

    ### Text Response
    - Clear, concise language
    - Match reading level: {{ modality_context.accessibility.reading_level }}
    - Include quick reply suggestions when appropriate

    ### Voice Response
    - Conversational tone
    - Use SSML for emphasis, pauses, pronunciation
    - Keep under 30 seconds of speech

    ### Visual Elements
    - Use when comparing data or showing structure
    - Always include alt_text for images
    - Provide fallback_text for screen readers

    ### Actions
    - Limit to 3-4 actions maximum
    - Primary action first
    - Confirm destructive actions

    {{ ctx.output_format }}
  "#
}
```

**Success Criteria**:
- [ ] Generates appropriate responses for all modality combinations
- [ ] SSML is valid when voice response included
- [ ] Visual elements have accessibility metadata
- [ ] Actions are appropriately limited
- [ ] Works with existing IntentExtraction and ActionResult types

**Estimated Complexity**: High
**Dependencies**: Tasks 1.1-1.5

---

### Task 1.7: Accessibility Compliance

**Objective**: Ensure all multi-modal features meet WCAG 2.2 AA standards.

**Deliverables**:
- `baml_src/accessibility_validation.baml` - Accessibility types and validation
- `src/lui_simulator/accessibility.py` - Runtime validation

**Types**:

```baml
class AccessibilityRequirements {
  wcag_level WCAGLevel
  screen_reader_support bool
  voice_control_support bool
  reduced_motion bool
  high_contrast bool
  cognitive_support bool
}

enum WCAGLevel {
  A
  AA
  AAA
}

class AccessibilityViolation {
  rule_id string
  severity ViolationSeverity
  element string
  description string
  remediation string
}

enum ViolationSeverity {
  ERROR      // Must fix
  WARNING    // Should fix
  INFO       // Best practice
}

class AccessibilityReport {
  compliant bool
  wcag_level WCAGLevel
  violations AccessibilityViolation[]
  score float  // 0-100
}

function ValidateAccessibility(
  response: MultiModalResponse,
  requirements: AccessibilityRequirements
) -> AccessibilityReport {
  client GPT4o
  prompt #"
    Validate the multi-modal response for accessibility compliance.

    ## Response to Validate
    {{ response }}

    ## Requirements
    WCAG Level: {{ requirements.wcag_level }}
    Screen Reader: {{ requirements.screen_reader_support }}
    Voice Control: {{ requirements.voice_control_support }}

    ## WCAG 2.2 Checks

    ### Perceivable
    - 1.1.1: All images have alt text
    - 1.3.1: Information structure is programmatically determinable
    - 1.4.3: Contrast ratio ≥ 4.5:1 (AA)

    ### Operable
    - 2.1.1: All actions keyboard accessible
    - 2.4.4: Link/action purpose clear from text

    ### Understandable
    - 3.1.1: Language specified
    - 3.2.1: Predictable navigation

    ### Robust
    - 4.1.2: All elements have accessible names

    ## Voice-Specific
    - Speech rate adjustable
    - Sufficient pauses between concepts
    - No time limits on responses

    Report all violations with remediation guidance.

    {{ ctx.output_format }}
  "#
}
```

**Python Validation**:

```python
def validate_multimodal_response(response: MultiModalResponse) -> AccessibilityReport:
    """Runtime validation of multi-modal response accessibility."""
    violations = []

    # Check visual elements have alt text
    for element in response.visual or []:
        if element.element_type == "IMAGE" and not element.alt_text:
            violations.append(AccessibilityViolation(
                rule_id="WCAG-1.1.1",
                severity="ERROR",
                element=element.content,
                description="Image missing alt text",
                remediation="Add descriptive alt_text to image element"
            ))

    # Check voice response has plain text fallback
    if response.voice and not response.text:
        violations.append(AccessibilityViolation(
            rule_id="WCAG-1.1.1",
            severity="ERROR",
            element="voice_response",
            description="Voice response has no text fallback",
            remediation="Add text response as fallback for voice"
        ))

    # ... additional checks

    return AccessibilityReport(
        compliant=len([v for v in violations if v.severity == "ERROR"]) == 0,
        violations=violations,
        score=calculate_score(violations)
    )
```

**Success Criteria**:
- [ ] All visual elements validated for alt text
- [ ] Voice responses have text fallbacks
- [ ] Actions have clear accessible names
- [ ] SSML validated for screen reader compatibility
- [ ] Integration with usability analysis

**Estimated Complexity**: Medium-High
**Dependencies**: Tasks 1.1-1.6

---

### Task 1.8: Testing and Documentation

**Objective**: Comprehensive testing and documentation for multi-modal features.

**Deliverables**:
- `tests/test_multimodal.py` - Unit and integration tests
- `examples/multimodal_schema.json` - Example multi-modal schema
- `docs/MULTIMODAL_GUIDE.md` - User documentation

**Test Cases**:

```python
class TestMultiModalTypes:
    """Test BAML type construction and validation."""

    def test_multimodal_response_construction(self):
        """Test creating a complete multi-modal response."""

    def test_ssml_generation(self):
        """Test SSML generation from VoiceResponse."""

    def test_adaptive_card_export(self):
        """Test Adaptive Cards JSON export."""

    def test_accessibility_validation(self):
        """Test accessibility checks catch violations."""

class TestModalitySelection:
    """Test modality recommendation logic."""

    def test_voice_recommended_for_short_confirmation(self):
        """Voice should be recommended for short confirmations."""

    def test_visual_recommended_for_data_comparison(self):
        """Visual should be recommended for tables/comparisons."""

    def test_accessibility_overrides_preference(self):
        """Accessibility needs should override user preference."""

class TestGracefulDegradation:
    """Test fallback behavior when modalities fail."""

    def test_voice_to_text_fallback(self):
        """Voice failure should fall back to text."""

    def test_visual_to_text_fallback(self):
        """Visual failure should fall back to text."""

    def test_no_information_loss(self):
        """Degradation should preserve all essential info."""
```

**Documentation Sections**:

1. **Quick Start** - Basic multi-modal response generation
2. **Type Reference** - All BAML types documented
3. **Modality Selection** - When to use which modality
4. **Accessibility** - WCAG compliance guide
5. **Graceful Degradation** - Handling failures
6. **Examples** - Real-world usage patterns

**Success Criteria**:
- [ ] >90% code coverage for new modules
- [ ] All example schemas validate
- [ ] Documentation reviewed for clarity
- [ ] Integration tests pass with mock LLM

**Estimated Complexity**: Medium
**Dependencies**: Tasks 1.1-1.7

---

## Implementation Timeline

| Task | Estimated Effort | Dependencies |
|------|------------------|--------------|
| 1.1 Core Types | 2-3 hours | None |
| 1.2 SSML | 3-4 hours | 1.1 |
| 1.3 Visual Elements | 4-5 hours | 1.1 |
| 1.4 Modality Selection | 3-4 hours | 1.1 |
| 1.5 Graceful Degradation | 3-4 hours | 1.1-1.3 |
| 1.6 Response Generation | 4-5 hours | 1.1-1.5 |
| 1.7 Accessibility | 4-5 hours | 1.1-1.6 |
| 1.8 Testing & Docs | 4-5 hours | 1.1-1.7 |

**Total Estimated Effort**: 27-35 hours

---

## Success Metrics

### Functional
- [ ] Generate responses for all modality combinations
- [ ] SSML validates against W3C spec
- [ ] Adaptive Cards render in Teams/Outlook
- [ ] Modality selection provides reasonable recommendations

### Quality
- [ ] >90% test coverage for new code
- [ ] All accessibility checks pass at AA level
- [ ] No information loss during degradation
- [ ] Documentation complete and clear

### Integration
- [ ] Works with existing IntentExtraction
- [ ] Integrates with usability analysis
- [ ] Schema export includes multi-modal components

---

## Research Sources

### Multi-Modal Frameworks
- [Pipecat](https://github.com/pipecat-ai/pipecat) - Real-time voice/video
- [LangGraph](https://www.langchain.com/langgraph) - State machine orchestration
- [Adaptive Cards](https://adaptivecards.io/) - Cross-platform visual elements
- [SSML Specification](https://www.w3.org/TR/speech-synthesis11/) - W3C standard

### Cognitive Research
- Modality switching increases cognitive load by ~34.9% (NASA-TLX studies)
- Users prefer same modality even with errors (HCI research)
- Recovery time after context switch: ~23 minutes

### Accessibility
- [WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/) - Accessibility guidelines
- [Chatbot Accessibility Playbook](https://mitre.github.io/chatbot-accessibility-playbook/) - MITRE
- [Orange Chatbot Guidelines](https://a11y-guidelines.orange.com/en/articles/chatbot/) - Best practices
