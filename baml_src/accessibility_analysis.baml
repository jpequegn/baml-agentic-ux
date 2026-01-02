// Accessibility Analysis for LUI Responses
// BAML types and functions for AI-powered accessibility analysis
// Issue #69 - Task 4.3: Response Accessibility Checker
// Part of #27 - Phase 4: LUI Accessibility Standards

// Dependencies:
// - ComplianceLevel from accessibility_types.baml
// - LUIAGAccessibilityConfig from accessibility_types.baml

// ============================================
// Violation Types
// ============================================

/// Severity levels for accessibility violations
enum ViolationSeverity {
  CRITICAL @description("Blocks accessibility - weight: 0.25")
  MAJOR @description("Significant impact - weight: 0.15")
  MINOR @description("Reduces usability - weight: 0.05")
  ADVISORY @description("Suggestions for improvement - weight: 0.02")
}

/// A single accessibility violation found in a response
class AccessibilityViolation {
  criterion string @description("Criterion reference (e.g., 'A.1.1', 'AA.3.1')")
  severity ViolationSeverity @description("Severity of this violation")
  description string @description("Human-readable description of the issue")
  remediation string @description("Suggested fix for the issue")
  element string? @description("Specific text that caused the violation")
  line_number int? @description("Line or sentence number if applicable")
}

// ============================================
// Analysis Request/Response Types
// ============================================

/// Configuration for accessibility analysis
class AccessibilityAnalysisConfig {
  target_level ComplianceLevel @description("Target compliance level to check")
  check_readability bool @description("Whether to check reading level")
  check_vocabulary bool @description("Whether to check vocabulary complexity")
  check_structure bool @description("Whether to check sentence/paragraph structure")
  check_tone bool @description("Whether to check for appropriate tone")
  check_clarity bool @description("Whether to check for clarity and directness")
  custom_criteria string[]? @description("Additional custom criteria to check")
}

/// Readability metrics for the analyzed response
class ResponseReadabilityMetrics {
  word_count int @description("Total number of words")
  sentence_count int @description("Total number of sentences")
  average_sentence_length float @description("Average words per sentence")
  flesch_reading_ease float @description("Flesch Reading Ease score (0-100)")
  flesch_kincaid_grade float @description("Flesch-Kincaid grade level")
  polysyllable_percentage float @description("Percentage of words with 3+ syllables")
}

/// Complete result of accessibility analysis
class ResponseAccessibilityAnalysis {
  passes bool @description("Whether response passes target level requirements")
  target_level ComplianceLevel @description("The level that was targeted")
  achieved_level ComplianceLevel? @description("Highest level actually achieved")
  score float @description("Accessibility score from 0.0 to 1.0")
  violations AccessibilityViolation[] @description("List of violations found")
  readability ResponseReadabilityMetrics? @description("Readability metrics if analyzed")
  summary string @description("Human-readable summary of findings")
  recommendations string[] @description("Prioritized list of recommendations")
  confidence float @description("Confidence in this analysis (0.0-1.0)")
}

// ============================================
// AI Analysis Functions
// ============================================

/// Analyze a response for accessibility compliance
function AnalyzeResponseAccessibility(
  response string,
  config AccessibilityAnalysisConfig
) -> ResponseAccessibilityAnalysis {
  client CustomSonnet4
  prompt #"
    Analyze this response for LUIAG (Language User Interface Accessibility Guidelines) compliance.

    Response to analyze:
    {{ response }}

    Analysis configuration:
    {{ config }}

    Apply these thresholds based on compliance level:

    Level A (Minimum):
    - Max reading grade: 12.0
    - Max sentence length: 35 words
    - Allow some passive voice
    - Allow technical terms with explanation

    Level AA (Standard):
    - Max reading grade: 8.0
    - Max sentence length: 25 words
    - Minimize passive voice
    - Prefer common vocabulary

    Level AAA (Enhanced):
    - Max reading grade: 6.0
    - Max sentence length: 20 words
    - No passive voice
    - Simple vocabulary only
    - No unexplained technical terms

    For each violation found:
    1. Assign appropriate criterion code (e.g., A.1.1, AA.2.1, AAA.3.1)
    2. Determine severity based on impact
    3. Provide specific remediation guidance
    4. Quote the problematic element if applicable

    Calculate the overall score:
    - Start at 1.0
    - Subtract CRITICAL violations × 0.25
    - Subtract MAJOR violations × 0.15
    - Subtract MINOR violations × 0.05
    - Subtract ADVISORY notices × 0.02
    - Minimum score is 0.0

    Determine achieved level:
    - AAA if no CRITICAL/MAJOR violations at AAA level
    - AA if no CRITICAL/MAJOR violations at AA level
    - A if no CRITICAL/MAJOR violations at A level
    - null if fails all levels

    {{ ctx.output_format }}
  "#
}

/// Suggest improvements to make a response more accessible
function SuggestAccessibilityImprovements(
  response string,
  target_level ComplianceLevel
) -> AccessibilityImprovementSuggestions {
  client CustomSonnet4
  prompt #"
    Suggest specific improvements to make this response meet {{ target_level }} accessibility requirements.

    Current response:
    {{ response }}

    For each suggestion:
    1. Identify the specific issue
    2. Provide the original text
    3. Provide an improved version
    4. Explain why the improvement helps

    Focus on:
    - Simplifying vocabulary
    - Shortening sentences
    - Improving clarity
    - Removing passive voice
    - Defining technical terms

    Prioritize suggestions by impact - most important first.

    {{ ctx.output_format }}
  "#
}

/// Suggestions for improving accessibility
class AccessibilityImprovementSuggestions {
  original_score float @description("Estimated current accessibility score")
  projected_score float @description("Projected score after improvements")
  suggestions TextImprovement[] @description("Specific text improvements")
  general_advice string[] @description("General advice for this content type")
}

/// A specific text improvement suggestion
class TextImprovement {
  issue string @description("What issue this addresses")
  original_text string @description("The original problematic text")
  improved_text string @description("The suggested improved version")
  explanation string @description("Why this improvement helps")
  priority int @description("Priority 1-10 (higher = more important)")
}

/// Rewrite a response to meet accessibility requirements
function RewriteForAccessibility(
  response string,
  target_level ComplianceLevel,
  preserve_meaning bool
) -> AccessibleRewrite {
  client CustomSonnet4
  prompt #"
    Rewrite this response to meet {{ target_level }} accessibility requirements.

    Original response:
    {{ response }}

    Requirements:
    {% if target_level == "LEVEL_A" %}
    - Reading grade ≤ 12
    - Sentence length ≤ 35 words
    - Define technical terms
    {% elsif target_level == "LEVEL_AA" %}
    - Reading grade ≤ 8
    - Sentence length ≤ 25 words
    - Use common vocabulary
    - Minimize passive voice
    {% else %}
    - Reading grade ≤ 6
    - Sentence length ≤ 20 words
    - Simple vocabulary only
    - No passive voice
    - No unexplained jargon
    {% endif %}

    {% if preserve_meaning %}
    IMPORTANT: Preserve all essential meaning and information.
    {% endif %}

    Provide:
    1. The rewritten text
    2. List of changes made
    3. Estimated new accessibility score

    {{ ctx.output_format }}
  "#
}

/// Result of rewriting for accessibility
class AccessibleRewrite {
  original_text string @description("The original text")
  rewritten_text string @description("The accessibility-improved text")
  changes_made string[] @description("List of changes applied")
  estimated_score float @description("Estimated accessibility score of rewrite")
  target_level_met bool @description("Whether the rewrite meets target level")
  word_count_change int @description("Change in word count (positive = longer)")
}

// ============================================
// Schema-Level Accessibility Evaluation
// Issue #70 - Task 4.4: Schema Accessibility Evaluator
// ============================================

/// A schema violation with location information
class SchemaAccessibilityViolation {
  criterion string @description("Criterion reference (e.g., 'A.1.1', 'AA.3.1')")
  severity ViolationSeverity @description("Severity of this violation")
  description string @description("Human-readable description of the issue")
  remediation string @description("Suggested fix for the issue")
  location string @description("Path to the violation (e.g., 'components[0].feedback.success_template')")
  element string? @description("Specific text or value that caused the violation")
}

/// Accessibility evaluation for a single component
class ComponentAccessibilityEval {
  component_id string @description("Unique component identifier")
  component_type string @description("Type of component (ACTION, QUERY, etc.)")
  score float @description("Component accessibility score 0.0-1.0")
  passes bool @description("Whether component passes target level")
  achieved_level ComplianceLevel? @description("Highest level achieved by component")
  violations SchemaAccessibilityViolation[] @description("Violations for this component")
}

/// Summary of accessibility findings
class AccessibilitySummary {
  total_violations int @description("Total number of violations")
  critical_count int @description("Number of critical violations")
  major_count int @description("Number of major violations")
  minor_count int @description("Number of minor violations")
  advisory_count int @description("Number of advisory notices")
  passing_components int @description("Number of components that pass")
  total_components int @description("Total number of components")
  key_issues string[] @description("Top issues to address")
}

/// Complete schema accessibility evaluation result
class LUIAccessibilityEvaluation {
  schema_name string @description("Name of the schema evaluated")
  target_level ComplianceLevel @description("Target compliance level")
  achieved_level ComplianceLevel? @description("Highest level achieved")
  overall_score float @description("Overall accessibility score 0.0-1.0")
  passes bool @description("Whether schema passes target level")
  component_evaluations ComponentAccessibilityEval[] @description("Per-component evaluations")
  schema_violations SchemaAccessibilityViolation[] @description("Schema-level violations")
  summary AccessibilitySummary @description("Summary of findings")
  recommendations string[] @description("Prioritized recommendations")
  confidence float @description("Confidence in this evaluation (0.0-1.0)")
}

/// Evaluate a complete LUI schema for accessibility compliance
function EvaluateLUIAccessibility(
  schema InterfaceSchema,
  target_level ComplianceLevel
) -> LUIAccessibilityEvaluation {
  client CustomSonnet4
  prompt #"
    Evaluate this LUI (Language User Interface) schema for LUIAG accessibility compliance.

    Schema to evaluate:
    {{ schema }}

    Target compliance level: {{ target_level }}

    Perform these checks:

    1. SCHEMA-LEVEL CHECKS:
       - Verify accessibility configuration is present (schema.accessibility)
       - Check for default_config in accessibility settings
       - Verify supported_compliance_levels includes target level
       - Check timing configurations meet level requirements

    2. COMPONENT CHECKS (for each component):
       - Verify AccessibilityConfig is present
       - Check for screen_reader_label
       - At AA/AAA: Check for voice_hints
       - Evaluate feedback templates for readability

    3. FEEDBACK TEMPLATE ANALYSIS:
       - Check success_template, error_template, progress_template
       - Apply reading level thresholds:
         * Level A: max grade 12, max 35 words/sentence
         * Level AA: max grade 8, max 25 words/sentence
         * Level AAA: max grade 6, max 20 words/sentence

    4. TIMING REQUIREMENTS:
       - Level A: min timeout 20 seconds
       - Level AA: min timeout 30 seconds, timeout extension required
       - Level AAA: min timeout 60 seconds, full extension support

    For each violation:
    - Assign criterion code (A.x.x, AA.x.x, AAA.x.x)
    - Set severity (CRITICAL, MAJOR, MINOR, ADVISORY)
    - Provide location path (e.g., "components[0].feedback.success_template")
    - Include specific remediation

    Calculate scores:
    - Component scores: 1.0 minus weighted violations
    - Overall: 40% schema-level + 60% average component score

    Determine achieved level:
    - AAA: No CRITICAL/MAJOR violations at any level
    - AA: No CRITICAL/MAJOR at A or AA level
    - A: No CRITICAL/MAJOR at A level
    - null: Has A-level CRITICAL/MAJOR violations

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test analyze_simple_response {
  functions [AnalyzeResponseAccessibility]
  args {
    response "The cat sat on the mat."
    config {
      target_level LEVEL_AA
      check_readability true
      check_vocabulary true
      check_structure true
      check_tone false
      check_clarity true
    }
  }
}

test analyze_complex_response {
  functions [AnalyzeResponseAccessibility]
  args {
    response "The authentication protocol necessitates verification of credentials prior to authorization."
    config {
      target_level LEVEL_AA
      check_readability true
      check_vocabulary true
      check_structure true
      check_tone false
      check_clarity true
    }
  }
}

test suggest_improvements {
  functions [SuggestAccessibilityImprovements]
  args {
    response "The authentication protocol necessitates verification of credentials prior to authorization."
    target_level LEVEL_AA
  }
}
