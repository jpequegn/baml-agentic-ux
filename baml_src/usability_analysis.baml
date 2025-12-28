// Usability Analysis for Language User Interfaces
// Provides comprehensive evaluation of LUI schemas for usability

/// Overall usability analysis result
class UsabilityAnalysis {
  overall_score float @description("Overall usability score from 0-100")
  grade UsabilityGrade @description("Letter grade based on overall score")
  summary string @description("Brief summary of the analysis")
  category_scores CategoryScore[] @description("Scores for each usability category")
  issues UsabilityIssue[] @description("Identified usability issues")
  recommendations UsabilityRecommendation[] @description("Improvement recommendations")
  strengths string[] @description("Notable strengths of the LUI design")
  comparison_to_gui GUIComparisonResult? @description("Comparison with traditional GUI")
}

/// Letter grade for usability
enum UsabilityGrade {
  A_PLUS @description("Exceptional: 95-100")
  A @description("Excellent: 90-94")
  B @description("Good: 80-89")
  C @description("Acceptable: 70-79")
  D @description("Poor: 60-69")
  F @description("Failing: Below 60")
}

/// Score for a specific usability category
class CategoryScore {
  category UsabilityCategory
  score float @description("Score from 0-100")
  weight float @description("Weight of this category in overall score (0-1)")
  notes string @description("Explanation of the score")
  key_findings string[] @description("Key observations for this category")
}

/// Categories of usability to evaluate
enum UsabilityCategory {
  DISCOVERABILITY @description("Can users find and understand available features")
  LEARNABILITY @description("How easy is it to learn invocation patterns")
  EFFICIENCY @description("How quickly can users accomplish tasks")
  ERROR_PREVENTION @description("Does the design prevent user mistakes")
  ERROR_RECOVERY @description("How well does it handle and recover from errors")
  ACCESSIBILITY @description("Works for users with different abilities and needs")
  CONSISTENCY @description("Are patterns consistent across the interface")
  FEEDBACK @description("Does the system provide clear feedback")
}

/// A usability issue identified in the schema
class UsabilityIssue {
  issue_id string @description("Unique identifier for tracking")
  severity IssueSeverity
  category UsabilityCategory
  component_ref string? @description("Reference to specific component if applicable")
  title string @description("Brief title of the issue")
  description string @description("Detailed description of the issue")
  example string? @description("Example demonstrating the issue")
  impact string @description("How this affects users")
  affected_users string[] @description("Which user types are most affected")
}

/// Severity levels for usability issues
enum IssueSeverity {
  CRITICAL @description("Prevents core functionality, must fix")
  MAJOR @description("Significantly impacts usability, should fix")
  MODERATE @description("Noticeable impact, recommended to fix")
  MINOR @description("Small impact, nice to fix")
  COSMETIC @description("Minimal impact, optional improvement")
}

/// A recommendation for improving usability
class UsabilityRecommendation {
  recommendation_id string @description("Unique identifier for tracking")
  priority RecommendationPriority
  category UsabilityCategory
  title string @description("Brief title of the recommendation")
  current_state string @description("Description of current behavior")
  suggested_change string @description("Proposed improvement")
  implementation_effort EffortLevel @description("Estimated effort to implement")
  expected_improvement string @description("Expected benefit from the change")
  related_issues string[] @description("Issue IDs this recommendation addresses")
}

/// Priority levels for recommendations
enum RecommendationPriority {
  CRITICAL @description("Must implement - blocking issue")
  HIGH @description("Should implement soon - major improvement")
  MEDIUM @description("Consider implementing - moderate improvement")
  LOW @description("Nice to have - minor improvement")
}

/// Effort level for implementing changes
enum EffortLevel {
  TRIVIAL @description("Minutes to implement")
  LOW @description("Hours to implement")
  MEDIUM @description("Days to implement")
  HIGH @description("Weeks to implement")
  MAJOR @description("Significant project")
}

/// Comparison between LUI and traditional GUI
class GUIComparisonResult {
  advantages_lui string[] @description("What LUI does better than GUI")
  advantages_gui string[] @description("What GUI does better than LUI")
  parity_features string[] @description("Features that work equally well")
  conversion_notes string @description("Notes on the GUI to LUI conversion")
  recommended_hybrid_approach string? @description("Suggestions for combining approaches")
}

/// User persona for targeted analysis
class UserPersona {
  persona_name string @description("Name of the persona")
  description string @description("Brief description of this user type")
  technical_skill TechnicalSkillLevel
  domain_knowledge DomainKnowledgeLevel
  accessibility_needs AccessibilityNeed[]
  primary_goals string[] @description("Main goals for using the interface")
  pain_points string[] @description("Common frustrations or challenges")
  preferred_interaction_style InteractionStyle
}

/// Technical skill levels
enum TechnicalSkillLevel {
  NOVICE @description("New to technology")
  BASIC @description("Can use common applications")
  INTERMEDIATE @description("Comfortable with technology")
  ADVANCED @description("Power user")
  EXPERT @description("Technical professional")
}

/// Domain knowledge levels
enum DomainKnowledgeLevel {
  NONE @description("No domain knowledge")
  BEGINNER @description("Basic understanding")
  INTERMEDIATE @description("Working knowledge")
  ADVANCED @description("Deep understanding")
  EXPERT @description("Domain specialist")
}

/// Accessibility needs
enum AccessibilityNeed {
  VISUAL @description("Visual impairment accommodations")
  AUDITORY @description("Hearing impairment accommodations")
  MOTOR @description("Motor impairment accommodations")
  COGNITIVE @description("Cognitive assistance needs")
  LANGUAGE @description("Language/literacy support")
  NONE @description("No specific accessibility needs")
}

/// Preferred interaction styles
enum InteractionStyle {
  COMMAND @description("Prefers explicit commands")
  CONVERSATIONAL @description("Prefers natural conversation")
  GUIDED @description("Prefers step-by-step guidance")
  EXPLORATORY @description("Likes to discover features")
  EFFICIENT @description("Wants fastest path to goal")
}

/// Simplified GUI spec for usability comparison
class UsabilityGUISpec {
  name string @description("Name of the GUI")
  description string @description("Brief description")
  screen_count int @description("Number of screens/views")
  main_features string[] @description("Primary features")
  navigation_style string @description("How users navigate")
  interaction_patterns string[] @description("Common interaction patterns")
}

/// Heuristic evaluation result
class HeuristicEvaluation {
  heuristic HeuristicType
  rating HeuristicRating
  findings string[] @description("Specific observations")
  violations HeuristicViolation[]
}

/// Nielsen's usability heuristics adapted for LUI
enum HeuristicType {
  VISIBILITY_OF_STATUS @description("System keeps users informed")
  MATCH_REAL_WORLD @description("Uses familiar language and concepts")
  USER_CONTROL @description("Users can undo and exit freely")
  CONSISTENCY @description("Follows conventions")
  ERROR_PREVENTION @description("Prevents problems from occurring")
  RECOGNITION_OVER_RECALL @description("Minimizes memory load")
  FLEXIBILITY @description("Accommodates different user preferences")
  AESTHETIC_MINIMAL @description("No unnecessary information")
  ERROR_RECOVERY @description("Helps users recover from errors")
  HELP_DOCUMENTATION @description("Help is available when needed")
}

/// Rating for heuristic compliance
enum HeuristicRating {
  EXCELLENT @description("Fully compliant, exemplary")
  GOOD @description("Mostly compliant, minor issues")
  ADEQUATE @description("Basic compliance, room for improvement")
  POOR @description("Significant violations")
  CRITICAL @description("Major violations, fails heuristic")
}

/// Specific heuristic violation
class HeuristicViolation {
  location string @description("Where the violation occurs")
  description string @description("What the violation is")
  severity IssueSeverity
  fix_suggestion string @description("How to address it")
}

// ===================
// Analysis Functions
// ===================

/// Main usability analysis function
function AnalyzeLUIUsability(
  schema: InterfaceSchema,
  target_users: UserPersona[]?,
  comparison_gui: UsabilityGUISpec?
) -> UsabilityAnalysis {
  client CustomSonnet4
  prompt #"
    You are a usability expert analyzing a Language User Interface (LUI) design.

    Analyze this LUI schema comprehensively for usability.

    ## Schema Information
    Name: {{ schema.name }}
    Description: {{ schema.description }}
    Version: {{ schema.version }}
    Domain: {{ schema.domain.domain_name }}

    ## Components
    {% for component in schema.components %}
    - **{{ component.component_id }}** ({{ component.component_type }}): {{ component.intent }}
      Primary invocation: "{{ component.invocation.primary_phrase }}"
      {% if component.invocation.alternate_phrases %}
      Alternates: {{ component.invocation.alternate_phrases }}
      {% endif %}
      {% if component.parameters %}
      Parameters:
      {% for param in component.parameters %}
        - {{ param.name }} ({{ param.param_type }})
      {% endfor %}
      {% endif %}
    {% endfor %}

    {% if schema.flows %}
    ## Conversational Flows
    {% for flow in schema.flows %}
    - {{ flow.name }}: {{ flow.description }}
    {% endfor %}
    {% endif %}

    {% if target_users %}
    ## Target Users
    {% for user in target_users %}
    - **{{ user.persona_name }}**: {{ user.description }}
      Technical skill: {{ user.technical_skill }}
      Goals: {{ user.primary_goals }}
    {% endfor %}
    {% endif %}

    {% if comparison_gui %}
    ## GUI Comparison
    Compare this LUI to the following GUI:
    - Name: {{ comparison_gui.name }}
    - Features: {{ comparison_gui.main_features }}
    - Navigation: {{ comparison_gui.navigation_style }}
    {% endif %}

    ## Evaluation Categories
    Evaluate across these categories (weight each 0.0-1.0, total should equal 1.0):

    1. **DISCOVERABILITY** (weight ~0.15): How will users know what's possible?
    2. **LEARNABILITY** (weight ~0.15): Are invocation patterns intuitive?
    3. **EFFICIENCY** (weight ~0.15): Can tasks be done quickly?
    4. **ERROR_PREVENTION** (weight ~0.10): Does it prevent mistakes?
    5. **ERROR_RECOVERY** (weight ~0.10): How are errors handled?
    6. **ACCESSIBILITY** (weight ~0.10): Works for diverse users?
    7. **CONSISTENCY** (weight ~0.15): Are patterns consistent?
    8. **FEEDBACK** (weight ~0.10): Is feedback clear and helpful?

    ## Instructions
    1. Score each category 0-100 based on the schema design
    2. Calculate overall_score as weighted average
    3. Assign grade: A+(95-100), A(90-94), B(80-89), C(70-79), D(60-69), F(<60)
    4. Identify specific issues with severity and impact
    5. Provide actionable recommendations
    6. Note strengths and positive aspects
    7. If comparison_gui provided, compare LUI vs GUI approaches

    Be specific and reference actual components/invocations in your analysis.

    {{ ctx.output_format }}
  "#
}

/// Quick usability score without detailed analysis
function QuickUsabilityScore(
  schema: InterfaceSchema
) -> CategoryScore[] {
  client CustomHaiku
  prompt #"
    Quickly evaluate this LUI schema across usability categories.

    Schema: {{ schema.name }}
    Components:
    {% for component in schema.components %}
    - {{ component.component_id }}: "{{ component.invocation.primary_phrase }}"
    {% endfor %}

    Score each category 0-100 with brief notes:
    - DISCOVERABILITY
    - LEARNABILITY
    - EFFICIENCY
    - ERROR_PREVENTION
    - ERROR_RECOVERY
    - ACCESSIBILITY
    - CONSISTENCY
    - FEEDBACK

    Weight each category appropriately (weights should sum to 1.0).

    {{ ctx.output_format }}
  "#
}

/// Detailed heuristic evaluation
function EvaluateHeuristics(
  schema: InterfaceSchema
) -> HeuristicEvaluation[] {
  client CustomSonnet4
  prompt #"
    Perform a heuristic evaluation of this LUI schema using Nielsen's heuristics adapted for language interfaces.

    Schema: {{ schema.name }}
    Components:
    {% for component in schema.components %}
    - {{ component.component_id }} ({{ component.component_type }}): "{{ component.invocation.primary_phrase }}"
      Feedback: success="{{ component.feedback.success_template }}", error="{{ component.feedback.error_template }}"
      {% if component.feedback.confirmation_required %}(requires confirmation){% endif %}
    {% endfor %}

    Evaluate each heuristic:

    1. VISIBILITY_OF_STATUS - Does the system keep users informed?
    2. MATCH_REAL_WORLD - Are terms and concepts familiar?
    3. USER_CONTROL - Can users undo, cancel, or exit?
    4. CONSISTENCY - Are invocation patterns consistent?
    5. ERROR_PREVENTION - Does design prevent errors?
    6. RECOGNITION_OVER_RECALL - Are options visible/suggested?
    7. FLEXIBILITY - Can users customize or take shortcuts?
    8. AESTHETIC_MINIMAL - Is information concise and relevant?
    9. ERROR_RECOVERY - Do error messages help recovery?
    10. HELP_DOCUMENTATION - Is help available?

    For each heuristic:
    - Rate: EXCELLENT, GOOD, ADEQUATE, POOR, or CRITICAL
    - List specific findings
    - Note any violations with location and fix suggestions

    {{ ctx.output_format }}
  "#
}

/// Analyze for specific user persona
function AnalyzeForPersona(
  schema: InterfaceSchema,
  persona: UserPersona
) -> UsabilityAnalysis {
  client CustomSonnet4
  prompt #"
    Analyze this LUI schema specifically for the given user persona.

    ## User Persona: {{ persona.persona_name }}
    - Description: {{ persona.description }}
    - Technical Skill: {{ persona.technical_skill }}
    - Domain Knowledge: {{ persona.domain_knowledge }}
    - Accessibility Needs: {{ persona.accessibility_needs }}
    - Primary Goals: {{ persona.primary_goals }}
    - Pain Points: {{ persona.pain_points }}
    - Preferred Style: {{ persona.preferred_interaction_style }}

    ## Schema: {{ schema.name }}
    {% for component in schema.components %}
    - {{ component.component_id }}: "{{ component.invocation.primary_phrase }}" ({{ component.component_type }})
    {% endfor %}

    Analyze usability from this persona's perspective:
    1. How well does the design serve their goals?
    2. Does it match their skill level?
    3. Are accessibility needs met?
    4. Does it align with their preferred interaction style?
    5. What pain points might they encounter?

    Provide persona-specific issues and recommendations.

    {{ ctx.output_format }}
  "#
}

/// Compare LUI to GUI implementation
function CompareLUIToGUI(
  lui_schema: InterfaceSchema,
  gui_spec: UsabilityGUISpec
) -> GUIComparisonResult {
  client CustomSonnet4
  prompt #"
    Compare this Language User Interface to a traditional Graphical User Interface.

    ## LUI Schema: {{ lui_schema.name }}
    Components:
    {% for component in lui_schema.components %}
    - {{ component.intent }}: "{{ component.invocation.primary_phrase }}"
    {% endfor %}

    ## GUI: {{ gui_spec.name }}
    - Description: {{ gui_spec.description }}
    - Screens: {{ gui_spec.screen_count }}
    - Features: {{ gui_spec.main_features }}
    - Navigation: {{ gui_spec.navigation_style }}
    - Patterns: {{ gui_spec.interaction_patterns }}

    Analyze:
    1. What does the LUI do better?
    2. What does the GUI do better?
    3. What features work equally well in both?
    4. Notes on the conversion from GUI to LUI
    5. Recommendations for a hybrid approach (if beneficial)

    Be specific about trade-offs and when each approach is preferred.

    {{ ctx.output_format }}
  "#
}

/// Generate improvement suggestions
function SuggestImprovements(
  schema: InterfaceSchema,
  issues: UsabilityIssue[]
) -> UsabilityRecommendation[] {
  client CustomSonnet4
  prompt #"
    Generate specific improvement recommendations for this LUI schema based on identified issues.

    ## Schema: {{ schema.name }}
    Components:
    {% for component in schema.components %}
    - {{ component.component_id }}: "{{ component.invocation.primary_phrase }}"
    {% endfor %}

    ## Identified Issues
    {% for issue in issues %}
    - [{{ issue.issue_id }}] {{ issue.severity }}/{{ issue.category }}: {{ issue.title }}
      {{ issue.description }}
    {% endfor %}

    For each recommendation:
    1. Link to related issues by ID
    2. Describe current state clearly
    3. Propose specific, implementable changes
    4. Estimate implementation effort
    5. Explain expected improvement

    Prioritize recommendations by impact and effort.

    {{ ctx.output_format }}
  "#
}
