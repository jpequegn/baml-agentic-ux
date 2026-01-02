"""Comprehensive tests for jargon detection and simplification.

Issue #71 - Task 4.5: Jargon Detection & Simplification
Part of #27 - Phase 4: LUI Accessibility Standards
"""

import pytest

from src.accessibility.jargon import (
    ABBREVIATION_DB,
    TECHNICAL_JARGON_DB,
    JargonCategory,
    JargonDetector,
    JargonTerm,
    SimplificationResult,
)


# ============================================
# JargonCategory Tests
# ============================================


class TestJargonCategory:
    """Tests for JargonCategory enum."""

    def test_all_categories_exist(self):
        """Verify all expected categories exist."""
        expected = [
            "TECHNICAL",
            "BUSINESS",
            "LEGAL",
            "ACADEMIC",
            "MEDICAL",
            "ABBREVIATION",
            "GENERAL",
        ]
        for cat in expected:
            assert hasattr(JargonCategory, cat)

    def test_category_values(self):
        """Check category values are lowercase strings."""
        assert JargonCategory.TECHNICAL.value == "technical"
        assert JargonCategory.BUSINESS.value == "business"
        assert JargonCategory.ABBREVIATION.value == "abbreviation"


# ============================================
# JargonTerm Tests
# ============================================


class TestJargonTerm:
    """Tests for JargonTerm dataclass."""

    def test_basic_creation(self):
        """Test creating a basic JargonTerm."""
        term = JargonTerm(
            term="authenticate",
            context="Please authenticate before proceeding",
        )
        assert term.term == "authenticate"
        assert term.context == "Please authenticate before proceeding"
        assert term.definition is None
        assert term.simple_alternative is None
        assert term.category == JargonCategory.GENERAL
        assert term.position == 0

    def test_full_creation(self):
        """Test creating a fully specified JargonTerm."""
        term = JargonTerm(
            term="authenticate",
            context="Please authenticate",
            definition="Verify identity",
            simple_alternative="log in",
            category=JargonCategory.TECHNICAL,
            position=7,
        )
        assert term.term == "authenticate"
        assert term.definition == "Verify identity"
        assert term.simple_alternative == "log in"
        assert term.category == JargonCategory.TECHNICAL
        assert term.position == 7

    def test_equality(self):
        """Test JargonTerm equality comparison."""
        term1 = JargonTerm(term="API", context="test", position=0)
        term2 = JargonTerm(term="api", context="other", position=0)
        term3 = JargonTerm(term="API", context="test", position=10)

        # Same term (case-insensitive) and position
        assert term1 == term2
        # Different position
        assert term1 != term3

    def test_hash(self):
        """Test JargonTerm hashing for set usage."""
        term1 = JargonTerm(term="API", context="test", position=0)
        term2 = JargonTerm(term="api", context="other", position=0)

        # Should hash the same
        assert hash(term1) == hash(term2)

        # Can be used in sets
        terms = {term1, term2}
        assert len(terms) == 1


# ============================================
# SimplificationResult Tests
# ============================================


class TestSimplificationResult:
    """Tests for SimplificationResult dataclass."""

    def test_default_values(self):
        """Test default values for SimplificationResult."""
        result = SimplificationResult(
            original_text="Hello",
            simplified_text="Hello",
        )
        assert result.changes_made == []
        assert result.terms_replaced == 0
        assert result.confidence == 1.0

    def test_with_changes(self):
        """Test SimplificationResult with changes."""
        result = SimplificationResult(
            original_text="Please authenticate",
            simplified_text="Please log in",
            changes_made=["'authenticate' -> 'log in'"],
            terms_replaced=1,
            confidence=0.95,
        )
        assert len(result.changes_made) == 1
        assert result.terms_replaced == 1
        assert result.confidence == 0.95


# ============================================
# Database Tests
# ============================================


class TestJargonDatabases:
    """Tests for jargon databases."""

    def test_technical_db_structure(self):
        """Verify technical database entries have required fields."""
        for term, info in TECHNICAL_JARGON_DB.items():
            assert isinstance(term, str), f"Term {term} is not a string"
            assert "simple" in info, f"Term {term} missing 'simple'"
            assert "category" in info, f"Term {term} missing 'category'"

    def test_abbreviation_db_structure(self):
        """Verify abbreviation database entries have required fields."""
        for abbr, info in ABBREVIATION_DB.items():
            assert isinstance(abbr, str), f"Abbreviation {abbr} is not a string"
            assert "definition" in info, f"Abbreviation {abbr} missing 'definition'"
            assert "simple" in info, f"Abbreviation {abbr} missing 'simple'"

    def test_common_technical_terms_exist(self):
        """Check that common technical terms are in the database."""
        expected_terms = [
            "authenticate",
            "endpoint",
            "parameter",
            "configure",
            "token",
        ]
        for term in expected_terms:
            assert term in TECHNICAL_JARGON_DB, f"Missing term: {term}"

    def test_common_business_terms_exist(self):
        """Check that common business jargon is in the database."""
        expected = ["leverage", "utilize", "optimize", "synergy"]
        for term in expected:
            assert term in TECHNICAL_JARGON_DB, f"Missing term: {term}"

    def test_common_abbreviations_exist(self):
        """Check that common abbreviations are in the database."""
        expected = ["API", "SDK", "URL", "JSON"]
        for abbr in expected:
            assert abbr in ABBREVIATION_DB, f"Missing abbreviation: {abbr}"


# ============================================
# JargonDetector Basic Tests
# ============================================


class TestJargonDetectorBasics:
    """Basic tests for JargonDetector."""

    def test_default_initialization(self):
        """Test default detector initialization."""
        detector = JargonDetector()
        assert detector.term_count > 0
        assert detector._include_abbreviations is True
        assert detector._categories is None

    def test_without_abbreviations(self):
        """Test detector without abbreviations."""
        detector = JargonDetector(include_abbreviations=False)
        # Should not include abbreviations
        terms = detector.detect("The API is ready")
        assert not any(t.term == "API" for t in terms)

    def test_with_category_filter(self):
        """Test detector with category filter."""
        detector = JargonDetector(categories=[JargonCategory.BUSINESS])
        assert detector.term_count > 0
        # All terms should be business category
        for term, info in detector._database.items():
            assert info.get("category") == JargonCategory.BUSINESS

    def test_with_custom_terms(self):
        """Test detector with custom terms."""
        custom = {
            "frobulate": {
                "definition": "Custom action",
                "simple": "do the thing",
                "category": JargonCategory.GENERAL,
            }
        }
        detector = JargonDetector(custom_terms=custom)
        terms = detector.detect("Please frobulate the widget")
        assert any(t.term == "frobulate" for t in terms)


# ============================================
# JargonDetector.detect() Tests
# ============================================


class TestJargonDetectorDetect:
    """Tests for JargonDetector.detect() method."""

    @pytest.fixture
    def detector(self):
        """Create a default detector."""
        return JargonDetector()

    def test_detect_empty_text(self, detector):
        """Test detecting in empty text."""
        assert detector.detect("") == []
        assert detector.detect("   ") == []
        assert detector.detect(None) == []

    def test_detect_no_jargon(self, detector):
        """Test text with no jargon."""
        text = "The cat sat on the mat."
        terms = detector.detect(text)
        assert len(terms) == 0

    def test_detect_single_term(self, detector):
        """Test detecting a single jargon term."""
        text = "Please authenticate to continue."
        terms = detector.detect(text)
        assert len(terms) == 1
        assert terms[0].term.lower() == "authenticate"
        assert terms[0].simple_alternative is not None
        assert terms[0].category == JargonCategory.TECHNICAL

    def test_detect_multiple_terms(self, detector):
        """Test detecting multiple jargon terms."""
        text = "Please authenticate before accessing the endpoint."
        terms = detector.detect(text)
        term_names = [t.term.lower() for t in terms]
        assert "authenticate" in term_names
        assert "endpoint" in term_names

    def test_detect_case_insensitive(self, detector):
        """Test that detection is case-insensitive."""
        text = "AUTHENTICATE with your CREDENTIALS"
        terms = detector.detect(text)
        term_names = [t.term.lower() for t in terms]
        assert "authenticate" in term_names
        assert "credentials" in term_names

    def test_detect_preserves_original_case(self, detector):
        """Test that detected terms preserve original case."""
        text = "AUTHENTICATE with your credentials"
        terms = detector.detect(text)
        # Should preserve original casing
        found_auth = next(t for t in terms if t.term.lower() == "authenticate")
        assert found_auth.term == "AUTHENTICATE"

    def test_detect_with_context(self, detector):
        """Test that context is captured correctly."""
        text = "You must authenticate before proceeding with the request."
        terms = detector.detect(text)
        assert len(terms) >= 1
        auth_term = next(t for t in terms if t.term.lower() == "authenticate")
        assert "must" in auth_term.context.lower()
        assert "before" in auth_term.context.lower()

    def test_detect_abbreviations(self, detector):
        """Test detecting abbreviations."""
        text = "The API returns JSON data."
        terms = detector.detect(text)
        term_names = [t.term for t in terms]
        assert "API" in term_names
        assert "JSON" in term_names

    def test_detect_position_tracking(self, detector):
        """Test that positions are correctly tracked."""
        text = "The endpoint is here and the other endpoint is there."
        terms = detector.detect(text)
        # Should find 'endpoint' twice at different positions
        endpoints = [t for t in terms if t.term.lower() == "endpoint"]
        assert len(endpoints) == 2
        assert endpoints[0].position < endpoints[1].position

    def test_detect_sorted_by_position(self, detector):
        """Test that results are sorted by position."""
        text = "The endpoint needs authentication with proper credentials."
        terms = detector.detect(text)
        positions = [t.position for t in terms]
        assert positions == sorted(positions)

    def test_detect_no_duplicates(self, detector):
        """Test that duplicate detections are removed."""
        text = "Please authenticate to authenticate."
        terms = detector.detect(text)
        # Should find 'authenticate' twice at different positions
        auth_terms = [t for t in terms if t.term.lower() == "authenticate"]
        assert len(auth_terms) == 2
        assert auth_terms[0].position != auth_terms[1].position

    def test_detect_business_jargon(self, detector):
        """Test detecting business jargon."""
        text = "We need to leverage synergy to optimize our deliverables."
        terms = detector.detect(text)
        term_names = [t.term.lower() for t in terms]
        assert "leverage" in term_names
        assert "synergy" in term_names
        assert "optimize" in term_names

    def test_detect_academic_jargon(self, detector):
        """Test detecting academic jargon."""
        text = "This necessitates a comprehensive methodology to facilitate research."
        terms = detector.detect(text)
        term_names = [t.term.lower() for t in terms]
        assert "necessitates" in term_names
        assert "methodology" in term_names
        assert "facilitate" in term_names


# ============================================
# JargonDetector.suggest_replacements() Tests
# ============================================


class TestJargonDetectorSuggestReplacements:
    """Tests for JargonDetector.suggest_replacements() method."""

    @pytest.fixture
    def detector(self):
        """Create a default detector."""
        return JargonDetector()

    def test_replace_empty_text(self, detector):
        """Test replacing in empty text."""
        assert detector.suggest_replacements("") == ""
        assert detector.suggest_replacements("   ") == "   "

    def test_replace_no_jargon(self, detector):
        """Test text with no jargon remains unchanged."""
        text = "The cat sat on the mat."
        result = detector.suggest_replacements(text)
        assert result == text

    def test_replace_single_term(self, detector):
        """Test replacing a single term."""
        text = "Please authenticate to continue."
        result = detector.suggest_replacements(text)
        assert "authenticate" not in result.lower()
        assert "verify your identity" in result.lower() or "log in" in result.lower()

    def test_replace_preserves_case_lowercase(self, detector):
        """Test that lowercase is preserved."""
        text = "Please utilize this tool."
        result = detector.suggest_replacements(text)
        # 'use' should be lowercase
        assert "use" in result
        assert "USE" not in result

    def test_replace_preserves_case_uppercase(self, detector):
        """Test that uppercase is preserved."""
        text = "UTILIZE this tool."
        result = detector.suggest_replacements(text)
        # Should be 'USE' in uppercase
        assert "USE" in result

    def test_replace_preserves_case_titlecase(self, detector):
        """Test that title case is preserved."""
        text = "Utilize this tool."
        result = detector.suggest_replacements(text)
        # Should be 'Use' with capital U
        assert result.startswith("Use")

    def test_replace_multiple_terms(self, detector):
        """Test replacing multiple terms."""
        text = "Please authenticate before accessing the endpoint."
        result = detector.suggest_replacements(text)
        assert "authenticate" not in result.lower()
        assert "endpoint" not in result.lower()

    def test_replace_expected_output(self, detector):
        """Test specific expected replacement."""
        text = "Please authenticate before accessing the endpoint."
        result = detector.suggest_replacements(text)
        # Should become something like:
        # "Please verify your identity before accessing the connection point."
        assert "authenticate" not in result.lower()
        assert "endpoint" not in result.lower()

    def test_replace_business_jargon(self, detector):
        """Test replacing business jargon."""
        text = "We need to leverage our resources."
        result = detector.suggest_replacements(text)
        assert "leverage" not in result.lower()
        assert "use" in result.lower()


# ============================================
# JargonDetector.simplify() Tests
# ============================================


class TestJargonDetectorSimplify:
    """Tests for JargonDetector.simplify() method."""

    @pytest.fixture
    def detector(self):
        """Create a default detector."""
        return JargonDetector()

    def test_simplify_empty_text(self, detector):
        """Test simplifying empty text."""
        result = detector.simplify("")
        assert isinstance(result, SimplificationResult)
        assert result.original_text == ""
        assert result.simplified_text == ""
        assert result.terms_replaced == 0

    def test_simplify_no_jargon(self, detector):
        """Test simplifying text with no jargon."""
        text = "The cat sat on the mat."
        result = detector.simplify(text)
        assert result.original_text == text
        assert result.simplified_text == text
        assert result.terms_replaced == 0
        assert result.changes_made == []

    def test_simplify_returns_result_object(self, detector):
        """Test that simplify returns a SimplificationResult."""
        result = detector.simplify("Please authenticate.")
        assert isinstance(result, SimplificationResult)

    def test_simplify_tracks_changes(self, detector):
        """Test that changes are tracked."""
        text = "Please authenticate before accessing the endpoint."
        result = detector.simplify(text)
        assert result.terms_replaced >= 2
        assert len(result.changes_made) >= 2

    def test_simplify_confidence_high_for_few_changes(self, detector):
        """Test confidence is high for few replacements."""
        text = "Please authenticate."
        result = detector.simplify(text)
        assert result.confidence >= 0.9

    def test_simplify_confidence_lower_for_many_changes(self, detector):
        """Test confidence drops for many replacements."""
        # Text with many jargon terms
        text = (
            "Please authenticate before accessing the endpoint. "
            "Configure the parameters and validate the token. "
            "The callback will facilitate the optimization."
        )
        result = detector.simplify(text)
        assert result.terms_replaced >= 5
        assert result.confidence < 1.0


# ============================================
# JargonDetector Lookup Methods Tests
# ============================================


class TestJargonDetectorLookups:
    """Tests for JargonDetector lookup methods."""

    @pytest.fixture
    def detector(self):
        """Create a default detector."""
        return JargonDetector()

    def test_get_definition_found(self, detector):
        """Test getting a definition for a known term."""
        definition = detector.get_definition("authenticate")
        assert definition is not None
        assert len(definition) > 0

    def test_get_definition_not_found(self, detector):
        """Test getting a definition for an unknown term."""
        definition = detector.get_definition("nonexistentterm123")
        assert definition is None

    def test_get_definition_case_insensitive(self, detector):
        """Test that definition lookup is case-insensitive."""
        def1 = detector.get_definition("authenticate")
        def2 = detector.get_definition("AUTHENTICATE")
        assert def1 == def2

    def test_get_alternatives_found(self, detector):
        """Test getting alternatives for a known term."""
        alternatives = detector.get_alternatives("authenticate")
        assert len(alternatives) > 0
        assert isinstance(alternatives, list)

    def test_get_alternatives_not_found(self, detector):
        """Test getting alternatives for an unknown term."""
        alternatives = detector.get_alternatives("nonexistentterm123")
        assert alternatives == []

    def test_get_alternatives_includes_simple(self, detector):
        """Test that alternatives include the simple replacement."""
        alternatives = detector.get_alternatives("authenticate")
        # Should include the simple alternative
        assert any("verify" in alt.lower() or "log" in alt.lower() for alt in alternatives)

    def test_get_alternatives_no_duplicates(self, detector):
        """Test that alternatives don't contain duplicates."""
        alternatives = detector.get_alternatives("authenticate")
        assert len(alternatives) == len(set(alternatives))


# ============================================
# JargonDetector Add/Remove Terms Tests
# ============================================


class TestJargonDetectorAddRemove:
    """Tests for JargonDetector add/remove methods."""

    def test_add_term_basic(self):
        """Test adding a basic term."""
        detector = JargonDetector()
        initial_count = detector.term_count
        detector.add_term("frobulate", "do stuff")
        assert detector.term_count == initial_count + 1

    def test_add_term_with_all_fields(self):
        """Test adding a term with all fields."""
        detector = JargonDetector()
        detector.add_term(
            term="frobulate",
            simple="do stuff",
            definition="A custom action",
            category=JargonCategory.TECHNICAL,
            alternatives=["act", "perform"],
        )
        terms = detector.detect("Please frobulate the widget.")
        assert len(terms) == 1
        assert terms[0].simple_alternative == "do stuff"
        assert terms[0].category == JargonCategory.TECHNICAL

    def test_add_term_is_detected(self):
        """Test that added terms are detected."""
        detector = JargonDetector()
        detector.add_term("grokify", "understand deeply")
        terms = detector.detect("We need to grokify this concept.")
        assert len(terms) == 1
        assert terms[0].term == "grokify"

    def test_remove_term_exists(self):
        """Test removing an existing term."""
        detector = JargonDetector()
        initial_count = detector.term_count
        result = detector.remove_term("authenticate")
        assert result is True
        assert detector.term_count == initial_count - 1

    def test_remove_term_not_found(self):
        """Test removing a non-existent term."""
        detector = JargonDetector()
        result = detector.remove_term("nonexistentterm123")
        assert result is False

    def test_remove_term_stops_detection(self):
        """Test that removed terms are no longer detected."""
        detector = JargonDetector()
        detector.remove_term("authenticate")
        terms = detector.detect("Please authenticate.")
        assert not any(t.term.lower() == "authenticate" for t in terms)


# ============================================
# JargonDetector Category Filtering Tests
# ============================================


class TestJargonDetectorCategoryFiltering:
    """Tests for category filtering in JargonDetector."""

    def test_term_count_property(self):
        """Test term_count property."""
        detector = JargonDetector()
        count = detector.term_count
        assert isinstance(count, int)
        assert count > 0

    def test_get_terms_by_category(self):
        """Test getting terms by category."""
        detector = JargonDetector()
        technical = detector.get_terms_by_category(JargonCategory.TECHNICAL)
        assert len(technical) > 0
        assert "authenticate" in technical

    def test_get_terms_by_category_business(self):
        """Test getting business terms."""
        detector = JargonDetector()
        business = detector.get_terms_by_category(JargonCategory.BUSINESS)
        assert len(business) > 0
        assert "leverage" in business

    def test_get_terms_by_category_abbreviation(self):
        """Test getting abbreviation terms."""
        detector = JargonDetector()
        abbreviations = detector.get_terms_by_category(JargonCategory.ABBREVIATION)
        assert len(abbreviations) > 0
        assert "API" in abbreviations

    def test_filtered_detector_only_has_category(self):
        """Test that filtered detector only detects specified categories."""
        detector = JargonDetector(categories=[JargonCategory.TECHNICAL])
        # Should detect technical jargon
        terms = detector.detect("Please authenticate at the endpoint.")
        assert len(terms) >= 2
        # Should not detect business jargon
        terms = detector.detect("We need to leverage synergies.")
        # leverage and synergy are business category, should not be detected
        term_names = [t.term.lower() for t in terms]
        assert "leverage" not in term_names


# ============================================
# Integration Tests
# ============================================


class TestJargonDetectorIntegration:
    """Integration tests for JargonDetector."""

    def test_issue_example_detection(self):
        """Test the example from issue #71."""
        detector = JargonDetector()
        text = "Please authenticate before accessing the endpoint."
        terms = detector.detect(text)

        # Should find authenticate and endpoint
        term_names = [t.term.lower() for t in terms]
        assert "authenticate" in term_names
        assert "endpoint" in term_names

        # Check alternatives
        auth_term = next(t for t in terms if t.term.lower() == "authenticate")
        assert auth_term.simple_alternative is not None

        endpoint_term = next(t for t in terms if t.term.lower() == "endpoint")
        assert endpoint_term.simple_alternative == "connection point"

    def test_issue_example_simplification(self):
        """Test the simplification example from issue #71."""
        detector = JargonDetector()
        text = "Please authenticate before accessing the endpoint."
        result = detector.simplify(text)

        # Original should be unchanged
        assert result.original_text == text

        # Simplified should not contain jargon
        assert "authenticate" not in result.simplified_text.lower()
        assert "endpoint" not in result.simplified_text.lower()

        # Should have replaced terms
        assert result.terms_replaced >= 2

    def test_complex_sentence_handling(self):
        """Test handling of complex sentences with multiple jargon types."""
        detector = JargonDetector()
        text = (
            "Subsequently, you must authenticate using your credentials "
            "to access the API endpoint and leverage the SDK functionality."
        )
        terms = detector.detect(text)
        assert len(terms) >= 5  # subsequently, authenticate, credentials, API, endpoint, leverage, SDK

        result = detector.simplify(text)
        assert result.terms_replaced >= 5
        assert "authenticate" not in result.simplified_text.lower()

    def test_preserves_non_jargon_content(self):
        """Test that non-jargon content is preserved."""
        detector = JargonDetector()
        text = "Hello world! Please authenticate. Goodbye!"
        result = detector.simplify(text)
        assert "Hello world!" in result.simplified_text
        assert "Goodbye!" in result.simplified_text

    def test_handles_punctuation(self):
        """Test proper handling of punctuation."""
        detector = JargonDetector()
        text = "Do you need to authenticate? Yes, authenticate now!"
        result = detector.simplify(text)
        # Should preserve question mark and exclamation
        assert "?" in result.simplified_text
        assert "!" in result.simplified_text


# ============================================
# Edge Case Tests
# ============================================


class TestJargonDetectorEdgeCases:
    """Edge case tests for JargonDetector."""

    @pytest.fixture
    def detector(self):
        """Create a default detector."""
        return JargonDetector()

    def test_word_boundaries(self, detector):
        """Test that word boundaries are respected."""
        # 'authenticate' shouldn't match 'authentication'
        text = "The authentication failed."
        terms = detector.detect(text)
        # Should find 'authentication' not 'authenticate' as substring
        term_names = [t.term.lower() for t in terms]
        assert "authentication" in term_names

    def test_very_long_text(self, detector):
        """Test handling of very long text."""
        text = "Please authenticate. " * 100
        terms = detector.detect(text)
        assert len(terms) == 100

    def test_unicode_text(self, detector):
        """Test handling of unicode characters."""
        text = "Plëâsé authenticate the üsér."
        terms = detector.detect(text)
        assert any(t.term.lower() == "authenticate" for t in terms)

    def test_multiline_text(self, detector):
        """Test handling of multiline text."""
        text = """Line 1: Please authenticate.
        Line 2: Access the endpoint.
        Line 3: Done!"""
        terms = detector.detect(text)
        assert len(terms) >= 2

    def test_special_characters_in_context(self, detector):
        """Test handling of special characters in context."""
        text = "***Please authenticate!!! @user***"
        terms = detector.detect(text)
        assert len(terms) >= 1
        assert terms[0].term.lower() == "authenticate"
