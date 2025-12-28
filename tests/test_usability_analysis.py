"""Tests for LUI Usability Analysis module."""

import pytest
from pathlib import Path

from baml_client.types import (
    InterfaceSchema,
    DomainInfo,
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
    ComponentParameter,
    ParameterType,
    # Usability analysis types
    UsabilityAnalysis,
    UsabilityGrade,
    CategoryScore,
    UsabilityCategory,
    UsabilityIssue,
    IssueSeverity,
    UsabilityRecommendation,
    RecommendationPriority,
    EffortLevel,
    GUIComparisonResult,
    UserPersona,
    TechnicalSkillLevel,
    DomainKnowledgeLevel,
    AccessibilityNeed,
    InteractionStyle,
    UsabilityGUISpec,
    HeuristicEvaluation,
    HeuristicType,
    HeuristicRating,
    HeuristicViolation,
)


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
def sample_schema() -> InterfaceSchema:
    """Create a sample interface schema for testing."""
    domain = DomainInfo(
        domain_name="task-management",
        subdomain="personal-productivity",
        description="Task and project management",
        key_concepts=["tasks", "projects", "deadlines"],
        terminology=None,
    )

    create_task = LUIComponent(
        component_id="create-task",
        component_type=LUIComponentType.ACTION,
        intent="Create a new task",
        invocation=InvocationPattern(
            primary_phrase="create task",
            alternate_phrases=["add task", "new task"],
            examples=["Create a task to review code"],
            context_requirements=None,
        ),
        parameters=[
            ComponentParameter(
                name="task_title",
                param_type=ParameterType.STRING,
                description="The title of the task",
                required=True,
                default_value=None,
                extraction_hints=["task called", "task named"],
                validation=None,
            )
        ],
        feedback=FeedbackConfig(
            success_template="Task '{title}' created successfully",
            error_template="Could not create task: {error}",
            progress_template=None,
            confirmation_required=False,
            confirmation_prompt=None,
        ),
        accessibility=None,
    )

    return InterfaceSchema(
        schema_id="test-schema-v1",
        name="Test Task Manager",
        description="A test task management schema",
        version="1.0.0",
        domain=domain,
        components=[create_task],
        flows=[],
        entities=[],
        global_context=None,
    )


@pytest.fixture
def sample_user_persona() -> UserPersona:
    """Create a sample user persona for testing."""
    return UserPersona(
        persona_name="Power User",
        description="Experienced user who values efficiency",
        technical_skill=TechnicalSkillLevel.ADVANCED,
        domain_knowledge=DomainKnowledgeLevel.INTERMEDIATE,
        accessibility_needs=[AccessibilityNeed.NONE],
        primary_goals=["Complete tasks quickly", "Minimize repetitive actions"],
        pain_points=["Slow interfaces", "Too many confirmations"],
        preferred_interaction_style=InteractionStyle.EFFICIENT,
    )


@pytest.fixture
def sample_gui_spec() -> UsabilityGUISpec:
    """Create a sample GUI specification for comparison."""
    return UsabilityGUISpec(
        name="Traditional Task App",
        description="A typical GUI task management application",
        screen_count=5,
        main_features=["Create tasks", "Edit tasks", "Delete tasks", "View task list"],
        navigation_style="Sidebar with main content area",
        interaction_patterns=["Click buttons", "Form submission", "Drag and drop"],
    )


# ============================================
# Test Usability Grade Enum
# ============================================

class TestUsabilityGrade:
    """Test UsabilityGrade enum."""

    def test_grade_values_exist(self):
        """Test that all grade values exist."""
        assert UsabilityGrade.A_PLUS is not None
        assert UsabilityGrade.A is not None
        assert UsabilityGrade.B is not None
        assert UsabilityGrade.C is not None
        assert UsabilityGrade.D is not None
        assert UsabilityGrade.F is not None

    def test_grade_count(self):
        """Test that we have 6 grade levels."""
        grades = list(UsabilityGrade)
        assert len(grades) == 6


# ============================================
# Test Usability Category Enum
# ============================================

class TestUsabilityCategory:
    """Test UsabilityCategory enum."""

    def test_category_values_exist(self):
        """Test that all category values exist."""
        assert UsabilityCategory.DISCOVERABILITY is not None
        assert UsabilityCategory.LEARNABILITY is not None
        assert UsabilityCategory.EFFICIENCY is not None
        assert UsabilityCategory.ERROR_PREVENTION is not None
        assert UsabilityCategory.ERROR_RECOVERY is not None
        assert UsabilityCategory.ACCESSIBILITY is not None
        assert UsabilityCategory.CONSISTENCY is not None
        assert UsabilityCategory.FEEDBACK is not None

    def test_category_count(self):
        """Test that we have 8 categories."""
        categories = list(UsabilityCategory)
        assert len(categories) == 8


# ============================================
# Test Issue Severity Enum
# ============================================

class TestIssueSeverity:
    """Test IssueSeverity enum."""

    def test_severity_values_exist(self):
        """Test that all severity values exist."""
        assert IssueSeverity.CRITICAL is not None
        assert IssueSeverity.MAJOR is not None
        assert IssueSeverity.MODERATE is not None
        assert IssueSeverity.MINOR is not None
        assert IssueSeverity.COSMETIC is not None

    def test_severity_count(self):
        """Test that we have 5 severity levels."""
        severities = list(IssueSeverity)
        assert len(severities) == 5


# ============================================
# Test Recommendation Priority Enum
# ============================================

class TestRecommendationPriority:
    """Test RecommendationPriority enum."""

    def test_priority_values_exist(self):
        """Test that all priority values exist."""
        assert RecommendationPriority.CRITICAL is not None
        assert RecommendationPriority.HIGH is not None
        assert RecommendationPriority.MEDIUM is not None
        assert RecommendationPriority.LOW is not None

    def test_priority_count(self):
        """Test that we have 4 priority levels."""
        priorities = list(RecommendationPriority)
        assert len(priorities) == 4


# ============================================
# Test Effort Level Enum
# ============================================

class TestEffortLevel:
    """Test EffortLevel enum."""

    def test_effort_values_exist(self):
        """Test that all effort values exist."""
        assert EffortLevel.TRIVIAL is not None
        assert EffortLevel.LOW is not None
        assert EffortLevel.MEDIUM is not None
        assert EffortLevel.HIGH is not None
        assert EffortLevel.MAJOR is not None

    def test_effort_count(self):
        """Test that we have 5 effort levels."""
        efforts = list(EffortLevel)
        assert len(efforts) == 5


# ============================================
# Test Technical Skill Level Enum
# ============================================

class TestTechnicalSkillLevel:
    """Test TechnicalSkillLevel enum."""

    def test_skill_values_exist(self):
        """Test that all skill values exist."""
        assert TechnicalSkillLevel.NOVICE is not None
        assert TechnicalSkillLevel.BASIC is not None
        assert TechnicalSkillLevel.INTERMEDIATE is not None
        assert TechnicalSkillLevel.ADVANCED is not None
        assert TechnicalSkillLevel.EXPERT is not None


# ============================================
# Test Domain Knowledge Level Enum
# ============================================

class TestDomainKnowledgeLevel:
    """Test DomainKnowledgeLevel enum."""

    def test_knowledge_values_exist(self):
        """Test that all knowledge values exist."""
        assert DomainKnowledgeLevel.NONE is not None
        assert DomainKnowledgeLevel.BEGINNER is not None
        assert DomainKnowledgeLevel.INTERMEDIATE is not None
        assert DomainKnowledgeLevel.ADVANCED is not None
        assert DomainKnowledgeLevel.EXPERT is not None


# ============================================
# Test Accessibility Need Enum
# ============================================

class TestAccessibilityNeed:
    """Test AccessibilityNeed enum."""

    def test_accessibility_values_exist(self):
        """Test that all accessibility values exist."""
        assert AccessibilityNeed.VISUAL is not None
        assert AccessibilityNeed.AUDITORY is not None
        assert AccessibilityNeed.MOTOR is not None
        assert AccessibilityNeed.COGNITIVE is not None
        assert AccessibilityNeed.LANGUAGE is not None
        assert AccessibilityNeed.NONE is not None


# ============================================
# Test Interaction Style Enum
# ============================================

class TestInteractionStyle:
    """Test InteractionStyle enum."""

    def test_style_values_exist(self):
        """Test that all style values exist."""
        assert InteractionStyle.COMMAND is not None
        assert InteractionStyle.CONVERSATIONAL is not None
        assert InteractionStyle.GUIDED is not None
        assert InteractionStyle.EXPLORATORY is not None
        assert InteractionStyle.EFFICIENT is not None


# ============================================
# Test Heuristic Type Enum
# ============================================

class TestHeuristicType:
    """Test HeuristicType enum (Nielsen's heuristics)."""

    def test_heuristic_values_exist(self):
        """Test that all heuristic values exist."""
        assert HeuristicType.VISIBILITY_OF_STATUS is not None
        assert HeuristicType.MATCH_REAL_WORLD is not None
        assert HeuristicType.USER_CONTROL is not None
        assert HeuristicType.CONSISTENCY is not None
        assert HeuristicType.ERROR_PREVENTION is not None
        assert HeuristicType.RECOGNITION_OVER_RECALL is not None
        assert HeuristicType.FLEXIBILITY is not None
        assert HeuristicType.AESTHETIC_MINIMAL is not None
        assert HeuristicType.ERROR_RECOVERY is not None
        assert HeuristicType.HELP_DOCUMENTATION is not None

    def test_heuristic_count(self):
        """Test that we have 10 heuristics (Nielsen's 10)."""
        heuristics = list(HeuristicType)
        assert len(heuristics) == 10


# ============================================
# Test Heuristic Rating Enum
# ============================================

class TestHeuristicRating:
    """Test HeuristicRating enum."""

    def test_rating_values_exist(self):
        """Test that all rating values exist."""
        assert HeuristicRating.EXCELLENT is not None
        assert HeuristicRating.GOOD is not None
        assert HeuristicRating.ADEQUATE is not None
        assert HeuristicRating.POOR is not None
        assert HeuristicRating.CRITICAL is not None


# ============================================
# Test Category Score Class
# ============================================

class TestCategoryScore:
    """Test CategoryScore class."""

    def test_create_category_score(self):
        """Test creating a category score."""
        score = CategoryScore(
            category=UsabilityCategory.DISCOVERABILITY,
            score=85.0,
            weight=0.15,
            notes="Good discoverability with clear invocation phrases",
            key_findings=["Clear primary phrases", "Multiple alternate phrases"],
        )

        assert score.category == UsabilityCategory.DISCOVERABILITY
        assert score.score == 85.0
        assert score.weight == 0.15
        assert "discoverability" in score.notes.lower()
        assert len(score.key_findings) == 2


# ============================================
# Test Usability Issue Class
# ============================================

class TestUsabilityIssue:
    """Test UsabilityIssue class."""

    def test_create_usability_issue(self):
        """Test creating a usability issue."""
        issue = UsabilityIssue(
            issue_id="ISS-001",
            severity=IssueSeverity.MAJOR,
            category=UsabilityCategory.ERROR_PREVENTION,
            component_ref="delete-task",
            title="Missing confirmation for destructive action",
            description="The delete action does not require confirmation",
            example="User might accidentally delete a task",
            impact="Data loss if user makes mistake",
            affected_users=["novice users", "mobile users"],
        )

        assert issue.issue_id == "ISS-001"
        assert issue.severity == IssueSeverity.MAJOR
        assert issue.category == UsabilityCategory.ERROR_PREVENTION
        assert issue.component_ref == "delete-task"
        assert "confirmation" in issue.title.lower()


# ============================================
# Test Usability Recommendation Class
# ============================================

class TestUsabilityRecommendation:
    """Test UsabilityRecommendation class."""

    def test_create_recommendation(self):
        """Test creating a usability recommendation."""
        rec = UsabilityRecommendation(
            recommendation_id="REC-001",
            priority=RecommendationPriority.HIGH,
            category=UsabilityCategory.ERROR_PREVENTION,
            title="Add confirmation for destructive actions",
            current_state="Delete action executes immediately",
            suggested_change="Add a confirmation prompt before deletion",
            implementation_effort=EffortLevel.LOW,
            expected_improvement="Prevent accidental data loss",
            related_issues=["ISS-001"],
        )

        assert rec.recommendation_id == "REC-001"
        assert rec.priority == RecommendationPriority.HIGH
        assert rec.implementation_effort == EffortLevel.LOW
        assert "ISS-001" in rec.related_issues


# ============================================
# Test GUI Comparison Result Class
# ============================================

class TestGUIComparisonResult:
    """Test GUIComparisonResult class."""

    def test_create_comparison_result(self):
        """Test creating a GUI comparison result."""
        result = GUIComparisonResult(
            advantages_lui=["Faster task entry", "Natural language input"],
            advantages_gui=["Visual feedback", "Drag and drop"],
            parity_features=["Task creation", "Task listing"],
            conversion_notes="LUI excels at quick data entry but lacks visual feedback",
            recommended_hybrid_approach="Use LUI for input, GUI for visualization",
        )

        assert len(result.advantages_lui) == 2
        assert len(result.advantages_gui) == 2
        assert "Faster task entry" in result.advantages_lui
        assert result.recommended_hybrid_approach is not None


# ============================================
# Test User Persona Class
# ============================================

class TestUserPersona:
    """Test UserPersona class."""

    def test_create_user_persona(self, sample_user_persona: UserPersona):
        """Test creating a user persona."""
        assert sample_user_persona.persona_name == "Power User"
        assert sample_user_persona.technical_skill == TechnicalSkillLevel.ADVANCED
        assert sample_user_persona.preferred_interaction_style == InteractionStyle.EFFICIENT

    def test_persona_with_accessibility_needs(self):
        """Test persona with accessibility needs."""
        persona = UserPersona(
            persona_name="Screen Reader User",
            description="User who relies on screen reader",
            technical_skill=TechnicalSkillLevel.INTERMEDIATE,
            domain_knowledge=DomainKnowledgeLevel.BEGINNER,
            accessibility_needs=[AccessibilityNeed.VISUAL],
            primary_goals=["Navigate efficiently", "Hear clear feedback"],
            pain_points=["Unlabeled elements", "Complex interactions"],
            preferred_interaction_style=InteractionStyle.COMMAND,
        )

        assert AccessibilityNeed.VISUAL in persona.accessibility_needs
        assert persona.preferred_interaction_style == InteractionStyle.COMMAND


# ============================================
# Test Usability GUI Spec Class
# ============================================

class TestUsabilityGUISpec:
    """Test UsabilityGUISpec class."""

    def test_create_gui_spec(self, sample_gui_spec: UsabilityGUISpec):
        """Test creating a GUI specification."""
        assert sample_gui_spec.name == "Traditional Task App"
        assert sample_gui_spec.screen_count == 5
        assert len(sample_gui_spec.main_features) == 4
        assert "Click buttons" in sample_gui_spec.interaction_patterns


# ============================================
# Test Heuristic Evaluation Class
# ============================================

class TestHeuristicEvaluation:
    """Test HeuristicEvaluation class."""

    def test_create_heuristic_evaluation(self):
        """Test creating a heuristic evaluation."""
        violation = HeuristicViolation(
            location="delete-task component",
            description="No undo option after deletion",
            severity=IssueSeverity.MAJOR,
            fix_suggestion="Add undo functionality or confirmation",
        )

        evaluation = HeuristicEvaluation(
            heuristic=HeuristicType.USER_CONTROL,
            rating=HeuristicRating.POOR,
            findings=["No undo option", "No cancel during processing"],
            violations=[violation],
        )

        assert evaluation.heuristic == HeuristicType.USER_CONTROL
        assert evaluation.rating == HeuristicRating.POOR
        assert len(evaluation.violations) == 1
        assert evaluation.violations[0].severity == IssueSeverity.MAJOR


# ============================================
# Test Heuristic Violation Class
# ============================================

class TestHeuristicViolation:
    """Test HeuristicViolation class."""

    def test_create_violation(self):
        """Test creating a heuristic violation."""
        violation = HeuristicViolation(
            location="create-task feedback",
            description="Success message disappears too quickly",
            severity=IssueSeverity.MINOR,
            fix_suggestion="Increase message display duration",
        )

        assert "create-task" in violation.location
        assert violation.severity == IssueSeverity.MINOR
        assert "duration" in violation.fix_suggestion.lower()


# ============================================
# Test Usability Analysis Class
# ============================================

class TestUsabilityAnalysis:
    """Test UsabilityAnalysis class."""

    def test_create_usability_analysis(self):
        """Test creating a complete usability analysis."""
        category_scores = [
            CategoryScore(
                category=UsabilityCategory.DISCOVERABILITY,
                score=85.0,
                weight=0.15,
                notes="Good discoverability",
                key_findings=["Clear phrases"],
            ),
            CategoryScore(
                category=UsabilityCategory.LEARNABILITY,
                score=90.0,
                weight=0.15,
                notes="Easy to learn",
                key_findings=["Intuitive patterns"],
            ),
        ]

        issues = [
            UsabilityIssue(
                issue_id="ISS-001",
                severity=IssueSeverity.MINOR,
                category=UsabilityCategory.FEEDBACK,
                component_ref=None,
                title="Limited feedback options",
                description="Feedback templates are basic",
                example=None,
                impact="Users may want more detail",
                affected_users=["power users"],
            ),
        ]

        recommendations = [
            UsabilityRecommendation(
                recommendation_id="REC-001",
                priority=RecommendationPriority.LOW,
                category=UsabilityCategory.FEEDBACK,
                title="Enhance feedback templates",
                current_state="Basic success/error messages",
                suggested_change="Add more detailed feedback options",
                implementation_effort=EffortLevel.MEDIUM,
                expected_improvement="Better user understanding",
                related_issues=["ISS-001"],
            ),
        ]

        analysis = UsabilityAnalysis(
            overall_score=87.5,
            grade=UsabilityGrade.B,
            summary="Good usability with minor improvements needed",
            category_scores=category_scores,
            issues=issues,
            recommendations=recommendations,
            strengths=["Clear invocation phrases", "Good error handling"],
            comparison_to_gui=None,
        )

        assert analysis.overall_score == 87.5
        assert analysis.grade == UsabilityGrade.B
        assert len(analysis.category_scores) == 2
        assert len(analysis.issues) == 1
        assert len(analysis.recommendations) == 1
        assert len(analysis.strengths) == 2

    def test_analysis_with_gui_comparison(self):
        """Test usability analysis with GUI comparison."""
        comparison = GUIComparisonResult(
            advantages_lui=["Speed", "Natural input"],
            advantages_gui=["Visual clarity"],
            parity_features=["Core task management"],
            conversion_notes="Good conversion",
            recommended_hybrid_approach=None,
        )

        analysis = UsabilityAnalysis(
            overall_score=85.0,
            grade=UsabilityGrade.B,
            summary="Good overall usability",
            category_scores=[],
            issues=[],
            recommendations=[],
            strengths=["Natural language"],
            comparison_to_gui=comparison,
        )

        assert analysis.comparison_to_gui is not None
        assert "Speed" in analysis.comparison_to_gui.advantages_lui


# ============================================
# Test Type Imports
# ============================================

class TestTypeImports:
    """Test that all types are properly importable from baml_client."""

    def test_all_usability_types_importable(self):
        """Test that all usability analysis types can be imported."""
        # This test passes if the imports at the top of the file succeed
        # If any import fails, pytest will report an error
        assert UsabilityAnalysis is not None
        assert UsabilityGrade is not None
        assert CategoryScore is not None
        assert UsabilityCategory is not None
        assert UsabilityIssue is not None
        assert IssueSeverity is not None
        assert UsabilityRecommendation is not None
        assert RecommendationPriority is not None
        assert EffortLevel is not None
        assert GUIComparisonResult is not None
        assert UserPersona is not None
        assert TechnicalSkillLevel is not None
        assert DomainKnowledgeLevel is not None
        assert AccessibilityNeed is not None
        assert InteractionStyle is not None
        assert UsabilityGUISpec is not None
        assert HeuristicEvaluation is not None
        assert HeuristicType is not None
        assert HeuristicRating is not None
        assert HeuristicViolation is not None
