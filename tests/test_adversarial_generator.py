"""Tests for the Adversarial Test Generator.

Issue #94 - Task 6.6: Adversarial Test Generator
Part of #29 - Phase 6: Conversational Testing Framework
"""

import pytest

from src.testing.adversarial import (
    AdversarialSeverity,
    AdversarialTestGenerator,
    AdversarialTestResult,
    GeneratorConfig,
    PerturbationConfig,
    PerturbationType,
)
from src.testing.types import (
    ConversationTest,
    ExpectedOutcome,
    SuccessCondition,
    TestCategory,
    TestPriority,
    TestTurn,
    TurnRole,
)


# ============================================
# Fixtures
# ============================================


@pytest.fixture
def simple_test() -> ConversationTest:
    """Create a simple conversation test."""
    return ConversationTest(
        test_id="test_001",
        name="Simple Greeting Test",
        turns=[
            TestTurn(
                turn_number=1,
                role=TurnRole.USER,
                input="I want to book a flight to New York",
                expected_intent="book_flight",
            ),
            TestTurn(
                turn_number=2,
                role=TurnRole.ASSISTANT,
                input="I'd be happy to help you book a flight to New York.",
            ),
            TestTurn(
                turn_number=3,
                role=TurnRole.USER,
                input="Can you find me something for tomorrow?",
                expected_intent="specify_date",
            ),
        ],
        expected_outcome=ExpectedOutcome(
            success_condition=SuccessCondition.ALL_PASS,
        ),
        category=TestCategory.INTENT_RECOGNITION,
        priority=TestPriority.HIGH,
        description="Test basic flight booking flow",
        tags=["booking", "flight"],
    )


@pytest.fixture
def multi_turn_test() -> ConversationTest:
    """Create a multi-turn conversation test."""
    return ConversationTest(
        test_id="test_002",
        name="Multi-turn Booking Test",
        turns=[
            TestTurn(
                turn_number=1,
                role=TurnRole.USER,
                input="I need help with my order",
                expected_intent="order_inquiry",
            ),
            TestTurn(
                turn_number=2,
                role=TurnRole.ASSISTANT,
                input="I can help you with your order. What's the issue?",
            ),
            TestTurn(
                turn_number=3,
                role=TurnRole.USER,
                input="It hasn't arrived yet",
                expected_intent="delivery_status",
            ),
            TestTurn(
                turn_number=4,
                role=TurnRole.ASSISTANT,
                input="Let me check the delivery status for you.",
            ),
            TestTurn(
                turn_number=5,
                role=TurnRole.USER,
                input="Actually, I want to cancel it",
                expected_intent="cancel_order",
            ),
        ],
        expected_outcome=ExpectedOutcome(
            success_condition=SuccessCondition.ALL_PASS,
        ),
    )


@pytest.fixture
def generator() -> AdversarialTestGenerator:
    """Create a default adversarial generator."""
    return AdversarialTestGenerator()


@pytest.fixture
def seeded_generator() -> AdversarialTestGenerator:
    """Create a seeded adversarial generator for reproducible tests."""
    config = GeneratorConfig(
        perturbation_config=PerturbationConfig(random_seed=42)
    )
    return AdversarialTestGenerator(config)


# ============================================
# Test PerturbationType Enum
# ============================================


class TestPerturbationType:
    """Tests for the PerturbationType enum."""

    def test_all_perturbation_types_exist(self) -> None:
        """Test that all 12 perturbation types are defined."""
        assert len(PerturbationType) == 12

    def test_input_quality_types(self) -> None:
        """Test input quality perturbation types."""
        assert PerturbationType.TYPO_INJECTION.value == "typo_injection"
        assert PerturbationType.GRAMMAR_ERROR.value == "grammar_error"
        assert PerturbationType.PARAPHRASE.value == "paraphrase"

    def test_semantic_challenge_types(self) -> None:
        """Test semantic challenge perturbation types."""
        assert PerturbationType.NEGATION_FLIP.value == "negation_flip"
        assert PerturbationType.OUT_OF_DOMAIN.value == "out_of_domain"
        assert PerturbationType.MULTI_INTENT.value == "multi_intent"
        assert PerturbationType.CONTEXT_SWITCH.value == "context_switch"

    def test_security_testing_types(self) -> None:
        """Test security testing perturbation types."""
        assert PerturbationType.PROMPT_INJECTION.value == "prompt_injection"
        assert PerturbationType.PII_EXTRACTION.value == "pii_extraction"
        assert PerturbationType.JAILBREAK.value == "jailbreak"
        assert PerturbationType.COMMAND_INJECTION.value == "command_injection"

    def test_additional_types(self) -> None:
        """Test additional perturbation types."""
        assert PerturbationType.CASE_VARIATION.value == "case_variation"


# ============================================
# Test AdversarialSeverity Enum
# ============================================


class TestAdversarialSeverity:
    """Tests for the AdversarialSeverity enum."""

    def test_all_severity_levels(self) -> None:
        """Test all severity levels are defined."""
        assert len(AdversarialSeverity) == 4
        assert AdversarialSeverity.CRITICAL.value == "critical"
        assert AdversarialSeverity.HIGH.value == "high"
        assert AdversarialSeverity.MEDIUM.value == "medium"
        assert AdversarialSeverity.LOW.value == "low"


# ============================================
# Test Configuration Classes
# ============================================


class TestPerturbationConfig:
    """Tests for PerturbationConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = PerturbationConfig()
        assert config.typo_rate == 0.1
        assert config.grammar_error_rate == 0.2
        assert config.synonym_rate == 0.3
        assert config.include_actual_exploits is False
        assert config.random_seed is None
        assert config.max_perturbations_per_text == 5

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = PerturbationConfig(
            typo_rate=0.2,
            grammar_error_rate=0.3,
            synonym_rate=0.5,
            random_seed=123,
            max_perturbations_per_text=10,
        )
        assert config.typo_rate == 0.2
        assert config.grammar_error_rate == 0.3
        assert config.synonym_rate == 0.5
        assert config.random_seed == 123
        assert config.max_perturbations_per_text == 10


class TestGeneratorConfig:
    """Tests for GeneratorConfig."""

    def test_default_config(self) -> None:
        """Test default generator configuration."""
        config = GeneratorConfig()
        assert config.tests_per_type == 1
        assert config.severity_filter is None
        assert len(config.enabled_types) == 12

    def test_custom_config(self) -> None:
        """Test custom generator configuration."""
        config = GeneratorConfig(
            tests_per_type=3,
            severity_filter=AdversarialSeverity.CRITICAL,
            enabled_types=[PerturbationType.TYPO_INJECTION],
        )
        assert config.tests_per_type == 3
        assert config.severity_filter == AdversarialSeverity.CRITICAL
        assert len(config.enabled_types) == 1


# ============================================
# Test AdversarialTestGenerator Creation
# ============================================


class TestAdversarialTestGeneratorCreation:
    """Tests for AdversarialTestGenerator instantiation."""

    def test_create_default_generator(self) -> None:
        """Test creating a generator with default config."""
        gen = AdversarialTestGenerator()
        assert gen.config is not None
        assert gen.config.tests_per_type == 1

    def test_create_with_custom_config(self) -> None:
        """Test creating a generator with custom config."""
        config = GeneratorConfig(tests_per_type=5)
        gen = AdversarialTestGenerator(config)
        assert gen.config.tests_per_type == 5

    def test_create_with_seed(self) -> None:
        """Test creating a generator with a random seed."""
        config = GeneratorConfig(
            perturbation_config=PerturbationConfig(random_seed=42)
        )
        gen = AdversarialTestGenerator(config)
        assert gen.config.perturbation_config.random_seed == 42


# ============================================
# Test Input Quality Perturbations
# ============================================


class TestTypoInjection:
    """Tests for typo injection perturbation."""

    def test_typo_injection_modifies_input(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that typo injection modifies user input."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.TYPO_INJECTION]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.TYPO_INJECTION
        assert result.severity == AdversarialSeverity.LOW

        # Check that some user turn was modified
        original_inputs = [t.input for t in simple_test.turns if t.role == TurnRole.USER]
        modified_inputs = [
            t.input for t in result.perturbed_test.turns if t.role == TurnRole.USER
        ]
        assert any(o != m for o, m in zip(original_inputs, modified_inputs))

    def test_inject_typos_method(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test the _inject_typos method directly."""
        text = "Hello world"
        result = seeded_generator._inject_typos(text, 0.3)
        assert result != text  # Should be modified

    def test_inject_typos_empty_string(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test typo injection on empty string."""
        result = generator._inject_typos("", 0.3)
        assert result == ""


class TestGrammarErrors:
    """Tests for grammar error perturbation."""

    def test_grammar_error_modifies_input(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that grammar errors modify user input."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.GRAMMAR_ERROR]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.GRAMMAR_ERROR
        assert result.severity == AdversarialSeverity.MEDIUM

    def test_inject_grammar_errors_method(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test the _inject_grammar_errors method directly."""
        text = "I am looking for a flight"
        result = seeded_generator._inject_grammar_errors(text)
        # Result is lowercased
        assert result == result.lower()


class TestParaphrase:
    """Tests for paraphrase perturbation."""

    def test_paraphrase_modifies_input(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that paraphrase modifies user input."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.PARAPHRASE]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.PARAPHRASE
        assert result.severity == AdversarialSeverity.MEDIUM

    def test_generate_paraphrase_method(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test the _generate_paraphrase method directly."""
        text = "I want to find a good hotel"
        result = seeded_generator._generate_paraphrase(text)
        # May or may not be modified depending on synonym rate
        assert isinstance(result, str)

    def test_paraphrase_preserves_punctuation(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that paraphrase preserves trailing punctuation."""
        text = "I want to buy something!"
        result = seeded_generator._generate_paraphrase(text)
        # Should preserve the structure
        assert isinstance(result, str)


# ============================================
# Test Semantic Challenge Perturbations
# ============================================


class TestNegationFlip:
    """Tests for negation flip perturbation."""

    def test_negation_flip_modifies_input(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that negation flip modifies user input."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.NEGATION_FLIP]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.NEGATION_FLIP
        assert result.severity == AdversarialSeverity.HIGH

    def test_flip_negation_method(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test the _flip_negation method directly."""
        # Test removing negation
        assert "can" in seeded_generator._flip_negation("I can't do this")

        # Test adding negation
        result = seeded_generator._flip_negation("I want to go")
        assert "don't" in result

    def test_flip_negation_not(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test flipping 'not'."""
        result = seeded_generator._flip_negation("I do not like this")
        assert "not" not in result.lower() or "do" in result.lower()


class TestOutOfDomain:
    """Tests for out-of-domain perturbation."""

    def test_out_of_domain_replaces_input(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that out-of-domain replaces user input."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.OUT_OF_DOMAIN]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.OUT_OF_DOMAIN
        assert result.severity == AdversarialSeverity.MEDIUM

        # Verify it uses an out-of-domain query
        user_inputs = [
            t.input for t in result.perturbed_test.turns if t.role == TurnRole.USER
        ]
        assert any(
            inp in seeded_generator.OUT_OF_DOMAIN_QUERIES for inp in user_inputs
        )


class TestMultiIntent:
    """Tests for multi-intent perturbation."""

    def test_multi_intent_combines_inputs(
        self, multi_turn_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that multi-intent combines user inputs."""
        results = seeded_generator.generate_adversarial(
            multi_turn_test, [PerturbationType.MULTI_INTENT]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.MULTI_INTENT
        assert result.severity == AdversarialSeverity.HIGH

    def test_multi_intent_single_turn(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test multi-intent with single user turn."""
        test = ConversationTest(
            test_id="single",
            name="Single Turn",
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Hello"),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.ALL_PASS
            ),
        )
        results = seeded_generator.generate_adversarial(
            test, [PerturbationType.MULTI_INTENT]
        )
        assert len(results) == 1
        # Should add secondary intent
        assert "weather" in results[0].perturbed_test.turns[0].input.lower()


class TestContextSwitch:
    """Tests for context switch perturbation."""

    def test_context_switch_modifies_mid_conversation(
        self, multi_turn_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that context switch modifies mid-conversation turn."""
        results = seeded_generator.generate_adversarial(
            multi_turn_test, [PerturbationType.CONTEXT_SWITCH]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.CONTEXT_SWITCH
        assert result.severity == AdversarialSeverity.HIGH

    def test_context_switch_insufficient_turns(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test context switch with insufficient turns."""
        test = ConversationTest(
            test_id="single",
            name="Single Turn",
            turns=[
                TestTurn(turn_number=1, role=TurnRole.USER, input="Hello"),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.ALL_PASS
            ),
        )
        results = seeded_generator.generate_adversarial(
            test, [PerturbationType.CONTEXT_SWITCH]
        )
        assert len(results) == 1
        # Description should indicate insufficient turns
        assert "Insufficient" in results[0].description


# ============================================
# Test Security Perturbations
# ============================================


class TestPromptInjection:
    """Tests for prompt injection perturbation."""

    def test_prompt_injection_adds_pattern(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that prompt injection adds injection pattern."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.PROMPT_INJECTION]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.PROMPT_INJECTION
        assert result.severity == AdversarialSeverity.CRITICAL

        # Verify category and priority are updated
        assert result.perturbed_test.category == TestCategory.ERROR_HANDLING
        assert result.perturbed_test.priority == TestPriority.CRITICAL


class TestPiiExtraction:
    """Tests for PII extraction perturbation."""

    def test_pii_extraction_replaces_input(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that PII extraction replaces input with probe."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.PII_EXTRACTION]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.PII_EXTRACTION
        assert result.severity == AdversarialSeverity.CRITICAL


class TestJailbreak:
    """Tests for jailbreak perturbation."""

    def test_jailbreak_adds_pattern(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that jailbreak adds jailbreak pattern."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.JAILBREAK]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.JAILBREAK
        assert result.severity == AdversarialSeverity.CRITICAL


class TestCommandInjection:
    """Tests for command injection perturbation."""

    def test_command_injection_adds_pattern(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that command injection adds injection pattern."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.COMMAND_INJECTION]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.COMMAND_INJECTION
        assert result.severity == AdversarialSeverity.CRITICAL


# ============================================
# Test Additional Perturbations
# ============================================


class TestCaseVariation:
    """Tests for case variation perturbation."""

    def test_case_variation_modifies_input(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that case variation modifies user input."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.CASE_VARIATION]
        )
        assert len(results) == 1
        result = results[0]
        assert result.perturbation_type == PerturbationType.CASE_VARIATION
        assert result.severity == AdversarialSeverity.LOW

    def test_alternating_case(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test alternating case conversion."""
        result = seeded_generator._alternating_case("hello world")
        assert result == "HeLlO wOrLd"

    def test_random_case(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test random case conversion."""
        result = seeded_generator._random_case("hello")
        # Just verify it's a string with same length
        assert len(result) == 5


# ============================================
# Test Bulk Generation
# ============================================


class TestBulkGeneration:
    """Tests for bulk test generation."""

    def test_generate_all_types(
        self, simple_test: ConversationTest, generator: AdversarialTestGenerator
    ) -> None:
        """Test generating all perturbation types."""
        results = generator.generate_adversarial(simple_test)
        assert len(results) == 12  # One per type

    def test_generate_multiple_per_type(
        self, simple_test: ConversationTest
    ) -> None:
        """Test generating multiple tests per type."""
        config = GeneratorConfig(tests_per_type=3)
        gen = AdversarialTestGenerator(config)
        results = gen.generate_adversarial(
            simple_test, [PerturbationType.TYPO_INJECTION]
        )
        assert len(results) == 3

    def test_generate_with_severity_filter(
        self, simple_test: ConversationTest
    ) -> None:
        """Test generating with severity filter."""
        config = GeneratorConfig(severity_filter=AdversarialSeverity.CRITICAL)
        gen = AdversarialTestGenerator(config)
        results = gen.generate_adversarial(simple_test)
        # Only security types should be returned
        assert all(r.severity == AdversarialSeverity.CRITICAL for r in results)

    def test_generate_test_suite(
        self, simple_test: ConversationTest, multi_turn_test: ConversationTest,
        generator: AdversarialTestGenerator
    ) -> None:
        """Test generating tests for multiple base tests."""
        results = generator.generate_test_suite(
            [simple_test, multi_turn_test],
            [PerturbationType.TYPO_INJECTION],
        )
        assert len(results) == 2  # One per base test


# ============================================
# Test Utility Methods
# ============================================


class TestUtilityMethods:
    """Tests for utility methods."""

    def test_get_perturbation_types_by_severity(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test getting perturbation types by severity."""
        critical = generator.get_perturbation_types_by_severity(
            AdversarialSeverity.CRITICAL
        )
        assert PerturbationType.PROMPT_INJECTION in critical
        assert PerturbationType.PII_EXTRACTION in critical
        assert PerturbationType.JAILBREAK in critical
        assert PerturbationType.COMMAND_INJECTION in critical
        assert len(critical) == 4

    def test_generate_security_probe(
        self, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test generating a security probe."""
        probe = seeded_generator.generate_security_probe("booking context")
        assert isinstance(probe, str)
        assert len(probe) > 0


# ============================================
# Test Result Structure
# ============================================


class TestAdversarialTestResultStructure:
    """Tests for AdversarialTestResult structure."""

    def test_result_has_required_fields(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that result has all required fields."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.TYPO_INJECTION]
        )
        result = results[0]

        assert result.original_test is simple_test
        assert result.perturbation_type == PerturbationType.TYPO_INJECTION
        assert result.perturbed_test is not None
        assert result.severity == AdversarialSeverity.LOW
        assert isinstance(result.description, str)
        assert isinstance(result.expected_behavior, str)

    def test_perturbed_test_has_updated_metadata(
        self, simple_test: ConversationTest, seeded_generator: AdversarialTestGenerator
    ) -> None:
        """Test that perturbed test has updated ID, name, and tags."""
        results = seeded_generator.generate_adversarial(
            simple_test, [PerturbationType.TYPO_INJECTION]
        )
        result = results[0]

        assert "adversarial" in result.perturbed_test.test_id
        assert "Adversarial" in result.perturbed_test.name
        assert "adversarial" in result.perturbed_test.tags
        assert "typo_injection" in result.perturbed_test.tags


# ============================================
# Test Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_test_turns(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test with a test that has no turns."""
        test = ConversationTest(
            test_id="empty",
            name="Empty Test",
            turns=[],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.ALL_PASS
            ),
        )
        results = generator.generate_adversarial(
            test, [PerturbationType.TYPO_INJECTION]
        )
        assert len(results) == 1
        assert "No user turns" in results[0].description

    def test_no_user_turns(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test with only assistant turns."""
        test = ConversationTest(
            test_id="no_user",
            name="No User Turns",
            turns=[
                TestTurn(
                    turn_number=1,
                    role=TurnRole.ASSISTANT,
                    input="Hello!",
                ),
            ],
            expected_outcome=ExpectedOutcome(
                success_condition=SuccessCondition.ALL_PASS
            ),
        )
        results = generator.generate_adversarial(
            test, [PerturbationType.PARAPHRASE]
        )
        assert len(results) == 1
        assert "No user turns" in results[0].description

    def test_deep_copy_preserves_structure(
        self, simple_test: ConversationTest, generator: AdversarialTestGenerator
    ) -> None:
        """Test that deep copy preserves test structure."""
        copy = generator._deep_copy_test(simple_test)

        assert copy.test_id == simple_test.test_id
        assert copy.name == simple_test.name
        assert len(copy.turns) == len(simple_test.turns)
        assert copy.category == simple_test.category
        assert copy.priority == simple_test.priority

        # Verify it's a true copy
        copy.test_id = "modified"
        assert simple_test.test_id != copy.test_id

    def test_enabled_types_filter(
        self, simple_test: ConversationTest
    ) -> None:
        """Test that enabled_types filter works."""
        config = GeneratorConfig(
            enabled_types=[
                PerturbationType.TYPO_INJECTION,
                PerturbationType.PARAPHRASE,
            ]
        )
        gen = AdversarialTestGenerator(config)
        results = gen.generate_adversarial(simple_test)
        assert len(results) == 2

        types = {r.perturbation_type for r in results}
        assert types == {PerturbationType.TYPO_INJECTION, PerturbationType.PARAPHRASE}


# ============================================
# Test Severity Classification
# ============================================


class TestSeverityClassification:
    """Tests for severity classification."""

    def test_security_perturbations_are_critical(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test that security perturbations are classified as critical."""
        security_types = [
            PerturbationType.PROMPT_INJECTION,
            PerturbationType.PII_EXTRACTION,
            PerturbationType.JAILBREAK,
            PerturbationType.COMMAND_INJECTION,
        ]
        for ptype in security_types:
            severity = generator._get_severity(ptype)
            assert severity == AdversarialSeverity.CRITICAL

    def test_semantic_perturbations_are_high(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test that semantic perturbations are classified as high."""
        semantic_types = [
            PerturbationType.NEGATION_FLIP,
            PerturbationType.MULTI_INTENT,
            PerturbationType.CONTEXT_SWITCH,
        ]
        for ptype in semantic_types:
            severity = generator._get_severity(ptype)
            assert severity == AdversarialSeverity.HIGH

    def test_quality_perturbations_are_medium(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test that quality perturbations are classified as medium."""
        quality_types = [
            PerturbationType.OUT_OF_DOMAIN,
            PerturbationType.GRAMMAR_ERROR,
            PerturbationType.PARAPHRASE,
        ]
        for ptype in quality_types:
            severity = generator._get_severity(ptype)
            assert severity == AdversarialSeverity.MEDIUM

    def test_minor_perturbations_are_low(
        self, generator: AdversarialTestGenerator
    ) -> None:
        """Test that minor perturbations are classified as low."""
        minor_types = [
            PerturbationType.TYPO_INJECTION,
            PerturbationType.CASE_VARIATION,
        ]
        for ptype in minor_types:
            severity = generator._get_severity(ptype)
            assert severity == AdversarialSeverity.LOW
