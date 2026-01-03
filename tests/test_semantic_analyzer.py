"""Tests for semantic analyzer.

Issue #79 - Task 5.2: Semantic Analyzer
Part of #28 - Phase 5: Intent Drift Detection
"""

import time

import pytest

from src.intent_drift import (
    AbstractionLevel,
    DriftType,
    TemporalReferenceType,
)
from src.intent_drift.semantic_analyzer import (
    DOMAIN_SHIFT_THRESHOLD,
    IN_SCOPE_THRESHOLD,
    SCOPE_EXPANSION_MIN,
    IntentDefinition,
    SemanticAnalyzer,
    SemanticAnalyzerConfig,
    SimilarityResult,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def analyzer():
    """Create a default semantic analyzer."""
    return SemanticAnalyzer()


@pytest.fixture
def custom_config():
    """Create a custom configuration."""
    return SemanticAnalyzerConfig(
        in_scope_threshold=0.8,
        scope_expansion_min=0.5,
        domain_shift_threshold=0.2,
        top_n_intents=3,
    )


@pytest.fixture
def sample_intents():
    """Create sample intent definitions."""
    return [
        IntentDefinition(
            name="password_reset",
            description="Reset user password",
            keywords=["password", "reset", "forgot", "change"],
            examples=[
                "I forgot my password",
                "How do I reset my password?",
                "Can you help me change my password?",
            ],
            capability_id="auth.password.reset",
            domain="authentication",
        ),
        IntentDefinition(
            name="account_info",
            description="Get account information",
            keywords=["account", "info", "details", "profile"],
            examples=[
                "Show my account details",
                "What is my account information?",
                "Display my profile",
            ],
            capability_id="account.info.get",
            domain="account",
        ),
        IntentDefinition(
            name="order_status",
            description="Check order status",
            keywords=["order", "status", "tracking", "shipment"],
            examples=[
                "Where is my order?",
                "Track my shipment",
                "What is my order status?",
            ],
            capability_id="order.status.check",
            domain="orders",
        ),
    ]


@pytest.fixture
def sample_intent_dicts(sample_intents):
    """Convert sample intents to dictionaries."""
    return [
        {
            "name": intent.name,
            "description": intent.description,
            "keywords": intent.keywords,
            "examples": intent.examples,
            "capability_id": intent.capability_id,
            "domain": intent.domain,
        }
        for intent in sample_intents
    ]


@pytest.fixture
def domain_keywords():
    """Sample domain keywords."""
    return ["password", "account", "order", "user", "profile", "security"]


@pytest.fixture
def domain_keywords_map():
    """Sample domain keyword map."""
    return {
        "authentication": ["password", "login", "logout", "security", "auth"],
        "account": ["account", "profile", "user", "settings"],
        "orders": ["order", "shipment", "tracking", "delivery"],
    }


# ============================================
# Test SimilarityResult
# ============================================


class TestSimilarityResult:
    """Tests for SimilarityResult dataclass."""

    def test_create_similarity_result(self):
        """Test creating a similarity result."""
        result = SimilarityResult(
            score=0.75,
            method="cosine",
            details={"dot_product": 0.75},
        )
        assert result.score == 0.75
        assert result.method == "cosine"
        assert result.details["dot_product"] == 0.75

    def test_score_validation_too_low(self):
        """Test that score below 0 raises error."""
        with pytest.raises(ValueError, match="score must be between"):
            SimilarityResult(score=-0.1, method="test")

    def test_score_validation_too_high(self):
        """Test that score above 1 raises error."""
        with pytest.raises(ValueError, match="score must be between"):
            SimilarityResult(score=1.1, method="test")

    def test_boundary_scores(self):
        """Test boundary score values."""
        result_zero = SimilarityResult(score=0.0, method="test")
        result_one = SimilarityResult(score=1.0, method="test")
        assert result_zero.score == 0.0
        assert result_one.score == 1.0


# ============================================
# Test IntentDefinition
# ============================================


class TestIntentDefinition:
    """Tests for IntentDefinition dataclass."""

    def test_create_intent_definition(self):
        """Test creating an intent definition."""
        intent = IntentDefinition(
            name="test_intent",
            description="A test intent",
            keywords=["test", "example"],
            examples=["This is a test"],
        )
        assert intent.name == "test_intent"
        assert intent.description == "A test intent"
        assert len(intent.keywords) == 2
        assert len(intent.examples) == 1

    def test_intent_definition_defaults(self):
        """Test intent definition default values."""
        intent = IntentDefinition(name="minimal", description="Minimal intent")
        assert intent.keywords == []
        assert intent.examples == []
        assert intent.capability_id is None
        assert intent.domain is None


# ============================================
# Test SemanticAnalyzerConfig
# ============================================


class TestSemanticAnalyzerConfig:
    """Tests for SemanticAnalyzerConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SemanticAnalyzerConfig.default()
        assert config.in_scope_threshold == IN_SCOPE_THRESHOLD
        assert config.scope_expansion_min == SCOPE_EXPANSION_MIN
        assert config.domain_shift_threshold == DOMAIN_SHIFT_THRESHOLD
        assert config.top_n_intents == 5

    def test_custom_config(self, custom_config):
        """Test custom configuration."""
        assert custom_config.in_scope_threshold == 0.8
        assert custom_config.scope_expansion_min == 0.5
        assert custom_config.top_n_intents == 3

    def test_config_has_indicators(self):
        """Test that config has indicator lists."""
        config = SemanticAnalyzerConfig.default()
        assert len(config.abstraction_indicators) > 0
        assert len(config.meta_indicators) > 0
        assert len(config.philosophical_indicators) > 0


# ============================================
# Test Jaccard Similarity
# ============================================


class TestJaccardSimilarity:
    """Tests for Jaccard similarity calculation."""

    def test_identical_texts(self, analyzer):
        """Test similarity of identical texts."""
        result = analyzer.calculate_jaccard_similarity(
            "hello world", "hello world"
        )
        assert result.score == 1.0
        assert result.method == "jaccard"

    def test_completely_different_texts(self, analyzer):
        """Test similarity of completely different texts."""
        result = analyzer.calculate_jaccard_similarity(
            "apple banana cherry",
            "dog elephant frog",
        )
        assert result.score == 0.0

    def test_partial_overlap(self, analyzer):
        """Test similarity with partial overlap."""
        result = analyzer.calculate_jaccard_similarity(
            "apple banana cherry",
            "apple banana dragon",
        )
        # 2 common tokens (apple, banana), 4 total unique = 0.5
        assert result.score == pytest.approx(0.5, abs=0.1)

    def test_empty_texts(self, analyzer):
        """Test similarity of empty texts."""
        result = analyzer.calculate_jaccard_similarity("", "")
        assert result.score == 1.0

    def test_one_empty_text(self, analyzer):
        """Test similarity with one empty text."""
        result = analyzer.calculate_jaccard_similarity("hello", "")
        assert result.score == 0.0

    def test_single_word_match(self, analyzer):
        """Test single word exact match."""
        result = analyzer.calculate_jaccard_similarity("test", "test")
        assert result.score == 1.0

    def test_performance_under_5ms(self, analyzer):
        """Test that similarity calculation is under 5ms."""
        text1 = "This is a longer text with multiple words for testing"
        text2 = "Another longer text with different words for comparison"

        start = time.perf_counter()
        for _ in range(100):
            analyzer.calculate_jaccard_similarity(text1, text2)
        elapsed = (time.perf_counter() - start) / 100

        assert elapsed < 0.005  # 5ms per comparison


# ============================================
# Test Cosine Similarity
# ============================================


class TestCosineSimilarity:
    """Tests for cosine similarity calculation."""

    def test_identical_texts(self, analyzer):
        """Test similarity of identical texts."""
        result = analyzer.calculate_cosine_similarity(
            "hello world test", "hello world test"
        )
        assert result.score == pytest.approx(1.0, abs=0.01)
        assert result.method == "cosine"

    def test_completely_different_texts(self, analyzer):
        """Test similarity of completely different texts."""
        result = analyzer.calculate_cosine_similarity(
            "apple banana cherry",
            "dog elephant frog",
        )
        assert result.score == 0.0

    def test_partial_overlap(self, analyzer):
        """Test similarity with partial overlap."""
        result = analyzer.calculate_cosine_similarity(
            "reset password account",
            "password reset help",
        )
        # Should have high similarity due to common terms
        assert result.score > 0.5

    def test_empty_texts(self, analyzer):
        """Test similarity of empty texts."""
        result = analyzer.calculate_cosine_similarity("", "")
        assert result.score == 1.0

    def test_one_empty_text(self, analyzer):
        """Test similarity with one empty text."""
        result = analyzer.calculate_cosine_similarity("hello", "")
        assert result.score == 0.0

    def test_performance_under_5ms(self, analyzer):
        """Test that similarity calculation is under 5ms."""
        text1 = "This is a longer text with multiple words for testing"
        text2 = "Another longer text with different words for comparison"

        start = time.perf_counter()
        for _ in range(100):
            analyzer.calculate_cosine_similarity(text1, text2)
        elapsed = (time.perf_counter() - start) / 100

        assert elapsed < 0.005  # 5ms per comparison


# ============================================
# Test Combined Similarity
# ============================================


class TestCombinedSimilarity:
    """Tests for combined similarity calculation."""

    def test_combined_identical_texts(self, analyzer):
        """Test combined similarity of identical texts."""
        result = analyzer.calculate_combined_similarity(
            "hello world", "hello world"
        )
        assert result.score == pytest.approx(1.0, abs=0.01)
        assert result.method == "combined"

    def test_combined_has_component_scores(self, analyzer):
        """Test that combined result has component scores."""
        result = analyzer.calculate_combined_similarity(
            "password reset", "reset my password"
        )
        assert "jaccard_score" in result.details
        assert "cosine_score" in result.details
        assert "jaccard_weight" in result.details
        assert "cosine_weight" in result.details

    def test_custom_weights(self, analyzer):
        """Test custom weights in combined similarity."""
        result = analyzer.calculate_combined_similarity(
            "test text",
            "test text",
            jaccard_weight=0.8,
            cosine_weight=0.2,
        )
        assert result.details["jaccard_weight"] == 0.8
        assert result.details["cosine_weight"] == 0.2


# ============================================
# Test Abstraction Detection
# ============================================


class TestAbstractionDetection:
    """Tests for abstraction level detection."""

    def test_concrete_request(self, analyzer):
        """Test detection of concrete request."""
        level = analyzer.detect_abstraction_level("Create a new user account")
        assert level == AbstractionLevel.CONCRETE

    def test_concrete_with_action_verb(self, analyzer):
        """Test concrete detection with action verbs."""
        level = analyzer.detect_abstraction_level("Delete the file")
        assert level == AbstractionLevel.CONCRETE

    def test_philosophical_request(self, analyzer):
        """Test detection of philosophical request."""
        level = analyzer.detect_abstraction_level(
            "What is the meaning of life and consciousness?"
        )
        assert level == AbstractionLevel.PHILOSOPHICAL

    def test_abstract_request(self, analyzer):
        """Test detection of abstract request."""
        level = analyzer.detect_abstraction_level(
            "What can you do? Tell me about yourself."
        )
        assert level == AbstractionLevel.ABSTRACT

    def test_moderate_abstraction(self, analyzer):
        """Test detection of moderate abstraction."""
        level = analyzer.detect_abstraction_level(
            "Generally speaking, how does this work?"
        )
        assert level in (AbstractionLevel.MODERATE, AbstractionLevel.ABSTRACT)

    def test_meta_question(self, analyzer):
        """Test detection of meta-level questions."""
        level = analyzer.detect_abstraction_level(
            "What are your capabilities and limits?"
        )
        assert level == AbstractionLevel.ABSTRACT

    def test_abstraction_detection_accuracy(self, analyzer):
        """Test >80% accuracy for abstraction detection."""
        test_cases = [
            # (text, expected_concrete_or_moderate)
            ("Create a new file", True),
            ("Delete this account", True),
            ("Show me the dashboard", True),
            ("Reset my password", True),
            ("Send an email", True),
            ("What is the meaning of life?", False),
            ("Tell me about consciousness", False),
            ("What can you do?", False),
            ("Who made you?", False),
            ("What is reality?", False),
        ]

        correct = 0
        for text, should_be_concrete in test_cases:
            level = analyzer.detect_abstraction_level(text)
            is_concrete = level in (
                AbstractionLevel.CONCRETE,
                AbstractionLevel.MODERATE,
            )
            if is_concrete == should_be_concrete:
                correct += 1

        accuracy = correct / len(test_cases)
        assert accuracy >= 0.8  # >80% accuracy


# ============================================
# Test Temporal Reference Detection
# ============================================


class TestTemporalReferenceDetection:
    """Tests for temporal reference detection."""

    def test_detect_yesterday(self, analyzer):
        """Test detection of 'yesterday'."""
        refs = analyzer.detect_temporal_references("I ordered yesterday")
        assert len(refs) == 1
        assert refs[0].reference_type == TemporalReferenceType.PAST_RELATIVE

    def test_detect_tomorrow(self, analyzer):
        """Test detection of 'tomorrow'."""
        refs = analyzer.detect_temporal_references("Ship it tomorrow")
        assert len(refs) == 1
        assert refs[0].reference_type == TemporalReferenceType.FUTURE_RELATIVE

    def test_detect_now(self, analyzer):
        """Test detection of 'now'."""
        refs = analyzer.detect_temporal_references("I need this now")
        assert len(refs) >= 1
        present_refs = [
            r for r in refs
            if r.reference_type == TemporalReferenceType.PRESENT
        ]
        assert len(present_refs) >= 1

    def test_detect_hypothetical(self, analyzer):
        """Test detection of hypothetical references."""
        refs = analyzer.detect_temporal_references(
            "What if I ordered last week?"
        )
        hypothetical = [
            r for r in refs
            if r.reference_type == TemporalReferenceType.HYPOTHETICAL
        ]
        assert len(hypothetical) >= 1

    def test_detect_absolute_past(self, analyzer):
        """Test detection of absolute past dates."""
        refs = analyzer.detect_temporal_references(
            "In 2020, I made a purchase"
        )
        past_absolute = [
            r for r in refs
            if r.reference_type == TemporalReferenceType.PAST_ABSOLUTE
        ]
        assert len(past_absolute) >= 1

    def test_no_temporal_reference(self, analyzer):
        """Test text with no temporal reference."""
        refs = analyzer.detect_temporal_references("Reset my password")
        assert len(refs) == 0

    def test_drift_risk_calculation(self, analyzer):
        """Test that drift risk is calculated correctly."""
        refs = analyzer.detect_temporal_references("I need help now")
        present_refs = [
            r for r in refs
            if r.reference_type == TemporalReferenceType.PRESENT
        ]
        if present_refs:
            assert present_refs[0].drift_risk == 0.0

        refs = analyzer.detect_temporal_references("In 2050")
        future_refs = [
            r for r in refs
            if r.reference_type == TemporalReferenceType.FUTURE_ABSOLUTE
        ]
        if future_refs:
            assert future_refs[0].drift_risk > 0.5


# ============================================
# Test Entity Detection
# ============================================


class TestEntityDetection:
    """Tests for entity mention detection."""

    def test_detect_person_reference(self, analyzer):
        """Test detection of person references."""
        entities = analyzer.detect_entities("Show my account")
        person_entities = [e for e in entities if "my" in e.text.lower()]
        assert len(person_entities) >= 1

    def test_personalization_flag(self, analyzer):
        """Test personalization flag is set correctly."""
        entities = analyzer.detect_entities("Update my profile")
        if entities:
            person_entities = [e for e in entities if "my" in e.text.lower()]
            if person_entities:
                assert person_entities[0].requires_personalization

    def test_no_entities(self, analyzer):
        """Test text with no recognizable entities."""
        entities = analyzer.detect_entities("hello world")
        # May still detect some patterns, but should handle gracefully
        assert isinstance(entities, list)


# ============================================
# Test Domain Similarity
# ============================================


class TestDomainSimilarity:
    """Tests for domain similarity calculation."""

    def test_in_domain_text(self, analyzer, domain_keywords):
        """Test text clearly in domain."""
        similarity = analyzer.calculate_domain_similarity(
            "Reset my password for this account",
            domain_keywords,
        )
        assert similarity > 0.0

    def test_out_of_domain_text(self, analyzer, domain_keywords):
        """Test text clearly out of domain."""
        similarity = analyzer.calculate_domain_similarity(
            "What is the weather like today?",
            domain_keywords,
        )
        assert similarity < DOMAIN_SHIFT_THRESHOLD

    def test_empty_domain_keywords(self, analyzer):
        """Test with no domain keywords."""
        similarity = analyzer.calculate_domain_similarity("test text", [])
        assert similarity == 0.5  # Neutral

    def test_empty_text(self, analyzer, domain_keywords):
        """Test with empty text."""
        similarity = analyzer.calculate_domain_similarity("", domain_keywords)
        assert similarity == 0.0


# ============================================
# Test Nearest Intent Ranking
# ============================================


class TestNearestIntentRanking:
    """Tests for nearest intent ranking."""

    def test_rank_password_intent(self, analyzer, sample_intents):
        """Test ranking for password-related query."""
        intents = analyzer.rank_nearest_intents(
            "I forgot my password",
            sample_intents,
        )
        assert len(intents) > 0
        # Password reset should be top or near top
        top_intent = intents[0]
        assert top_intent.similarity > 0

    def test_returns_top_n(self, analyzer, sample_intents, custom_config):
        """Test that only top_n intents are returned."""
        analyzer_custom = SemanticAnalyzer(config=custom_config)
        intents = analyzer_custom.rank_nearest_intents(
            "test query",
            sample_intents,
        )
        assert len(intents) <= custom_config.top_n_intents

    def test_intents_sorted_by_similarity(self, analyzer, sample_intents):
        """Test that intents are sorted by similarity descending."""
        intents = analyzer.rank_nearest_intents(
            "account password order",
            sample_intents,
        )
        for i in range(len(intents) - 1):
            assert intents[i].similarity >= intents[i + 1].similarity

    def test_clarification_flag(self, analyzer, sample_intents):
        """Test clarification flag for ambiguous matches."""
        intents = analyzer.rank_nearest_intents(
            "something vague",
            sample_intents,
        )
        # Low similarity intents might need clarification
        for intent in intents:
            if (
                intent.similarity < IN_SCOPE_THRESHOLD
                and intent.similarity >= SCOPE_EXPANSION_MIN
            ):
                assert intent.requires_clarification

    def test_empty_intents(self, analyzer):
        """Test with no available intents."""
        intents = analyzer.rank_nearest_intents("test query", [])
        assert intents == []


# ============================================
# Test Drift Type Classification
# ============================================


class TestDriftTypeClassification:
    """Tests for drift type classification."""

    def test_no_drift_high_similarity(self, analyzer):
        """Test no drift for high similarity."""
        drift_type = analyzer.classify_drift_type(
            similarity_score=0.8,
            abstraction_level=AbstractionLevel.CONCRETE,
            domain_similarity=0.7,
            has_personalization_need=False,
            has_temporal_drift_risk=False,
        )
        assert drift_type == DriftType.NONE

    def test_abstraction_climb(self, analyzer):
        """Test abstraction climb detection."""
        drift_type = analyzer.classify_drift_type(
            similarity_score=0.3,
            abstraction_level=AbstractionLevel.PHILOSOPHICAL,
            domain_similarity=0.5,
            has_personalization_need=False,
            has_temporal_drift_risk=False,
        )
        assert drift_type == DriftType.ABSTRACTION_CLIMB

    def test_personalization_drift(self, analyzer):
        """Test personalization drift detection."""
        drift_type = analyzer.classify_drift_type(
            similarity_score=0.5,
            abstraction_level=AbstractionLevel.CONCRETE,
            domain_similarity=0.5,
            has_personalization_need=True,
            has_temporal_drift_risk=False,
        )
        assert drift_type == DriftType.PERSONALIZATION

    def test_temporal_drift(self, analyzer):
        """Test temporal drift detection."""
        drift_type = analyzer.classify_drift_type(
            similarity_score=0.5,
            abstraction_level=AbstractionLevel.CONCRETE,
            domain_similarity=0.5,
            has_personalization_need=False,
            has_temporal_drift_risk=True,
        )
        assert drift_type == DriftType.TEMPORAL_DRIFT

    def test_domain_shift(self, analyzer):
        """Test domain shift detection."""
        drift_type = analyzer.classify_drift_type(
            similarity_score=0.2,
            abstraction_level=AbstractionLevel.CONCRETE,
            domain_similarity=0.1,
            has_personalization_need=False,
            has_temporal_drift_risk=False,
        )
        assert drift_type == DriftType.DOMAIN_SHIFT

    def test_scope_expansion(self, analyzer):
        """Test scope expansion detection."""
        drift_type = analyzer.classify_drift_type(
            similarity_score=0.5,
            abstraction_level=AbstractionLevel.CONCRETE,
            domain_similarity=0.5,
            has_personalization_need=False,
            has_temporal_drift_risk=False,
        )
        assert drift_type == DriftType.SCOPE_EXPANSION


# ============================================
# Test Domain Classification
# ============================================


class TestDomainClassification:
    """Tests for domain classification."""

    def test_classify_authentication_domain(self, analyzer, domain_keywords_map):
        """Test classification of authentication domain."""
        domains = analyzer.classify_domains(
            "I need to reset my password",
            domain_keywords_map,
        )
        assert "authentication" in domains

    def test_classify_orders_domain(self, analyzer, domain_keywords_map):
        """Test classification of orders domain."""
        domains = analyzer.classify_domains(
            "Track my order shipment",
            domain_keywords_map,
        )
        assert "orders" in domains

    def test_classify_multiple_domains(self, analyzer, domain_keywords_map):
        """Test classification of text matching multiple domains."""
        domains = analyzer.classify_domains(
            "Check my account order status",
            domain_keywords_map,
        )
        assert len(domains) >= 2

    def test_no_domain_match(self, analyzer, domain_keywords_map):
        """Test text matching no domains."""
        domains = analyzer.classify_domains(
            "What is the weather?",
            domain_keywords_map,
        )
        assert len(domains) == 0

    def test_empty_domain_map(self, analyzer):
        """Test with empty domain map."""
        domains = analyzer.classify_domains("test text", None)
        assert domains == []


# ============================================
# Test Full Analysis
# ============================================


class TestFullAnalysis:
    """Tests for complete semantic analysis."""

    def test_analyze_password_reset(
        self, analyzer, sample_intent_dicts, domain_keywords
    ):
        """Test full analysis of password reset query."""
        result = analyzer.analyze(
            user_input="How do I reset my password?",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
        )

        assert result.input_text == "How do I reset my password?"
        assert result.abstraction_level in (
            AbstractionLevel.CONCRETE,
            AbstractionLevel.MODERATE,
        )
        assert len(result.nearest_intents) > 0

    def test_analyze_empty_input(
        self, analyzer, sample_intent_dicts, domain_keywords
    ):
        """Test analysis of empty input."""
        result = analyzer.analyze(
            user_input="",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
        )

        assert result.input_text == ""
        assert result.abstraction_level == AbstractionLevel.CONCRETE
        assert result.nearest_intents == []

    def test_analyze_whitespace_input(
        self, analyzer, sample_intent_dicts, domain_keywords
    ):
        """Test analysis of whitespace-only input."""
        result = analyzer.analyze(
            user_input="   ",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
        )

        assert result.nearest_intents == []

    def test_analyze_single_word(
        self, analyzer, sample_intent_dicts, domain_keywords
    ):
        """Test analysis of single word input."""
        result = analyzer.analyze(
            user_input="password",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
        )

        assert len(result.nearest_intents) > 0

    def test_analyze_philosophical_query(
        self, analyzer, sample_intent_dicts, domain_keywords
    ):
        """Test analysis of philosophical query."""
        result = analyzer.analyze(
            user_input="What is the meaning of life?",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
        )

        assert result.abstraction_level == AbstractionLevel.PHILOSOPHICAL

    def test_analyze_with_temporal_reference(
        self, analyzer, sample_intent_dicts, domain_keywords
    ):
        """Test analysis including temporal references."""
        result = analyzer.analyze(
            user_input="Check my order from yesterday",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
        )

        assert len(result.temporal_references) > 0

    def test_analyze_with_domain_map(
        self, analyzer, sample_intent_dicts, domain_keywords, domain_keywords_map
    ):
        """Test analysis with domain keyword map."""
        result = analyzer.analyze(
            user_input="Reset my password",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
            domain_keywords_map=domain_keywords_map,
        )

        assert "authentication" in result.domain_classification


# ============================================
# Test Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_special_characters(self, analyzer):
        """Test handling of special characters."""
        result = analyzer.calculate_jaccard_similarity(
            "Hello!!! @#$%",
            "Hello??? &*()",
        )
        # Should still find "Hello" as common
        assert result.score > 0

    def test_unicode_text(self, analyzer):
        """Test handling of unicode text."""
        result = analyzer.calculate_jaccard_similarity(
            "café résumé",
            "cafe resume",
        )
        # May not match perfectly due to accents
        assert isinstance(result.score, float)

    def test_very_long_text(self, analyzer):
        """Test handling of very long text."""
        long_text = " ".join(["word"] * 1000)
        result = analyzer.calculate_combined_similarity(long_text, long_text)
        assert result.score == pytest.approx(1.0, abs=0.01)

    def test_numbers_in_text(self, analyzer):
        """Test handling of numbers in text."""
        result = analyzer.calculate_jaccard_similarity(
            "Order 12345",
            "Order 67890",
        )
        # "Order" should match
        assert result.score > 0

    def test_mixed_case(self, analyzer):
        """Test case insensitivity."""
        result = analyzer.calculate_jaccard_similarity(
            "HELLO WORLD",
            "hello world",
        )
        assert result.score == 1.0

    def test_none_input_handling(self, analyzer, sample_intent_dicts, domain_keywords):
        """Test handling of None input (should handle gracefully)."""
        # The analyze method should handle empty string
        result = analyzer.analyze(
            user_input="",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
        )
        assert result.input_text == ""


# ============================================
# Test Threshold Constants
# ============================================


class TestThresholds:
    """Tests for threshold constants."""

    def test_threshold_values(self):
        """Test threshold values are as expected."""
        assert IN_SCOPE_THRESHOLD == 0.7
        assert SCOPE_EXPANSION_MIN == 0.4
        assert DOMAIN_SHIFT_THRESHOLD == 0.3

    def test_threshold_ordering(self):
        """Test thresholds are in correct order."""
        assert IN_SCOPE_THRESHOLD > SCOPE_EXPANSION_MIN
        assert SCOPE_EXPANSION_MIN > DOMAIN_SHIFT_THRESHOLD


# ============================================
# Test Integration
# ============================================


class TestIntegration:
    """Integration tests for semantic analyzer."""

    def test_full_workflow(
        self, analyzer, sample_intent_dicts, domain_keywords, domain_keywords_map
    ):
        """Test complete analysis workflow."""
        # Simulate a user asking about password reset
        result = analyzer.analyze(
            user_input="I forgot my password and need help resetting it",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
            domain_keywords_map=domain_keywords_map,
        )

        # Should have analysis results
        assert result.input_text
        assert result.abstraction_level == AbstractionLevel.CONCRETE
        assert len(result.nearest_intents) > 0

        # Top intent should be password-related
        top_intent = result.nearest_intents[0]
        assert "password" in top_intent.intent_name.lower()

        # Should classify as authentication domain
        assert "authentication" in result.domain_classification

    def test_out_of_domain_workflow(
        self, analyzer, sample_intent_dicts, domain_keywords, domain_keywords_map
    ):
        """Test analysis of out-of-domain query."""
        result = analyzer.analyze(
            user_input="What is the capital of France?",
            available_intents=sample_intent_dicts,
            domain_keywords=domain_keywords,
            domain_keywords_map=domain_keywords_map,
        )

        # Should have low similarity to all intents
        if result.nearest_intents:
            top_similarity = result.nearest_intents[0].similarity
            assert top_similarity < IN_SCOPE_THRESHOLD

        # Should not match any domain
        assert len(result.domain_classification) == 0
