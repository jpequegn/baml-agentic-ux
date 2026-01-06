"""
Tests for Conversational Testing Framework Loader.

Part of Phase 6: Conversational Testing Framework
Issue #110 - Task 6.11: Testing & Documentation
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.testing.loader import (
    ConversationTestLoader,
    LoaderConfig,
    ValidationError,
    ValidationResult,
    ValidationSeverity,
    TestTemplate,
)
from src.testing.types import (
    TestCategory,
    TestPriority,
    TurnRole,
)


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_basic_creation(self):
        """Test basic ValidationError creation."""
        error = ValidationError(
            message="Test is missing required field",
            severity=ValidationSeverity.ERROR,
        )
        assert error.message == "Test is missing required field"
        assert error.severity == ValidationSeverity.ERROR

    def test_with_location_info(self):
        """Test ValidationError with location information."""
        error = ValidationError(
            message="Invalid enum value",
            severity=ValidationSeverity.ERROR,
            path="tests/basic.yaml",
            line=15,
            column=10,
            field="category",
            expected="one of: intent_recognition, entity_extraction",
            actual="invalid_category",
        )
        assert error.path == "tests/basic.yaml"
        assert error.line == 15
        assert error.field == "category"

    def test_str_representation(self):
        """Test ValidationError string representation."""
        error = ValidationError(
            message="Missing required field",
            severity=ValidationSeverity.ERROR,
            path="test.yaml",
            line=10,
        )
        str_repr = str(error)
        assert "Missing required field" in str_repr
        assert "test.yaml" in str_repr

    def test_str_with_expected_actual(self):
        """Test ValidationError string with expected/actual values."""
        error = ValidationError(
            message="Invalid value",
            severity=ValidationSeverity.ERROR,
            expected="string",
            actual="int",
        )
        str_repr = str(error)
        assert "expected: string" in str_repr
        assert "got: int" in str_repr


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_valid_result(self):
        """Test ValidationResult for valid test."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[],
        )
        assert result.valid is True
        assert len(result.errors) == 0

    def test_invalid_result_with_errors(self):
        """Test ValidationResult with errors."""
        result = ValidationResult(
            valid=False,
            errors=[
                ValidationError(
                    message="Missing test_id",
                    severity=ValidationSeverity.ERROR,
                ),
            ],
            warnings=[],
        )
        assert result.valid is False
        assert len(result.errors) == 1

    def test_with_warnings(self):
        """Test ValidationResult with warnings."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=[
                ValidationError(
                    message="Test has no assertions",
                    severity=ValidationSeverity.WARNING,
                ),
            ],
        )
        assert result.valid is True
        assert len(result.warnings) == 1

    def test_error_count_property(self):
        """Test error_count property."""
        result = ValidationResult(
            valid=False,
            errors=[
                ValidationError(message="Error 1", severity=ValidationSeverity.ERROR),
                ValidationError(message="Error 2", severity=ValidationSeverity.ERROR),
            ],
        )
        assert result.error_count == 2

    def test_warning_count_property(self):
        """Test warning_count property."""
        result = ValidationResult(
            valid=True,
            warnings=[
                ValidationError(message="Warning 1", severity=ValidationSeverity.WARNING),
            ],
        )
        assert result.warning_count == 1

    def test_add_error_method(self):
        """Test add_error method."""
        result = ValidationResult(valid=True)
        result.add_error(
            ValidationError(message="New error", severity=ValidationSeverity.ERROR)
        )
        assert result.valid is False
        assert result.error_count == 1

    def test_add_warning_via_add_error(self):
        """Test adding warning via add_error method."""
        result = ValidationResult(valid=True)
        result.add_error(
            ValidationError(message="New warning", severity=ValidationSeverity.WARNING)
        )
        assert result.valid is True  # Warnings don't invalidate
        assert result.warning_count == 1


class TestLoaderConfig:
    """Tests for LoaderConfig dataclass."""

    def test_default_config(self):
        """Test default LoaderConfig creation."""
        config = LoaderConfig()
        assert config.strict_validation is True
        assert config.allow_unknown_fields is False
        assert config.default_category == TestCategory.QUALITY_ASSURANCE
        assert config.default_priority == TestPriority.MEDIUM
        assert config.template_dir is None

    def test_custom_config(self):
        """Test custom LoaderConfig creation."""
        config = LoaderConfig(
            strict_validation=False,
            allow_unknown_fields=True,
            default_category=TestCategory.REGRESSION,
            default_priority=TestPriority.HIGH,
            template_dir="/templates",
        )
        assert config.strict_validation is False
        assert config.allow_unknown_fields is True
        assert config.default_category == TestCategory.REGRESSION
        assert config.default_priority == TestPriority.HIGH
        assert config.template_dir == "/templates"


class TestTestTemplate:
    """Tests for TestTemplate dataclass."""

    def test_template_creation(self):
        """Test TestTemplate creation with actual interface."""
        template = TestTemplate(
            template_id="basic_intent_test",
            name_pattern="Intent Test: {intent_name}",
            base_test={
                "category": "intent_recognition",
                "priority": "medium",
                "turns": [
                    {
                        "turn_number": 1,
                        "role": "user",
                        "input": "{user_input}",
                        "expected_intent": "{expected_intent}",
                    }
                ],
                "expected_outcome": {"success_condition": "all_pass"},
            },
            parameters=[
                {"intent_name": "greet", "user_input": "Hello", "expected_intent": "greet"},
                {"intent_name": "goodbye", "user_input": "Bye", "expected_intent": "goodbye"},
            ],
        )
        assert template.template_id == "basic_intent_test"
        assert "{intent_name}" in template.name_pattern
        assert len(template.parameters) == 2

    def test_template_with_inheritance(self):
        """Test TestTemplate with inherit_from."""
        template = TestTemplate(
            template_id="extended_test",
            name_pattern="Extended: {name}",
            base_test={"additional_field": "value"},
            inherit_from="basic_intent_test",
        )
        assert template.inherit_from == "basic_intent_test"


class TestConversationTestLoader:
    """Tests for ConversationTestLoader class."""

    @pytest.fixture
    def loader(self):
        """Create a default loader instance."""
        return ConversationTestLoader()

    @pytest.fixture
    def loader_lenient(self):
        """Create a lenient loader instance."""
        config = LoaderConfig(strict_validation=False, allow_unknown_fields=True)
        return ConversationTestLoader(config=config)

    @pytest.fixture
    def sample_yaml(self, tmp_path):
        """Create a sample YAML test file."""
        yaml_content = """
test_id: test_greet_001
name: Basic greeting test
description: Test basic greeting intent recognition
category: intent_recognition
priority: high
turns:
  - turn_number: 1
    role: user
    input: "Hello there!"
    expected_intent: greet
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "test_greet.yaml"
        yaml_file.write_text(yaml_content)
        return yaml_file

    @pytest.fixture
    def invalid_yaml(self, tmp_path):
        """Create an invalid YAML test file (missing required fields)."""
        yaml_content = """
name: Missing test_id
description: This test is missing required test_id
turns: []
"""
        yaml_file = tmp_path / "invalid_test.yaml"
        yaml_file.write_text(yaml_content)
        return yaml_file

    def test_loader_initialization(self, loader):
        """Test loader initialization."""
        assert loader.config is not None
        assert loader.config.strict_validation is True

    def test_loader_with_custom_config(self):
        """Test loader with custom config."""
        config = LoaderConfig(
            strict_validation=False,
            default_category=TestCategory.PERFORMANCE,
        )
        loader = ConversationTestLoader(config=config)
        assert loader.config.strict_validation is False
        assert loader.config.default_category == TestCategory.PERFORMANCE

    def test_load_and_validate_valid_file(self, loader, sample_yaml):
        """Test load_and_validate with a valid YAML file."""
        result = loader.load_and_validate(str(sample_yaml))
        assert result.valid is True
        assert result.test is not None
        assert result.test.test_id == "test_greet_001"
        assert result.test.category == TestCategory.INTENT_RECOGNITION
        assert result.test.priority == TestPriority.HIGH

    def test_load_test_valid_file(self, loader, sample_yaml):
        """Test load_test with a valid file."""
        test = loader.load_test(str(sample_yaml))
        assert test.test_id == "test_greet_001"
        assert test.name == "Basic greeting test"
        assert len(test.turns) == 1

    def test_load_yaml_turns(self, loader, sample_yaml):
        """Test that turns are loaded correctly."""
        test = loader.load_test(str(sample_yaml))
        assert len(test.turns) == 1
        turn = test.turns[0]
        assert turn.turn_number == 1
        assert turn.role == TurnRole.USER
        assert turn.input == "Hello there!"
        assert turn.expected_intent == "greet"

    def test_validate_test_dict(self, loader):
        """Test validate_test with a dict."""
        test_data = {
            "test_id": "test_dict_001",
            "name": "Dict test",
            "turns": [
                {"turn_number": 1, "role": "user", "input": "Hello"}
            ],
            "expected_outcome": {"success_condition": "all_pass"},
        }
        result = loader.validate_test(test_data)
        assert result.valid is True
        assert result.test is not None
        assert result.test.test_id == "test_dict_001"

    def test_load_nonexistent_file(self, loader):
        """Test loading a nonexistent file."""
        result = loader.load_and_validate("/nonexistent/path/test.yaml")
        assert result.valid is False
        assert result.error_count > 0

    def test_load_test_raises_on_invalid(self, loader):
        """Test load_test raises ValueError on invalid file."""
        with pytest.raises(ValueError):
            loader.load_test("/nonexistent/path/test.yaml")

    def test_load_directory_with_pattern(self, loader, tmp_path):
        """Test loading all tests from a directory pattern."""
        # Create multiple test files
        for i in range(3):
            yaml_content = f"""
test_id: test_{i:03d}
name: Test {i}
description: Test number {i}
category: intent_recognition
priority: medium
turns:
  - turn_number: 1
    role: user
    input: "Test input {i}"
expected_outcome:
  success_condition: all_pass
"""
            (tmp_path / f"test_{i}.yaml").write_text(yaml_content)

        tests = loader.load_directory(str(tmp_path / "*.yaml"))
        assert len(tests) == 3


class TestConversationTestLoaderValidation:
    """Tests for loader validation functionality."""

    @pytest.fixture
    def loader(self):
        """Create a default loader instance."""
        return ConversationTestLoader()

    def test_validate_missing_test_id(self, loader, tmp_path):
        """Test validation catches missing test_id."""
        yaml_content = """
name: No ID test
description: Missing test_id
category: intent_recognition
priority: medium
turns:
  - turn_number: 1
    role: user
    input: "Hello"
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "missing_id.yaml"
        yaml_file.write_text(yaml_content)

        result = loader.load_and_validate(str(yaml_file))
        assert result.valid is False
        # Should have an error about missing test_id
        error_messages = [e.message for e in result.errors]
        assert any("test_id" in msg for msg in error_messages)

    def test_validate_missing_name(self, loader, tmp_path):
        """Test validation catches missing name."""
        yaml_content = """
test_id: test_no_name
description: Missing name
category: intent_recognition
turns:
  - turn_number: 1
    role: user
    input: "Hello"
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "missing_name.yaml"
        yaml_file.write_text(yaml_content)

        result = loader.load_and_validate(str(yaml_file))
        assert result.valid is False
        error_messages = [e.message for e in result.errors]
        assert any("name" in msg for msg in error_messages)

    def test_validate_invalid_category(self, loader, tmp_path):
        """Test validation catches invalid category."""
        yaml_content = """
test_id: test_invalid_category
name: Invalid category test
description: Has invalid category
category: not_a_valid_category
priority: medium
turns:
  - turn_number: 1
    role: user
    input: "Hello"
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "invalid_category.yaml"
        yaml_file.write_text(yaml_content)

        result = loader.load_and_validate(str(yaml_file))
        # Should have an error about invalid category
        assert result.valid is False

    def test_validate_empty_turns(self, loader, tmp_path):
        """Test validation of test with empty turns."""
        yaml_content = """
test_id: test_no_turns
name: No turns test
description: Has no turns
category: intent_recognition
priority: medium
turns: []
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "no_turns.yaml"
        yaml_file.write_text(yaml_content)

        result = loader.load_and_validate(str(yaml_file))
        # Should fail because turns must have at least one turn
        assert result.valid is False

    def test_validate_missing_turns(self, loader, tmp_path):
        """Test validation catches missing turns field."""
        yaml_content = """
test_id: test_missing_turns
name: Missing turns test
description: No turns field
category: intent_recognition
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "missing_turns.yaml"
        yaml_file.write_text(yaml_content)

        result = loader.load_and_validate(str(yaml_file))
        assert result.valid is False


class TestConversationTestLoaderEdgeCases:
    """Edge case tests for ConversationTestLoader."""

    @pytest.fixture
    def loader(self):
        """Create a default loader instance."""
        return ConversationTestLoader()

    def test_load_empty_file(self, loader, tmp_path):
        """Test loading an empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        yaml_file.write_text("")

        result = loader.load_and_validate(str(yaml_file))
        assert result.valid is False

    def test_load_malformed_yaml(self, loader, tmp_path):
        """Test loading malformed YAML."""
        yaml_file = tmp_path / "malformed.yaml"
        yaml_file.write_text("this: is: not: valid: yaml:")

        result = loader.load_and_validate(str(yaml_file))
        assert result.valid is False

    def test_unicode_in_test(self, loader, tmp_path):
        """Test handling of unicode characters."""
        yaml_content = """
test_id: test_unicode
name: "Unicode test \u4f60\u597d\u4e16\u754c"
description: Test with unicode characters
category: intent_recognition
priority: medium
turns:
  - turn_number: 1
    role: user
    input: "Bonjour! Comment ça va? \U0001F389"
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "unicode.yaml"
        yaml_file.write_text(yaml_content, encoding="utf-8")

        result = loader.load_and_validate(str(yaml_file))
        assert result.valid is True
        assert result.test is not None

    def test_large_test_file(self, loader, tmp_path):
        """Test loading a file with many turns."""
        turns_yaml = "\n".join([
            f"""  - turn_number: {i}
    role: user
    input: "Test turn {i}" """
            for i in range(1, 11)
        ])

        yaml_content = f"""
test_id: test_large
name: Large test
description: Test with many turns
category: dialogue_flow
priority: medium
turns:
{turns_yaml}
expected_outcome:
  success_condition: all_pass
"""
        yaml_file = tmp_path / "large.yaml"
        yaml_file.write_text(yaml_content)

        result = loader.load_and_validate(str(yaml_file))
        assert result.valid is True
        assert result.test is not None
        assert len(result.test.turns) == 10


class TestConversationTestLoaderTemplates:
    """Tests for template functionality."""

    @pytest.fixture
    def loader(self):
        """Create a default loader instance."""
        return ConversationTestLoader()

    def test_register_template(self, loader):
        """Test registering a template."""
        template = TestTemplate(
            template_id="test_template",
            name_pattern="Test: {name}",
            base_test={
                "category": "intent_recognition",
                "turns": [{"turn_number": 1, "role": "user", "input": "{input}"}],
                "expected_outcome": {"success_condition": "all_pass"},
            },
        )
        loader.register_template(template)
        assert "test_template" in loader._templates

    def test_expand_template(self, loader):
        """Test expanding a template."""
        template = TestTemplate(
            template_id="greet_template",
            name_pattern="Greeting Test: {greeting_type}",
            base_test={
                "category": "intent_recognition",
                "priority": "medium",
                "turns": [
                    {
                        "turn_number": 1,
                        "role": "user",
                        "input": "{greeting_input}",
                        "expected_intent": "greet",
                    }
                ],
                "expected_outcome": {"success_condition": "all_pass"},
            },
        )
        loader.register_template(template)

        test = loader.expand_template(
            "greet_template",
            {"greeting_type": "formal", "greeting_input": "Good morning"},
        )
        assert test is not None
        assert "formal" in test.name
        assert test.turns[0].input == "Good morning"

    def test_expand_unknown_template(self, loader):
        """Test expanding an unknown template raises error."""
        with pytest.raises(KeyError):
            loader.expand_template("nonexistent", {})

    def test_load_template_file(self, loader, tmp_path):
        """Test loading a template from file."""
        template_content = """
template_id: file_template
name_pattern: "File Test: {test_name}"
base_test:
  category: quality_assurance
  priority: low
  turns:
    - turn_number: 1
      role: user
      input: "{user_message}"
  expected_outcome:
    success_condition: all_pass
parameters:
  - test_name: basic
    user_message: Hello
"""
        template_file = tmp_path / "template.yaml"
        template_file.write_text(template_content)

        template = loader.load_template(str(template_file))
        assert template.template_id == "file_template"
        assert len(template.parameters) == 1


class TestConversationTestLoaderSuites:
    """Tests for test suite loading."""

    @pytest.fixture
    def loader(self):
        """Create a default loader instance."""
        return ConversationTestLoader()

    def test_load_suite(self, loader, tmp_path):
        """Test loading a test suite."""
        suite_content = """
suite_id: test_suite_001
name: Basic Test Suite
description: A collection of basic tests
tests:
  - test_id: suite_test_001
    name: Suite Test 1
    turns:
      - turn_number: 1
        role: user
        input: "Hello"
    expected_outcome:
      success_condition: all_pass
  - test_id: suite_test_002
    name: Suite Test 2
    turns:
      - turn_number: 1
        role: user
        input: "Goodbye"
    expected_outcome:
      success_condition: all_pass
"""
        suite_file = tmp_path / "suite.yaml"
        suite_file.write_text(suite_content)

        suite = loader.load_suite(str(suite_file))
        assert suite.suite_id == "test_suite_001"
        assert suite.name == "Basic Test Suite"
        assert len(suite.tests) == 2

    def test_load_suite_nonexistent(self, loader):
        """Test loading nonexistent suite raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            loader.load_suite("/nonexistent/suite.yaml")

    def test_load_empty_suite(self, loader, tmp_path):
        """Test loading empty suite raises ValueError."""
        suite_file = tmp_path / "empty_suite.yaml"
        suite_file.write_text("")

        with pytest.raises(ValueError):
            loader.load_suite(str(suite_file))
