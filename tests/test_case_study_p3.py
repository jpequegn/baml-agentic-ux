"""Tests for P3 Podcast Processor case study."""

import json
import pytest
from pathlib import Path

from baml_client.types import (
    InterfaceSchema,
    LUIComponent,
    LUIComponentType,
    DomainInfo,
    ParameterType,
    UserPersona,
    TechnicalSkillLevel,
    DomainKnowledgeLevel,
    AccessibilityNeed,
    InteractionStyle,
    UsabilityGUISpec,
)

# Import from simulator to load schema
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from lui_simulator.simulator import load_schema_from_dict


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
def p3_schema_path() -> Path:
    """Get path to P3 schema."""
    return Path(__file__).parent.parent / "examples" / "p3_podcast_schema.json"


@pytest.fixture
def p3_schema(p3_schema_path: Path) -> InterfaceSchema:
    """Load the P3 LUI schema."""
    with open(p3_schema_path) as f:
        data = json.load(f)
    return load_schema_from_dict(data)


@pytest.fixture
def casual_listener_persona() -> UserPersona:
    """Create casual listener persona."""
    return UserPersona(
        persona_name="Casual Podcast Listener",
        description="Someone who wants summaries without technical complexity",
        technical_skill=TechnicalSkillLevel.BASIC,
        domain_knowledge=DomainKnowledgeLevel.BEGINNER,
        accessibility_needs=[AccessibilityNeed.NONE],
        primary_goals=["Get summaries", "Search topics"],
        pain_points=["Too many commands"],
        preferred_interaction_style=InteractionStyle.CONVERSATIONAL,
    )


@pytest.fixture
def podcast_gui_spec() -> UsabilityGUISpec:
    """Create GUI specification for comparison."""
    return UsabilityGUISpec(
        name="Traditional Podcast App",
        description="Desktop podcast application",
        screen_count=6,
        main_features=["Podcast list", "Episode player", "Search"],
        navigation_style="Sidebar navigation",
        interaction_patterns=["Click", "Drag", "Search"],
    )


# ============================================
# Test Schema Loading
# ============================================

class TestP3SchemaLoading:
    """Test that P3 schema loads correctly."""

    def test_schema_file_exists(self, p3_schema_path: Path):
        """Test that schema file exists."""
        assert p3_schema_path.exists()

    def test_schema_loads_successfully(self, p3_schema: InterfaceSchema):
        """Test that schema loads without errors."""
        assert p3_schema is not None

    def test_schema_has_correct_id(self, p3_schema: InterfaceSchema):
        """Test schema ID."""
        assert p3_schema.schema_id == "p3-podcast-processor-v1"

    def test_schema_has_correct_name(self, p3_schema: InterfaceSchema):
        """Test schema name."""
        assert p3_schema.name == "P3 Podcast Processor LUI"

    def test_schema_has_version(self, p3_schema: InterfaceSchema):
        """Test schema version."""
        assert p3_schema.version == "1.0.0"


# ============================================
# Test Domain Information
# ============================================

class TestP3DomainInfo:
    """Test P3 domain configuration."""

    def test_domain_exists(self, p3_schema: InterfaceSchema):
        """Test that domain info exists."""
        assert p3_schema.domain is not None

    def test_domain_name(self, p3_schema: InterfaceSchema):
        """Test domain name."""
        assert p3_schema.domain.domain_name == "podcast-processing"

    def test_subdomain(self, p3_schema: InterfaceSchema):
        """Test subdomain."""
        assert p3_schema.domain.subdomain == "content-automation"

    def test_key_concepts_count(self, p3_schema: InterfaceSchema):
        """Test number of key concepts."""
        assert len(p3_schema.domain.key_concepts) >= 5

    def test_key_concepts_content(self, p3_schema: InterfaceSchema):
        """Test key concepts include essential terms."""
        concepts = p3_schema.domain.key_concepts
        assert "podcasts" in concepts
        assert "episodes" in concepts
        assert "transcripts" in concepts


# ============================================
# Test Components
# ============================================

class TestP3Components:
    """Test P3 component definitions."""

    def test_component_count(self, p3_schema: InterfaceSchema):
        """Test that schema has expected number of components."""
        assert len(p3_schema.components) >= 10

    def test_has_action_components(self, p3_schema: InterfaceSchema):
        """Test that action components exist."""
        action_components = [
            c for c in p3_schema.components
            if c.component_type == LUIComponentType.ACTION
        ]
        assert len(action_components) >= 5

    def test_has_query_components(self, p3_schema: InterfaceSchema):
        """Test that query components exist."""
        query_components = [
            c for c in p3_schema.components
            if c.component_type == LUIComponentType.QUERY
        ]
        assert len(query_components) >= 5

    def test_has_navigation_component(self, p3_schema: InterfaceSchema):
        """Test that navigation component exists."""
        nav_components = [
            c for c in p3_schema.components
            if c.component_type == LUIComponentType.NAVIGATION
        ]
        assert len(nav_components) >= 1


class TestFetchComponent:
    """Test fetch-episodes component."""

    def test_fetch_exists(self, p3_schema: InterfaceSchema):
        """Test that fetch component exists."""
        fetch = next(
            (c for c in p3_schema.components if c.component_id == "fetch-episodes"),
            None
        )
        assert fetch is not None

    def test_fetch_type(self, p3_schema: InterfaceSchema):
        """Test fetch component type."""
        fetch = next(c for c in p3_schema.components if c.component_id == "fetch-episodes")
        assert fetch.component_type == LUIComponentType.ACTION

    def test_fetch_invocation(self, p3_schema: InterfaceSchema):
        """Test fetch invocation patterns."""
        fetch = next(c for c in p3_schema.components if c.component_id == "fetch-episodes")
        assert fetch.invocation.primary_phrase == "fetch new episodes"
        assert len(fetch.invocation.alternate_phrases) >= 3


class TestQueryComponent:
    """Test query-episode component."""

    def test_query_exists(self, p3_schema: InterfaceSchema):
        """Test that query component exists."""
        query = next(
            (c for c in p3_schema.components if c.component_id == "query-episode"),
            None
        )
        assert query is not None

    def test_query_type(self, p3_schema: InterfaceSchema):
        """Test query component type."""
        query = next(c for c in p3_schema.components if c.component_id == "query-episode")
        assert query.component_type == LUIComponentType.QUERY

    def test_query_intent(self, p3_schema: InterfaceSchema):
        """Test query intent is defined."""
        query = next(c for c in p3_schema.components if c.component_id == "query-episode")
        assert "question" in query.intent.lower() or "ask" in query.intent.lower()


class TestWriteBlogComponent:
    """Test write-blog component."""

    def test_write_blog_exists(self, p3_schema: InterfaceSchema):
        """Test that write-blog component exists."""
        write = next(
            (c for c in p3_schema.components if c.component_id == "write-blog"),
            None
        )
        assert write is not None

    def test_write_blog_intent(self, p3_schema: InterfaceSchema):
        """Test write-blog intent is defined."""
        write = next(c for c in p3_schema.components if c.component_id == "write-blog")
        assert "blog" in write.intent.lower()


class TestPipelineComponent:
    """Test run-pipeline composite component."""

    def test_pipeline_exists(self, p3_schema: InterfaceSchema):
        """Test that pipeline component exists."""
        pipeline = next(
            (c for c in p3_schema.components if c.component_id == "run-pipeline"),
            None
        )
        assert pipeline is not None

    def test_pipeline_requires_confirmation(self, p3_schema: InterfaceSchema):
        """Test that pipeline requires confirmation."""
        pipeline = next(c for c in p3_schema.components if c.component_id == "run-pipeline")
        assert pipeline.feedback.confirmation_required is True


# ============================================
# Test Schema JSON Structure
# ============================================

class TestP3SchemaJSON:
    """Test P3 schema JSON file structure (raw data)."""

    def test_json_has_flows(self, p3_schema_path: Path):
        """Test that JSON defines flows."""
        with open(p3_schema_path) as f:
            data = json.load(f)
        assert "flows" in data
        assert len(data["flows"]) >= 1

    def test_json_has_entities(self, p3_schema_path: Path):
        """Test that JSON defines entities."""
        with open(p3_schema_path) as f:
            data = json.load(f)
        assert "entities" in data
        assert len(data["entities"]) >= 2

    def test_json_has_global_context(self, p3_schema_path: Path):
        """Test that JSON defines global context."""
        with open(p3_schema_path) as f:
            data = json.load(f)
        assert "global_context" in data
        assert "session_variables" in data["global_context"]

    def test_json_has_component_parameters(self, p3_schema_path: Path):
        """Test that JSON components have parameters."""
        with open(p3_schema_path) as f:
            data = json.load(f)

        # Find fetch-episodes component
        fetch = next(
            (c for c in data["components"] if c["component_id"] == "fetch-episodes"),
            None
        )
        assert fetch is not None
        assert "parameters" in fetch
        assert len(fetch["parameters"]) >= 2


# ============================================
# Test User Personas
# ============================================

class TestUserPersonas:
    """Test user persona definitions for P3."""

    def test_casual_listener_creation(self, casual_listener_persona: UserPersona):
        """Test casual listener persona is valid."""
        assert casual_listener_persona.persona_name == "Casual Podcast Listener"
        assert casual_listener_persona.technical_skill == TechnicalSkillLevel.BASIC
        assert casual_listener_persona.preferred_interaction_style == InteractionStyle.CONVERSATIONAL


# ============================================
# Test GUI Comparison Spec
# ============================================

class TestGUISpec:
    """Test GUI specification for comparison."""

    def test_gui_spec_creation(self, podcast_gui_spec: UsabilityGUISpec):
        """Test GUI spec is valid."""
        assert podcast_gui_spec.name == "Traditional Podcast App"
        assert podcast_gui_spec.screen_count == 6
        assert len(podcast_gui_spec.main_features) >= 3


# ============================================
# Test Case Study Files
# ============================================

class TestCaseStudyFiles:
    """Test that case study documentation files exist."""

    def test_current_interface_doc_exists(self):
        """Test current interface documentation exists."""
        doc_path = (
            Path(__file__).parent.parent
            / "case_studies"
            / "p3_podcast_processor"
            / "01_current_interface.md"
        )
        assert doc_path.exists()

    def test_usability_analysis_script_exists(self):
        """Test usability analysis script exists."""
        script_path = (
            Path(__file__).parent.parent
            / "case_studies"
            / "p3_podcast_processor"
            / "02_usability_analysis.py"
        )
        assert script_path.exists()

    def test_learnings_doc_exists(self):
        """Test learnings documentation exists."""
        doc_path = (
            Path(__file__).parent.parent
            / "case_studies"
            / "p3_podcast_processor"
            / "03_learnings_and_comparison.md"
        )
        assert doc_path.exists()


# ============================================
# Test Invocation Quality
# ============================================

class TestInvocationQuality:
    """Test quality of invocation patterns."""

    def test_all_components_have_examples(self, p3_schema: InterfaceSchema):
        """Test that all components have usage examples."""
        for component in p3_schema.components:
            assert component.invocation.examples is not None
            assert len(component.invocation.examples) >= 1, (
                f"{component.component_id} has no examples"
            )

    def test_all_components_have_alternates(self, p3_schema: InterfaceSchema):
        """Test that all components have alternate phrases."""
        for component in p3_schema.components:
            assert component.invocation.alternate_phrases is not None
            assert len(component.invocation.alternate_phrases) >= 1, (
                f"{component.component_id} has no alternate phrases"
            )

    def test_feedback_templates_exist(self, p3_schema: InterfaceSchema):
        """Test that all components have feedback templates."""
        for component in p3_schema.components:
            assert component.feedback.success_template is not None
            assert len(component.feedback.success_template) > 0
            assert component.feedback.error_template is not None
            assert len(component.feedback.error_template) > 0
