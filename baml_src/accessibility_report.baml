// Accessibility Report Types
// BAML types for comprehensive accessibility compliance reports
// Issue #76 - Task 4.10: Accessibility Report Generator
// Part of #27 - Phase 4: LUI Accessibility Standards

// ============================================
// Report Summary Types
// ============================================

/// Executive summary of accessibility report
class AccessibilitySummary {
  total_components int @description("Total number of components evaluated")
  passing_components int @description("Components meeting target level")
  critical_violations int @description("Count of critical violations")
  major_violations int @description("Count of major violations")
  minor_violations int @description("Count of minor violations")
  advisory_count int @description("Count of advisory notices")
  top_issues string[] @description("Top 5 issues found")
  remediation_priority string[] @description("Prioritized remediations")
}

/// Recommendation with priority and impact
class AccessibilityRecommendation {
  priority string @description("Priority level: high, medium, low")
  title string @description("Short recommendation title")
  description string @description("Detailed description")
  affected_components string[] @description("Components affected")
  impact string @description("Impact if not addressed")
  effort string @description("Estimated effort: low, medium, high")
}

// ============================================
// Component Report Types
// ============================================

/// Accessibility report for a single component
class ComponentAccessibilityReport {
  component_id string @description("Unique component identifier")
  component_type string @description("Type of component")
  score float @description("Accessibility score 0.0-1.0")
  passes bool @description("Whether component passes target level")
  achieved_level string? @description("Achieved compliance level")
  violation_count int @description("Number of violations")
  recommendations string[] @description("Component-specific recommendations")
}

// ============================================
// Disability Coverage Types
// ============================================

/// Accessibility report for a disability type
class DisabilityAccessibilityReport {
  disability_type string @description("Type of disability (visual, hearing, motor, etc.)")
  accommodation_score float @description("Accommodation score 0.0-1.0")
  passes bool @description("Whether accommodations are adequate")
  barriers_count int @description("Total barriers found")
  critical_barriers int @description("Critical barriers found")
  accommodations_present string[] @description("Accommodations already in place")
  accommodations_missing string[] @description("Missing accommodations")
  recommendations string[] @description("Disability-specific recommendations")
}

// ============================================
// Violation Types
// ============================================

/// Severity levels for violations
enum ViolationSeverityLevel {
  CRITICAL @description("Blocks accessibility")
  MAJOR @description("Significant impact")
  MINOR @description("Reduces usability")
  ADVISORY @description("Suggestion only")
}

/// Single accessibility violation
class ReportViolation {
  criterion string @description("LUIAG criterion ID (e.g., A.1.1)")
  severity ViolationSeverityLevel @description("Violation severity")
  description string @description("What the violation is")
  remediation string @description("How to fix it")
  element string? @description("Specific element that caused violation")
  line_number int? @description("Line number if applicable")
}

// ============================================
// Full Report Types
// ============================================

/// Complete accessibility compliance report
class AccessibilityReport {
  schema_name string @description("Name of the evaluated schema")
  target_level string @description("Target compliance level (A, AA, AAA)")
  achieved_level string? @description("Actually achieved level")
  overall_score float @description("Overall accessibility score 0.0-1.0")
  score_percentage int @description("Score as percentage")
  passes bool @description("Whether target level was achieved")
  generated_at string @description("ISO timestamp of report generation")
  summary AccessibilitySummary @description("Executive summary")
  component_details ComponentAccessibilityReport[] @description("Per-component details")
  disability_coverage DisabilityAccessibilityReport[] @description("Per-disability coverage")
  violations ReportViolation[] @description("All violations found")
  recommendations AccessibilityRecommendation[] @description("Prioritized recommendations")
}

// ============================================
// Report Generation Input
// ============================================

/// Input for report generation
class ReportGenerationInput {
  schema_name string @description("Name for the report")
  target_level string @description("Target compliance level")
  include_components bool @description("Include component details")
  include_disability bool @description("Include disability coverage")
  max_violations int @description("Maximum violations to include")
  max_recommendations int @description("Maximum recommendations to include")
}

// ============================================
// AI Analysis Functions
// ============================================

/// Generate executive summary from violations
function GenerateAccessibilitySummary(
  violations ReportViolation[],
  component_count int,
  passing_count int
) -> AccessibilitySummary {
  client CustomSonnet4
  prompt #"
    Generate an executive summary of accessibility findings.

    Violations: {{ violations }}
    Total Components: {{ component_count }}
    Passing Components: {{ passing_count }}

    Create a clear summary that:
    1. Accurately counts violations by severity
    2. Identifies the top 5 most impactful issues
    3. Prioritizes remediations by impact and effort
    4. Uses clear, actionable language

    Focus on issues that affect the most users or have the highest severity.

    {{ ctx.output_format }}
  "#
}

/// Generate prioritized recommendations
function GenerateRecommendations(
  violations ReportViolation[],
  disability_reports DisabilityAccessibilityReport[]
) -> AccessibilityRecommendation[] {
  client CustomSonnet4
  prompt #"
    Generate prioritized accessibility recommendations.

    Violations: {{ violations }}
    Disability Coverage: {{ disability_reports }}

    Create recommendations that:
    1. Address critical issues first
    2. Group related violations into single recommendations
    3. Provide clear, actionable titles
    4. Estimate effort realistically
    5. Explain impact in terms of user groups affected

    Priority levels:
    - high: Blocks accessibility or affects many users
    - medium: Significant impact on subset of users
    - low: Minor improvements or edge cases

    Limit to 10-15 most important recommendations.

    {{ ctx.output_format }}
  "#
}

/// Analyze schema for accessibility and generate full report
function AnalyzeAccessibility(
  schema_json string,
  target_level string
) -> AccessibilityReport {
  client CustomSonnet4
  prompt #"
    Analyze the schema for accessibility compliance.

    Schema: {{ schema_json }}
    Target Level: {{ target_level }}

    Evaluate against LUIAG criteria:
    - Level A: Basic accessibility (max grade 12, max 35 words/sentence)
    - Level AA: Standard accessibility (max grade 8, max 25 words/sentence)
    - Level AAA: Enhanced accessibility (max grade 6, max 20 words/sentence)

    Check for:
    1. Reading level (Flesch-Kincaid grade)
    2. Sentence length
    3. Complex vocabulary
    4. Passive voice usage
    5. Technical jargon
    6. Timing configurations
    7. Input method compatibility
    8. Disability accommodations

    Generate a comprehensive report with all findings.

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test generate_summary {
  functions [GenerateAccessibilitySummary]
  args {
    violations [
      {
        criterion "AA.1.1"
        severity MAJOR
        description "Reading level 9.2 exceeds maximum 8.0"
        remediation "Simplify vocabulary"
      },
      {
        criterion "AA.2.1"
        severity MINOR
        description "Complex word 'utilize' found"
        remediation "Use 'use' instead"
      }
    ]
    component_count 5
    passing_count 3
  }
}

test generate_recommendations {
  functions [GenerateRecommendations]
  args {
    violations [
      {
        criterion "A.1.2"
        severity MAJOR
        description "Sentence exceeds 35 words"
        remediation "Split into shorter sentences"
      }
    ]
    disability_reports [
      {
        disability_type "visual"
        accommodation_score 0.8
        passes true
        barriers_count 2
        critical_barriers 0
        accommodations_present ["High contrast support"]
        accommodations_missing ["Screen reader labels"]
        recommendations ["Add aria-label attributes"]
      }
    ]
  }
}
