// Intent Drift Detection Types
// Defines types for detecting and handling intent drift in conversations
//
// Issue #78 - Task 5.1: Drift Analysis Types
// Part of #28 - Phase 5: Intent Drift Detection

// ============================================
// Core Drift Types
// ============================================

/// Main drift detection result
class DriftAnalysis {
  original_intent string? @description("The original user intent if known")
  current_input string @description("The current user input being analyzed")
  drift_score float @description("0.0 = on topic, 1.0 = completely off topic")
  drift_type DriftType @description("Classification of the type of drift")
  confidence float @description("Confidence in the drift detection (0-1)")
  last_supported_intent string? @description("Last intent that was within capability")
  semantic_distance float @description("Semantic distance from supported intents")
  suggested_redirects RedirectSuggestion[] @description("Suggested alternative capabilities")
  graceful_response string @description("Suggested response handling the drift")
}

/// Types of intent drift
enum DriftType {
  NONE @description("Within capability - no drift detected")
  SCOPE_EXPANSION @description("Related but unsupported feature request")
  DOMAIN_SHIFT @description("Different domain entirely from capabilities")
  ABSTRACTION_CLIMB @description("Too abstract or philosophical for practical handling")
  PERSONALIZATION @description("Requires user-specific data not available")
  TEMPORAL_DRIFT @description("Past/future beyond knowledge cutoff")
  AMBIGUOUS @description("Multiple intents detected, needs clarification")
}

/// Alternative capability suggestion
class RedirectSuggestion {
  target_intent string @description("The suggested alternative intent")
  similarity_score float @description("How similar to original request (0-1)")
  redirect_reason string @description("Why this is suggested as alternative")
  transition_phrase string @description("Natural language to transition to this")
  confidence float @description("Confidence in this suggestion")
}

// ============================================
// Semantic Analysis Types
// ============================================

/// Semantic analysis of user input
class SemanticAnalysis {
  input_text string @description("The analyzed input text")
  embedding_vector float[]? @description("Semantic embedding if computed")
  nearest_intents NearestIntent[] @description("Closest matching supported intents")
  abstraction_level AbstractionLevel @description("How abstract the request is")
  domain_classification string[] @description("Detected domains in input")
  temporal_references TemporalReference[] @description("Time expressions found")
  entity_mentions EntityMention[] @description("Named entities detected")
}

/// A supported intent close to the user's request
class NearestIntent {
  intent_name string @description("Name of the supported intent")
  similarity float @description("Cosine similarity or other distance metric")
  capability_id string? @description("Associated capability ID")
  requires_clarification bool @description("Whether clarification is needed")
}

/// How abstract or concrete a request is
enum AbstractionLevel {
  CONCRETE @description("Specific, actionable request")
  MODERATE @description("Somewhat abstract but handleable")
  ABSTRACT @description("High-level, may need grounding")
  PHILOSOPHICAL @description("Too abstract for practical action")
}

/// Time expression analysis
class TemporalReference {
  expression string @description("The temporal expression found")
  reference_type TemporalReferenceType @description("Type of temporal reference")
  resolved_date string? @description("ISO 8601 date if resolvable")
  is_within_knowledge bool @description("Whether within knowledge cutoff")
  drift_risk float @description("Risk this causes temporal drift (0-1)")
}

/// Types of temporal references
enum TemporalReferenceType {
  PAST_ABSOLUTE @description("Specific past date")
  PAST_RELATIVE @description("Relative past reference (yesterday, last week)")
  PRESENT @description("Current time reference")
  FUTURE_RELATIVE @description("Relative future reference (tomorrow, next week)")
  FUTURE_ABSOLUTE @description("Specific future date")
  HYPOTHETICAL @description("Hypothetical time scenario")
}

/// Entity mentioned in user input
class EntityMention {
  text string @description("The entity text")
  entity_type string @description("Type of entity (person, org, location, etc.)")
  start_offset int @description("Character offset start")
  end_offset int @description("Character offset end")
  requires_personalization bool @description("Whether entity requires user data")
}

// ============================================
// Confidence Assessment Types
// ============================================

/// Multi-factor confidence assessment
class ConfidenceAssessment {
  overall_confidence float @description("Overall confidence score (0-1)")
  confidence_tier ConfidenceTier @description("Tiered confidence level")
  recommended_action RecommendedAction @description("Suggested action based on confidence")
  factor_scores ConfidenceFactorScore[] @description("Individual factor scores")
  explanation string @description("Human-readable confidence explanation")
}

/// Tiered confidence levels
enum ConfidenceTier {
  VERY_HIGH @description("95%+ confidence - proceed normally")
  HIGH @description("80-94% confidence - proceed with minor caveats")
  MEDIUM @description("60-79% confidence - may need clarification")
  LOW @description("40-59% confidence - clarification recommended")
  VERY_LOW @description("Below 40% - should not proceed without clarification")
}

/// Recommended action based on confidence
enum RecommendedAction {
  PROCEED @description("Proceed with detected intent")
  PROCEED_WITH_CAVEAT @description("Proceed but mention uncertainty")
  CLARIFY @description("Ask for clarification before proceeding")
  REDIRECT @description("Suggest alternative capabilities")
  ESCALATE @description("Escalate to human or higher authority")
  DECLINE @description("Politely decline the request")
}

/// Individual confidence factor score
class ConfidenceFactorScore {
  factor_name string @description("Name of the confidence factor")
  score float @description("Score for this factor (0-1)")
  weight float @description("Weight of this factor in overall score")
  explanation string? @description("Why this score was assigned")
}

// ============================================
// Graceful Response Types
// ============================================

/// Structure for handling drift gracefully
class GracefulResponse {
  response_type GracefulResponseType @description("Type of graceful response")
  primary_message string @description("Main response message")
  acknowledgment string? @description("Acknowledgment of user's request")
  explanation string? @description("Why we can't fully help")
  alternatives Redirect[] @description("Alternative actions offered")
  follow_up_prompt string? @description("Prompt to continue conversation")
  tone DriftResponseTone @description("Tone of the response")
}

/// Types of graceful responses
enum GracefulResponseType {
  CLARIFICATION @description("Asking for more information")
  PARTIAL_HELP @description("Can help with part of the request")
  REDIRECT @description("Suggesting alternative capabilities")
  BOUNDARY_STATEMENT @description("Explaining capability boundaries")
  ESCALATION @description("Offering to escalate")
  ACKNOWLEDGMENT @description("Acknowledging but cannot help")
}

/// Redirect to alternative capability
class Redirect {
  capability_name string @description("Name of alternative capability")
  description string @description("What this capability can do")
  relevance_score float @description("How relevant to original request")
  action_phrase string @description("Phrase to invoke this capability")
}

/// Tone for drift response delivery
enum DriftResponseTone {
  EMPATHETIC @description("Understanding and supportive")
  HELPFUL @description("Focused on finding solutions")
  PROFESSIONAL @description("Neutral and business-like")
  APOLOGETIC @description("Expressing regret for limitations")
  ENCOURAGING @description("Positive about alternatives")
}

/// Template for drift responses
class DriftResponseTemplate {
  template_id string @description("Unique template identifier")
  drift_types DriftType[] @description("Applicable drift types")
  template_text string @description("Template with {placeholders}")
  required_variables string[] @description("Variables that must be filled")
  tone DriftResponseTone @description("Intended tone")
  example_output string? @description("Example of filled template")
}

// ============================================
// Conversation Context Types
// ============================================

/// Multi-turn conversation tracking
class ConversationDriftContext {
  session_id string @description("Unique session identifier")
  turns DriftConversationTurn[] @description("Conversation turns")
  initial_intent string? @description("First detected intent in session")
  current_topic string? @description("Current conversation topic")
  drift_history DriftEvent[] @description("History of drift events")
  coherence CoherenceAnalysis @description("Overall conversation coherence")
}

/// Single conversation turn for drift tracking
class DriftConversationTurn {
  turn_id string @description("Unique turn identifier")
  turn_number int @description("Sequential turn number")
  user_input string @description("User's input text")
  detected_intent string? @description("Detected intent for this turn")
  drift_analysis DriftAnalysis? @description("Drift analysis if performed")
  response string? @description("System response")
  timestamp string @description("ISO 8601 timestamp")
}

/// A recorded drift event
class DriftEvent {
  turn_id string @description("Turn where drift occurred")
  drift_type DriftType @description("Type of drift detected")
  drift_score float @description("Severity of drift")
  recovery_attempted bool @description("Whether recovery was attempted")
  recovery_successful bool @description("Whether recovery succeeded")
  notes string? @description("Additional notes")
}

/// Conversation coherence analysis
class CoherenceAnalysis {
  coherence_score float @description("Overall coherence (0-1)")
  topic_consistency float @description("How consistent topics are")
  intent_stability float @description("How stable intents are across turns")
  turn_relevance_scores float[] @description("Relevance score for each turn")
  coherence_trend CoherenceTrend @description("Whether coherence is improving")
  warnings string[] @description("Coherence warnings if any")
}

/// Trend in conversation coherence
enum CoherenceTrend {
  IMPROVING @description("Conversation getting more focused")
  STABLE @description("Coherence relatively constant")
  DEGRADING @description("Conversation losing focus")
  VOLATILE @description("Coherence varying significantly")
}

// ============================================
// Drift Detection Configuration
// ============================================

/// Configuration for drift detection
class DriftDetectionConfig {
  drift_threshold float @description("Score above which drift is detected (default 0.5)")
  confidence_threshold float @description("Minimum confidence for detection")
  max_semantic_distance float @description("Maximum acceptable semantic distance")
  temporal_cutoff_date string? @description("Knowledge cutoff date")
  supported_domains string[] @description("Domains considered in-scope")
  abstraction_tolerance AbstractionLevel @description("Max abstraction tolerated")
  enable_personalization_detection bool @description("Detect personalization requests")
}

/// Result of applying drift detection
class DriftDetectionResult {
  input string @description("The analyzed input")
  config DriftDetectionConfig @description("Configuration used")
  analysis DriftAnalysis @description("The drift analysis result")
  confidence_assessment ConfidenceAssessment @description("Confidence details")
  semantic_analysis SemanticAnalysis @description("Semantic analysis details")
  suggested_response GracefulResponse? @description("Suggested response if drifted")
  processing_time_ms int @description("Processing time in milliseconds")
}

// ============================================
// Integration Types
// ============================================

/// Request for drift analysis
class DriftAnalysisRequest {
  input string @description("User input to analyze")
  context ConversationDriftContext? @description("Optional conversation context")
  config DriftDetectionConfig? @description("Optional custom configuration")
  include_semantic_analysis bool @description("Whether to include semantic analysis")
  include_suggestions bool @description("Whether to include redirect suggestions")
}

/// Batch drift analysis for multiple inputs
class BatchDriftAnalysis {
  requests DriftAnalysisRequest[] @description("Inputs to analyze")
  results DriftDetectionResult[] @description("Results for each input")
  aggregate_stats DriftAggregateStats @description("Aggregate statistics")
}

/// Aggregate statistics for batch analysis
class DriftAggregateStats {
  total_inputs int @description("Total inputs analyzed")
  drift_count int @description("Number with drift detected")
  drift_rate float @description("Percentage with drift")
  avg_drift_score float @description("Average drift score")
  drift_type_counts map<string, int> @description("Count by drift type")
  avg_confidence float @description("Average confidence score")
}
