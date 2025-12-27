"""Simulator context and configuration types."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum

from baml_client.types import (
    ConversationContext,
    ConversationMessage,
    MessageRole,
    ResponseStyle,
    ResponseTone,
    FormalityLevel,
    UserContext,
    ExpertiseLevel,
    InterfaceSchema,
)


class SimulatorMode(Enum):
    """Operating modes for the simulator."""

    INTERACTIVE = "interactive"  # Normal conversation mode
    DEBUG = "debug"  # Shows internal state
    VERBOSE = "verbose"  # Shows all processing steps
    QUIET = "quiet"  # Minimal output


@dataclass
class SimulatorConfig:
    """Configuration for the LUI simulator."""

    # Response style settings
    tone: ResponseTone = ResponseTone.FRIENDLY
    formality: FormalityLevel = FormalityLevel.NEUTRAL

    # Simulation settings
    simulate_latency: bool = False
    latency_ms: int = 500
    auto_confirm: bool = False  # Auto-confirm confirmation prompts

    # Context settings
    max_history_length: int = 10
    expertise_level: ExpertiseLevel = ExpertiseLevel.INTERMEDIATE

    # Debug settings
    mode: SimulatorMode = SimulatorMode.INTERACTIVE
    log_to_file: bool = False
    log_file_path: str | None = None

    def get_response_style(self) -> ResponseStyle:
        """Create a ResponseStyle from config settings."""
        return ResponseStyle(
            tone=self.tone,
            formality=self.formality,
            personality=None,
            brand_voice=None,
        )

    def get_user_context(self, interaction_count: int = 0) -> UserContext:
        """Create a UserContext from config settings."""
        return UserContext(
            user_id="simulator-user",
            preferences=None,
            interaction_count=interaction_count,
            expertise_level=self.expertise_level,
            accessibility_needs=None,
            locale="en-US",
            previous_responses=None,
        )


@dataclass
class SimulatorContext:
    """Manages conversation context and state for the simulator."""

    schema: InterfaceSchema
    config: SimulatorConfig = field(default_factory=SimulatorConfig)

    # Conversation state
    messages: list[ConversationMessage] = field(default_factory=list)
    current_state: str | None = None
    active_entity: str | None = None
    active_flow_id: str | None = None

    # Session metadata
    session_id: str = field(default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S"))
    started_at: datetime = field(default_factory=datetime.now)
    interaction_count: int = 0

    # Variable storage for flows
    variables: dict[str, Any] = field(default_factory=dict)

    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation history."""
        message = ConversationMessage(
            role=MessageRole.USER,
            content=content,
            timestamp=datetime.now().isoformat(),
            extracted_intent=None,
        )
        self.messages.append(message)
        self._trim_history()

    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation history."""
        message = ConversationMessage(
            role=MessageRole.ASSISTANT,
            content=content,
            timestamp=datetime.now().isoformat(),
            extracted_intent=None,
        )
        self.messages.append(message)
        self._trim_history()

    def _trim_history(self) -> None:
        """Keep only the most recent messages based on config."""
        if len(self.messages) > self.config.max_history_length:
            self.messages = self.messages[-self.config.max_history_length :]

    def get_conversation_context(self) -> ConversationContext:
        """Get the current conversation context for BAML functions."""
        return ConversationContext(
            recent_messages=self.messages,
            current_state=self.current_state,
            active_entity=self.active_entity,
            user_preferences=None,
        )

    def set_variable(self, name: str, value: Any) -> None:
        """Store a variable in the context."""
        self.variables[name] = value

    def get_variable(self, name: str, default: Any = None) -> Any:
        """Retrieve a variable from the context."""
        return self.variables.get(name, default)

    def clear_variables(self) -> None:
        """Clear all stored variables."""
        self.variables.clear()

    def reset(self) -> None:
        """Reset the context to initial state."""
        self.messages.clear()
        self.current_state = None
        self.active_entity = None
        self.active_flow_id = None
        self.variables.clear()
        self.interaction_count = 0

    def get_debug_info(self) -> dict[str, Any]:
        """Get debug information about the current context."""
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "interaction_count": self.interaction_count,
            "message_count": len(self.messages),
            "current_state": self.current_state,
            "active_entity": self.active_entity,
            "active_flow_id": self.active_flow_id,
            "variables": self.variables,
            "schema_name": self.schema.name,
            "component_count": len(self.schema.components),
            "flow_count": len(self.schema.flows) if self.schema.flows else 0,
        }
