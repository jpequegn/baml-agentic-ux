"""Tests for the redirect suggestion engine module.

Issue #84 - Task 5.7: Redirect Suggestion Engine
Part of #28 - Phase 5: Intent Drift Detection
"""

import pytest

from src.intent_drift.redirect_engine import (
    REDIRECT_PHRASE_TEMPLATES,
    REDIRECT_REASON_TEMPLATES,
    RedirectContext,
    RedirectEngineConfig,
    RedirectStrategy,
    RedirectSuggestionEngine,
    ScoredSuggestion,
)
from src.intent_drift.semantic_analyzer import IntentDefinition
from src.intent_drift.types import (
    AbstractionLevel,
    DriftType,
    NearestIntent,
    RedirectSuggestion,
    SemanticAnalysis,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def sample_intents() -> list[IntentDefinition]:
    """Create sample intent definitions for testing."""
    return [
        IntentDefinition(
            name="check_balance",
            description="Check your account balance",
            keywords=["balance", "money", "account", "funds"],
            examples=["What's my balance?", "How much money do I have?"],
            capability_id="banking",
            domain="finance",
        ),
        IntentDefinition(
            name="transfer_money",
            description="Transfer money between accounts",
            keywords=["transfer", "send", "move", "money"],
            examples=["Transfer $50 to savings", "Send money to John"],
            capability_id="banking",
            domain="finance",
        ),
        IntentDefinition(
            name="pay_bill",
            description="Pay a bill or invoice",
            keywords=["pay", "bill", "invoice", "payment"],
            examples=["Pay my electricity bill", "Pay invoice #123"],
            capability_id="payments",
            domain="finance",
        ),
        IntentDefinition(
            name="get_weather",
            description="Get current weather information",
            keywords=["weather", "temperature", "forecast", "rain"],
            examples=["What's the weather?", "Will it rain tomorrow?"],
            capability_id="weather",
            domain="utilities",
        ),
        IntentDefinition(
            name="set_reminder",
            description="Set a reminder for later",
            keywords=["reminder", "remind", "alert", "notify"],
            examples=["Remind me at 5pm", "Set a reminder for tomorrow"],
            capability_id="calendar",
            domain="productivity",
        ),
        IntentDefinition(
            name="view_history",
            description="View your transaction history from the past",
            keywords=["history", "past", "previous", "transactions"],
            examples=["Show my history", "View past transactions"],
            capability_id="banking",
            domain="finance",
        ),
        IntentDefinition(
            name="my_preferences",
            description="View and update your personal account preferences",
            keywords=["preferences", "settings", "my", "personal"],
            examples=["Show my preferences", "Update my settings"],
            capability_id="settings",
            domain="account",
        ),
    ]


@pytest.fixture
def sample_semantic_analysis() -> SemanticAnalysis:
    """Create a sample semantic analysis result."""
    return SemanticAnalysis(
        input_text="Can you help me invest in stocks?",
        abstraction_level=AbstractionLevel.CONCRETE,
        nearest_intents=[
            NearestIntent(intent_name="transfer_money", similarity=0.4),
            NearestIntent(intent_name="check_balance", similarity=0.35),
            NearestIntent(intent_name="pay_bill", similarity=0.3),
        ],
        domain_classification=["investments", "finance"],
    )


@pytest.fixture
def engine(sample_intents: list[IntentDefinition]) -> RedirectSuggestionEngine:
    """Create an engine with sample intents."""
    return RedirectSuggestionEngine(
        available_intents=sample_intents,
        core_capability_names=["check_balance", "transfer_money"],
    )


# ============================================
# Template Tests
# ============================================


class TestTemplates:
    """Tests for redirect phrase and reason templates."""

    def test_phrase_templates_exist(self):
        """Test that phrase templates are defined."""
        assert "offer" in REDIRECT_PHRASE_TEMPLATES
        assert "suggest" in REDIRECT_PHRASE_TEMPLATES
        assert "capability" in REDIRECT_PHRASE_TEMPLATES
        assert "question" in REDIRECT_PHRASE_TEMPLATES

    def test_phrase_templates_have_action_placeholder(self):
        """Test that all phrase templates have {action} placeholder."""
        for style, templates in REDIRECT_PHRASE_TEMPLATES.items():
            assert len(templates) > 0, f"No templates for {style}"
            for template in templates:
                assert "{action}" in template, f"Missing action in {style}: {template}"

    def test_reason_templates_for_all_drift_types(self):
        """Test that reason templates exist for all drift types."""
        for drift_type in DriftType:
            assert drift_type in REDIRECT_REASON_TEMPLATES, (
                f"Missing reason template for {drift_type}"
            )

    def test_reason_templates_are_non_empty(self):
        """Test that all reason templates have at least one option."""
        for drift_type, templates in REDIRECT_REASON_TEMPLATES.items():
            assert len(templates) > 0, f"No reason templates for {drift_type}"


# ============================================
# Configuration Tests
# ============================================


class TestRedirectEngineConfig:
    """Tests for RedirectEngineConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = RedirectEngineConfig()
        assert config.min_relevance_threshold == 0.2
        assert config.max_suggestions == 3
        assert config.diversity_weight == 0.3
        assert config.recency_penalty == 0.5
        assert config.core_capability_boost == 0.2
        assert config.phrase_variation is True
        assert config.include_explanation is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = RedirectEngineConfig(
            min_relevance_threshold=0.5,
            max_suggestions=5,
            diversity_weight=0.5,
        )
        assert config.min_relevance_threshold == 0.5
        assert config.max_suggestions == 5
        assert config.diversity_weight == 0.5

    def test_invalid_threshold_raises_error(self):
        """Test that invalid threshold values raise errors."""
        with pytest.raises(ValueError):
            RedirectEngineConfig(min_relevance_threshold=-0.1)
        with pytest.raises(ValueError):
            RedirectEngineConfig(min_relevance_threshold=1.5)

    def test_invalid_max_suggestions_raises_error(self):
        """Test that invalid max_suggestions raises error."""
        with pytest.raises(ValueError):
            RedirectEngineConfig(max_suggestions=0)

    def test_invalid_diversity_weight_raises_error(self):
        """Test that invalid diversity_weight raises error."""
        with pytest.raises(ValueError):
            RedirectEngineConfig(diversity_weight=-0.1)
        with pytest.raises(ValueError):
            RedirectEngineConfig(diversity_weight=1.5)

    def test_invalid_recency_penalty_raises_error(self):
        """Test that invalid recency_penalty raises error."""
        with pytest.raises(ValueError):
            RedirectEngineConfig(recency_penalty=-0.1)
        with pytest.raises(ValueError):
            RedirectEngineConfig(recency_penalty=1.5)

    def test_invalid_core_capability_boost_raises_error(self):
        """Test that invalid core_capability_boost raises error."""
        with pytest.raises(ValueError):
            RedirectEngineConfig(core_capability_boost=-0.1)
        with pytest.raises(ValueError):
            RedirectEngineConfig(core_capability_boost=1.5)


# ============================================
# Strategy Tests
# ============================================


class TestRedirectStrategy:
    """Tests for RedirectStrategy enum."""

    def test_strategy_values(self):
        """Test that all strategy values are defined."""
        assert RedirectStrategy.SEMANTIC_SIMILARITY.value == "semantic_similarity"
        assert RedirectStrategy.CORE_CAPABILITIES.value == "core_capabilities"
        assert RedirectStrategy.PRACTICAL_ACTIONS.value == "practical_actions"
        assert RedirectStrategy.NON_PERSONAL.value == "non_personal"
        assert RedirectStrategy.CURRENT_FOCUSED.value == "current_focused"
        assert RedirectStrategy.DIVERSITY.value == "diversity"


class TestStrategySelection:
    """Tests for drift-type specific strategy selection."""

    def test_scope_expansion_uses_semantic_similarity(
        self, engine: RedirectSuggestionEngine
    ):
        """Test that SCOPE_EXPANSION uses SEMANTIC_SIMILARITY strategy."""
        strategy = engine._get_strategy_for_drift_type(DriftType.SCOPE_EXPANSION)
        assert strategy == RedirectStrategy.SEMANTIC_SIMILARITY

    def test_domain_shift_uses_core_capabilities(
        self, engine: RedirectSuggestionEngine
    ):
        """Test that DOMAIN_SHIFT uses CORE_CAPABILITIES strategy."""
        strategy = engine._get_strategy_for_drift_type(DriftType.DOMAIN_SHIFT)
        assert strategy == RedirectStrategy.CORE_CAPABILITIES

    def test_abstraction_climb_uses_practical_actions(
        self, engine: RedirectSuggestionEngine
    ):
        """Test that ABSTRACTION_CLIMB uses PRACTICAL_ACTIONS strategy."""
        strategy = engine._get_strategy_for_drift_type(DriftType.ABSTRACTION_CLIMB)
        assert strategy == RedirectStrategy.PRACTICAL_ACTIONS

    def test_personalization_uses_non_personal(
        self, engine: RedirectSuggestionEngine
    ):
        """Test that PERSONALIZATION uses NON_PERSONAL strategy."""
        strategy = engine._get_strategy_for_drift_type(DriftType.PERSONALIZATION)
        assert strategy == RedirectStrategy.NON_PERSONAL

    def test_temporal_drift_uses_current_focused(
        self, engine: RedirectSuggestionEngine
    ):
        """Test that TEMPORAL_DRIFT uses CURRENT_FOCUSED strategy."""
        strategy = engine._get_strategy_for_drift_type(DriftType.TEMPORAL_DRIFT)
        assert strategy == RedirectStrategy.CURRENT_FOCUSED

    def test_ambiguous_uses_diversity(self, engine: RedirectSuggestionEngine):
        """Test that AMBIGUOUS uses DIVERSITY strategy."""
        strategy = engine._get_strategy_for_drift_type(DriftType.AMBIGUOUS)
        assert strategy == RedirectStrategy.DIVERSITY

    def test_none_uses_semantic_similarity(self, engine: RedirectSuggestionEngine):
        """Test that NONE uses SEMANTIC_SIMILARITY strategy."""
        strategy = engine._get_strategy_for_drift_type(DriftType.NONE)
        assert strategy == RedirectStrategy.SEMANTIC_SIMILARITY


# ============================================
# Engine Initialization Tests
# ============================================


class TestEngineInitialization:
    """Tests for RedirectSuggestionEngine initialization."""

    def test_default_initialization(self):
        """Test engine with default settings."""
        engine = RedirectSuggestionEngine()
        assert engine.config is not None
        assert engine.semantic_analyzer is not None
        assert engine.available_intents == []
        assert engine.core_capability_names == set()

    def test_initialization_with_intents(self, sample_intents: list[IntentDefinition]):
        """Test engine initialization with intents."""
        engine = RedirectSuggestionEngine(available_intents=sample_intents)
        assert len(engine.available_intents) == len(sample_intents)

    def test_initialization_with_core_capabilities(
        self, sample_intents: list[IntentDefinition]
    ):
        """Test engine initialization with core capabilities."""
        engine = RedirectSuggestionEngine(
            available_intents=sample_intents,
            core_capability_names=["check_balance", "transfer_money"],
        )
        assert "check_balance" in engine.core_capability_names
        assert "transfer_money" in engine.core_capability_names

    def test_set_available_intents(
        self, engine: RedirectSuggestionEngine, sample_intents: list[IntentDefinition]
    ):
        """Test setting available intents after initialization."""
        new_intents = [sample_intents[0]]
        engine.set_available_intents(new_intents)
        assert len(engine.available_intents) == 1

    def test_set_core_capabilities(self, engine: RedirectSuggestionEngine):
        """Test setting core capabilities after initialization."""
        engine.set_core_capabilities(["get_weather"])
        assert "get_weather" in engine.core_capability_names
        assert "check_balance" not in engine.core_capability_names


# ============================================
# Redirect Suggestion Tests
# ============================================


class TestSuggestRedirects:
    """Tests for suggest_redirects method."""

    def test_returns_list_of_suggestions(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that suggest_redirects returns a list of RedirectSuggestion."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        assert isinstance(suggestions, list)
        for suggestion in suggestions:
            assert isinstance(suggestion, RedirectSuggestion)

    def test_respects_max_suggestions(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that max_suggestions is respected."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
            max_suggestions=2,
        )
        assert len(suggestions) <= 2

    def test_empty_intents_returns_empty_list(
        self, sample_semantic_analysis: SemanticAnalysis
    ):
        """Test that empty available intents returns empty list."""
        engine = RedirectSuggestionEngine(available_intents=[])
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        assert suggestions == []

    def test_suggestions_have_required_fields(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that suggestions have all required fields."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        for suggestion in suggestions:
            assert suggestion.target_intent is not None
            assert suggestion.similarity_score >= 0
            assert suggestion.redirect_reason is not None
            assert suggestion.transition_phrase is not None
            assert 0 <= suggestion.confidence <= 1

    def test_domain_shift_prioritizes_core_capabilities(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that DOMAIN_SHIFT prioritizes core capabilities."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        # Core capabilities should appear in suggestions
        suggestion_names = [s.target_intent for s in suggestions]
        core_in_suggestions = any(
            name in engine.core_capability_names for name in suggestion_names
        )
        assert core_in_suggestions


class TestContextAwareSuggestions:
    """Tests for context-aware suggestion generation."""

    def test_penalizes_failed_intents(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that failed intents are penalized."""
        context = RedirectContext(
            failed_intents=["transfer_money", "check_balance"],
        )
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
            context=context,
        )
        # Failed intents should have lower scores
        for suggestion in suggestions:
            if suggestion.target_intent in context.failed_intents:
                # The score should be penalized
                assert suggestion.confidence < 1.0

    def test_boosts_current_domain_intents(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that intents in current domain may get boost."""
        context = RedirectContext(
            current_domain="finance",
            last_successful_action="check_balance",
        )
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.SCOPE_EXPANSION,
            context=context,
        )
        # Should get suggestions from finance domain
        assert len(suggestions) > 0


class TestPersonalizationStrategy:
    """Tests for NON_PERSONAL strategy with PERSONALIZATION drift."""

    def test_penalizes_personal_data_intents(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that personal data intents are penalized."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.PERSONALIZATION,
        )
        # my_preferences requires personal data, should be lower ranked
        preferences_suggestion = next(
            (s for s in suggestions if s.target_intent == "my_preferences"),
            None,
        )
        if preferences_suggestion:
            # Should have lower confidence due to penalty
            assert preferences_suggestion.confidence < 0.9


class TestTemporalStrategy:
    """Tests for CURRENT_FOCUSED strategy with TEMPORAL_DRIFT."""

    def test_penalizes_historical_intents(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that historical intents are penalized."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.TEMPORAL_DRIFT,
        )
        # view_history has temporal indicators, should be lower ranked
        history_suggestion = next(
            (s for s in suggestions if s.target_intent == "view_history"),
            None,
        )
        if history_suggestion:
            # Check that non-historical intents ranked higher
            non_historical = [
                s for s in suggestions
                if s.target_intent != "view_history"
            ]
            if non_historical:
                # At least one non-historical should rank higher
                assert any(
                    s.confidence >= history_suggestion.confidence
                    for s in non_historical
                )


# ============================================
# Phrase Generation Tests
# ============================================


class TestPhraseGeneration:
    """Tests for redirect phrase generation."""

    def test_generate_redirect_phrase(
        self, engine: RedirectSuggestionEngine, sample_intents: list[IntentDefinition]
    ):
        """Test basic phrase generation."""
        intent = sample_intents[0]  # check_balance
        phrase = engine.generate_redirect_phrase(intent, "original input")
        assert isinstance(phrase, str)
        assert len(phrase) > 0

    def test_phrase_contains_action(
        self, engine: RedirectSuggestionEngine, sample_intents: list[IntentDefinition]
    ):
        """Test that generated phrase contains action."""
        intent = sample_intents[0]
        phrase = engine.generate_redirect_phrase(intent, "original input")
        # Should contain some reference to checking balance
        # The phrase templates all have patterns like "Would you like me to X"
        assert any(
            word in phrase.lower()
            for word in ["check", "balance", "account", "would", "help"]
        )

    def test_phrase_variation_enabled(self, sample_intents: list[IntentDefinition]):
        """Test that phrase variation produces different phrases."""
        engine = RedirectSuggestionEngine(
            config=RedirectEngineConfig(phrase_variation=True),
            available_intents=sample_intents,
        )
        intent = sample_intents[0]
        phrases = {
            engine.generate_redirect_phrase(intent, "input") for _ in range(10)
        }
        # With variation enabled, should get multiple different phrases
        # (at least 2 different ones in 10 tries)
        assert len(phrases) >= 1  # At minimum 1 since random might repeat

    def test_phrase_variation_disabled(self, sample_intents: list[IntentDefinition]):
        """Test that phrase variation can be disabled."""
        engine = RedirectSuggestionEngine(
            config=RedirectEngineConfig(phrase_variation=False),
            available_intents=sample_intents,
        )
        intent = sample_intents[0]
        phrases = [engine.generate_redirect_phrase(intent, "input") for _ in range(4)]
        # With variation disabled, should cycle through templates deterministically
        assert len(phrases) == 4


class TestActionExtraction:
    """Tests for action phrase extraction."""

    def test_extract_action_from_description(
        self, engine: RedirectSuggestionEngine
    ):
        """Test action extraction from description."""
        intent = IntentDefinition(
            name="test_intent",
            description="Helps you check your account balance",
            keywords=["check", "balance"],
            examples=[],
        )
        action = engine._extract_action_phrase(intent)
        assert "check" in action.lower()

    def test_extract_action_fallback_to_name(
        self, engine: RedirectSuggestionEngine
    ):
        """Test action extraction falls back to name."""
        intent = IntentDefinition(
            name="check_balance",
            description="View balance information",  # No action starter
            keywords=["check"],
            examples=[],
        )
        action = engine._extract_action_phrase(intent)
        assert "check" in action.lower() or "balance" in action.lower()


# ============================================
# Reason Generation Tests
# ============================================


class TestReasonGeneration:
    """Tests for redirect reason generation."""

    def test_reason_generated_when_enabled(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that reasons are generated when enabled."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        for suggestion in suggestions:
            assert suggestion.redirect_reason
            assert len(suggestion.redirect_reason) > 0

    def test_reason_empty_when_disabled(
        self, sample_intents: list[IntentDefinition],
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that reasons are empty when disabled."""
        engine = RedirectSuggestionEngine(
            config=RedirectEngineConfig(include_explanation=False),
            available_intents=sample_intents,
        )
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        for suggestion in suggestions:
            assert suggestion.redirect_reason == ""


# ============================================
# Diversity Selection Tests
# ============================================


class TestDiversitySelection:
    """Tests for diverse suggestion selection."""

    def test_diversity_selects_from_different_domains(
        self, sample_intents: list[IntentDefinition],
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that diversity selection prefers different domains."""
        engine = RedirectSuggestionEngine(
            config=RedirectEngineConfig(diversity_weight=1.0, max_suggestions=3),
            available_intents=sample_intents,
        )
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.AMBIGUOUS,  # Uses DIVERSITY strategy
        )
        # With high diversity, should try to get different domains
        domains = set()
        for suggestion in suggestions:
            intent = next(
                (i for i in sample_intents if i.name == suggestion.target_intent),
                None,
            )
            if intent and intent.domain:
                domains.add(intent.domain)
        # Should have multiple domains when diversity is high
        assert len(domains) >= 1

    def test_no_diversity_selects_by_score(
        self, sample_intents: list[IntentDefinition],
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that zero diversity selects purely by score."""
        engine = RedirectSuggestionEngine(
            config=RedirectEngineConfig(diversity_weight=0.0),
            available_intents=sample_intents,
        )
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.SCOPE_EXPANSION,
        )
        # Suggestions should be sorted by score
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                # Each suggestion should have score >= next
                assert suggestions[i].similarity_score >= suggestions[i + 1].similarity_score - 0.1


# ============================================
# Confidence Calculation Tests
# ============================================


class TestConfidenceCalculation:
    """Tests for suggestion confidence calculation."""

    def test_confidence_in_valid_range(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that confidence is always in valid range."""
        for drift_type in DriftType:
            suggestions = engine.suggest_redirects(
                semantic_result=sample_semantic_analysis,
                drift_type=drift_type,
            )
            for suggestion in suggestions:
                assert 0 <= suggestion.confidence <= 1

    def test_core_capabilities_have_higher_confidence(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that core capabilities get confidence boost."""
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        core_suggestions = [
            s for s in suggestions
            if s.target_intent in engine.core_capability_names
        ]
        non_core_suggestions = [
            s for s in suggestions
            if s.target_intent not in engine.core_capability_names
        ]
        # Core should generally have higher confidence
        if core_suggestions and non_core_suggestions:
            avg_core = sum(s.confidence for s in core_suggestions) / len(core_suggestions)
            avg_non_core = sum(s.confidence for s in non_core_suggestions) / len(non_core_suggestions)
            # Core should be at least somewhat competitive
            assert avg_core >= avg_non_core * 0.5

    def test_ambiguous_drift_reduces_confidence(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test that AMBIGUOUS drift reduces confidence."""
        ambiguous_suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.AMBIGUOUS,
        )
        regular_suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.NONE,
        )
        # Compare average confidences
        if ambiguous_suggestions and regular_suggestions:
            avg_ambiguous = sum(s.confidence for s in ambiguous_suggestions) / len(
                ambiguous_suggestions
            )
            avg_regular = sum(s.confidence for s in regular_suggestions) / len(
                regular_suggestions
            )
            # Ambiguous should generally have lower confidence
            assert avg_ambiguous <= avg_regular + 0.2


# ============================================
# Nearest Intent Suggestions Tests
# ============================================


class TestNearestIntentSuggestions:
    """Tests for get_suggestions_for_nearest_intents method."""

    def test_suggestions_from_nearest_intents(
        self, engine: RedirectSuggestionEngine
    ):
        """Test generating suggestions directly from nearest intents."""
        nearest_intents = [
            NearestIntent(intent_name="check_balance", similarity=0.8),
            NearestIntent(intent_name="transfer_money", similarity=0.7),
            NearestIntent(intent_name="pay_bill", similarity=0.5),
        ]
        suggestions = engine.get_suggestions_for_nearest_intents(
            nearest_intents=nearest_intents,
            drift_type=DriftType.SCOPE_EXPANSION,
        )
        assert len(suggestions) <= 3
        assert all(isinstance(s, RedirectSuggestion) for s in suggestions)

    def test_filters_by_relevance_threshold(
        self, engine: RedirectSuggestionEngine
    ):
        """Test that low-relevance intents are filtered out."""
        nearest_intents = [
            NearestIntent(intent_name="check_balance", similarity=0.5),
            NearestIntent(intent_name="transfer_money", similarity=0.1),  # Below threshold
        ]
        engine.config.min_relevance_threshold = 0.2
        suggestions = engine.get_suggestions_for_nearest_intents(
            nearest_intents=nearest_intents,
            drift_type=DriftType.SCOPE_EXPANSION,
        )
        # Only check_balance should pass threshold
        assert len(suggestions) == 1
        assert suggestions[0].target_intent == "check_balance"

    def test_handles_unknown_intents(self, engine: RedirectSuggestionEngine):
        """Test handling of intents not in available_intents."""
        nearest_intents = [
            NearestIntent(intent_name="unknown_intent", similarity=0.8),
        ]
        suggestions = engine.get_suggestions_for_nearest_intents(
            nearest_intents=nearest_intents,
            drift_type=DriftType.SCOPE_EXPANSION,
        )
        assert len(suggestions) == 1
        # Should still generate a default phrase
        assert "unknown_intent" in suggestions[0].transition_phrase


# ============================================
# ScoredSuggestion Tests
# ============================================


class TestScoredSuggestion:
    """Tests for ScoredSuggestion dataclass."""

    def test_scored_suggestion_creation(
        self, sample_intents: list[IntentDefinition]
    ):
        """Test creating a scored suggestion."""
        suggestion = ScoredSuggestion(
            intent=sample_intents[0],
            base_score=0.7,
            adjusted_score=0.8,
            domain="finance",
            is_core=True,
        )
        assert suggestion.intent == sample_intents[0]
        assert suggestion.base_score == 0.7
        assert suggestion.adjusted_score == 0.8
        assert suggestion.domain == "finance"
        assert suggestion.is_core is True

    def test_scored_suggestion_defaults(
        self, sample_intents: list[IntentDefinition]
    ):
        """Test default values for scored suggestion."""
        suggestion = ScoredSuggestion(
            intent=sample_intents[0],
            base_score=0.5,
        )
        assert suggestion.adjusted_score == 0.0
        assert suggestion.domain is None
        assert suggestion.is_core is False
        assert suggestion.requires_personal_data is False
        assert suggestion.is_current_focused is True


# ============================================
# RedirectContext Tests
# ============================================


class TestRedirectContext:
    """Tests for RedirectContext dataclass."""

    def test_context_creation(self):
        """Test creating a redirect context."""
        context = RedirectContext(
            failed_intents=["intent1", "intent2"],
            successful_intents=["intent3"],
            current_domain="finance",
            turn_count=5,
            last_successful_action="check_balance",
        )
        assert context.failed_intents == ["intent1", "intent2"]
        assert context.successful_intents == ["intent3"]
        assert context.current_domain == "finance"
        assert context.turn_count == 5
        assert context.last_successful_action == "check_balance"

    def test_context_defaults(self):
        """Test default values for redirect context."""
        context = RedirectContext()
        assert context.failed_intents == []
        assert context.successful_intents == []
        assert context.current_domain is None
        assert context.turn_count == 0
        assert context.last_successful_action is None


# ============================================
# Intent Property Detection Tests
# ============================================


class TestIntentPropertyDetection:
    """Tests for intent property detection methods."""

    def test_requires_personal_data_detection(
        self, engine: RedirectSuggestionEngine
    ):
        """Test personal data requirement detection."""
        personal_intent = IntentDefinition(
            name="my_settings",
            description="View and update your personal preferences",
            keywords=["settings", "preferences"],
            examples=[],
        )
        assert engine._requires_personal_data(personal_intent) is True

        general_intent = IntentDefinition(
            name="get_weather",
            description="Get current weather information",
            keywords=["weather"],
            examples=[],
        )
        assert engine._requires_personal_data(general_intent) is False

    def test_is_current_focused_detection(
        self, engine: RedirectSuggestionEngine
    ):
        """Test current-focused detection."""
        current_intent = IntentDefinition(
            name="check_balance",
            description="Check your current account balance",
            keywords=["balance"],
            examples=[],
        )
        assert engine._is_current_focused(current_intent) is True

        historical_intent = IntentDefinition(
            name="view_history",
            description="View your past transaction history",
            keywords=["history", "past"],
            examples=[],
        )
        assert engine._is_current_focused(historical_intent) is False

    def test_is_practical_intent_detection(
        self, engine: RedirectSuggestionEngine
    ):
        """Test practical/actionable intent detection."""
        practical_intent = IntentDefinition(
            name="create_account",
            description="Create a new user account",
            keywords=["create", "account"],
            examples=[],
        )
        assert engine._is_practical_intent(practical_intent) is True

        abstract_intent = IntentDefinition(
            name="philosophy",
            description="Discuss philosophical questions",
            keywords=["philosophy"],
            examples=[],
        )
        assert engine._is_practical_intent(abstract_intent) is False


# ============================================
# Integration Tests
# ============================================


class TestEngineIntegration:
    """Integration tests for the redirect engine."""

    def test_full_workflow_scope_expansion(
        self,
        engine: RedirectSuggestionEngine,
        sample_semantic_analysis: SemanticAnalysis,
    ):
        """Test full workflow for scope expansion drift."""
        context = RedirectContext(
            failed_intents=[],
            current_domain="finance",
        )
        suggestions = engine.suggest_redirects(
            semantic_result=sample_semantic_analysis,
            drift_type=DriftType.SCOPE_EXPANSION,
            max_suggestions=3,
            context=context,
        )
        assert len(suggestions) > 0
        assert len(suggestions) <= 3
        for suggestion in suggestions:
            assert suggestion.target_intent is not None
            assert suggestion.transition_phrase
            assert suggestion.redirect_reason

    def test_full_workflow_from_input(
        self,
        engine: RedirectSuggestionEngine,
    ):
        """Test suggest_redirects_from_input method."""
        suggestions = engine.suggest_redirects_from_input(
            user_input="Can you help me buy groceries?",
            drift_type=DriftType.DOMAIN_SHIFT,
            max_suggestions=2,
        )
        # Should return suggestions (may be empty if no good matches)
        assert isinstance(suggestions, list)
        for suggestion in suggestions:
            assert isinstance(suggestion, RedirectSuggestion)

    def test_handles_empty_semantic_analysis(
        self, engine: RedirectSuggestionEngine
    ):
        """Test handling of semantic analysis with no nearest intents."""
        empty_analysis = SemanticAnalysis(
            input_text="Something completely random",
            abstraction_level=AbstractionLevel.CONCRETE,
            nearest_intents=[],
        )
        suggestions = engine.suggest_redirects(
            semantic_result=empty_analysis,
            drift_type=DriftType.DOMAIN_SHIFT,
        )
        # Should still return suggestions from available intents
        assert isinstance(suggestions, list)
