"""Tests for LUI Component Types."""

import pytest
from baml_client.types import (
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    ComponentParameter,
    ParameterType,
    ValidationRule,
    ValidationRuleType,
    FeedbackConfig,
    AccessibilityConfig,
    ContextRequirement,
    ContextType,
    ExecutionContext,
    ResourceReference,
    ConversationTurn,
    ConversationRole,
    ContextValidationResult,
    UtteranceMatch,
    ExtractedParameter,
)


class TestLUIComponentTypes:
    """Test LUI component type definitions."""

    def test_lui_component_type_enum_values(self):
        """Verify all expected component types exist."""
        expected_types = {
            "ACTION",
            "QUERY",
            "NAVIGATION",
            "INPUT",
            "CONFIRMATION",
            "FEEDBACK",
        }
        actual_types = {t.name for t in LUIComponentType}
        assert actual_types == expected_types

    def test_parameter_type_enum_values(self):
        """Verify all expected parameter types exist."""
        expected_types = {
            "STRING",
            "NUMBER",
            "BOOLEAN",
            "DATE",
            "ENUM",
            "ENTITY",
            "LIST",
        }
        actual_types = {t.name for t in ParameterType}
        assert actual_types == expected_types

    def test_context_type_enum_values(self):
        """Verify all expected context types exist."""
        expected_types = {
            "USER_AUTHENTICATED",
            "RESOURCE_SELECTED",
            "PREVIOUS_ACTION_COMPLETE",
            "PERMISSION_GRANTED",
            "DATA_AVAILABLE",
            "SESSION_ACTIVE",
            "FEATURE_ENABLED",
        }
        actual_types = {t.name for t in ContextType}
        assert actual_types == expected_types


class TestLUIComponentCreation:
    """Test creating LUI component instances."""

    def test_create_action_component(self):
        """Test creating a basic ACTION component."""
        feedback = FeedbackConfig(
            success_template="Message sent successfully to {recipient}",
            error_template="Failed to send message: {error}",
            progress_template="Sending message...",
            confirmation_required=True,
            confirmation_prompt="Send this message to {recipient}?",
        )

        invocation = InvocationPattern(
            primary_phrase="send message",
            alternate_phrases=["send a message", "message", "text"],
            examples=[
                "send a message to John",
                "message Sarah about the meeting",
                "text the team about the update",
            ],
            context_requirements=None,
        )

        param = ComponentParameter(
            name="recipient",
            param_type=ParameterType.ENTITY,
            description="The person or group to send the message to",
            required=True,
            default_value=None,
            extraction_hints=["to", "for", "recipient"],
            validation=None,
        )

        component = LUIComponent(
            component_id="send-message",
            component_type=LUIComponentType.ACTION,
            intent="Send a message to another user or group",
            invocation=invocation,
            parameters=[param],
            feedback=feedback,
            accessibility=None,
        )

        assert component.component_id == "send-message"
        assert component.component_type == LUIComponentType.ACTION
        assert len(component.parameters) == 1
        assert component.feedback.confirmation_required is True

    def test_create_query_component(self):
        """Test creating a QUERY component."""
        feedback = FeedbackConfig(
            success_template="Found {count} results for '{query}'",
            error_template="Search failed: {error}",
            progress_template=None,
            confirmation_required=False,
            confirmation_prompt=None,
        )

        invocation = InvocationPattern(
            primary_phrase="search",
            alternate_phrases=["find", "look for", "search for"],
            examples=[
                "search for quarterly reports",
                "find documents about marketing",
                "look for files from last week",
            ],
            context_requirements=None,
        )

        component = LUIComponent(
            component_id="search-documents",
            component_type=LUIComponentType.QUERY,
            intent="Search for documents in the library",
            invocation=invocation,
            parameters=[],
            feedback=feedback,
            accessibility=None,
        )

        assert component.component_type == LUIComponentType.QUERY
        assert component.feedback.confirmation_required is False


class TestContextTypes:
    """Test context-related types."""

    def test_create_context_requirement(self):
        """Test creating a context requirement."""
        req = ContextRequirement(
            context_type=ContextType.USER_AUTHENTICATED,
            description="User must be logged in to send messages",
            fallback_action="Please log in first",
            error_message="You need to be logged in to send messages",
        )

        assert req.context_type == ContextType.USER_AUTHENTICATED
        assert req.fallback_action is not None

    def test_create_execution_context(self):
        """Test creating an execution context."""
        resource = ResourceReference(
            resource_type="document",
            resource_id="doc-123",
            display_name="Q4 Report",
        )

        turn = ConversationTurn(
            role=ConversationRole.USER,
            content="Search for quarterly reports",
            timestamp="2025-01-15T10:30:00Z",
            component_id=None,
        )

        ctx = ExecutionContext(
            session_id="sess-abc123",
            user_id="user-456",
            authenticated=True,
            permissions=["read", "write"],
            active_resources=[resource],
            conversation_history=[turn],
            feature_flags=["new-search-ui"],
        )

        assert ctx.authenticated is True
        assert len(ctx.active_resources) == 1
        assert ctx.active_resources[0].resource_type == "document"


class TestValidation:
    """Test validation types."""

    def test_create_validation_rules(self):
        """Test creating validation rules for parameters."""
        min_length = ValidationRule(
            rule_type=ValidationRuleType.MIN_LENGTH,
            value="1",
            error_message="Message cannot be empty",
        )

        max_length = ValidationRule(
            rule_type=ValidationRuleType.MAX_LENGTH,
            value="1000",
            error_message="Message is too long (max 1000 characters)",
        )

        param = ComponentParameter(
            name="message_content",
            param_type=ParameterType.STRING,
            description="The message content to send",
            required=True,
            default_value=None,
            extraction_hints=["message", "saying", "content"],
            validation=[min_length, max_length],
        )

        assert param.validation is not None
        assert len(param.validation) == 2
        assert param.validation[0].rule_type == ValidationRuleType.MIN_LENGTH


class TestUtteranceMatching:
    """Test utterance matching types."""

    def test_create_utterance_match(self):
        """Test creating an utterance match result."""
        extracted = ExtractedParameter(
            parameter_name="recipient",
            extracted_value="John",
            confidence=0.95,
        )

        match = UtteranceMatch(
            matches=True,
            confidence=0.92,
            extracted_parameters=[extracted],
            missing_required_parameters=[],
            clarification_needed=None,
        )

        assert match.matches is True
        assert match.confidence > 0.9
        assert len(match.extracted_parameters) == 1

    def test_create_partial_match_needing_clarification(self):
        """Test a partial match that needs clarification."""
        match = UtteranceMatch(
            matches=True,
            confidence=0.75,
            extracted_parameters=[],
            missing_required_parameters=["recipient"],
            clarification_needed="Who would you like to send the message to?",
        )

        assert match.matches is True
        assert len(match.missing_required_parameters) == 1
        assert match.clarification_needed is not None


class TestAccessibility:
    """Test accessibility configuration."""

    def test_create_accessibility_config(self):
        """Test creating accessibility configuration."""
        config = AccessibilityConfig(
            screen_reader_label="Send message button",
            keyboard_shortcut="Ctrl+Enter",
            voice_hints=["send message", "submit"],
            haptic_feedback=True,
        )

        assert config.screen_reader_label is not None
        assert config.keyboard_shortcut == "Ctrl+Enter"
        assert config.haptic_feedback is True
