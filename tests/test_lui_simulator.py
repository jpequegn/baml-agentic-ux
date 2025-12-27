"""Tests for LUI Simulator."""

import pytest
from datetime import datetime
from pathlib import Path
import json
import tempfile

from baml_client.types import (
    InterfaceSchema,
    DomainInfo,
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
    ResponseTone,
    FormalityLevel,
    ExpertiseLevel,
    MessageRole,
    ResponseType,
)

# Import simulator modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lui_simulator.context import SimulatorContext, SimulatorConfig, SimulatorMode
from lui_simulator.logger import ConversationLogger, ConversationEntry, EntryType


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
def sample_component() -> LUIComponent:
    """Create a sample LUI component for testing."""
    return LUIComponent(
        component_id="create-task",
        component_type=LUIComponentType.ACTION,
        intent="Create a new task",
        invocation=InvocationPattern(
            primary_phrase="create task",
            alternate_phrases=["add task", "new task"],
            examples=["Create a task to review code"],
            context_requirements=None,
        ),
        parameters=[],
        feedback=FeedbackConfig(
            success_template="Task '{title}' created successfully",
            error_template="Could not create task: {error}",
            progress_template=None,
            confirmation_required=False,
            confirmation_prompt=None,
        ),
        accessibility=None,
    )


@pytest.fixture
def sample_schema(sample_component: LUIComponent) -> InterfaceSchema:
    """Create a sample interface schema for testing."""
    domain = DomainInfo(
        domain_name="task-management",
        subdomain=None,
        description="Task tracking",
        key_concepts=["tasks", "projects"],
        terminology=None,
    )

    list_component = LUIComponent(
        component_id="list-tasks",
        component_type=LUIComponentType.QUERY,
        intent="List all tasks",
        invocation=InvocationPattern(
            primary_phrase="list tasks",
            alternate_phrases=["show tasks", "my tasks"],
            examples=["Show me my tasks"],
            context_requirements=None,
        ),
        parameters=[],
        feedback=FeedbackConfig(
            success_template="Here are your tasks",
            error_template="Could not list tasks",
            progress_template=None,
            confirmation_required=False,
            confirmation_prompt=None,
        ),
        accessibility=None,
    )

    return InterfaceSchema(
        schema_id="test-schema-v1",
        name="Test Task Manager",
        description="A test task management schema",
        version="1.0.0",
        domain=domain,
        components=[sample_component, list_component],
        flows=[],
        entities=[],
        global_context=None,
    )


@pytest.fixture
def simulator_config() -> SimulatorConfig:
    """Create a simulator configuration for testing."""
    return SimulatorConfig(
        tone=ResponseTone.FRIENDLY,
        formality=FormalityLevel.NEUTRAL,
        mode=SimulatorMode.INTERACTIVE,
        max_history_length=5,
        expertise_level=ExpertiseLevel.INTERMEDIATE,
    )


# ============================================
# Test SimulatorConfig
# ============================================

class TestSimulatorConfig:
    """Test SimulatorConfig creation and methods."""

    def test_default_config(self):
        """Test creating default configuration."""
        config = SimulatorConfig()

        assert config.tone == ResponseTone.FRIENDLY
        assert config.formality == FormalityLevel.NEUTRAL
        assert config.mode == SimulatorMode.INTERACTIVE
        assert config.simulate_latency is False
        assert config.max_history_length == 10

    def test_get_response_style(self):
        """Test getting response style from config."""
        config = SimulatorConfig(
            tone=ResponseTone.PROFESSIONAL,
            formality=FormalityLevel.FORMAL,
        )

        style = config.get_response_style()

        assert style.tone == ResponseTone.PROFESSIONAL
        assert style.formality == FormalityLevel.FORMAL

    def test_get_user_context(self):
        """Test getting user context from config."""
        config = SimulatorConfig(expertise_level=ExpertiseLevel.EXPERT)

        context = config.get_user_context(interaction_count=10)

        assert context.user_id == "simulator-user"
        assert context.expertise_level == ExpertiseLevel.EXPERT
        assert context.interaction_count == 10


# ============================================
# Test SimulatorContext
# ============================================

class TestSimulatorContext:
    """Test SimulatorContext state management."""

    def test_create_context(self, sample_schema: InterfaceSchema):
        """Test creating a simulator context."""
        context = SimulatorContext(schema=sample_schema)

        assert context.schema == sample_schema
        assert context.interaction_count == 0
        assert len(context.messages) == 0
        assert context.current_state is None

    def test_add_user_message(self, sample_schema: InterfaceSchema):
        """Test adding a user message."""
        context = SimulatorContext(schema=sample_schema)

        context.add_user_message("Create a new task")

        assert len(context.messages) == 1
        assert context.messages[0].role == MessageRole.USER
        assert context.messages[0].content == "Create a new task"

    def test_add_assistant_message(self, sample_schema: InterfaceSchema):
        """Test adding an assistant message."""
        context = SimulatorContext(schema=sample_schema)

        context.add_assistant_message("Task created!")

        assert len(context.messages) == 1
        assert context.messages[0].role == MessageRole.ASSISTANT

    def test_trim_history(self, sample_schema: InterfaceSchema):
        """Test that history is trimmed to max length."""
        config = SimulatorConfig(max_history_length=3)
        context = SimulatorContext(schema=sample_schema, config=config)

        # Add more messages than max
        for i in range(5):
            context.add_user_message(f"Message {i}")

        assert len(context.messages) == 3
        assert context.messages[0].content == "Message 2"

    def test_set_and_get_variable(self, sample_schema: InterfaceSchema):
        """Test variable storage."""
        context = SimulatorContext(schema=sample_schema)

        context.set_variable("task_id", "123")
        context.set_variable("priority", "high")

        assert context.get_variable("task_id") == "123"
        assert context.get_variable("priority") == "high"
        assert context.get_variable("missing", "default") == "default"

    def test_reset(self, sample_schema: InterfaceSchema):
        """Test resetting context."""
        context = SimulatorContext(schema=sample_schema)
        context.add_user_message("Test")
        context.current_state = "some-state"
        context.set_variable("key", "value")
        context.interaction_count = 5

        context.reset()

        assert len(context.messages) == 0
        assert context.current_state is None
        assert context.get_variable("key") is None
        assert context.interaction_count == 0

    def test_get_conversation_context(self, sample_schema: InterfaceSchema):
        """Test getting conversation context for BAML."""
        context = SimulatorContext(schema=sample_schema)
        context.add_user_message("Hello")
        context.current_state = "greeting"
        context.active_entity = "user-1"

        conv_context = context.get_conversation_context()

        assert len(conv_context.recent_messages) == 1
        assert conv_context.current_state == "greeting"
        assert conv_context.active_entity == "user-1"

    def test_get_debug_info(self, sample_schema: InterfaceSchema):
        """Test getting debug information."""
        context = SimulatorContext(schema=sample_schema)
        context.interaction_count = 3
        context.current_state = "active"

        info = context.get_debug_info()

        assert info["interaction_count"] == 3
        assert info["current_state"] == "active"
        assert info["schema_name"] == "Test Task Manager"
        assert info["component_count"] == 2


# ============================================
# Test ConversationLogger
# ============================================

class TestConversationLogger:
    """Test conversation logging functionality."""

    def test_create_logger(self):
        """Test creating a conversation logger."""
        logger = ConversationLogger(session_id="test-session")

        assert logger.session_id == "test-session"
        assert len(logger.entries) == 0

    def test_log_user_input(self):
        """Test logging user input."""
        logger = ConversationLogger(session_id="test")

        entry = logger.log_user_input("Hello, world!")

        assert entry.entry_type == EntryType.USER_INPUT
        assert entry.content == "Hello, world!"
        assert len(logger.entries) == 1

    def test_log_intent(self):
        """Test logging extracted intent."""
        logger = ConversationLogger(session_id="test")

        entry = logger.log_intent(
            intent_name="CreateTask",
            confidence=0.95,
            target_component="create-task",
            parameters={"title": "Review PR"},
        )

        assert entry.entry_type == EntryType.INTENT_EXTRACTED
        assert entry.metadata["confidence"] == 0.95
        assert entry.metadata["parameters"]["title"] == "Review PR"

    def test_log_action(self):
        """Test logging action execution."""
        logger = ConversationLogger(session_id="test")

        entry = logger.log_action(
            action_name="create-task",
            status="SUCCESS",
            result_data="Task created",
        )

        assert entry.entry_type == EntryType.ACTION_EXECUTED
        assert entry.metadata["status"] == "SUCCESS"

    def test_log_response(self):
        """Test logging generated response."""
        logger = ConversationLogger(session_id="test")

        entry = logger.log_response(
            response_text="Task created successfully!",
            response_type="CONFIRMATION",
            has_follow_up=True,
        )

        assert entry.entry_type == EntryType.RESPONSE_GENERATED
        assert entry.metadata["has_follow_up"] is True

    def test_log_error(self):
        """Test logging errors."""
        logger = ConversationLogger(session_id="test")

        entry = logger.log_error("Something went wrong", ValueError("test"))

        assert entry.entry_type == EntryType.ERROR
        assert entry.metadata["error_type"] == "ValueError"

    def test_get_summary(self):
        """Test getting log summary."""
        logger = ConversationLogger(session_id="test")
        logger.log_user_input("Hello")
        logger.log_response("Hi there!", "RESULT")
        logger.log_user_input("Create task")

        summary = logger.get_summary()

        assert summary["total_entries"] == 3
        assert summary["entry_counts"]["user_input"] == 2
        assert summary["entry_counts"]["response_generated"] == 1

    def test_get_transcript(self):
        """Test getting conversation transcript."""
        logger = ConversationLogger(session_id="test")
        logger.log_user_input("Hello")
        logger.log_response("Hi there!", "RESULT")
        logger.log_user_input("Create task")
        logger.log_response("Task created!", "CONFIRMATION")

        transcript = logger.get_conversation_transcript()

        assert "User: Hello" in transcript
        assert "LUI: Hi there!" in transcript
        assert "User: Create task" in transcript
        assert "LUI: Task created!" in transcript

    def test_save_and_load_session(self):
        """Test saving and loading session."""
        logger = ConversationLogger(session_id="test-save")
        logger.log_user_input("Test message")
        logger.log_response("Test response", "RESULT")

        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "session.json"
            logger.save_session(save_path)

            # Load and verify
            loaded = ConversationLogger.load_session(save_path)

            assert loaded.session_id == "test-save"
            assert len(loaded.entries) == 2
            assert loaded.entries[0].content == "Test message"


# ============================================
# Test ConversationEntry
# ============================================

class TestConversationEntry:
    """Test ConversationEntry serialization."""

    def test_to_dict(self):
        """Test converting entry to dictionary."""
        entry = ConversationEntry(
            entry_type=EntryType.USER_INPUT,
            timestamp=datetime(2025, 1, 15, 10, 30, 0),
            content="Hello",
            metadata={"key": "value"},
        )

        data = entry.to_dict()

        assert data["type"] == "user_input"
        assert data["content"] == "Hello"
        assert data["metadata"]["key"] == "value"

    def test_from_dict(self):
        """Test creating entry from dictionary."""
        data = {
            "type": "user_input",
            "timestamp": "2025-01-15T10:30:00",
            "content": "Hello",
            "metadata": {"key": "value"},
        }

        entry = ConversationEntry.from_dict(data)

        assert entry.entry_type == EntryType.USER_INPUT
        assert entry.content == "Hello"
        assert entry.metadata["key"] == "value"


# ============================================
# Test Schema Loading
# ============================================

class TestSchemaLoading:
    """Test schema loading functionality."""

    def test_load_schema_from_dict(self):
        """Test loading schema from dictionary."""
        from lui_simulator.simulator import load_schema_from_dict

        data = {
            "schema_id": "test-v1",
            "name": "Test Schema",
            "description": "A test schema",
            "version": "1.0.0",
            "domain": {
                "domain_name": "testing",
                "description": "For testing",
                "key_concepts": ["tests"],
            },
            "components": [
                {
                    "component_id": "test-action",
                    "component_type": "ACTION",
                    "intent": "Do a test action",
                    "invocation": {
                        "primary_phrase": "test action",
                        "alternate_phrases": ["do test"],
                        "examples": ["Run a test"],
                    },
                    "feedback": {
                        "success_template": "Test completed",
                        "error_template": "Test failed",
                    },
                }
            ],
        }

        schema = load_schema_from_dict(data)

        assert schema.schema_id == "test-v1"
        assert schema.name == "Test Schema"
        assert len(schema.components) == 1
        assert schema.components[0].component_id == "test-action"
        assert schema.components[0].component_type == LUIComponentType.ACTION

    def test_load_example_schema(self):
        """Test loading the example schema file."""
        from lui_simulator.simulator import load_schema_from_dict

        schema_path = Path(__file__).parent.parent / "examples" / "task_manager_schema.json"

        if schema_path.exists():
            with open(schema_path) as f:
                data = json.load(f)

            schema = load_schema_from_dict(data)

            assert schema.name == "Task Manager LUI"
            assert len(schema.components) == 7


# ============================================
# Test SimulatorMode
# ============================================

class TestSimulatorMode:
    """Test simulator mode enum."""

    def test_mode_values(self):
        """Verify all simulator modes exist."""
        expected = {"INTERACTIVE", "DEBUG", "VERBOSE", "QUIET"}
        actual = {m.name for m in SimulatorMode}
        assert actual == expected
