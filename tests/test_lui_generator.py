"""Tests for LUI Generator Types."""

import pytest
from baml_client.types import (
    # Generator types
    DomainContext,
    TerminologyEntry,
    StylePreferences,
    Tone,
    Verbosity,
    Formality,
    GenerationOptions,
    # Refinement types
    RefinementFocus,
    RefinementResult,
    SchemaChange,
    ChangeType,
    # Analysis types
    RequirementsAnalysis,
    IdentifiedNeed,
    FlowSuggestion,
    Priority,
    ComplexityLevel,
    # Comparison types
    ComparisonResult,
    InteractionDifference,
    AccessibilityComparison,
    # Interface schema types (for integration)
    InterfaceSchema,
    DomainInfo,
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
)


class TestGeneratorEnums:
    """Test generator enum definitions."""

    def test_tone_enum_values(self):
        """Verify all expected tone values exist."""
        expected = {"PROFESSIONAL", "FRIENDLY", "TECHNICAL", "CASUAL", "EMPATHETIC"}
        actual = {t.name for t in Tone}
        assert actual == expected

    def test_verbosity_enum_values(self):
        """Verify all expected verbosity values exist."""
        expected = {"CONCISE", "STANDARD", "DETAILED", "ADAPTIVE"}
        actual = {v.name for v in Verbosity}
        assert actual == expected

    def test_formality_enum_values(self):
        """Verify all expected formality values exist."""
        expected = {"FORMAL", "NEUTRAL", "INFORMAL", "MIXED"}
        actual = {f.name for f in Formality}
        assert actual == expected

    def test_refinement_focus_enum_values(self):
        """Verify all expected refinement focus values exist."""
        expected = {
            "INVOCATION_PATTERNS",
            "ERROR_HANDLING",
            "FLOW_LOGIC",
            "ENTITY_COVERAGE",
            "ACCESSIBILITY",
            "PERFORMANCE",
            "CONSISTENCY",
        }
        actual = {r.name for r in RefinementFocus}
        assert actual == expected

    def test_priority_enum_values(self):
        """Verify all expected priority values exist."""
        expected = {"CRITICAL", "HIGH", "MEDIUM", "LOW"}
        actual = {p.name for p in Priority}
        assert actual == expected

    def test_complexity_level_enum_values(self):
        """Verify all expected complexity levels exist."""
        expected = {"SIMPLE", "MODERATE", "COMPLEX", "ENTERPRISE"}
        actual = {c.name for c in ComplexityLevel}
        assert actual == expected

    def test_change_type_enum_values(self):
        """Verify all expected change types exist."""
        expected = {"ADDED", "MODIFIED", "REMOVED", "RESTRUCTURED"}
        actual = {c.name for c in ChangeType}
        assert actual == expected


class TestDomainContext:
    """Test DomainContext creation."""

    def test_create_minimal_domain_context(self):
        """Test creating a minimal domain context."""
        ctx = DomainContext(
            domain_name="e-commerce",
            key_concepts=["products", "orders", "customers"],
            existing_terminology=None,
            target_users=None,
            constraints=None,
        )
        assert ctx.domain_name == "e-commerce"
        assert len(ctx.key_concepts) == 3

    def test_create_full_domain_context(self):
        """Test creating a complete domain context."""
        terminology = [
            TerminologyEntry(
                term="SKU",
                meaning="Stock Keeping Unit - unique product identifier",
                preferred=True,
            ),
            TerminologyEntry(
                term="item number",
                meaning="Alternative term for SKU",
                preferred=False,
            ),
        ]

        ctx = DomainContext(
            domain_name="inventory-management",
            key_concepts=["products", "stock levels", "warehouses", "reorder points"],
            existing_terminology=terminology,
            target_users=["warehouse managers", "inventory clerks"],
            constraints=["Real-time sync required", "Barcode scanner integration"],
        )

        assert ctx.domain_name == "inventory-management"
        assert len(ctx.key_concepts) == 4
        assert ctx.existing_terminology is not None
        assert len(ctx.existing_terminology) == 2
        assert ctx.existing_terminology[0].preferred is True
        assert ctx.target_users is not None
        assert len(ctx.target_users) == 2
        assert ctx.constraints is not None
        assert len(ctx.constraints) == 2


class TestStylePreferences:
    """Test StylePreferences creation."""

    def test_create_minimal_style_preferences(self):
        """Test creating minimal style preferences."""
        prefs = StylePreferences(
            tone=Tone.PROFESSIONAL,
            verbosity=Verbosity.STANDARD,
            formality=Formality.NEUTRAL,
            language_code=None,
            brand_voice=None,
        )
        assert prefs.tone == Tone.PROFESSIONAL
        assert prefs.verbosity == Verbosity.STANDARD

    def test_create_full_style_preferences(self):
        """Test creating complete style preferences."""
        prefs = StylePreferences(
            tone=Tone.EMPATHETIC,
            verbosity=Verbosity.ADAPTIVE,
            formality=Formality.INFORMAL,
            language_code="en-US",
            brand_voice="Warm, supportive, and solution-focused. Like a helpful friend.",
        )
        assert prefs.tone == Tone.EMPATHETIC
        assert prefs.language_code == "en-US"
        assert prefs.brand_voice is not None


class TestGenerationOptions:
    """Test GenerationOptions creation."""

    def test_create_generation_options(self):
        """Test creating generation options."""
        options = GenerationOptions(
            include_examples=True,
            include_error_handling=True,
            include_accessibility=True,
            max_components=10,
            max_flows=5,
            component_types=[LUIComponentType.ACTION, LUIComponentType.QUERY],
        )
        assert options.include_examples is True
        assert options.max_components == 10
        assert options.component_types is not None
        assert len(options.component_types) == 2


class TestRequirementsAnalysis:
    """Test RequirementsAnalysis types."""

    def test_create_identified_need(self):
        """Test creating an identified need."""
        need = IdentifiedNeed(
            need_id="need-1",
            description="Allow users to create new tasks",
            component_type=LUIComponentType.ACTION,
            suggested_phrases=["create task", "add task", "new task"],
            parameters=["title", "description", "due_date"],
            related_needs=["need-2", "need-3"],
            priority=Priority.CRITICAL,
        )
        assert need.need_id == "need-1"
        assert need.component_type == LUIComponentType.ACTION
        assert need.priority == Priority.CRITICAL
        assert len(need.suggested_phrases) == 3

    def test_create_flow_suggestion(self):
        """Test creating a flow suggestion."""
        flow = FlowSuggestion(
            flow_name="Task Creation Flow",
            description="Multi-step flow for creating a task",
            trigger_phrases=["create a task", "I need to add a task"],
            involves_needs=["need-1", "need-4"],
            estimated_steps=4,
        )
        assert flow.flow_name == "Task Creation Flow"
        assert flow.estimated_steps == 4
        assert len(flow.involves_needs) == 2

    def test_create_requirements_analysis(self):
        """Test creating a complete requirements analysis."""
        need = IdentifiedNeed(
            need_id="need-1",
            description="Search functionality",
            component_type=LUIComponentType.QUERY,
            suggested_phrases=["search", "find"],
            parameters=["query"],
            related_needs=[],
            priority=Priority.HIGH,
        )

        flow = FlowSuggestion(
            flow_name="Search Flow",
            description="Search and filter results",
            trigger_phrases=["search for"],
            involves_needs=["need-1"],
            estimated_steps=2,
        )

        analysis = RequirementsAnalysis(
            identified_needs=[need],
            suggested_flows=[flow],
            domain_entities=["Product", "Category", "User"],
            complexity_assessment=ComplexityLevel.MODERATE,
            estimated_components=8,
            notes=["Consider adding faceted search", "May need pagination"],
        )

        assert len(analysis.identified_needs) == 1
        assert analysis.complexity_assessment == ComplexityLevel.MODERATE
        assert analysis.estimated_components == 8


class TestRefinementTypes:
    """Test refinement-related types."""

    def test_create_schema_change(self):
        """Test creating a schema change record."""
        change = SchemaChange(
            change_type=ChangeType.MODIFIED,
            location="components[0].invocation.primary_phrase",
            description="Made invocation phrase more natural",
            before="create-task",
            after="create a new task",
            rationale="Users don't typically use hyphens in speech",
        )
        assert change.change_type == ChangeType.MODIFIED
        assert change.before == "create-task"
        assert change.after == "create a new task"

    def test_create_refinement_result(self):
        """Test creating a refinement result."""
        # Create a minimal schema for testing
        domain = DomainInfo(
            domain_name="test",
            subdomain=None,
            description="Test domain",
            key_concepts=["test"],
            terminology=None,
        )

        component = LUIComponent(
            component_id="test-component",
            component_type=LUIComponentType.ACTION,
            intent="Test action",
            invocation=InvocationPattern(
                primary_phrase="test",
                alternate_phrases=[],
                examples=[],
                context_requirements=None,
            ),
            parameters=[],
            feedback=FeedbackConfig(
                success_template="Done",
                error_template="Failed",
                progress_template=None,
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
        )

        schema = InterfaceSchema(
            schema_id="test-v1",
            name="Test Schema",
            description="For testing",
            version="1.0.0",
            domain=domain,
            components=[component],
            flows=[],
            entities=[],
            global_context=None,
        )

        change = SchemaChange(
            change_type=ChangeType.ADDED,
            location="components[1]",
            description="Added new component",
            before=None,
            after="new component definition",
            rationale="Feedback requested additional functionality",
        )

        result = RefinementResult(
            refined_schema=schema,
            changes_made=[change],
            feedback_addressed=["Add more natural invocation patterns"],
            suggestions=["Consider adding voice hints for accessibility"],
        )

        assert result.refined_schema.schema_id == "test-v1"
        assert len(result.changes_made) == 1
        assert len(result.feedback_addressed) == 1


class TestComparisonTypes:
    """Test comparison-related types."""

    def test_create_interaction_difference(self):
        """Test creating an interaction difference."""
        diff = InteractionDifference(
            aspect="Navigation",
            lui_approach="Natural language commands like 'go to settings'",
            traditional_approach="Click hamburger menu, then settings icon",
            winner="lui",
            reasoning="LUI is faster and more accessible for screen reader users",
        )
        assert diff.aspect == "Navigation"
        assert diff.winner == "lui"

    def test_create_accessibility_comparison(self):
        """Test creating an accessibility comparison."""
        comparison = AccessibilityComparison(
            lui_accessibility_score=0.85,
            traditional_accessibility_score=0.72,
            lui_strengths=["Voice control", "No visual navigation required"],
            traditional_strengths=["Visual feedback", "Familiar patterns"],
            improvement_opportunities=[
                "Add confirmation sounds to LUI",
                "Improve color contrast in traditional UI",
            ],
        )
        assert comparison.lui_accessibility_score == 0.85
        assert len(comparison.lui_strengths) == 2
        assert len(comparison.improvement_opportunities) == 2

    def test_create_comparison_result(self):
        """Test creating a complete comparison result."""
        diff = InteractionDifference(
            aspect="Data Entry",
            lui_approach="Conversational form filling",
            traditional_approach="Form with text inputs",
            winner="tie",
            reasoning="Both have advantages depending on data type",
        )

        acc = AccessibilityComparison(
            lui_accessibility_score=0.80,
            traditional_accessibility_score=0.75,
            lui_strengths=["Voice input"],
            traditional_strengths=["Visual layout"],
            improvement_opportunities=["Add haptic feedback"],
        )

        result = ComparisonResult(
            lui_advantages=["Faster for experienced users", "Better accessibility"],
            traditional_advantages=["Visual overview", "Familiar to most users"],
            interaction_differences=[diff],
            accessibility_comparison=acc,
            recommendations=["Use LUI for power users", "Keep traditional for onboarding"],
            hybrid_suggestions=["Offer both modalities", "Let users choose preference"],
        )

        assert len(result.lui_advantages) == 2
        assert len(result.hybrid_suggestions) == 2
        assert result.accessibility_comparison.lui_accessibility_score == 0.80
