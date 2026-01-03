"""Test Loader and Validator for Conversational Testing Framework.

This module provides YAML-based test file loading and validation.

Issue #90 - Task 6.2: Test Loader & Validator
Part of #29 - Phase 6: Conversational Testing Framework
"""

import glob
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Optional, TypeVar, Union

import yaml

from .types import (
    AssertionOperator,
    AssertionSeverity,
    AssertionTarget,
    AssertionType,
    ContextRequirement,
    ConversationAssertion,
    ConversationTest,
    ExecutionOrder,
    ExpectedEntity,
    ExpectedOutcome,
    ExpertiseLevel,
    InitialEntity,
    MatchType,
    MockResponse,
    MockResponseType,
    QualityRequirements,
    QualityThresholds,
    SuccessCondition,
    SystemState,
    TestCategory,
    TestPriority,
    TestSetup,
    TestSuite,
    TestTurn,
    TestUserProfile,
    TurnRole,
)


# ============================================
# Validation Types
# ============================================


class ValidationSeverity(Enum):
    """Severity level of validation errors."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationError:
    """Detailed validation error with location info."""

    message: str
    severity: ValidationSeverity = ValidationSeverity.ERROR
    path: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    field: Optional[str] = None
    expected: Optional[str] = None
    actual: Optional[str] = None

    def __str__(self) -> str:
        """Format error for display."""
        parts = []
        if self.path:
            parts.append(f"{self.path}")
        if self.line is not None:
            parts.append(f"line {self.line}")
        if self.column is not None:
            parts.append(f"col {self.column}")
        if self.field:
            parts.append(f"field '{self.field}'")

        location = ":".join(parts) if parts else "unknown location"
        msg = f"[{self.severity.value.upper()}] {location}: {self.message}"

        if self.expected and self.actual:
            msg += f" (expected: {self.expected}, got: {self.actual})"

        return msg


@dataclass
class ValidationResult:
    """Result of validating a test file or test definition."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)
    test: Optional[ConversationTest] = None
    file_path: Optional[str] = None

    @property
    def error_count(self) -> int:
        """Count of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return len(self.warnings)

    def add_error(self, error: ValidationError) -> None:
        """Add an error to the result."""
        if error.severity == ValidationSeverity.ERROR:
            self.errors.append(error)
            self.valid = False
        elif error.severity == ValidationSeverity.WARNING:
            self.warnings.append(error)
        # INFO level is ignored for validation purposes


@dataclass
class LoaderConfig:
    """Configuration for the test loader."""

    default_category: TestCategory = TestCategory.QUALITY_ASSURANCE
    default_priority: TestPriority = TestPriority.MEDIUM
    strict_validation: bool = True
    allow_unknown_fields: bool = False
    template_dir: Optional[str] = None


# ============================================
# Template Support
# ============================================


@dataclass
class TestTemplate:
    """Template for generating parameterized tests."""

    template_id: str
    name_pattern: str
    base_test: dict[str, Any]
    parameters: list[dict[str, Any]] = field(default_factory=list)
    inherit_from: Optional[str] = None


# ============================================
# Loader Implementation
# ============================================


T = TypeVar("T", bound=Enum)


class ConversationTestLoader:
    """Loads and validates conversation test files from YAML."""

    def __init__(self, config: Optional[LoaderConfig] = None) -> None:
        """Initialize the loader with optional configuration."""
        self.config = config or LoaderConfig()
        self._templates: dict[str, TestTemplate] = {}
        self._loaded_tests: dict[str, ConversationTest] = {}

    def load_test(self, path: str) -> ConversationTest:
        """Load a single test file.

        Args:
            path: Path to the YAML test file.

        Returns:
            ConversationTest instance.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the file is invalid.
        """
        result = self.load_and_validate(path)
        if not result.valid:
            error_messages = "\n".join(str(e) for e in result.errors)
            raise ValueError(f"Invalid test file {path}:\n{error_messages}")
        if result.test is None:
            raise ValueError(f"No test found in {path}")
        return result.test

    def load_and_validate(self, path: str) -> ValidationResult:
        """Load and validate a test file, returning detailed results.

        Args:
            path: Path to the YAML test file.

        Returns:
            ValidationResult with test and any errors/warnings.
        """
        result = ValidationResult(valid=True, file_path=path)

        # Check file exists
        if not os.path.exists(path):
            result.add_error(
                ValidationError(
                    message=f"File not found: {path}",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                )
            )
            return result

        # Parse YAML
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            line = getattr(e, "problem_mark", None)
            result.add_error(
                ValidationError(
                    message=f"YAML parse error: {e}",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    line=line.line + 1 if line else None,
                    column=line.column + 1 if line else None,
                )
            )
            return result

        if data is None:
            result.add_error(
                ValidationError(
                    message="Empty test file",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                )
            )
            return result

        # Validate and convert to ConversationTest
        test = self._validate_and_convert(data, result, path)
        if test:
            result.test = test
            self._loaded_tests[test.test_id] = test

        return result

    def load_directory(
        self,
        pattern: str,
        tags: Optional[list[str]] = None,
        categories: Optional[list[TestCategory]] = None,
        priorities: Optional[list[TestPriority]] = None,
    ) -> list[ConversationTest]:
        """Load tests from files matching a glob pattern.

        Args:
            pattern: Glob pattern for test files (e.g., "tests/conversations/*.yaml").
            tags: Optional list of tags to filter by (any match).
            categories: Optional list of categories to filter by.
            priorities: Optional list of priorities to filter by.

        Returns:
            List of valid ConversationTest instances.

        Raises:
            ValueError: If any test file is invalid (in strict mode).
        """
        tests: list[ConversationTest] = []
        errors: list[ValidationResult] = []

        # Find matching files
        files = glob.glob(pattern, recursive=True)

        for file_path in sorted(files):
            result = self.load_and_validate(file_path)
            if result.valid and result.test:
                # Apply filters
                test = result.test
                if tags and not any(tag in test.tags for tag in tags):
                    continue
                if categories and test.category not in categories:
                    continue
                if priorities and test.priority not in priorities:
                    continue
                tests.append(test)
            elif not result.valid:
                errors.append(result)

        # In strict mode, raise if any errors
        if self.config.strict_validation and errors:
            all_errors = []
            for err_result in errors:
                all_errors.extend(str(e) for e in err_result.errors)
            raise ValueError(f"Invalid test files found:\n" + "\n".join(all_errors))

        return tests

    def load_suite(self, path: str) -> TestSuite:
        """Load a test suite from a YAML file.

        Args:
            path: Path to the suite YAML file.

        Returns:
            TestSuite instance.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the suite is invalid.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Suite file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        if data is None:
            raise ValueError(f"Empty suite file: {path}")

        return self._convert_suite(data, path)

    def validate_test(self, test_data: dict[str, Any]) -> ValidationResult:
        """Validate a test definition dict without loading from file.

        Args:
            test_data: Dictionary containing test definition.

        Returns:
            ValidationResult with validation details.
        """
        result = ValidationResult(valid=True)
        test = self._validate_and_convert(test_data, result)
        if test:
            result.test = test
        return result

    def register_template(self, template: TestTemplate) -> None:
        """Register a test template for reuse.

        Args:
            template: TestTemplate to register.
        """
        self._templates[template.template_id] = template

    def load_template(self, path: str) -> TestTemplate:
        """Load a template from a YAML file.

        Args:
            path: Path to template file.

        Returns:
            TestTemplate instance.
        """
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template file not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        template = TestTemplate(
            template_id=data.get("template_id", Path(path).stem),
            name_pattern=data.get("name_pattern", "{name}"),
            base_test=data.get("base_test", {}),
            parameters=data.get("parameters", []),
            inherit_from=data.get("inherit_from"),
        )

        self.register_template(template)
        return template

    def expand_template(
        self, template_id: str, parameters: dict[str, Any]
    ) -> ConversationTest:
        """Expand a template with parameters to create a test.

        Args:
            template_id: ID of registered template.
            parameters: Parameters to substitute.

        Returns:
            ConversationTest instance.

        Raises:
            KeyError: If template not found.
            ValueError: If expansion fails.
        """
        if template_id not in self._templates:
            raise KeyError(f"Template not found: {template_id}")

        template = self._templates[template_id]

        # Start with base test, apply inheritance if needed
        test_data = dict(template.base_test)
        if template.inherit_from and template.inherit_from in self._templates:
            parent = self._templates[template.inherit_from]
            test_data = self._merge_dicts(parent.base_test, test_data)

        # Substitute parameters
        test_data = self._substitute_parameters(test_data, parameters)

        # Generate name from pattern
        if "name" not in test_data:
            test_data["name"] = template.name_pattern.format(**parameters)

        # Generate test_id if not provided
        if "test_id" not in test_data:
            safe_name = re.sub(r"[^a-zA-Z0-9]", "_", test_data.get("name", "test"))
            test_data["test_id"] = f"template_{template_id}_{safe_name}".lower()

        result = self.validate_test(test_data)
        if not result.valid:
            raise ValueError(
                f"Template expansion failed: {[str(e) for e in result.errors]}"
            )

        return result.test  # type: ignore

    # ============================================
    # Private Validation Methods
    # ============================================

    def _validate_and_convert(
        self,
        data: dict[str, Any],
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> Optional[ConversationTest]:
        """Validate and convert dict to ConversationTest."""
        # Required fields
        if "test_id" not in data:
            result.add_error(
                ValidationError(
                    message="Missing required field 'test_id'",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field="test_id",
                )
            )

        if "name" not in data:
            result.add_error(
                ValidationError(
                    message="Missing required field 'name'",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field="name",
                )
            )

        if "turns" not in data:
            result.add_error(
                ValidationError(
                    message="Missing required field 'turns'",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field="turns",
                )
            )
        elif not isinstance(data["turns"], list):
            result.add_error(
                ValidationError(
                    message="Field 'turns' must be a list",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field="turns",
                    expected="list",
                    actual=type(data["turns"]).__name__,
                )
            )
        elif len(data["turns"]) == 0:
            result.add_error(
                ValidationError(
                    message="Test must have at least one turn",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field="turns",
                )
            )

        # If basic validation failed, return early
        if not result.valid:
            return None

        # Convert turns
        turns: list[TestTurn] = []
        for i, turn_data in enumerate(data["turns"]):
            turn = self._validate_turn(turn_data, i, result, path)
            if turn:
                turns.append(turn)

        # Convert expected_outcome
        expected_outcome = self._validate_expected_outcome(
            data.get("expected_outcome", {}), result, path
        )

        # Convert optional fields
        category = self._parse_enum(
            data.get("category"),
            TestCategory,
            self.config.default_category,
            "category",
            result,
            path,
        )

        priority = self._parse_enum(
            data.get("priority"),
            TestPriority,
            self.config.default_priority,
            "priority",
            result,
            path,
        )

        setup = None
        if "setup" in data:
            setup = self._validate_setup(data["setup"], result, path)

        quality_thresholds = None
        if "quality_thresholds" in data:
            quality_thresholds = self._validate_quality_thresholds(
                data["quality_thresholds"], result, path
            )

        # Check for unknown fields
        if not self.config.allow_unknown_fields:
            known_fields = {
                "test_id",
                "name",
                "description",
                "category",
                "priority",
                "tags",
                "setup",
                "turns",
                "expected_outcome",
                "quality_thresholds",
                "timeout_seconds",
                "metadata",
            }
            unknown = set(data.keys()) - known_fields
            for field_name in unknown:
                result.add_error(
                    ValidationError(
                        message=f"Unknown field '{field_name}'",
                        severity=ValidationSeverity.WARNING,
                        path=path,
                        field=field_name,
                    )
                )

        if not result.valid:
            return None

        return ConversationTest(
            test_id=data["test_id"],
            name=data["name"],
            description=data.get("description"),
            category=category,
            priority=priority,
            tags=data.get("tags", []),
            setup=setup,
            turns=turns,
            expected_outcome=expected_outcome,
            quality_thresholds=quality_thresholds,
            timeout_seconds=data.get("timeout_seconds"),
            metadata=data.get("metadata"),
        )

    def _validate_turn(
        self,
        data: dict[str, Any],
        index: int,
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> Optional[TestTurn]:
        """Validate and convert a turn definition."""
        field_prefix = f"turns[{index}]"

        # Required fields
        if "turn_number" not in data:
            # Auto-assign turn number if not provided
            data["turn_number"] = index + 1

        if "role" not in data:
            result.add_error(
                ValidationError(
                    message=f"Missing required field 'role' in turn {index}",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field=f"{field_prefix}.role",
                )
            )

        if "input" not in data:
            result.add_error(
                ValidationError(
                    message=f"Missing required field 'input' in turn {index}",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field=f"{field_prefix}.input",
                )
            )

        if not result.valid:
            return None

        role = self._parse_enum(
            data.get("role"),
            TurnRole,
            TurnRole.USER,
            f"{field_prefix}.role",
            result,
            path,
        )

        # Convert expected entities
        expected_entities: list[ExpectedEntity] = []
        for j, entity_data in enumerate(data.get("expected_entities", [])):
            entity = self._validate_expected_entity(
                entity_data, f"{field_prefix}.expected_entities[{j}]", result, path
            )
            if entity:
                expected_entities.append(entity)

        # Convert assertions
        assertions: list[ConversationAssertion] = []
        for j, assertion_data in enumerate(data.get("assertions", [])):
            assertion = self._validate_assertion(
                assertion_data, f"{field_prefix}.assertions[{j}]", result, path
            )
            if assertion:
                assertions.append(assertion)

        # Convert context requirements
        context_requirements: list[ContextRequirement] = []
        for j, ctx_data in enumerate(data.get("context_requirements", [])):
            ctx_req = self._validate_context_requirement(
                ctx_data, f"{field_prefix}.context_requirements[{j}]", result, path
            )
            if ctx_req:
                context_requirements.append(ctx_req)

        return TestTurn(
            turn_number=data.get("turn_number", index + 1),
            role=role,
            input=data["input"],
            expected_intent=data.get("expected_intent"),
            expected_entities=expected_entities,
            assertions=assertions,
            context_requirements=context_requirements,
            delay_ms=data.get("delay_ms"),
            metadata=data.get("metadata"),
        )

    def _validate_expected_entity(
        self,
        data: dict[str, Any],
        field_prefix: str,
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> Optional[ExpectedEntity]:
        """Validate and convert an expected entity."""
        if "entity_type" not in data:
            result.add_error(
                ValidationError(
                    message=f"Missing required field 'entity_type'",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field=f"{field_prefix}.entity_type",
                )
            )
            return None

        return ExpectedEntity(
            entity_type=data["entity_type"],
            required=data.get("required", True),
            value=data.get("value"),
            value_pattern=data.get("value_pattern"),
            slot_name=data.get("slot_name"),
        )

    def _validate_assertion(
        self,
        data: dict[str, Any],
        field_prefix: str,
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> Optional[ConversationAssertion]:
        """Validate and convert an assertion."""
        required_fields = ["assertion_id", "assertion_type", "target", "operator"]
        for field_name in required_fields:
            if field_name not in data:
                result.add_error(
                    ValidationError(
                        message=f"Missing required field '{field_name}'",
                        severity=ValidationSeverity.ERROR,
                        path=path,
                        field=f"{field_prefix}.{field_name}",
                    )
                )

        if not result.valid:
            return None

        assertion_type = self._parse_enum(
            data.get("assertion_type"),
            AssertionType,
            AssertionType.CUSTOM,
            f"{field_prefix}.assertion_type",
            result,
            path,
        )

        target = self._parse_enum(
            data.get("target"),
            AssertionTarget,
            AssertionTarget.RESPONSE,
            f"{field_prefix}.target",
            result,
            path,
        )

        operator = self._parse_enum(
            data.get("operator"),
            AssertionOperator,
            AssertionOperator.EQUALS,
            f"{field_prefix}.operator",
            result,
            path,
        )

        severity = self._parse_enum(
            data.get("severity"),
            AssertionSeverity,
            AssertionSeverity.ERROR,
            f"{field_prefix}.severity",
            result,
            path,
        )

        return ConversationAssertion(
            assertion_id=data["assertion_id"],
            assertion_type=assertion_type,
            target=target,
            operator=operator,
            severity=severity,
            expected_value=data.get("expected_value"),
            threshold=data.get("threshold"),
            tolerance=data.get("tolerance"),
            message=data.get("message"),
        )

    def _validate_context_requirement(
        self,
        data: dict[str, Any],
        field_prefix: str,
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> Optional[ContextRequirement]:
        """Validate and convert a context requirement."""
        if "key" not in data:
            result.add_error(
                ValidationError(
                    message="Missing required field 'key'",
                    severity=ValidationSeverity.ERROR,
                    path=path,
                    field=f"{field_prefix}.key",
                )
            )
            return None

        match_type = self._parse_enum(
            data.get("match_type"),
            MatchType,
            MatchType.EXISTS,
            f"{field_prefix}.match_type",
            result,
            path,
        )

        return ContextRequirement(
            key=data["key"],
            match_type=match_type,
            value_match=data.get("value_match"),
        )

    def _validate_expected_outcome(
        self,
        data: dict[str, Any],
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> ExpectedOutcome:
        """Validate and convert expected outcome."""
        success_condition = self._parse_enum(
            data.get("success_condition"),
            SuccessCondition,
            SuccessCondition.ALL_PASS,
            "expected_outcome.success_condition",
            result,
            path,
        )

        quality_requirements = None
        if "quality_requirements" in data:
            qr_data = data["quality_requirements"]
            quality_requirements = QualityRequirements(
                min_coherence=qr_data.get("min_coherence"),
                min_naturalness=qr_data.get("min_naturalness"),
                min_accuracy=qr_data.get("min_accuracy"),
                min_relevance=qr_data.get("min_relevance"),
                max_drift_score=qr_data.get("max_drift_score"),
                min_confidence=qr_data.get("min_confidence"),
            )

        return ExpectedOutcome(
            success_condition=success_condition,
            min_assertions_passed=data.get("min_assertions_passed"),
            required_assertions=data.get("required_assertions", []),
            max_warnings=data.get("max_warnings"),
            final_intent=data.get("final_intent"),
            final_context_state=data.get("final_context_state"),
            quality_requirements=quality_requirements,
        )

    def _validate_setup(
        self,
        data: dict[str, Any],
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> TestSetup:
        """Validate and convert test setup."""
        # Convert initial entities
        initial_entities: list[InitialEntity] = []
        for i, entity_data in enumerate(data.get("initial_entities", [])):
            if "entity_type" in entity_data and "value" in entity_data:
                initial_entities.append(
                    InitialEntity(
                        entity_type=entity_data["entity_type"],
                        value=entity_data["value"],
                        slot_name=entity_data.get("slot_name"),
                        confidence=entity_data.get("confidence"),
                    )
                )
            else:
                result.add_error(
                    ValidationError(
                        message="Initial entity must have 'entity_type' and 'value'",
                        severity=ValidationSeverity.ERROR,
                        path=path,
                        field=f"setup.initial_entities[{i}]",
                    )
                )

        # Convert user profile
        user_profile = None
        if "user_profile" in data:
            up_data = data["user_profile"]
            if "user_id" in up_data:
                expertise_level = self._parse_enum(
                    up_data.get("expertise_level"),
                    ExpertiseLevel,
                    ExpertiseLevel.INTERMEDIATE,
                    "setup.user_profile.expertise_level",
                    result,
                    path,
                )
                user_profile = TestUserProfile(
                    user_id=up_data["user_id"],
                    expertise_level=expertise_level,
                    preferences=up_data.get("preferences"),
                    history_summary=up_data.get("history_summary"),
                    accessibility_needs=up_data.get("accessibility_needs", []),
                )

        # Convert system state
        system_state = None
        if "system_state" in data:
            ss_data = data["system_state"]
            system_state = SystemState(
                active_capabilities=ss_data.get("active_capabilities", []),
                disabled_capabilities=ss_data.get("disabled_capabilities", []),
                rate_limits=ss_data.get("rate_limits"),
                feature_flags=ss_data.get("feature_flags"),
            )

        # Convert mock responses
        mock_responses: list[MockResponse] = []
        for i, mock_data in enumerate(data.get("mock_responses", [])):
            if "trigger_pattern" in mock_data and "response_data" in mock_data:
                response_type = self._parse_enum(
                    mock_data.get("response_type"),
                    MockResponseType,
                    MockResponseType.API_RESPONSE,
                    f"setup.mock_responses[{i}].response_type",
                    result,
                    path,
                )
                mock_responses.append(
                    MockResponse(
                        trigger_pattern=mock_data["trigger_pattern"],
                        response_type=response_type,
                        response_data=mock_data["response_data"],
                        delay_ms=mock_data.get("delay_ms"),
                        fail_after=mock_data.get("fail_after"),
                    )
                )

        return TestSetup(
            initial_context=data.get("initial_context"),
            initial_entities=initial_entities,
            user_profile=user_profile,
            system_state=system_state,
            mock_responses=mock_responses,
            environment_variables=data.get("environment_variables"),
        )

    def _validate_quality_thresholds(
        self,
        data: dict[str, Any],
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> QualityThresholds:
        """Validate and convert quality thresholds."""
        return QualityThresholds(
            coherence_threshold=data.get("coherence_threshold", 0.85),
            naturalness_threshold=data.get("naturalness_threshold", 0.80),
            accuracy_threshold=data.get("accuracy_threshold", 0.90),
            relevance_threshold=data.get("relevance_threshold", 0.75),
            confidence_threshold=data.get("confidence_threshold", 0.70),
            max_drift_threshold=data.get("max_drift_threshold", 0.50),
            latency_threshold_ms=data.get("latency_threshold_ms", 2000),
            strict_mode=data.get("strict_mode", False),
        )

    def _convert_suite(self, data: dict[str, Any], path: str) -> TestSuite:
        """Convert dict to TestSuite."""
        result = ValidationResult(valid=True, file_path=path)

        if "suite_id" not in data:
            raise ValueError(f"Suite must have 'suite_id': {path}")
        if "name" not in data:
            raise ValueError(f"Suite must have 'name': {path}")

        # Load tests - either inline or from paths
        tests: list[ConversationTest] = []

        # Inline tests
        for test_data in data.get("tests", []):
            test = self._validate_and_convert(test_data, result, path)
            if test:
                tests.append(test)

        # Tests from paths
        for test_path in data.get("test_paths", []):
            resolved_path = (
                test_path
                if os.path.isabs(test_path)
                else os.path.join(os.path.dirname(path), test_path)
            )
            loaded_tests = self.load_directory(resolved_path)
            tests.extend(loaded_tests)

        # Convert default setup
        default_setup = None
        if "default_setup" in data:
            default_setup = self._validate_setup(data["default_setup"], result, path)

        # Convert default thresholds
        default_thresholds = None
        if "default_thresholds" in data:
            default_thresholds = self._validate_quality_thresholds(
                data["default_thresholds"], result, path
            )

        execution_order = self._parse_enum(
            data.get("execution_order"),
            ExecutionOrder,
            ExecutionOrder.SEQUENTIAL,
            "execution_order",
            result,
            path,
        )

        return TestSuite(
            suite_id=data["suite_id"],
            name=data["name"],
            description=data.get("description"),
            tests=tests,
            default_setup=default_setup,
            default_thresholds=default_thresholds,
            execution_order=execution_order,
            stop_on_failure=data.get("stop_on_failure", False),
            parallel_execution=data.get("parallel_execution", False),
            tags=data.get("tags", []),
        )

    def _parse_enum(
        self,
        value: Optional[str],
        enum_class: type[T],
        default: T,
        field_name: str,
        result: ValidationResult,
        path: Optional[str] = None,
    ) -> T:
        """Parse a string value to an enum, handling errors gracefully."""
        if value is None:
            return default

        # Try direct match (case-insensitive)
        for member in enum_class:
            if member.value == value or member.name.lower() == str(value).lower():
                return member

        # Not found - add error and return default
        valid_values = [m.value for m in enum_class]
        result.add_error(
            ValidationError(
                message=f"Invalid value for '{field_name}'",
                severity=ValidationSeverity.ERROR,
                path=path,
                field=field_name,
                expected=f"one of {valid_values}",
                actual=str(value),
            )
        )
        return default

    def _substitute_parameters(
        self, data: Any, parameters: dict[str, Any]
    ) -> Any:
        """Recursively substitute {param} placeholders in data."""
        if isinstance(data, str):
            for key, value in parameters.items():
                data = data.replace(f"{{{key}}}", str(value))
            return data
        elif isinstance(data, dict):
            return {k: self._substitute_parameters(v, parameters) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._substitute_parameters(item, parameters) for item in data]
        return data

    def _merge_dicts(
        self, base: dict[str, Any], override: dict[str, Any]
    ) -> dict[str, Any]:
        """Deep merge two dicts, with override taking precedence."""
        result = dict(base)
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dicts(result[key], value)
            else:
                result[key] = value
        return result
