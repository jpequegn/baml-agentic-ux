// Context Primitives for Session State Management
// Phase 7: BAML Context Primitives Implementation
//
// Issue #baml-agentic-ux-bdi - Task 7.1: Context Type Definitions
// Part of Phase 7: Context Primitives for Session State
//
// These types enable session state management in Language User Interfaces,
// supporting conversation history tracking, context variables, and multi-turn
// interactions with configurable storage backends.

// ============================================
// Session Context Types
// ============================================

/// Session-level context information for tracking conversation state
class SessionContext {
  session_id string @description("Unique session identifier (UUID recommended)")
  user_id string? @description("Optional user identifier for personalization")
  created_at string @description("ISO 8601 timestamp of session creation")
  last_activity string @description("ISO 8601 timestamp of last interaction")
  metadata map<string, string>? @description("Custom session metadata (e.g., client, channel)")
  ttl_seconds int? @description("Session time-to-live in seconds")
  is_active bool @description("Whether session is currently active")
}

// ============================================
// Conversation History Types
// ============================================

/// Single conversation turn for detailed history tracking
class ContextConversationTurn {
  turn_id int @description("Sequential turn number (1-indexed)")
  timestamp string @description("ISO 8601 timestamp of this turn")
  user_input string @description("User's message or input")
  detected_intent string? @description("Extracted intent from user input")
  extracted_entities map<string, string>? @description("Extracted entities from input")
  assistant_response string @description("System/assistant response")
  confidence float? @description("Intent detection confidence score (0-1)")
  component_id string? @description("LUI component that handled this turn")
  duration_ms int? @description("Processing time in milliseconds")
}

/// Conversation history with sliding window and summarization support
class ContextConversationHistory {
  session_id string @description("Associated session identifier")
  turns ContextConversationTurn[] @description("Recent conversation turns (windowed)")
  max_turns int @description("Maximum turns to retain in window (default: 20)")
  total_turns int @description("Total turns including summarized ones")
  summary string? @description("LLM-generated summary of older turns")
  summary_updated_at string? @description("When summary was last updated")
  token_count int? @description("Estimated token count for context window")
}

// ============================================
// Context Variables Types
// ============================================

/// Type discriminator for context variable values
enum ContextValueType {
  STRING @description("Plain string value")
  NUMBER @description("Numeric value (integer or float)")
  BOOLEAN @description("Boolean true/false value")
  LIST @description("Array of string values")
  OBJECT @description("Nested key-value object")
  NULL @description("Explicit null/empty value")
}

/// Flexible context variable value with type tracking
class ContextValue {
  value_type ContextValueType @description("Type of the stored value")
  string_value string? @description("String value if type is STRING")
  number_value float? @description("Numeric value if type is NUMBER")
  boolean_value bool? @description("Boolean value if type is BOOLEAN")
  list_value string[]? @description("List value if type is LIST")
  object_value map<string, string>? @description("Object value if type is OBJECT")
}

/// Context variables that persist across conversation turns
class ContextVariables {
  session_id string @description("Associated session identifier")
  variables map<string, ContextValue> @description("Named variable storage")
  updated_at string @description("ISO 8601 timestamp of last update")
}

// ============================================
// Execution Context Types
// ============================================

/// Full execution context combining all components for BAML function injection
class FullExecutionContext {
  session SessionContext @description("Session-level context")
  history ContextConversationHistory @description("Conversation history with windowing")
  variables ContextVariables @description("Persistent context variables")
  current_intent string? @description("Currently detected intent")
  current_entities map<string, string>? @description("Currently extracted entities")
}

/// Lightweight conversation context for injection into BAML functions
/// Note: Named SessionConversationContext to avoid conflict with ConversationContext in intent_extraction.baml
class SessionConversationContext {
  session_id string @description("Session identifier")
  user_id string? @description("User identifier if known")
  recent_turns RecentTurn[] @description("Recent conversation turns (typically last 10)")
  variables map<string, string>? @description("Flattened context variables as strings")
  history_summary string? @description("Summary of older conversation history")
  turn_count int @description("Total number of turns in conversation")
}

/// Simplified turn representation for context injection
class RecentTurn {
  user_input string @description("What the user said")
  assistant_response string @description("What the assistant responded")
  detected_intent string? @description("Detected intent for this turn")
  extracted_entities map<string, string>? @description("Entities extracted")
}

// ============================================
// Context Configuration Types
// ============================================

/// Storage backend options for context persistence
enum ContextBackend {
  IN_MEMORY @description("In-memory storage (development/testing only)")
  REDIS @description("Redis for hot session storage with TTL")
  POSTGRESQL @description("PostgreSQL for persistent history storage")
  DYNAMODB @description("DynamoDB for serverless deployments")
  HYBRID @description("Redis (hot) + PostgreSQL (persistence) combination")
}

/// Configuration for context management system
class ContextConfig {
  max_history_turns int @description("Maximum turns to keep in window (default: 20)")
  summarize_after int @description("Summarize after N turns (default: 10)")
  token_limit int @description("Maximum tokens for history context (default: 4000)")
  persistence_backend ContextBackend @description("Storage backend type")
  ttl_seconds int? @description("Default session TTL in seconds (default: 3600)")
  enable_summarization bool @description("Whether to auto-summarize old turns")
  summarization_model string? @description("Model to use for summarization")
}

// ============================================
// Context Update Types
// ============================================

/// Types of context updates that can be triggered
enum ContextUpdateType {
  SET_VARIABLE @description("Set or update a context variable")
  DELETE_VARIABLE @description("Remove a context variable")
  UPDATE_ENTITY @description("Update an entity value")
  ADD_TURN @description("Add a conversation turn")
  UPDATE_SUMMARY @description("Update conversation summary")
  CLEAR_CONTEXT @description("Clear all context for session")
  EXTEND_TTL @description("Extend session time-to-live")
}

/// Individual context update operation
class ContextUpdate {
  update_type ContextUpdateType @description("Type of update operation")
  key string @description("Variable key or identifier")
  value ContextValue? @description("New value (for SET operations)")
  reason string? @description("Why this update is being made")
  timestamp string @description("ISO 8601 timestamp of update")
}

/// Result from a context-aware BAML function
class ContextualResult {
  result string @description("The actual function result (serialized)")
  context_updates ContextUpdate[] @description("Triggered context updates")
  new_variables map<string, ContextValue>? @description("Newly set variables")
  should_persist bool @description("Whether updates should be persisted")
}

// ============================================
// History Management Types
// ============================================

/// Strategy for truncating conversation history
/// Note: Named HistoryTruncationStrategy to avoid conflict with TruncationStrategy class in multimodal_types.baml
enum HistoryTruncationStrategy {
  SLIDING_WINDOW @description("Keep last N turns, discard older")
  TOKEN_BASED @description("Keep turns until token limit reached")
  IMPORTANCE_BASED @description("Score turns and keep most important")
  SUMMARIZE @description("Summarize old turns before discarding")
  HYBRID @description("Combine summarization with windowing")
}

/// Configuration for history truncation
class TruncationConfig {
  strategy HistoryTruncationStrategy @description("Truncation strategy to use")
  max_turns int @description("Maximum turns for SLIDING_WINDOW")
  max_tokens int @description("Maximum tokens for TOKEN_BASED")
  importance_threshold float @description("Threshold for IMPORTANCE_BASED (0-1)")
  summarization_prompt string? @description("Custom prompt for summarization")
}

/// Turn importance assessment for importance-based truncation
class TurnImportance {
  turn_id int @description("Which turn this assessment is for")
  recency_score float @description("Score based on how recent (0-1)")
  relevance_score float @description("Score based on relevance to current (0-1)")
  entity_score float @description("Score based on entity presence (0-1)")
  overall_score float @description("Weighted combination of scores (0-1)")
  should_retain bool @description("Whether this turn should be kept")
}

// ============================================
// Summarization Types
// ============================================

/// Request for conversation summarization
class SummarizationRequest {
  turns ContextConversationTurn[] @description("Turns to summarize")
  existing_summary string? @description("Previous summary to update")
  max_length int? @description("Maximum summary length in characters")
  focus_topics string[]? @description("Topics to emphasize in summary")
}

/// Result of conversation summarization
class ConversationSummary {
  summary string @description("Concise summary of the conversation")
  key_entities string[]? @description("Important entities mentioned")
  key_intents string[]? @description("Main intents from summarized turns")
  current_state string? @description("Current conversation state/topic")
  turn_range TurnRange @description("Range of turns covered by summary")
  token_count int @description("Token count of the summary")
}

/// Range of turns covered by a summary
class TurnRange {
  start_turn int @description("First turn number in range")
  end_turn int @description("Last turn number in range")
  turn_count int @description("Total turns summarized")
}

// ============================================
// Serialization Types
// ============================================

/// Serialization format for context storage
enum SerializationFormat {
  JSON @description("Standard JSON (human-readable)")
  MSGPACK @description("MessagePack binary (faster, smaller)")
  COMPRESSED @description("Gzip-compressed JSON")
  MSGPACK_COMPRESSED @description("Compressed MessagePack (smallest)")
}

/// Serialization metadata for stored context
class SerializationMetadata {
  format SerializationFormat @description("Format used for serialization")
  version string @description("Schema version for compatibility")
  compressed bool @description("Whether compression was applied")
  original_size int @description("Size before compression in bytes")
  compressed_size int? @description("Size after compression if applied")
  checksum string? @description("Integrity checksum")
}

// ============================================
// BAML Function Integration Types
// ============================================

/// Wrapper for BAML function execution with context
class ContextAwareFunctionCall {
  function_name string @description("Name of the BAML function")
  session_id string @description("Session to use for context")
  inject_history bool @description("Whether to inject conversation history")
  inject_variables bool @description("Whether to inject context variables")
  record_interaction bool @description("Whether to record this as a turn")
  inputs map<string, string> @description("Function inputs")
}

/// Result of context-aware function execution
class ContextAwareFunctionResult {
  function_name string @description("Executed function name")
  session_id string @description("Session used")
  result string @description("Function result (serialized)")
  context_before ConversationContext @description("Context before execution")
  context_after ConversationContext @description("Context after execution")
  updates_applied ContextUpdate[] @description("Context updates that were applied")
  execution_time_ms int @description("Execution time in milliseconds")
}

// ============================================
// Provider Interface Types
// ============================================

/// Status of a context provider
class ProviderStatus {
  backend ContextBackend @description("Which backend this provider uses")
  connected bool @description("Whether connection is established")
  healthy bool @description("Whether provider is healthy")
  last_health_check string @description("ISO 8601 timestamp of last check")
  error_message string? @description("Error message if unhealthy")
  sessions_active int @description("Number of active sessions")
  storage_used_bytes int? @description("Storage used if available")
}

/// Result of cleanup operation
class CleanupResult {
  sessions_deleted int @description("Number of expired sessions deleted")
  turns_archived int @description("Number of turns archived")
  bytes_freed int? @description("Storage bytes freed if available")
  duration_ms int @description("Time taken for cleanup")
  errors string[]? @description("Any errors encountered")
}

// ============================================
// Summarization Functions
// ============================================

/// Summarize conversation turns into a concise context summary
/// Used by HistoryManager for context window management
function SummarizeConversation(
  turns: ContextConversationTurn[],
  existing_summary: string?,
  max_length: int?
) -> ConversationSummary {
  client CustomSonnet4
  prompt #"
    You are a conversation summarization expert. Your task is to create a concise,
    informative summary that preserves the essential context for future conversation turns.

    {{ ctx.output_format }}

    {% if existing_summary %}
    PREVIOUS SUMMARY:
    {{ existing_summary }}

    The following turns occurred after the previous summary. Create an UPDATED summary
    that incorporates both the previous context and the new information.
    {% endif %}

    CONVERSATION TURNS TO SUMMARIZE:
    {% for turn in turns %}
    ---
    Turn {{ turn.turn_id }} ({{ turn.timestamp }}):
    User: {{ turn.user_input }}
    {% if turn.detected_intent %}Intent: {{ turn.detected_intent }}{% endif %}
    {% if turn.extracted_entities %}Entities: {{ turn.extracted_entities }}{% endif %}
    Assistant: {{ turn.assistant_response }}
    ---
    {% endfor %}

    {% if max_length %}
    CONSTRAINT: Keep the summary under {{ max_length }} characters.
    {% endif %}

    INSTRUCTIONS:
    1. Create a concise summary capturing the key information and context
    2. Identify the main topics/intents discussed
    3. Extract important entities mentioned (names, dates, IDs, etc.)
    4. Note the current conversation state/topic
    5. Preserve information needed for continuity

    Focus on WHAT was discussed and WHAT was decided/accomplished, not the mechanics
    of the conversation. The summary should enable an AI to continue the conversation
    naturally without access to the full history.
  "#
}

/// Score conversation turns by importance for context retention
/// Used by HistoryManager for importance-based truncation
function ScoreTurnImportance(
  turns: ContextConversationTurn[],
  current_context: string?,
  important_entities: string[]?
) -> TurnImportance[] {
  client CustomSonnet4
  prompt #"
    You are evaluating conversation turns for importance to determine which should
    be retained in a limited context window.

    {{ ctx.output_format }}

    {% if current_context %}
    CURRENT CONVERSATION CONTEXT:
    {{ current_context }}
    {% endif %}

    {% if important_entities %}
    IMPORTANT ENTITIES TO TRACK:
    {{ important_entities }}
    {% endif %}

    TURNS TO EVALUATE:
    {% for turn in turns %}
    ---
    Turn {{ turn.turn_id }}:
    User: {{ turn.user_input }}
    {% if turn.detected_intent %}Intent: {{ turn.detected_intent }} (confidence: {{ turn.confidence }}){% endif %}
    {% if turn.extracted_entities %}Entities: {{ turn.extracted_entities }}{% endif %}
    Assistant: {{ turn.assistant_response }}
    ---
    {% endfor %}

    SCORING CRITERIA:
    1. Recency: How recently did this turn occur? (0-1, higher = more recent)
    2. Relevance: How relevant is this turn to the current context? (0-1)
    3. Entity Score: Does this turn contain important entities? (0-1)
    4. Overall Score: Weighted combination (recency 30%, relevance 40%, entities 30%)

    For each turn, determine:
    - Individual factor scores
    - Overall importance score (0-1)
    - Whether to retain (true if overall >= 0.3)

    Prioritize turns that:
    - Establish key context or decisions
    - Contain important entity references
    - Are directly relevant to current topic
    - Would be needed to understand later turns
  "#
}
