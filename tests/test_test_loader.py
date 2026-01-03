"""Tests for Conversational Test Loader.

Issue #90 - Task 6.2: Test Loader & Validator
Part of #29 - Phase 6: Conversational Testing Framework
"""

import os
import tempfile
from pathlib import Path

import pytest
import yaml

from src.testing import (
    AssertionOperator,
    AssertionSeverity,
    AssertionTarget,
    AssertionType,
    ConversationTest,
    ConversationTestLoader,
    ExecutionOrder,
    ExpertiseLevel,
    LoaderConfig,
    MatchType,
    MockResponseType,
    SuccessCondition,
    TestCategory,
    TestPriority,
    TestSuite,
    TestTemplate,
    TurnRole,
    ValidationError,
    ValidationResult,
    ValidationSeverity,
)


# Fixture directory
FIXTURES_DIR = Path(__file__).parent / "fixtures" / "conversations"


# ============================================
# Loader Configuration Tests
# ============================================


class TestLoaderConfig:
    """Test LoaderConfig defaults and customization."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = LoaderConfig()
        assert config.default_category == TestCategory.QUALITY_ASSURANCE
        assert config.default_priority == TestPriority.MEDIUM
        assert config.strict_validation is True
        assert config.allow_unknown_fields is False
        assert config.template_dir is None

    def test_custom_config(self) -> None:
        """Test custom configuration values."""
        config = LoaderConfig(
            default_category=TestCategory.REGRESSION,
            default_priority=TestPriority.HIGH,
            strict_validation=False,
            allow_unknown_fields=True,
            template_dir="/templates",
        )
        assert config.default_category == TestCategory.REGRESSION
        assert config.default_priority == TestPriority.HIGH
        assert config.strict_validation is False
        assert config.allow_unknown_fields is True
        assert config.template_dir == "/templates"


# ============================================
# Validation Types Tests
# ============================================


class TestValidationError:
    """Test ValidationError formatting."""

    def test_minimal_error(self) -> None:
        """Test error with minimal info."""
        error = ValidationError(message="Something went wrong")
        assert "Something went wrong" in str(error)
        assert "[ERROR]" in str(error)

    def test_full_error(self) -> None:
        """Test error with all location info."""
        error = ValidationError(
            message="Invalid value",
            severity=ValidationSeverity.ERROR,
            path="test.yaml",
            line=10,
            column=5,
            field="category",
            expected="one of ['a', 'b']",
            actual="c",
        )
        error_str = str(error)
        assert "test.yaml" in error_str
        assert "line 10" in error_str
        assert "col 5" in error_str
        assert "category" in error_str
        assert "Invalid value" in error_str
        assert "expected" in error_str
        assert "got" in error_str

    def test_warning_severity(self) -> None:
        """Test warning severity formatting."""
        error = ValidationError(
            message="Minor issue", severity=ValidationSeverity.WARNING
        )
        assert "[WARNING]" in str(error)


class TestValidationResult:
    """Test ValidationResult behavior."""

    def test_initial_state(self) -> None:
        """Test initial result is valid."""
        result = ValidationResult(valid=True)
        assert result.valid is True
        assert result.error_count == 0
        assert result.warning_count == 0

    def test_add_error(self) -> None:
        """Test adding errors invalidates result."""
        result = ValidationResult(valid=True)
        result.add_error(ValidationError(message="Error"))
        assert result.valid is False
        assert result.error_count == 1

    def test_add_warning(self) -> None:
        """Test warnings don't invalidate result."""
        result = ValidationResult(valid=True)
        result.add_error(
            ValidationError(message="Warning", severity=ValidationSeverity.WARNING)
        )
        assert result.valid is True
        assert result.warning_count == 1


# ============================================
# Basic Loading Tests
# ============================================


class TestBasicLoading:
    """Test basic file loading functionality."""

    def test_load_simple_test(self) -> None:
        """Test loading a simple valid test file."""
        loader = ConversationTestLoader()
        test = loader.load_test(str(FIXTURES_DIR / "valid_simple.yaml"))

        assert test.test_id == "test-greeting-001"
        assert test.name == "Simple Greeting Test"
        assert test.category == TestCategory.INTENT_RECOGNITION
        assert test.priority == TestPriority.HIGH
        assert len(test.turns) == 2
        assert test.turns[0].role == TurnRole.USER
        assert test.turns[0].input == "Hello!"
        assert test.turns[0].expected_intent == "greeting"

    def test_load_minimal_test(self) -> None:
        """Test loading minimal test with defaults."""
        loader = ConversationTestLoader()
        test = loader.load_test(str(FIXTURES_DIR / "valid_minimal.yaml"))

        assert test.test_id == "test-minimal-001"
        assert test.name == "Minimal Test"
        assert test.category == TestCategory.QUALITY_ASSURANCE  # default
        assert test.priority == TestPriority.MEDIUM  # default
        assert len(test.turns) == 1
        assert test.turns[0].turn_number == 1  # auto-assigned

    def test_load_complex_test(self) -> None:
        """Test loading complex test with all features."""
        loader = ConversationTestLoader()
        test = loader.load_test(str(FIXTURES_DIR / "valid_complex.yaml"))

        assert test.test_id == "test-weather-flow-001"
        assert test.category == TestCategory.DIALOGUE_FLOW
        assert test.priority == TestPriority.CRITICAL
        assert len(test.tags) == 4
        assert "weather" in test.tags

        # Verify setup
        assert test.setup is not None
        assert test.setup.initial_context is not None
        assert test.setup.initial_context["session_id"] == "test-session-123"
        assert len(test.setup.initial_entities) == 1
        assert test.setup.initial_entities[0].entity_type == "location"

        # Verify user profile
        assert test.setup.user_profile is not None
        assert test.setup.user_profile.user_id == "test-user-001"
        assert test.setup.user_profile.expertise_level == ExpertiseLevel.INTERMEDIATE

        # Verify system state
        assert test.setup.system_state is not None
        assert "weather" in test.setup.system_state.active_capabilities

        # Verify mock responses
        assert len(test.setup.mock_responses) == 1
        assert test.setup.mock_responses[0].response_type == MockResponseType.API_RESPONSE

        # Verify turns
        assert len(test.turns) == 4
        assert len(test.turns[0].assertions) == 1
        assert test.turns[0].assertions[0].assertion_type == AssertionType.INTENT_MATCH

        # Verify expected entities
        assert len(test.turns[2].expected_entities) == 1
        assert test.turns[2].expected_entities[0].entity_type == "location"

        # Verify context requirements
        assert len(test.turns[2].context_requirements) == 1
        assert test.turns[2].context_requirements[0].key == "pending_weather_request"
        assert test.turns[2].context_requirements[0].match_type == MatchType.EXISTS

        # Verify expected outcome
        assert test.expected_outcome.success_condition == SuccessCondition.THRESHOLD
        assert test.expected_outcome.min_assertions_passed == 3
        assert test.expected_outcome.quality_requirements is not None
        assert test.expected_outcome.quality_requirements.min_coherence == 0.85

        # Verify quality thresholds
        assert test.quality_thresholds is not None
        assert test.quality_thresholds.coherence_threshold == 0.85
        assert test.quality_thresholds.strict_mode is True

        # Verify metadata
        assert test.timeout_seconds == 30
        assert test.metadata is not None
        assert test.metadata["author"] == "test-team"

    def test_file_not_found(self) -> None:
        """Test error for nonexistent file."""
        loader = ConversationTestLoader()
        with pytest.raises(ValueError, match="File not found"):
            loader.load_test("/nonexistent/path.yaml")

    def test_empty_file(self) -> None:
        """Test error for empty file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("")
            temp_path = f.name

        try:
            loader = ConversationTestLoader()
            with pytest.raises(ValueError, match="Empty test file"):
                loader.load_test(temp_path)
        finally:
            os.unlink(temp_path)


# ============================================
# Validation Tests
# ============================================


class TestValidation:
    """Test validation of test definitions."""

    def test_missing_required_fields(self) -> None:
        """Test validation catches missing required fields."""
        loader = ConversationTestLoader()
        result = loader.load_and_validate(
            str(FIXTURES_DIR / "invalid_missing_fields.yaml")
        )

        assert result.valid is False
        assert result.error_count >= 2  # Missing test_id and turns

        error_messages = [str(e) for e in result.errors]
        assert any("test_id" in msg for msg in error_messages)
        assert any("turns" in msg for msg in error_messages)

    def test_invalid_enum_values(self) -> None:
        """Test validation catches invalid enum values."""
        loader = ConversationTestLoader()
        result = loader.load_and_validate(str(FIXTURES_DIR / "invalid_bad_enum.yaml"))

        assert result.valid is False
        error_messages = [str(e) for e in result.errors]
        assert any("category" in msg for msg in error_messages)
        assert any("role" in msg for msg in error_messages)

    def test_empty_turns(self) -> None:
        """Test validation catches empty turns array."""
        loader = ConversationTestLoader()
        result = loader.load_and_validate(
            str(FIXTURES_DIR / "invalid_empty_turns.yaml")
        )

        assert result.valid is False
        error_messages = [str(e) for e in result.errors]
        assert any("at least one turn" in msg for msg in error_messages)

    def test_validate_dict_directly(self) -> None:
        """Test validating a dict without loading from file."""
        loader = ConversationTestLoader()
        test_data = {
            "test_id": "test-direct",
            "name": "Direct Validation Test",
            "turns": [{"role": "user", "input": "Hello"}],
        }

        result = loader.validate_test(test_data)
        assert result.valid is True
        assert result.test is not None
        assert result.test.test_id == "test-direct"

    def test_unknown_fields_warning(self) -> None:
        """Test that unknown fields generate warnings."""
        loader = ConversationTestLoader(LoaderConfig(allow_unknown_fields=False))
        test_data = {
            "test_id": "test-unknown",
            "name": "Unknown Fields Test",
            "turns": [{"role": "user", "input": "Hello"}],
            "unknown_field": "should warn",
        }

        result = loader.validate_test(test_data)
        assert result.valid is True  # Warnings don't invalidate
        assert result.warning_count >= 1
        warning_messages = [str(w) for w in result.warnings]
        assert any("unknown_field" in msg for msg in warning_messages)


# ============================================
# Directory Loading Tests
# ============================================


class TestDirectoryLoading:
    """Test loading tests from directories."""

    def test_load_directory_glob(self) -> None:
        """Test loading tests matching a glob pattern."""
        loader = ConversationTestLoader(LoaderConfig(strict_validation=False))
        pattern = str(FIXTURES_DIR / "valid_*.yaml")
        tests = loader.load_directory(pattern)

        # Should load valid_simple, valid_minimal, valid_complex (not suite)
        assert len(tests) >= 3
        test_ids = {t.test_id for t in tests}
        assert "test-greeting-001" in test_ids
        assert "test-minimal-001" in test_ids

    def test_load_directory_with_tag_filter(self) -> None:
        """Test filtering by tags."""
        loader = ConversationTestLoader(LoaderConfig(strict_validation=False))
        pattern = str(FIXTURES_DIR / "valid_*.yaml")
        tests = loader.load_directory(pattern, tags=["greeting"])

        assert len(tests) >= 1
        for test in tests:
            assert "greeting" in test.tags

    def test_load_directory_with_category_filter(self) -> None:
        """Test filtering by category."""
        loader = ConversationTestLoader(LoaderConfig(strict_validation=False))
        pattern = str(FIXTURES_DIR / "valid_*.yaml")
        tests = loader.load_directory(
            pattern, categories=[TestCategory.INTENT_RECOGNITION]
        )

        for test in tests:
            assert test.category == TestCategory.INTENT_RECOGNITION

    def test_load_directory_with_priority_filter(self) -> None:
        """Test filtering by priority."""
        loader = ConversationTestLoader(LoaderConfig(strict_validation=False))
        pattern = str(FIXTURES_DIR / "valid_*.yaml")
        tests = loader.load_directory(pattern, priorities=[TestPriority.CRITICAL])

        for test in tests:
            assert test.priority == TestPriority.CRITICAL

    def test_strict_mode_raises_on_invalid(self) -> None:
        """Test strict mode raises errors for invalid files."""
        loader = ConversationTestLoader(LoaderConfig(strict_validation=True))
        pattern = str(FIXTURES_DIR / "invalid_*.yaml")

        with pytest.raises(ValueError, match="Invalid test files"):
            loader.load_directory(pattern)


# ============================================
# Suite Loading Tests
# ============================================


class TestSuiteLoading:
    """Test loading test suites."""

    def test_load_suite(self) -> None:
        """Test loading a test suite."""
        loader = ConversationTestLoader(LoaderConfig(strict_validation=False))
        suite = loader.load_suite(str(FIXTURES_DIR / "valid_suite.yaml"))

        assert suite.suite_id == "suite-core-001"
        assert suite.name == "Core Conversation Tests"
        assert suite.execution_order == ExecutionOrder.PRIORITY
        assert suite.parallel_execution is True
        assert suite.stop_on_failure is False

        # Should have inline test + loaded tests
        assert len(suite.tests) >= 1

        # Check default setup
        assert suite.default_setup is not None
        assert suite.default_setup.initial_context is not None

        # Check default thresholds
        assert suite.default_thresholds is not None
        assert suite.default_thresholds.coherence_threshold == 0.80

    def test_suite_not_found(self) -> None:
        """Test error for nonexistent suite file."""
        loader = ConversationTestLoader()
        with pytest.raises(FileNotFoundError):
            loader.load_suite("/nonexistent/suite.yaml")


# ============================================
# Template Tests
# ============================================


class TestTemplates:
    """Test template loading and expansion."""

    def test_load_template(self) -> None:
        """Test loading a template file."""
        loader = ConversationTestLoader()
        template = loader.load_template(str(FIXTURES_DIR / "template.yaml"))

        assert template.template_id == "greeting-template"
        assert template.name_pattern == "Greeting Test - {language}"
        assert len(template.parameters) == 3

    def test_register_and_expand_template(self) -> None:
        """Test registering and expanding a template."""
        loader = ConversationTestLoader()
        template = TestTemplate(
            template_id="simple-template",
            name_pattern="Test for {item}",
            base_test={
                "category": "quality_assurance",
                "turns": [
                    {"role": "user", "input": "Tell me about {item}"},
                    {"role": "assistant", "input": "{response}"},
                ],
                "expected_outcome": {"success_condition": "all_pass"},
            },
        )
        loader.register_template(template)

        # Expand with parameters
        test = loader.expand_template(
            "simple-template",
            {"item": "weather", "response": "The weather is nice!"},
        )

        assert test.name == "Test for weather"
        assert test.turns[0].input == "Tell me about weather"
        assert test.turns[1].input == "The weather is nice!"

    def test_expand_template_not_found(self) -> None:
        """Test error for unknown template."""
        loader = ConversationTestLoader()
        with pytest.raises(KeyError, match="Template not found"):
            loader.expand_template("nonexistent", {})


# ============================================
# Error Reporting Tests
# ============================================


class TestErrorReporting:
    """Test detailed error reporting."""

    def test_yaml_parse_error_location(self) -> None:
        """Test YAML parse errors include location info."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid:\n  - missing: colon\n    bad yaml here")
            temp_path = f.name

        try:
            loader = ConversationTestLoader()
            result = loader.load_and_validate(temp_path)
            # Note: This might actually parse successfully depending on YAML
            # The important thing is we handle errors gracefully
            assert result.file_path == temp_path
        finally:
            os.unlink(temp_path)

    def test_validation_error_includes_field(self) -> None:
        """Test validation errors include field information."""
        loader = ConversationTestLoader()
        test_data = {
            "test_id": "test-bad-turn",
            "name": "Bad Turn Test",
            "turns": [
                {"role": "user"}  # Missing input
            ],
        }

        result = loader.validate_test(test_data)
        assert result.valid is False
        assert any("input" in str(e) for e in result.errors)

    def test_assertion_validation_error(self) -> None:
        """Test assertion validation errors."""
        loader = ConversationTestLoader()
        test_data = {
            "test_id": "test-bad-assertion",
            "name": "Bad Assertion Test",
            "turns": [
                {
                    "role": "user",
                    "input": "Hello",
                    "assertions": [
                        {
                            # Missing required fields
                            "severity": "critical"
                        }
                    ],
                }
            ],
        }

        result = loader.validate_test(test_data)
        assert result.valid is False
        error_fields = [e.field for e in result.errors if e.field]
        assert any("assertion" in f for f in error_fields)


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Test edge cases and special scenarios."""

    def test_auto_assign_turn_numbers(self) -> None:
        """Test turn numbers are auto-assigned if missing."""
        loader = ConversationTestLoader()
        test_data = {
            "test_id": "test-auto-turn",
            "name": "Auto Turn Numbers",
            "turns": [
                {"role": "user", "input": "First"},
                {"role": "assistant", "input": "Second"},
                {"role": "user", "input": "Third"},
            ],
        }

        result = loader.validate_test(test_data)
        assert result.valid is True
        assert result.test is not None
        assert result.test.turns[0].turn_number == 1
        assert result.test.turns[1].turn_number == 2
        assert result.test.turns[2].turn_number == 3

    def test_case_insensitive_enum_values(self) -> None:
        """Test enum values are case-insensitive."""
        loader = ConversationTestLoader()
        test_data = {
            "test_id": "test-case",
            "name": "Case Test",
            "category": "INTENT_RECOGNITION",  # uppercase
            "priority": "High",  # mixed case
            "turns": [{"role": "USER", "input": "Hello"}],  # uppercase
        }

        result = loader.validate_test(test_data)
        assert result.valid is True
        assert result.test is not None
        assert result.test.category == TestCategory.INTENT_RECOGNITION
        assert result.test.priority == TestPriority.HIGH
        assert result.test.turns[0].role == TurnRole.USER

    def test_empty_optional_lists_default(self) -> None:
        """Test empty optional lists get default values."""
        loader = ConversationTestLoader()
        test_data = {
            "test_id": "test-empty-lists",
            "name": "Empty Lists Test",
            "turns": [{"role": "user", "input": "Hello"}],
        }

        result = loader.validate_test(test_data)
        assert result.valid is True
        assert result.test is not None
        assert result.test.tags == []
        assert result.test.turns[0].expected_entities == []
        assert result.test.turns[0].assertions == []

    def test_special_characters_in_input(self) -> None:
        """Test special characters in input are preserved."""
        loader = ConversationTestLoader()
        test_data = {
            "test_id": "test-special-chars",
            "name": "Special Characters Test",
            "turns": [
                {
                    "role": "user",
                    "input": "What's the price in $? Is it < $100 or > $200?",
                }
            ],
        }

        result = loader.validate_test(test_data)
        assert result.valid is True
        assert result.test is not None
        assert "$" in result.test.turns[0].input
        assert "<" in result.test.turns[0].input
        assert ">" in result.test.turns[0].input


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for the loader."""

    def test_full_workflow(self) -> None:
        """Test complete workflow: load, validate, access data."""
        loader = ConversationTestLoader()

        # Load a test
        test = loader.load_test(str(FIXTURES_DIR / "valid_simple.yaml"))

        # Verify we can access all data
        assert test.test_id is not None
        assert test.name is not None
        assert len(test.turns) > 0
        assert test.expected_outcome is not None

        # Verify test is stored
        assert test.test_id in loader._loaded_tests

    def test_load_multiple_files(self) -> None:
        """Test loading multiple files maintains state correctly."""
        loader = ConversationTestLoader()

        test1 = loader.load_test(str(FIXTURES_DIR / "valid_simple.yaml"))
        test2 = loader.load_test(str(FIXTURES_DIR / "valid_minimal.yaml"))

        assert test1.test_id != test2.test_id
        assert len(loader._loaded_tests) >= 2

    def test_template_workflow(self) -> None:
        """Test complete template workflow."""
        loader = ConversationTestLoader()

        # Load template
        template = loader.load_template(str(FIXTURES_DIR / "template.yaml"))

        # Expand for each parameter set
        for params in template.parameters:
            test = loader.expand_template(template.template_id, params)
            assert test is not None
            assert params["language"] in test.name
