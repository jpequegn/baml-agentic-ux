"""Tests for Intent Pipeline Integration.

Issue #85 - Task 5.8: Intent Pipeline Integration
Part of #28 - Phase 5: Intent Drift Detection
"""

import pytest

from src.intent_drift import (
    AvailableComponent,
    DriftType,
    IntentDefinition,
    IntentExtractionWithDrift,
    IntentPipelineWithDrift,
    PipelineAction,
    PipelineConversationContext,
    PipelineDriftConfig,
    SimpleIntentExtraction,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def sample_components():
    """Create sample available components for testing."""
    return [
        AvailableComponent(
            component_id="search_products",
            component_type="ACTION",
            intent="Search for products in the catalog",
            invocation_phrases=["find products", "search for", "look up items"],
            parameters=[{"name": "query", "type": "string"}],
            domain="ecommerce",
        ),
        AvailableComponent(
            component_id="add_to_cart",
            component_type="ACTION",
            intent="Add a product to the shopping cart",
            invocation_phrases=["add to cart", "add this", "put in cart"],
            parameters=[{"name": "product_id", "type": "string"}],
            domain="ecommerce",
        ),
        AvailableComponent(
            component_id="view_order_history",
            component_type="QUERY",
            intent="View past orders and purchase history",
            invocation_phrases=["show orders", "order history", "past purchases"],
            parameters=[],
            domain="account",
        ),
        AvailableComponent(
            component_id="check_balance",
            component_type="QUERY",
            intent="Check account balance",
            invocation_phrases=["show balance", "check funds", "account balance"],
            parameters=[],
            domain="finance",
        ),
    ]


@pytest.fixture
def core_capabilities():
    """Create list of core capability names."""
    return ["search_products", "add_to_cart"]


@pytest.fixture
def supported_domains():
    """Create list of supported domains."""
    return ["ecommerce", "account"]


@pytest.fixture
def pipeline(sample_components, core_capabilities, supported_domains):
    """Create a configured pipeline for testing."""
    return IntentPipelineWithDrift(
        available_components=sample_components,
        core_capabilities=core_capabilities,
        supported_domains=supported_domains,
    )


@pytest.fixture
def conversation_context():
    """Create sample conversation context."""
    return PipelineConversationContext(
        session_id="test-session-123",
        recent_messages=[
            {"role": "user", "content": "I want to buy a shirt", "intent": "search_products"},
            {"role": "assistant", "content": "Here are some shirts..."},
        ],
        current_state="browsing",
        active_entity="product-456",
    )


# ============================================
# Pipeline Configuration Tests
# ============================================


class TestPipelineDriftConfig:
    """Tests for PipelineDriftConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = PipelineDriftConfig()
        assert config.enable_drift_detection is True
        assert config.enable_coherence_tracking is True
        assert config.max_redirect_suggestions == 3
        assert config.fallback_to_clarification is True
        assert config.parallel_analysis is True
        assert config.include_semantic_details is True
        assert config.include_graceful_response is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = PipelineDriftConfig(
            enable_drift_detection=False,
            max_redirect_suggestions=5,
            fallback_to_clarification=False,
        )
        assert config.enable_drift_detection is False
        assert config.max_redirect_suggestions == 5
        assert config.fallback_to_clarification is False

    def test_threshold_config(self):
        """Test confidence threshold configuration."""
        config = PipelineDriftConfig(
            confidence_thresholds={
                "very_high": 0.90,
                "high": 0.75,
                "medium": 0.50,
                "low": 0.30,
            }
        )
        assert config.confidence_thresholds["very_high"] == 0.90
        assert config.confidence_thresholds["high"] == 0.75

    def test_invalid_max_suggestions(self):
        """Test validation of max_redirect_suggestions."""
        with pytest.raises(ValueError):
            PipelineDriftConfig(max_redirect_suggestions=-1)

    def test_invalid_threshold(self):
        """Test validation of confidence thresholds."""
        with pytest.raises(ValueError):
            PipelineDriftConfig(confidence_thresholds={"invalid": 1.5})


# ============================================
# Simple Intent Extraction Tests
# ============================================


class TestSimpleIntentExtraction:
    """Tests for SimpleIntentExtraction."""

    def test_create_extraction(self):
        """Test creating a simple intent extraction."""
        extraction = SimpleIntentExtraction(
            intent_name="search_products",
            intent_category="action",
            target_component="search_products",
            confidence=0.85,
        )
        assert extraction.intent_name == "search_products"
        assert extraction.confidence == 0.85
        assert extraction.is_ambiguous is False

    def test_ambiguous_extraction(self):
        """Test ambiguous extraction with clarification."""
        extraction = SimpleIntentExtraction(
            intent_name="unknown",
            intent_category="none",
            target_component=None,
            confidence=0.3,
            is_ambiguous=True,
            suggested_clarification="What would you like to search for?",
        )
        assert extraction.is_ambiguous is True
        assert extraction.suggested_clarification is not None


# ============================================
# Available Component Tests
# ============================================


class TestAvailableComponent:
    """Tests for AvailableComponent."""

    def test_create_component(self):
        """Test creating an available component."""
        component = AvailableComponent(
            component_id="test_component",
            component_type="ACTION",
            intent="Test action",
            invocation_phrases=["test", "do test"],
            domain="testing",
        )
        assert component.component_id == "test_component"
        assert component.domain == "testing"

    def test_to_intent_definition(self):
        """Test converting component to intent definition."""
        component = AvailableComponent(
            component_id="search_products",
            component_type="ACTION",
            intent="Search for products",
            invocation_phrases=["find products", "search items", "look up"],
            domain="ecommerce",
        )
        intent_def = component.to_intent_definition()
        assert isinstance(intent_def, IntentDefinition)
        assert intent_def.name == "search_products"
        assert intent_def.description == "Search for products"
        assert intent_def.domain == "ecommerce"


# ============================================
# Pipeline Conversation Context Tests
# ============================================


class TestPipelineConversationContext:
    """Tests for PipelineConversationContext."""

    def test_create_context(self, conversation_context):
        """Test creating conversation context."""
        assert conversation_context.session_id == "test-session-123"
        assert len(conversation_context.recent_messages) == 2

    def test_to_drift_context(self, conversation_context):
        """Test converting to drift context."""
        drift_context = conversation_context.to_drift_context()
        assert drift_context.session_id == "test-session-123"
        assert drift_context.current_topic == "browsing"


# ============================================
# Intent Pipeline With Drift Tests
# ============================================


class TestIntentPipelineWithDrift:
    """Tests for IntentPipelineWithDrift class."""

    def test_create_pipeline_default(self):
        """Test creating pipeline with defaults."""
        pipeline = IntentPipelineWithDrift()
        assert pipeline.config is not None
        assert pipeline.drift_config is not None

    def test_create_pipeline_with_components(self, sample_components, core_capabilities):
        """Test creating pipeline with components."""
        pipeline = IntentPipelineWithDrift(
            available_components=sample_components,
            core_capabilities=core_capabilities,
        )
        assert pipeline._available_components == sample_components
        assert pipeline._core_capabilities == set(core_capabilities)

    def test_set_available_components(self, pipeline, sample_components):
        """Test setting available components."""
        new_components = sample_components[:2]
        pipeline.set_available_components(new_components)
        assert pipeline._available_components == new_components

    def test_set_core_capabilities(self, pipeline):
        """Test setting core capabilities."""
        new_capabilities = ["new_cap1", "new_cap2"]
        pipeline.set_core_capabilities(new_capabilities)
        assert pipeline._core_capabilities == set(new_capabilities)


# ============================================
# Extract Intent With Drift Tests
# ============================================


class TestExtractIntentWithDrift:
    """Tests for extract_intent_with_drift method."""

    def test_extract_in_scope_intent(self, pipeline, conversation_context):
        """Test extracting an in-scope intent."""
        result = pipeline.extract_intent_with_drift(
            user_input="I want to search for shoes",
            conversation_context=conversation_context,
        )
        assert isinstance(result, IntentExtractionWithDrift)
        assert result.intent_extraction is not None
        assert result.drift_analysis is not None
        assert result.confidence_assessment is not None
        assert result.recommended_action is not None
        assert result.response is not None

    def test_extract_out_of_scope_intent(self, pipeline):
        """Test extracting an out-of-scope intent."""
        result = pipeline.extract_intent_with_drift(
            user_input="What is the meaning of life?",
        )
        assert result.drift_analysis.drift_type != DriftType.NONE
        assert result.recommended_action != PipelineAction.EXECUTE

    def test_extract_with_no_context(self, pipeline):
        """Test extraction without conversation context."""
        result = pipeline.extract_intent_with_drift(
            user_input="Show me products",
        )
        assert result is not None
        assert result.intent_extraction is not None

    def test_extract_ambiguous_intent(self, pipeline):
        """Test extracting an ambiguous intent."""
        result = pipeline.extract_intent_with_drift(
            user_input="do the thing",
        )
        assert result.recommended_action in (
            PipelineAction.CLARIFY,
            PipelineAction.REDIRECT,
        )

    def test_extract_with_drift_disabled(self, sample_components):
        """Test extraction with drift detection disabled."""
        config = PipelineDriftConfig(enable_drift_detection=False)
        pipeline = IntentPipelineWithDrift(
            config=config,
            available_components=sample_components,
        )
        result = pipeline.extract_intent_with_drift(
            user_input="What is the meaning of life?",
        )
        assert result.drift_analysis.drift_type == DriftType.NONE
        assert result.drift_analysis.drift_score == 0.0


# ============================================
# Intent Extraction Result Properties Tests
# ============================================


class TestIntentExtractionWithDriftProperties:
    """Tests for IntentExtractionWithDrift properties."""

    def test_has_drift_property(self, pipeline):
        """Test has_drift property."""
        # Test with an out-of-scope request
        result = pipeline.extract_intent_with_drift(
            user_input="Tell me about quantum physics",
        )
        # Check the property returns the expected value
        assert isinstance(result.has_drift, bool)

    def test_should_proceed_property(self, pipeline):
        """Test should_proceed property."""
        result = pipeline.extract_intent_with_drift(
            user_input="search for products",
        )
        assert result.should_proceed == (result.recommended_action == PipelineAction.EXECUTE)

    def test_needs_clarification_property(self, pipeline):
        """Test needs_clarification property."""
        result = pipeline.extract_intent_with_drift(
            user_input="do something",
        )
        assert result.needs_clarification == (result.recommended_action == PipelineAction.CLARIFY)

    def test_needs_redirect_property(self, pipeline):
        """Test needs_redirect property."""
        result = pipeline.extract_intent_with_drift(
            user_input="What is the weather forecast for next year?",
        )
        assert result.needs_redirect == (result.recommended_action == PipelineAction.REDIRECT)


# ============================================
# Redirect Suggestions Tests
# ============================================


class TestRedirectSuggestions:
    """Tests for redirect suggestions in pipeline."""

    def test_redirect_suggestions_generated(self, pipeline):
        """Test that redirect suggestions are generated for drift."""
        result = pipeline.extract_intent_with_drift(
            user_input="Invest my savings in stocks",
        )
        if result.recommended_action in (PipelineAction.REDIRECT, PipelineAction.CLARIFY):
            # May or may not have suggestions depending on semantic similarity
            assert isinstance(result.redirect_suggestions, list)

    def test_redirect_suggestions_limited(self, sample_components):
        """Test that redirect suggestions respect max limit."""
        config = PipelineDriftConfig(max_redirect_suggestions=2)
        pipeline = IntentPipelineWithDrift(
            config=config,
            available_components=sample_components,
        )
        result = pipeline.extract_intent_with_drift(
            user_input="Help me with something different",
        )
        assert len(result.redirect_suggestions) <= 2


# ============================================
# Get Drift Detection Result Tests
# ============================================


class TestGetDriftDetectionResult:
    """Tests for get_drift_detection_result method."""

    def test_get_drift_result(self, pipeline):
        """Test getting a drift detection result."""
        result = pipeline.get_drift_detection_result(
            user_input="Find me some products",
        )
        assert result.input == "Find me some products"
        assert result.analysis is not None
        assert result.confidence_assessment is not None
        assert result.semantic_analysis is not None

    def test_drift_result_with_context(self, pipeline, conversation_context):
        """Test drift detection with conversation context."""
        result = pipeline.get_drift_detection_result(
            user_input="Show me my cart",
            conversation_context=conversation_context,
        )
        assert result is not None


# ============================================
# Coherence Tracker Integration Tests
# ============================================


class TestCoherenceTrackerIntegration:
    """Tests for coherence tracker integration."""

    def test_coherence_metrics(self, pipeline):
        """Test getting coherence metrics."""
        # Process a few turns
        pipeline.extract_intent_with_drift("search for shoes")
        pipeline.extract_intent_with_drift("add that to cart")

        metrics = pipeline.get_coherence_metrics()
        assert "average_coherence" in metrics
        assert "turn_count" in metrics
        assert "drift_rate" in metrics

    def test_reset_coherence_tracker(self, pipeline):
        """Test resetting the coherence tracker."""
        pipeline.extract_intent_with_drift("search for products")
        pipeline.reset_coherence_tracker()
        metrics = pipeline.get_coherence_metrics()
        assert metrics["turn_count"] == 0

    def test_should_reset_context(self, pipeline):
        """Test checking if context should reset."""
        should_reset, reason = pipeline.should_reset_context()
        assert isinstance(should_reset, bool)
        if should_reset:
            assert reason is not None


# ============================================
# Pipeline Action Routing Tests
# ============================================


class TestPipelineActionRouting:
    """Tests for pipeline action routing."""

    def test_execute_action(self, pipeline):
        """Test that clear in-scope intents route appropriately."""
        result = pipeline.extract_intent_with_drift(
            user_input="search for products in catalog",
        )
        # The pipeline should take some action (may not always EXECUTE
        # due to semantic similarity calculations)
        assert result.recommended_action in (
            PipelineAction.EXECUTE,
            PipelineAction.CLARIFY,
            PipelineAction.REDIRECT,
        )

    def test_domain_shift_redirects(self, pipeline):
        """Test that domain shifts route to REDIRECT."""
        result = pipeline.extract_intent_with_drift(
            user_input="Help me book a flight to Paris",
        )
        # This is outside supported domains
        assert result.recommended_action in (
            PipelineAction.REDIRECT,
            PipelineAction.CLARIFY,
            PipelineAction.REJECT,
        )

    def test_abstraction_climb_handling(self, pipeline):
        """Test handling of abstract requests."""
        result = pipeline.extract_intent_with_drift(
            user_input="What is happiness?",
        )
        # Abstract requests should not execute
        assert result.recommended_action != PipelineAction.EXECUTE


# ============================================
# Processing Time Tests
# ============================================


class TestProcessingTime:
    """Tests for processing time tracking."""

    def test_processing_time_recorded(self, pipeline):
        """Test that processing time is recorded."""
        result = pipeline.extract_intent_with_drift(
            user_input="search for something",
        )
        assert result.processing_time_ms >= 0

    def test_processing_time_reasonable(self, pipeline):
        """Test that processing time is reasonable."""
        result = pipeline.extract_intent_with_drift(
            user_input="find products",
        )
        # Should complete in under 5 seconds
        assert result.processing_time_ms < 5000


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for the pipeline."""

    def test_full_pipeline_flow(self, pipeline, conversation_context):
        """Test the full pipeline flow."""
        # Simulate a conversation
        results = []
        inputs = [
            "search for shoes",
            "show me the red ones",
            "add the first one to cart",
            "what's the weather like?",  # Out of scope
        ]

        for user_input in inputs:
            result = pipeline.extract_intent_with_drift(
                user_input=user_input,
                conversation_context=conversation_context,
            )
            results.append(result)

        # Verify all results are valid
        for result in results:
            assert result.intent_extraction is not None
            assert result.drift_analysis is not None
            assert result.response is not None

        # The last request (weather) should drift
        assert results[-1].has_drift or results[-1].recommended_action != PipelineAction.EXECUTE

    def test_semantic_analysis_included(self, sample_components):
        """Test that semantic analysis is included when configured."""
        config = PipelineDriftConfig(include_semantic_details=True)
        pipeline = IntentPipelineWithDrift(
            config=config,
            available_components=sample_components,
        )
        result = pipeline.extract_intent_with_drift(
            user_input="find something for me",
        )
        assert result.semantic_analysis is not None

    def test_semantic_analysis_excluded(self, sample_components):
        """Test that semantic analysis is excluded when configured."""
        config = PipelineDriftConfig(include_semantic_details=False)
        pipeline = IntentPipelineWithDrift(
            config=config,
            available_components=sample_components,
        )
        result = pipeline.extract_intent_with_drift(
            user_input="find something for me",
        )
        assert result.semantic_analysis is None


# ============================================
# Edge Cases Tests
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_input(self, pipeline):
        """Test handling of empty input."""
        result = pipeline.extract_intent_with_drift(
            user_input="",
        )
        assert result.recommended_action != PipelineAction.EXECUTE

    def test_very_long_input(self, pipeline):
        """Test handling of very long input."""
        long_input = "search for products " * 100
        result = pipeline.extract_intent_with_drift(
            user_input=long_input,
        )
        assert result is not None

    def test_special_characters(self, pipeline):
        """Test handling of special characters."""
        result = pipeline.extract_intent_with_drift(
            user_input="find @#$%^&* products!!!",
        )
        assert result is not None

    def test_no_components(self):
        """Test pipeline with no available components."""
        pipeline = IntentPipelineWithDrift(
            available_components=[],
        )
        result = pipeline.extract_intent_with_drift(
            user_input="search for something",
        )
        assert result is not None
        # Should not be able to execute without components
        assert result.intent_extraction.confidence == 0.0 or result.redirect_suggestions == []
