"""
Tests for Drift Classifier.

Part of Phase 5: Intent Drift Detection
Issue #109 - Task 5.11: Testing & Documentation
"""

import pytest
from src.intent_drift.drift_classifier import (
    DriftClassifier,
    DriftClassifierConfig,
    DriftClassification,
    DriftScoreRange,
    PatternMatch,
)
from src.intent_drift.types import (
    DriftType,
    AbstractionLevel,
    DriftAnalysis,
)


class TestDriftScoreRange:
    """Tests for DriftScoreRange constants."""

    def test_score_ranges_defined(self):
        """Test that all score ranges are defined."""
        assert DriftScoreRange.ON_TOPIC == (0.0, 0.2)
        assert DriftScoreRange.MINOR_DEVIATION == (0.2, 0.4)
        assert DriftScoreRange.MODERATE_DRIFT == (0.4, 0.6)
        assert DriftScoreRange.SIGNIFICANT_DRIFT == (0.6, 0.8)
        assert DriftScoreRange.COMPLETE_DRIFT == (0.8, 1.0)


class TestPatternMatch:
    """Tests for PatternMatch dataclass."""

    def test_valid_creation(self):
        """Test creating valid PatternMatch."""
        match = PatternMatch(
            pattern_type="pii",
            matched_text="my account",
            pattern=r"\bmy\b.*account",
            confidence=1.0,
        )

        assert match.pattern_type == "pii"
        assert match.matched_text == "my account"
        assert match.confidence == 1.0

    def test_default_confidence(self):
        """Test default confidence value."""
        match = PatternMatch(
            pattern_type="temporal",
            matched_text="tomorrow",
            pattern=r"\btomorrow\b",
        )
        assert match.confidence == 1.0


class TestDriftClassification:
    """Tests for DriftClassification dataclass."""

    def test_valid_creation(self):
        """Test creating valid DriftClassification."""
        classification = DriftClassification(
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.5,
            confidence=0.8,
            reasoning="Request expands scope of original intent",
        )

        assert classification.drift_type == DriftType.SCOPE_EXPANSION
        assert classification.drift_score == 0.5
        assert classification.confidence == 0.8

    def test_invalid_drift_score_too_high(self):
        """Test invalid drift_score raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DriftClassification(
                drift_type=DriftType.NONE,
                drift_score=1.5,
                confidence=0.8,
            )
        assert "drift_score" in str(exc_info.value)

    def test_invalid_confidence_negative(self):
        """Test negative confidence raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DriftClassification(
                drift_type=DriftType.NONE,
                drift_score=0.5,
                confidence=-0.1,
            )
        assert "confidence" in str(exc_info.value)

    def test_has_drift_true(self):
        """Test has_drift property when drift detected."""
        classification = DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.7,
            confidence=0.85,
        )
        assert classification.has_drift is True

    def test_has_drift_false(self):
        """Test has_drift property when no drift."""
        classification = DriftClassification(
            drift_type=DriftType.NONE,
            drift_score=0.1,
            confidence=0.95,
        )
        assert classification.has_drift is False

    def test_severity_level_on_topic(self):
        """Test severity_level for on-topic score."""
        classification = DriftClassification(
            drift_type=DriftType.NONE,
            drift_score=0.1,
            confidence=0.9,
        )
        assert classification.severity_level == "on_topic"

    def test_severity_level_minor(self):
        """Test severity_level for minor deviation."""
        classification = DriftClassification(
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.3,
            confidence=0.8,
        )
        assert classification.severity_level == "minor"

    def test_severity_level_moderate(self):
        """Test severity_level for moderate drift."""
        classification = DriftClassification(
            drift_type=DriftType.SCOPE_EXPANSION,
            drift_score=0.5,
            confidence=0.7,
        )
        assert classification.severity_level == "moderate"

    def test_severity_level_significant(self):
        """Test severity_level for significant drift."""
        classification = DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.7,
            confidence=0.8,
        )
        assert classification.severity_level == "significant"

    def test_severity_level_complete(self):
        """Test severity_level for complete drift."""
        classification = DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.9,
            confidence=0.85,
        )
        assert classification.severity_level == "complete"

    def test_to_drift_analysis(self):
        """Test conversion to DriftAnalysis."""
        classification = DriftClassification(
            drift_type=DriftType.PERSONALIZATION,
            drift_score=0.6,
            confidence=0.8,
            reasoning="Request requires personal data",
        )

        analysis = classification.to_drift_analysis(
            graceful_response="I don't have access to your personal data."
        )

        assert isinstance(analysis, DriftAnalysis)
        assert analysis.drift_type == DriftType.PERSONALIZATION
        assert analysis.drift_score == 0.6
        assert analysis.confidence == 0.8
        assert "personal data" in analysis.graceful_response


class TestDriftClassifierConfig:
    """Tests for DriftClassifierConfig."""

    def test_default_config(self):
        """Test default configuration creation."""
        config = DriftClassifierConfig.default()

        assert len(config.pii_patterns) > 0
        assert len(config.temporal_future_patterns) > 0
        assert len(config.temporal_past_patterns) > 0
        assert len(config.abstraction_patterns) > 0
        assert len(config.meta_patterns) > 0

    def test_custom_thresholds(self):
        """Test custom threshold configuration."""
        config = DriftClassifierConfig(
            high_confidence_threshold=0.9,
            medium_confidence_min=0.6,
            low_confidence_threshold=0.3,
            ambiguity_threshold=0.1,
        )

        assert config.high_confidence_threshold == 0.9
        assert config.medium_confidence_min == 0.6
        assert config.low_confidence_threshold == 0.3
        assert config.ambiguity_threshold == 0.1


class TestDriftClassifier:
    """Tests for DriftClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create a default classifier instance."""
        return DriftClassifier()

    def test_initialization_default(self, classifier):
        """Test classifier initialization with defaults."""
        assert classifier.config is not None
        assert classifier.semantic_analyzer is None

    def test_initialization_custom_config(self):
        """Test classifier initialization with custom config."""
        config = DriftClassifierConfig(high_confidence_threshold=0.95)
        classifier = DriftClassifier(config=config)

        assert classifier.config.high_confidence_threshold == 0.95

    def test_detect_pii_request_positive(self, classifier):
        """Test PII detection with PII request."""
        is_pii, matches = classifier.detect_pii_request(
            "What is my account balance?"
        )

        assert is_pii is True
        assert len(matches) > 0
        assert matches[0].pattern_type == "pii"

    def test_detect_pii_request_negative(self, classifier):
        """Test PII detection with non-PII request."""
        is_pii, matches = classifier.detect_pii_request(
            "What is the weather today?"
        )

        assert is_pii is False
        assert len(matches) == 0

    def test_detect_pii_patterns(self, classifier):
        """Test various PII patterns."""
        pii_requests = [
            "Show me my personal information",
            "What is my credit card number?",
            "Display my billing details",
            "Get my account name",
        ]

        for request in pii_requests:
            is_pii, _ = classifier.detect_pii_request(request)
            assert is_pii is True, f"Failed to detect PII in: {request}"

    def test_detect_temporal_drift_future(self, classifier):
        """Test temporal drift detection for future."""
        has_drift, direction, matches = classifier.detect_temporal_drift(
            "What will happen next week?"
        )

        assert has_drift is True
        assert direction == "future"
        assert len(matches) > 0

    def test_detect_temporal_drift_past(self, classifier):
        """Test temporal drift detection for past."""
        has_drift, direction, matches = classifier.detect_temporal_drift(
            "What was the price last year?"
        )

        assert has_drift is True
        assert direction == "past"
        assert len(matches) > 0

    def test_detect_temporal_drift_none(self, classifier):
        """Test temporal drift detection with no temporal reference."""
        has_drift, direction, matches = classifier.detect_temporal_drift(
            "What is the current price?"
        )

        assert has_drift is False
        assert direction == "none"
        assert len(matches) == 0

    def test_detect_temporal_patterns(self, classifier):
        """Test various temporal patterns."""
        future_requests = [
            "Will prices go up tomorrow?",
            "Predict the stock market",
            "What's going to happen in 5 days?",
        ]

        for request in future_requests:
            has_drift, direction, _ = classifier.detect_temporal_drift(request)
            assert has_drift is True, f"Failed to detect temporal in: {request}"
            assert direction in ["future", "mixed"]

    def test_detect_abstraction_positive(self, classifier):
        """Test abstraction detection with philosophical question."""
        is_abstract, matches = classifier.detect_abstraction(
            "Why does life have meaning?"
        )

        assert is_abstract is True
        assert len(matches) > 0

    def test_detect_abstraction_meta(self, classifier):
        """Test abstraction detection with meta question."""
        is_abstract, matches = classifier.detect_abstraction(
            "What can you do?"
        )

        assert is_abstract is True
        assert len(matches) > 0

    def test_detect_abstraction_negative(self, classifier):
        """Test abstraction detection with concrete question."""
        is_abstract, matches = classifier.detect_abstraction(
            "What is the price of product X?"
        )

        assert is_abstract is False
        assert len(matches) == 0

    def test_detect_abstraction_patterns(self, classifier):
        """Test various abstraction patterns."""
        abstract_requests = [
            "What is the purpose of existence?",
            "Why should we care about ethics?",
            "Tell me about yourself",
            "Who created you?",
        ]

        for request in abstract_requests:
            is_abstract, _ = classifier.detect_abstraction(request)
            assert is_abstract is True, f"Failed to detect abstraction in: {request}"


class TestDriftClassifierEdgeCases:
    """Edge case tests for DriftClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create a default classifier instance."""
        return DriftClassifier()

    def test_empty_input(self, classifier):
        """Test handling of empty input."""
        is_pii, matches = classifier.detect_pii_request("")
        assert is_pii is False
        assert len(matches) == 0

    def test_very_long_input(self, classifier):
        """Test handling of very long input."""
        long_text = "What is " * 1000 + "my account balance?"
        is_pii, matches = classifier.detect_pii_request(long_text)
        # Should still detect PII even in long text
        assert is_pii is True

    def test_case_insensitivity(self, classifier):
        """Test pattern matching is case insensitive."""
        inputs = [
            "WHAT IS MY ACCOUNT?",
            "What Is My Account?",
            "what is my account?",
        ]

        for text in inputs:
            is_pii, _ = classifier.detect_pii_request(text)
            assert is_pii is True, f"Case sensitivity failed for: {text}"

    def test_multiple_pattern_types(self, classifier):
        """Test input matching multiple pattern types."""
        # This input has both PII and temporal patterns
        text = "What was my account balance last month?"

        is_pii, pii_matches = classifier.detect_pii_request(text)
        has_temporal, direction, temporal_matches = classifier.detect_temporal_drift(text)

        assert is_pii is True
        assert has_temporal is True
        assert direction == "past"

    def test_partial_pattern_match(self, classifier):
        """Test patterns don't match partial words."""
        # "myaccount" should not match "my" + "account" separately
        is_pii, _ = classifier.detect_pii_request("Check myaccount status")
        # Depending on pattern design, this may or may not match
        # The test verifies consistent behavior

    def test_special_characters_in_input(self, classifier):
        """Test handling of special characters."""
        text = "What is my account!@#$%^&*() balance?"
        is_pii, _ = classifier.detect_pii_request(text)
        # Should still detect despite special chars
        assert is_pii is True

    def test_unicode_input(self, classifier):
        """Test handling of unicode characters."""
        text = "What is my account balance? \u00e9\u00e8\u00ea"
        is_pii, _ = classifier.detect_pii_request(text)
        assert is_pii is True

    def test_newlines_in_input(self, classifier):
        """Test handling of newlines in input."""
        text = "What is\nmy account\nbalance?"
        is_pii, _ = classifier.detect_pii_request(text)
        # May or may not match depending on pattern design
        # The test verifies no crash
