"""Conversation logging for the LUI simulator."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from enum import Enum
import json
from pathlib import Path


class EntryType(Enum):
    """Types of log entries."""

    USER_INPUT = "user_input"
    INTENT_EXTRACTED = "intent_extracted"
    ACTION_EXECUTED = "action_executed"
    RESPONSE_GENERATED = "response_generated"
    ERROR = "error"
    DEBUG = "debug"
    SYSTEM = "system"


@dataclass
class ConversationEntry:
    """A single entry in the conversation log."""

    entry_type: EntryType
    timestamp: datetime
    content: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert entry to dictionary for serialization."""
        return {
            "type": self.entry_type.value,
            "timestamp": self.timestamp.isoformat(),
            "content": self.content,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversationEntry":
        """Create entry from dictionary."""
        return cls(
            entry_type=EntryType(data["type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            content=data["content"],
            metadata=data.get("metadata"),
        )


@dataclass
class ConversationLogger:
    """Logs conversation interactions for debugging and analysis."""

    session_id: str
    entries: list[ConversationEntry] = field(default_factory=list)
    log_file_path: Path | None = None

    def log(
        self,
        entry_type: EntryType,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationEntry:
        """Add a new log entry."""
        entry = ConversationEntry(
            entry_type=entry_type,
            timestamp=datetime.now(),
            content=content,
            metadata=metadata,
        )
        self.entries.append(entry)

        # Write to file if configured
        if self.log_file_path:
            self._append_to_file(entry)

        return entry

    def log_user_input(self, user_input: str) -> ConversationEntry:
        """Log a user input."""
        return self.log(EntryType.USER_INPUT, user_input)

    def log_intent(
        self,
        intent_name: str,
        confidence: float,
        target_component: str,
        parameters: dict[str, str] | None = None,
    ) -> ConversationEntry:
        """Log an extracted intent."""
        return self.log(
            EntryType.INTENT_EXTRACTED,
            f"Intent: {intent_name} -> {target_component}",
            metadata={
                "intent_name": intent_name,
                "confidence": confidence,
                "target_component": target_component,
                "parameters": parameters,
            },
        )

    def log_action(
        self,
        action_name: str,
        status: str,
        result_data: str | None = None,
    ) -> ConversationEntry:
        """Log an action execution."""
        return self.log(
            EntryType.ACTION_EXECUTED,
            f"Action: {action_name} -> {status}",
            metadata={
                "action_name": action_name,
                "status": status,
                "result_data": result_data,
            },
        )

    def log_response(
        self,
        response_text: str,
        response_type: str,
        has_follow_up: bool = False,
    ) -> ConversationEntry:
        """Log a generated response."""
        return self.log(
            EntryType.RESPONSE_GENERATED,
            response_text,
            metadata={
                "response_type": response_type,
                "has_follow_up": has_follow_up,
            },
        )

    def log_error(self, error_message: str, exception: Exception | None = None) -> ConversationEntry:
        """Log an error."""
        metadata = {"error_type": type(exception).__name__} if exception else None
        return self.log(EntryType.ERROR, error_message, metadata=metadata)

    def log_debug(self, message: str, data: dict[str, Any] | None = None) -> ConversationEntry:
        """Log debug information."""
        return self.log(EntryType.DEBUG, message, metadata=data)

    def log_system(self, message: str) -> ConversationEntry:
        """Log a system message."""
        return self.log(EntryType.SYSTEM, message)

    def _append_to_file(self, entry: ConversationEntry) -> None:
        """Append an entry to the log file."""
        if not self.log_file_path:
            return

        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file_path, "a") as f:
            f.write(json.dumps(entry.to_dict()) + "\n")

    def save_session(self, path: Path | None = None) -> Path:
        """Save the entire session to a JSON file."""
        save_path = path or self.log_file_path or Path(f"logs/session_{self.session_id}.json")
        save_path.parent.mkdir(parents=True, exist_ok=True)

        session_data = {
            "session_id": self.session_id,
            "entry_count": len(self.entries),
            "entries": [e.to_dict() for e in self.entries],
        }

        with open(save_path, "w") as f:
            json.dump(session_data, f, indent=2)

        return save_path

    @classmethod
    def load_session(cls, path: Path) -> "ConversationLogger":
        """Load a session from a JSON file."""
        with open(path) as f:
            data = json.load(f)

        logger = cls(session_id=data["session_id"])
        logger.entries = [ConversationEntry.from_dict(e) for e in data["entries"]]
        return logger

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the conversation log."""
        type_counts: dict[str, int] = {}
        for entry in self.entries:
            type_name = entry.entry_type.value
            type_counts[type_name] = type_counts.get(type_name, 0) + 1

        return {
            "session_id": self.session_id,
            "total_entries": len(self.entries),
            "entry_counts": type_counts,
            "first_entry": self.entries[0].timestamp.isoformat() if self.entries else None,
            "last_entry": self.entries[-1].timestamp.isoformat() if self.entries else None,
        }

    def get_conversation_transcript(self) -> str:
        """Get a human-readable transcript of the conversation."""
        lines = []
        for entry in self.entries:
            if entry.entry_type == EntryType.USER_INPUT:
                lines.append(f"User: {entry.content}")
            elif entry.entry_type == EntryType.RESPONSE_GENERATED:
                lines.append(f"LUI: {entry.content}")
            elif entry.entry_type == EntryType.ERROR:
                lines.append(f"[Error: {entry.content}]")
            elif entry.entry_type == EntryType.SYSTEM:
                lines.append(f"[System: {entry.content}]")
        return "\n".join(lines)
