// ARIA Live Region Configuration
// BAML types for screen reader-compatible live regions
// Issue #75 - Task 4.9: ARIA Live Region Generator
// Part of #27 - Phase 4: LUI Accessibility Standards

// ============================================
// ARIA Politeness Levels
// ============================================

/// ARIA live region politeness levels
enum ARIAPoliteness {
  OFF @description("No announcements - content changes silently")
  POLITE @description("Wait for user idle before announcing (default)")
  ASSERTIVE @description("Interrupt immediately - use sparingly for critical messages")
}

/// ARIA landmark and widget roles for live regions
enum ARIARole {
  LOG @description("Sequential information log (chat history)")
  STATUS @description("Status information (non-critical)")
  ALERT @description("Important messages requiring attention")
  ALERTDIALOG @description("Alert that requires user response")
  PROGRESSBAR @description("Progress indication")
  TIMER @description("Time-related updates")
  MARQUEE @description("Scrolling text (non-essential)")
  REGION @description("Generic live region")
}

/// What types of changes to announce
enum ARIARelevant {
  ADDITIONS @description("Only new nodes")
  REMOVALS @description("Only removed nodes")
  TEXT @description("Only text changes")
  ALL @description("All changes")
  ADDITIONS_TEXT @description("New nodes and text changes (default)")
  ADDITIONS_REMOVALS @description("Node additions and removals")
}

/// Major screen reader platforms
enum ScreenReader {
  JAWS @description("Windows + Chrome/Firefox")
  NVDA @description("Windows + Firefox")
  VOICEOVER @description("macOS/iOS + Safari")
  TALKBACK @description("Android")
  NARRATOR @description("Windows built-in")
  ORCA @description("Linux")
}

/// Types of content for automatic ARIA configuration
enum ARIAContentType {
  MESSAGE @description("Standard message/response")
  ERROR @description("Error message")
  WARNING @description("Warning message")
  SUCCESS @description("Success confirmation")
  INFO @description("Informational message")
  PROGRESS @description("Progress update")
  CHAT @description("Chat/conversation message")
  NOTIFICATION @description("Notification")
}

// ============================================
// Configuration Types
// ============================================

/// Configuration for ARIA live region
class ARIAConfig {
  role ARIARole @description("ARIA role for the region")
  aria_live ARIAPoliteness @description("Politeness level (off/polite/assertive)")
  aria_atomic bool @description("Whether to announce entire region on changes")
  aria_relevant ARIARelevant @description("What types of changes to announce")
  aria_busy bool @description("Whether content is currently being updated")
  aria_label string? @description("Accessible label for the region")
  aria_labelledby string? @description("ID of element providing label")
  aria_describedby string? @description("ID of element providing description")
}

/// Screen reader-specific hints
class ScreenReaderHint {
  reader ScreenReader @description("Target screen reader")
  recommendation string @description("Specific configuration recommendation")
  notes string @description("Additional notes for developers")
}

// ============================================
// Live Region Generation
// ============================================

/// Input for live region generation
class LiveRegionInput {
  content string @description("Content to wrap in live region")
  politeness ARIAPoliteness @description("Politeness level")
  role ARIARole? @description("Optional specific role")
  content_type ARIAContentType? @description("Type of content for auto-config")
  sender string? @description("Who sent the message (for chat)")
  aria_label string? @description("Custom accessible label")
}

/// Result of live region generation
class LiveRegionResult {
  html string @description("Generated HTML markup")
  config ARIAConfig @description("Configuration used")
  screen_reader_hints ScreenReaderHint[] @description("Hints for major screen readers")
  is_valid bool @description("Whether generated HTML is valid")
  warnings string[] @description("Any warnings about the generation")
}

/// Conversation container input
class ConversationInput {
  messages MessageInput[] @description("List of messages")
  container_id string? @description("ID for the container")
  config ARIAConfig? @description("Custom configuration")
}

/// Single message input
class MessageInput {
  content string @description("Message content")
  sender string @description("Message sender (user/assistant)")
  aria_label string? @description("Custom label for screen readers")
}

/// Progress region input
class ProgressInput {
  message string @description("Progress description")
  value_now int? @description("Current progress value")
  value_min int @description("Minimum value")
  value_max int @description("Maximum value")
}

// ============================================
// Screen Reader Compatibility
// ============================================

/// Screen reader compatibility information
class ScreenReaderCompatibility {
  reader ScreenReader @description("Screen reader")
  platform string @description("Platform (Windows/macOS/iOS/Android/Linux)")
  browser string @description("Recommended browser")
  preferred_role ARIARole @description("Best role for this reader")
  preferred_politeness ARIAPoliteness @description("Best politeness level")
  notes string @description("Compatibility notes")
}

// ============================================
// AI Generation Functions
// ============================================

/// Generate ARIA live region for content
function GenerateLiveRegion(
  input: LiveRegionInput
) -> LiveRegionResult {
  client CustomSonnet4
  prompt #"
    Generate ARIA live region markup for the given content.

    Input:
    {{ input }}

    ARIA Live Region Best Practices:

    1. Role Selection:
       - role="log" for chat/conversation history
       - role="status" for non-critical status updates
       - role="alert" for important time-sensitive messages
       - role="progressbar" for progress indicators

    2. Politeness Levels:
       - polite (default): Wait for user idle, don't interrupt
       - assertive: Interrupt immediately (use sparingly)
       - off: No announcements

    3. aria-atomic:
       - false: Only announce changed content (default for chat)
       - true: Announce entire region (use for short status messages)

    4. aria-relevant:
       - "additions text" for chat messages
       - "all" for alerts
       - "text" for progress updates

    Generate valid HTML with proper ARIA attributes.
    Include screen reader hints for JAWS, NVDA, VoiceOver, and TalkBack.

    {{ ctx.output_format }}
  "#
}

/// Analyze content and recommend ARIA configuration
function RecommendARIAConfig(
  content: string,
  context: string
) -> ARIAConfig {
  client CustomSonnet4
  prompt #"
    Analyze the content and context to recommend optimal ARIA configuration.

    Content: {{ content }}
    Context: {{ context }}

    Consider:
    1. Is this an error, warning, or informational message?
    2. Does it require immediate attention (assertive) or can wait (polite)?
    3. Should the whole region be announced (atomic) or just changes?
    4. What role best describes this content?

    Screen reader considerations:
    - JAWS: Prefers aria-live="polite" for most content
    - NVDA: Works well with role="log" for conversations
    - VoiceOver: Benefits from aria-atomic="false" for messages
    - TalkBack: Test with role="status" for notifications

    {{ ctx.output_format }}
  "#
}

/// Validate ARIA live region markup
function ValidateARIAMarkup(
  html: string
) -> LiveRegionResult {
  client CustomSonnet4
  prompt #"
    Validate the ARIA live region markup for accessibility compliance.

    HTML: {{ html }}

    Validation checks:
    1. Required attributes present (role, aria-live)
    2. Valid role value
    3. Valid aria-live value (off/polite/assertive)
    4. Appropriate use of aria-atomic
    5. Valid aria-relevant value
    6. No conflicting attributes
    7. Proper HTML structure

    Common issues:
    - Using assertive when polite would suffice
    - Missing role attribute
    - Incorrect aria-relevant values
    - Overuse of aria-atomic="true"

    Return validation result with any issues found.

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test generate_polite_region {
  functions [GenerateLiveRegion]
  args {
    input {
      content "Task created successfully"
      politeness POLITE
      content_type SUCCESS
    }
  }
}

test generate_error_alert {
  functions [GenerateLiveRegion]
  args {
    input {
      content "Error: Invalid input provided"
      politeness ASSERTIVE
      role ALERT
      content_type ERROR
    }
  }
}

test generate_chat_message {
  functions [GenerateLiveRegion]
  args {
    input {
      content "Hello! How can I help you today?"
      politeness POLITE
      role LOG
      content_type CHAT
      sender "assistant"
      aria_label "Assistant message"
    }
  }
}

test recommend_config {
  functions [RecommendARIAConfig]
  args {
    content "Your session will expire in 5 minutes"
    context "User authentication warning in a web application"
  }
}
