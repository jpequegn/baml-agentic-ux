// Conversational Testing Framework Types
// Defines comprehensive types for conversation test definitions
//
// Issue #89 - Task 6.1: Test Definition Types
// Part of #29 - Phase 6: Conversational Testing Framework

// ============================================
// Core Test Types
// ============================================

/// Main conversation test definition
class ConversationTest {
  test_id string @description("Unique test identifier")
  name string @description("Human-readable test name")
  description string? @description("Test description and purpose")
  category TestCategory @description("Category of test")
  priority TestPriority @description("Test priority level")
  tags string[] @description("Tags for filtering and organization")
  setup TestSetup? @description("Pre-test configuration")
  turns TestTurn[] @description("Sequence of conversation turns")
  expected_outcome ExpectedOutcome @description("Success criteria for the test")
  quality_thresholds QualityThresholds? @description("Optional quality threshold overrides")
  timeout_seconds int? @description("Maximum test execution time")
  metadata map<string, string>? @description("Additional test metadata")
}

/// Category of conversation test
enum TestCategory {
  INTENT_RECOGNITION @description("Tests for intent detection accuracy")
  ENTITY_EXTRACTION @description("Tests for entity extraction")
  DIALOGUE_FLOW @description("Tests for conversation flow handling")
  ERROR_HANDLING @description("Tests for error and edge case handling")
  CONTEXT_RETENTION @description("Tests for context memory across turns")
  DRIFT_DETECTION @description("Tests for intent drift detection")
  QUALITY_ASSURANCE @description("General quality and coherence tests")
  REGRESSION @description("Regression tests for known issues")
  PERFORMANCE @description("Performance and latency tests")
}

/// Test priority level
enum TestPriority {
  CRITICAL @description("Must pass - blocks release")
  HIGH @description("Important - should be fixed soon")
  MEDIUM @description("Moderate importance")
  LOW @description("Nice to have")
  EXPLORATORY @description("Experimental or research tests")
}

// ============================================
// Test Turn Types
// ============================================

/// Individual conversation turn in a test
class TestTurn {
  turn_number int @description("Sequential turn number (1-indexed)")
  role TurnRole @description("Who is speaking")
  input string @description("The turn input text")
  expected_intent string? @description("Expected detected intent")
  expected_entities ExpectedEntity[] @description("Expected entity extractions")
  assertions ConversationAssertion[] @description("Assertions for this turn")
  context_requirements TestContextRequirement[] @description("Context that should be available")
  delay_ms int? @description("Optional delay before this turn")
  metadata map<string, string>? @description("Additional turn metadata")
}

/// Role in the conversation
enum TurnRole {
  USER @description("User input turn")
  ASSISTANT @description("Assistant/system response turn")
  SYSTEM @description("System message or context injection")
}

/// Expected entity to be extracted
class ExpectedEntity {
  entity_type string @description("Type of entity expected")
  value string? @description("Exact value expected (optional)")
  value_pattern string? @description("Regex pattern for value (optional)")
  required bool @description("Whether this entity must be extracted")
  slot_name string? @description("Slot name if filling a slot")
}

/// Context requirement for a turn
class TestContextRequirement {
  key string @description("Context key that should exist")
  value_match string? @description("Expected value or pattern")
  match_type MatchType @description("Type of value matching")
}

/// How to match values
enum MatchType {
  EXACT @description("Exact string match")
  CONTAINS @description("Value contains substring")
  REGEX @description("Regular expression match")
  SEMANTIC @description("Semantic similarity match")
  EXISTS @description("Just check if key exists")
  TYPE_CHECK @description("Check value type")
}

// ============================================
// Assertion Types
// ============================================

/// Flexible assertion for conversation testing
class ConversationAssertion {
  assertion_id string @description("Unique assertion identifier")
  assertion_type AssertionType @description("Type of assertion")
  target AssertionTarget @description("What the assertion checks")
  operator AssertionOperator @description("Comparison operator")
  expected_value string? @description("Expected value for comparison")
  threshold float? @description("Threshold for numeric comparisons")
  tolerance float? @description("Tolerance for approximate matches")
  message string? @description("Custom failure message")
  severity AssertionSeverity @description("How critical this assertion is")
}

/// Type of assertion
enum AssertionType {
  INTENT_MATCH @description("Assert detected intent matches expected")
  ENTITY_PRESENT @description("Assert entity was extracted")
  ENTITY_VALUE @description("Assert entity has specific value")
  RESPONSE_CONTAINS @description("Assert response contains text")
  RESPONSE_NOT_CONTAINS @description("Assert response doesn't contain text")
  RESPONSE_PATTERN @description("Assert response matches pattern")
  QUALITY_SCORE @description("Assert quality score above threshold")
  CONFIDENCE_SCORE @description("Assert confidence above threshold")
  CONTEXT_VALUE @description("Assert context has expected value")
  LATENCY @description("Assert response time within limit")
  TOKEN_COUNT @description("Assert token count within limit")
  CUSTOM @description("Custom assertion with expression")
}

/// What the assertion targets
enum AssertionTarget {
  INTENT @description("The detected intent")
  ENTITIES @description("Extracted entities")
  RESPONSE @description("The response text")
  CONTEXT @description("Conversation context")
  CONFIDENCE @description("Confidence scores")
  COHERENCE @description("Coherence metrics")
  NATURALNESS @description("Naturalness metrics")
  ACCURACY @description("Accuracy metrics")
  LATENCY @description("Response latency")
  TOKENS @description("Token counts")
  METADATA @description("Metadata fields")
}

/// Comparison operator for assertions
enum AssertionOperator {
  EQUALS @description("Exact equality")
  NOT_EQUALS @description("Not equal")
  GREATER_THAN @description("Greater than threshold")
  GREATER_OR_EQUAL @description("Greater than or equal")
  LESS_THAN @description("Less than threshold")
  LESS_OR_EQUAL @description("Less than or equal")
  CONTAINS @description("Contains substring")
  NOT_CONTAINS @description("Does not contain")
  MATCHES @description("Matches regex pattern")
  NOT_MATCHES @description("Does not match pattern")
  SEMANTIC_SIMILAR @description("Semantically similar")
  IN_SET @description("Value is in set")
  NOT_IN_SET @description("Value not in set")
}

/// How critical an assertion failure is
enum AssertionSeverity {
  CRITICAL @description("Test fails immediately on assertion failure")
  ERROR @description("Counts as test failure but continues")
  WARNING @description("Logged but doesn't fail test")
  INFO @description("Informational only")
}

// ============================================
// Expected Outcome Types
// ============================================

/// Success criteria for a test
class ExpectedOutcome {
  success_condition SuccessCondition @description("How success is determined")
  min_assertions_passed int? @description("Minimum passing assertions")
  required_assertions string[] @description("Assertion IDs that must pass")
  max_warnings int? @description("Maximum allowed warnings")
  final_intent string? @description("Expected final intent")
  final_context_state map<string, string>? @description("Expected final context")
  quality_requirements QualityRequirements? @description("Quality score requirements")
}

/// How test success is determined
enum SuccessCondition {
  ALL_PASS @description("All assertions must pass")
  THRESHOLD @description("Percentage of assertions must pass")
  REQUIRED_ONLY @description("Only required assertions must pass")
  CUSTOM @description("Custom success logic")
}

/// Quality score requirements for test success
class QualityRequirements {
  min_coherence float? @description("Minimum coherence score (0-1)")
  min_naturalness float? @description("Minimum naturalness score (0-1)")
  min_accuracy float? @description("Minimum accuracy score (0-1)")
  min_relevance float? @description("Minimum relevance score (0-1)")
  max_drift_score float? @description("Maximum allowed drift score")
  min_confidence float? @description("Minimum confidence score")
}

// ============================================
// Test Setup Types
// ============================================

/// Pre-test configuration
class TestSetup {
  initial_context map<string, string>? @description("Initial context to inject")
  initial_entities InitialEntity[] @description("Pre-populated entities")
  user_profile TestUserProfile? @description("Simulated user profile")
  system_state SystemState? @description("Initial system state")
  mock_responses MockResponse[] @description("Mocked external responses")
  environment_variables map<string, string>? @description("Environment overrides")
}

/// Pre-populated entity for test
class InitialEntity {
  entity_type string @description("Entity type")
  value string @description("Entity value")
  slot_name string? @description("Slot to fill")
  confidence float? @description("Confidence score to assign")
}

/// Simulated user profile for testing
class TestUserProfile {
  user_id string @description("Test user identifier")
  expertise_level TestExpertiseLevel @description("User's expertise level")
  preferences map<string, string>? @description("User preferences")
  history_summary string? @description("Summary of user history")
  accessibility_needs string[] @description("Accessibility requirements")
}

/// User expertise level
enum TestExpertiseLevel {
  NOVICE @description("New user, needs guidance")
  INTERMEDIATE @description("Familiar with basics")
  ADVANCED @description("Experienced user")
  EXPERT @description("Domain expert")
}

/// Initial system state for testing
class SystemState {
  active_capabilities string[] @description("Enabled capabilities")
  disabled_capabilities string[] @description("Disabled capabilities")
  rate_limits map<string, int>? @description("Rate limit overrides")
  feature_flags map<string, bool>? @description("Feature flag states")
}

/// Mocked external response
class MockResponse {
  trigger_pattern string @description("Pattern that triggers this mock")
  response_type MockResponseType @description("Type of mocked response")
  response_data string @description("The mocked response data")
  delay_ms int? @description("Optional response delay")
  fail_after int? @description("Fail after N uses (for testing)")
}

/// Type of mocked response
enum MockResponseType {
  API_RESPONSE @description("Mocked API response")
  DATABASE_RESULT @description("Mocked database query result")
  EXTERNAL_SERVICE @description("Mocked external service")
  ERROR @description("Mocked error condition")
}

// ============================================
// Quality Threshold Types
// ============================================

/// Configurable quality thresholds
class QualityThresholds {
  coherence_threshold float @description("Minimum coherence score (default 0.85)")
  naturalness_threshold float @description("Minimum naturalness score (default 0.80)")
  accuracy_threshold float @description("Minimum accuracy score (default 0.90)")
  relevance_threshold float @description("Minimum relevance score (default 0.75)")
  confidence_threshold float @description("Minimum confidence score (default 0.70)")
  max_drift_threshold float @description("Maximum drift score (default 0.50)")
  latency_threshold_ms int @description("Maximum latency in milliseconds")
  strict_mode bool @description("Whether to enforce all thresholds strictly")
}

// ============================================
// Test Execution Result Types
// ============================================

/// Result of executing a conversation test
class TestExecutionResult {
  test_id string @description("ID of the executed test")
  test_name string @description("Name of the test")
  status TestStatus @description("Overall test status")
  started_at string @description("ISO 8601 start timestamp")
  completed_at string @description("ISO 8601 completion timestamp")
  duration_ms int @description("Total execution time")
  turn_results TurnResult[] @description("Results for each turn")
  assertion_results AssertionResult[] @description("Results of all assertions")
  quality_scores QualityScores @description("Measured quality scores")
  failure_summary FailureSummary? @description("Summary if test failed")
  logs string[] @description("Execution logs")
}

/// Overall test status
enum TestStatus {
  PASSED @description("All criteria met")
  FAILED @description("One or more critical assertions failed")
  ERROR @description("Test encountered an error")
  SKIPPED @description("Test was skipped")
  TIMEOUT @description("Test exceeded timeout")
  PARTIAL @description("Some assertions passed, some failed")
}

/// Result of a single turn
class TurnResult {
  turn_number int @description("Turn number")
  input string @description("The input text")
  actual_response string? @description("The actual response")
  detected_intent string? @description("The detected intent")
  extracted_entities TestExtractedEntity[] @description("Entities that were extracted")
  latency_ms int @description("Turn latency")
  passed bool @description("Whether turn assertions passed")
}

/// Entity that was extracted during test
class TestExtractedEntity {
  entity_type string @description("Entity type")
  value string @description("Extracted value")
  confidence float @description("Extraction confidence")
  start_offset int? @description("Character offset start")
  end_offset int? @description("Character offset end")
}

/// Result of a single assertion
class AssertionResult {
  assertion_id string @description("Assertion identifier")
  turn_number int @description("Turn the assertion applies to")
  assertion_type AssertionType @description("Type of assertion")
  passed bool @description("Whether assertion passed")
  expected_value string? @description("What was expected")
  actual_value string? @description("What was found")
  message string? @description("Result message")
  severity AssertionSeverity @description("Assertion severity")
}

/// Measured quality scores from test
class QualityScores {
  coherence float @description("Measured coherence score")
  naturalness float @description("Measured naturalness score")
  accuracy float @description("Measured accuracy score")
  relevance float @description("Measured relevance score")
  avg_confidence float @description("Average confidence score")
  max_drift_score float @description("Maximum drift score observed")
  avg_latency_ms float @description("Average latency")
}

/// Summary of test failures
class FailureSummary {
  total_assertions int @description("Total assertions")
  passed_count int @description("Assertions that passed")
  failed_count int @description("Assertions that failed")
  critical_failures string[] @description("Critical assertion failure messages")
  first_failure_turn int @description("Turn where first failure occurred")
  failure_categories map<string, int> @description("Count of failures by category")
}

// ============================================
// Test Suite Types
// ============================================

/// Collection of related tests
class TestSuite {
  suite_id string @description("Unique suite identifier")
  name string @description("Suite name")
  description string? @description("Suite description")
  tests ConversationTest[] @description("Tests in this suite")
  default_setup TestSetup? @description("Default setup for all tests")
  default_thresholds QualityThresholds? @description("Default thresholds")
  execution_order TestExecutionOrder @description("How to order test execution")
  stop_on_failure bool @description("Whether to stop on first failure")
  parallel_execution bool @description("Whether tests can run in parallel")
  tags string[] @description("Suite tags")
}

/// Test execution order
enum TestExecutionOrder {
  SEQUENTIAL @description("Run in definition order")
  PRIORITY @description("Run by priority (critical first)")
  RANDOM @description("Random order for independence testing")
  DEPENDENCY @description("Respect test dependencies")
}

/// Result of executing a test suite
class TestSuiteResult {
  suite_id string @description("Suite identifier")
  suite_name string @description("Suite name")
  status TestStatus @description("Overall suite status")
  started_at string @description("ISO 8601 start timestamp")
  completed_at string @description("ISO 8601 completion timestamp")
  duration_ms int @description("Total execution time")
  test_results TestExecutionResult[] @description("Individual test results")
  summary SuiteSummary @description("Summary statistics")
}

/// Summary statistics for suite execution
class SuiteSummary {
  total_tests int @description("Total tests in suite")
  passed int @description("Tests that passed")
  failed int @description("Tests that failed")
  errors int @description("Tests with errors")
  skipped int @description("Tests skipped")
  pass_rate float @description("Percentage passed")
  avg_duration_ms float @description("Average test duration")
  coverage_estimate float? @description("Estimated coverage if available")
}
