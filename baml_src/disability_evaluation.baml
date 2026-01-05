// Disability-Specific Accessibility Evaluation
// BAML types and functions for disability-focused accessibility analysis
// Issue #72 - Task 4.6: Disability-Specific Evaluators
// Part of #27 - Phase 4: LUI Accessibility Standards

// Dependencies:
// - InterfaceSchema from schema_types.baml
// - ComplianceLevel from accessibility_types.baml

// ============================================
// Disability Types
// ============================================

/// Types of disabilities for targeted evaluation
enum DisabilityType {
  VISUAL @description("Visual impairments including blindness and low vision")
  HEARING @description("Hearing impairments including deafness and hard of hearing")
  MOTOR @description("Motor impairments affecting physical interaction")
  SPEECH @description("Speech impairments affecting voice-based interaction")
  COGNITIVE @description("Cognitive impairments affecting comprehension and memory")
  NEUROLOGICAL @description("Neurological conditions including epilepsy and vestibular disorders")
}

/// Categories of accessibility barriers
enum BarrierCategory {
  PERCEPTION @description("Barriers affecting ability to perceive content")
  OPERATION @description("Barriers affecting ability to operate the interface")
  UNDERSTANDING @description("Barriers affecting ability to understand content")
  ROBUSTNESS @description("Barriers affecting compatibility with assistive technology")
}

// ============================================
// Barrier Analysis Types
// ============================================

/// Severity levels for barriers (aligned with ViolationSeverity)
enum BarrierSeverity {
  CRITICAL @description("Complete barrier preventing access")
  MAJOR @description("Significant barrier reducing usability")
  MINOR @description("Partial barrier with workarounds available")
  ADVISORY @description("Potential barrier or improvement suggestion")
}

/// A specific accessibility barrier
class Barrier {
  category BarrierCategory @description("Type of barrier")
  severity BarrierSeverity @description("Severity of the barrier")
  description string @description("What the barrier is")
  location string @description("Where in the schema this barrier exists")
  impact string @description("How this affects users")
  remediation string @description("Suggested fix")
}

/// Analysis of barriers in a specific area
class BarrierAnalysis {
  area string @description("Component or area being analyzed")
  barriers Barrier[] @description("List of barriers found")
  barrier_count int @description("Total number of barriers")
  critical_count int @description("Number of critical barriers")
}

// ============================================
// Evaluation Result Types
// ============================================

/// Complete evaluation result for a disability type
class DisabilityEvaluation {
  disability_type DisabilityType @description("The disability being evaluated for")
  accommodation_score float @description("Accommodation score from 0.0 to 1.0")
  passes bool @description("Whether the schema passes for this disability")
  barriers BarrierAnalysis[] @description("Barriers found in the schema")
  accommodations_present string[] @description("Accommodations that are implemented")
  accommodations_missing string[] @description("Accommodations that are missing")
  recommendations string[] @description("Prioritized recommendations")
  summary string @description("Human-readable summary")
}

/// Combined evaluation across multiple disability types
class CombinedDisabilityEvaluation {
  overall_score float @description("Overall accessibility score 0.0-1.0")
  passing_count int @description("Number of disability categories passing")
  total_categories int @description("Total categories evaluated")
  evaluations DisabilityEvaluation[] @description("Individual evaluations")
  summary string @description("Overall summary")
  top_recommendations string[] @description("Most important recommendations across all types")
}

// ============================================
// AI Evaluation Functions
// ============================================

/// Evaluate a schema for a specific disability type
function EvaluateForDisability(
  schema: InterfaceSchema,
  disability_type: DisabilityType
) -> DisabilityEvaluation {
  client CustomSonnet4
  prompt #"
    Evaluate this LUI schema for accessibility for users with {{ disability_type }} impairments.

    Schema to evaluate:
    {{ schema }}

    Apply these disability-specific criteria:

    {% if disability_type == "VISUAL" %}
    VISUAL IMPAIRMENT CRITERIA:
    - Audio-first design: Is information available through audio?
    - Screen reader support: Are ARIA labels and live regions configured?
    - No visual-only information: Is all visual content described?
    - High contrast: Is high contrast mode supported?
    - Key metric: 100% audio confirmation for all actions
    {% elif disability_type == "HEARING" %}
    HEARING IMPAIRMENT CRITERIA:
    - Text alternatives: Is text available for all audio content?
    - Visual alerts: Are there visual alternatives to audio alerts?
    - Captions: Is real-time captioning supported?
    - Sign language: Is sign language interpretation available?
    - Key metric: 99% caption accuracy
    {% elif disability_type == "MOTOR" %}
    MOTOR IMPAIRMENT CRITERIA:
    - Extended timeout: Is timeout ≥5× standard (≥100 seconds)?
    - Single-action: Can all actions be completed with single gestures?
    - Touch targets: Are targets ≥44×44 pixels?
    - Voice input: Is voice input supported as alternative?
    - Switch access: Is switch device access supported?
    - Key metric: ≥5× timeout duration
    {% elif disability_type == "SPEECH" %}
    SPEECH IMPAIRMENT CRITERIA:
    - Text input: Is there 100% text fallback for voice?
    - AAC devices: Is AAC device input supported?
    - Gesture input: Are gesture alternatives available?
    - Key metric: 100% text fallback coverage
    {% elif disability_type == "COGNITIVE" %}
    COGNITIVE IMPAIRMENT CRITERIA:
    - Reading level: Is content at Grade 6-8 level?
    - Consistent navigation: Are patterns predictable?
    - Progress indicators: Are multi-step processes indicated?
    - Undo support: Can actions be reversed?
    - Auto-save: Is work automatically saved?
    - Key metric: Grade 6-8 reading level
    {% elif disability_type == "NEUROLOGICAL" %}
    NEUROLOGICAL CRITERIA:
    - Seizure safety: Are there no flashes >3Hz?
    - Animation controls: Can animations be paused/stopped?
    - Reduced motion: Is prefers-reduced-motion respected?
    - No auto-play: Is media auto-play prevented?
    - Key metric: Zero flashes above 3Hz
    {% endif %}

    For each barrier found:
    1. Categorize as PERCEPTION, OPERATION, UNDERSTANDING, or ROBUSTNESS
    2. Rate severity: CRITICAL (blocks access), MAJOR (significant), MINOR (workaround exists), ADVISORY
    3. Identify the specific location in the schema
    4. Explain the impact on users
    5. Provide specific remediation

    Calculate accommodation score:
    - Start at 1.0
    - Subtract CRITICAL barriers × 0.30
    - Subtract MAJOR barriers × 0.15
    - Subtract MINOR barriers × 0.05
    - Subtract ADVISORY notices × 0.02
    - Minimum score is 0.0

    Pass criteria:
    - Score ≥ 0.70
    - Zero CRITICAL barriers

    {{ ctx.output_format }}
  "#
}

/// Evaluate a schema for all disability types
function EvaluateAllDisabilities(
  schema: InterfaceSchema
) -> CombinedDisabilityEvaluation {
  client CustomSonnet4
  prompt #"
    Evaluate this LUI schema comprehensively for all disability types.

    Schema to evaluate:
    {{ schema }}

    Evaluate for each disability type:
    1. VISUAL - Blind and low vision users
    2. HEARING - Deaf and hard of hearing users
    3. MOTOR - Users with motor impairments
    4. SPEECH - Users with speech impairments
    5. COGNITIVE - Users with cognitive impairments
    6. NEUROLOGICAL - Users with neurological conditions

    For each disability type, identify:
    - Barriers to access (with severity and location)
    - Accommodations present
    - Accommodations missing
    - Specific recommendations

    Key metrics by disability:
    | Disability | Key Metric |
    |------------|------------|
    | VISUAL | 100% audio confirmation |
    | HEARING | 99% caption accuracy |
    | MOTOR | ≥5× timeout duration |
    | SPEECH | 100% text fallback |
    | COGNITIVE | Grade 6-8 reading level |
    | NEUROLOGICAL | Zero flashes >3Hz |

    Calculate overall score as average of individual scores.
    Identify top 5 most impactful recommendations across all types.

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test evaluate_visual_accessibility {
  functions [EvaluateForDisability]
  args {
    schema {
      name "TestSchema"
      description "A test schema"
      version "1.0.0"
      accessibility {
        audio_output_enabled true
        default_config {
          screen_reader_label "Test application"
        }
      }
      components []
    }
    disability_type VISUAL
  }
}

test evaluate_motor_accessibility {
  functions [EvaluateForDisability]
  args {
    schema {
      name "TestSchema"
      description "A test schema"
      version "1.0.0"
      accessibility {
        default_config {
          interaction_constraints {
            max_session_timeout_ms 120000
          }
        }
        voice_input_enabled true
      }
      components []
    }
    disability_type MOTOR
  }
}

test evaluate_cognitive_accessibility {
  functions [EvaluateForDisability]
  args {
    schema {
      name "TestSchema"
      description "A test schema for people"
      version "1.0.0"
      accessibility {
        consistent_navigation true
        progress_indicators_enabled true
        undo_support true
      }
      components []
    }
    disability_type COGNITIVE
  }
}
