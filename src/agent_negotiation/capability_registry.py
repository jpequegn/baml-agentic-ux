"""
Capability Registry & Discovery Service

Agent discovery and capability matching for Phase 3 agent negotiation.

Issue #55 - Phase 3: Agent-to-Agent Interface Negotiation
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
import re
import threading
import time
import uuid

from src.lui_simulator.agent_types import (
    AgentIdentity,
)
from src.agent_negotiation.agent_card import (
    AgentCard,
    ProtocolType,
)


# ============================================
# Discovery Constraints
# ============================================


class ConstraintType(Enum):
    """Types of constraints for agent discovery."""

    CAPABILITY = "capability"
    PROTOCOL = "protocol"
    COMPLIANCE = "compliance"
    TRUST_LEVEL = "trust_level"
    REGION = "region"
    PROVIDER = "provider"
    VERSION = "version"
    PERFORMANCE = "performance"


class ConstraintOperator(Enum):
    """Comparison operators for constraint matching."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    GREATER_OR_EQUAL = "greater_or_equal"
    LESS_OR_EQUAL = "less_or_equal"
    CONTAINS = "contains"
    IN = "in"
    NOT_IN = "not_in"
    REGEX = "regex"


@dataclass
class DiscoveryConstraint:
    """A constraint for filtering agents in discovery."""

    constraint_type: ConstraintType
    field: str
    operator: ConstraintOperator
    value: str
    weight: float = 1.0
    required: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "constraint_type": self.constraint_type.value,
            "field": self.field,
            "operator": self.operator.value,
            "value": self.value,
            "weight": self.weight,
            "required": self.required,
        }


# ============================================
# Discovery Source
# ============================================


class DiscoverySource(Enum):
    """Source of discovery results."""

    REGISTRY = "registry"
    CACHE = "cache"
    PEER_DISCOVERY = "peer_discovery"
    LOCAL = "local"
    WELL_KNOWN = "well_known"


# ============================================
# Discovery Request/Response
# ============================================


@dataclass
class DiscoveryRequest:
    """Request to discover agents with specific capabilities."""

    requester: AgentIdentity
    required_capabilities: list[str]
    constraints: list[DiscoveryConstraint] = field(default_factory=list)
    optional_capabilities: list[str] = field(default_factory=list)
    max_results: int = 10
    timeout_ms: int | None = None
    include_inactive: bool = False
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requested_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        # Convert requester to dict, filtering out None values
        requester_dict = {k: v for k, v in asdict(self.requester).items() if v is not None}
        result: dict[str, Any] = {
            "request_id": self.request_id,
            "requester": requester_dict,
            "required_capabilities": self.required_capabilities,
            "constraints": [c.to_dict() for c in self.constraints],
            "max_results": self.max_results,
            "include_inactive": self.include_inactive,
            "requested_at": self.requested_at,
        }
        if self.optional_capabilities:
            result["optional_capabilities"] = self.optional_capabilities
        if self.timeout_ms:
            result["timeout_ms"] = self.timeout_ms
        return result


@dataclass
class AgentMatch:
    """A matching agent with relevance scoring."""

    agent: AgentCard
    match_score: float
    capability_coverage: float
    constraint_satisfaction: float
    matched_capabilities: list[str]
    compatibility_notes: list[str] = field(default_factory=list)
    missing_capabilities: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "agent": self.agent.to_dict(),
            "match_score": self.match_score,
            "capability_coverage": self.capability_coverage,
            "constraint_satisfaction": self.constraint_satisfaction,
            "matched_capabilities": self.matched_capabilities,
        }
        if self.compatibility_notes:
            result["compatibility_notes"] = self.compatibility_notes
        if self.missing_capabilities:
            result["missing_capabilities"] = self.missing_capabilities
        return result


@dataclass
class DiscoveryResponse:
    """Response from capability discovery."""

    request_id: str
    agents: list[AgentMatch]
    total_count: int
    returned_count: int
    discovery_time_ms: int
    source: DiscoverySource
    cached: bool = False
    cache_expires_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "request_id": self.request_id,
            "agents": [a.to_dict() for a in self.agents],
            "total_count": self.total_count,
            "returned_count": self.returned_count,
            "discovery_time_ms": self.discovery_time_ms,
            "source": self.source.value,
            "cached": self.cached,
        }
        if self.cache_expires_at:
            result["cache_expires_at"] = self.cache_expires_at
        return result


# ============================================
# Registry Operations
# ============================================


@dataclass
class RegistrationRequest:
    """Request to register an agent in the registry."""

    agent_card: AgentCard
    ttl_seconds: int = 3600
    tags: list[str] = field(default_factory=list)
    priority: int = 0
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "request_id": self.request_id,
            "agent_card": self.agent_card.to_dict(),
            "ttl_seconds": self.ttl_seconds,
            "priority": self.priority,
        }
        if self.tags:
            result["tags"] = self.tags
        return result


@dataclass
class RegistrationError:
    """Error during registration."""

    error_code: str
    message: str
    field: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.field:
            result["field"] = self.field
        return result


@dataclass
class RegistrationResponse:
    """Response from agent registration."""

    request_id: str
    success: bool
    registration_id: str | None = None
    expires_at: str | None = None
    error: RegistrationError | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "request_id": self.request_id,
            "success": self.success,
        }
        if self.registration_id:
            result["registration_id"] = self.registration_id
        if self.expires_at:
            result["expires_at"] = self.expires_at
        if self.error:
            result["error"] = self.error.to_dict()
        return result

    @classmethod
    def success_response(
        cls, request_id: str, registration_id: str, expires_at: str
    ) -> "RegistrationResponse":
        """Create a successful registration response."""
        return cls(
            request_id=request_id,
            success=True,
            registration_id=registration_id,
            expires_at=expires_at,
        )

    @classmethod
    def error_response(
        cls, request_id: str, error_code: str, message: str, field: str | None = None
    ) -> "RegistrationResponse":
        """Create an error registration response."""
        return cls(
            request_id=request_id,
            success=False,
            error=RegistrationError(error_code, message, field),
        )


@dataclass
class DeregistrationRequest:
    """Request to deregister an agent."""

    registration_id: str
    agent_id: str
    reason: str | None = None
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "request_id": self.request_id,
            "registration_id": self.registration_id,
            "agent_id": self.agent_id,
        }
        if self.reason:
            result["reason"] = self.reason
        return result


@dataclass
class DeregistrationResponse:
    """Response from deregistration."""

    request_id: str
    success: bool
    message: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "request_id": self.request_id,
            "success": self.success,
        }
        if self.message:
            result["message"] = self.message
        return result


# ============================================
# Registry Status
# ============================================


@dataclass
class RegistryStatus:
    """Health status of the registry."""

    healthy: bool
    agent_count: int
    capability_count: int
    last_cleanup: str
    uptime_seconds: int
    cache_hit_rate: float

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "healthy": self.healthy,
            "agent_count": self.agent_count,
            "capability_count": self.capability_count,
            "last_cleanup": self.last_cleanup,
            "uptime_seconds": self.uptime_seconds,
            "cache_hit_rate": self.cache_hit_rate,
        }


@dataclass
class CapabilityStats:
    """Statistics about a registered capability."""

    capability_id: str
    agent_count: int
    average_version: str
    protocols: list[ProtocolType]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "capability_id": self.capability_id,
            "agent_count": self.agent_count,
            "average_version": self.average_version,
            "protocols": [p.value for p in self.protocols],
        }


@dataclass
class CapabilityIndex:
    """Index entry for fast capability lookup."""

    capability_id: str
    agent_ids: list[str]
    last_updated: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "capability_id": self.capability_id,
            "agent_ids": self.agent_ids,
            "last_updated": self.last_updated,
        }


# ============================================
# Registry Entry
# ============================================


@dataclass
class RegistryEntry:
    """Internal entry in the capability registry."""

    registration_id: str
    agent_card: AgentCard
    expires_at: datetime
    tags: list[str]
    priority: int
    registered_at: datetime


# ============================================
# Capability Registry
# ============================================


class CapabilityRegistry:
    """
    In-memory capability registry for agent discovery.

    Provides fast lookups via inverted index by capability.
    Supports TTL-based expiration and constraint filtering.
    """

    def __init__(self, cleanup_interval_seconds: int = 60):
        """Initialize the registry."""
        self._entries: dict[str, RegistryEntry] = {}
        self._agent_id_to_reg_id: dict[str, str] = {}
        self._capability_index: dict[str, set[str]] = {}
        self._protocol_index: dict[ProtocolType, set[str]] = {}
        self._provider_index: dict[str, set[str]] = {}
        self._lock = threading.RLock()
        self._start_time = datetime.now(timezone.utc)
        self._last_cleanup = datetime.now(timezone.utc)
        self._cache_hits = 0
        self._cache_misses = 0
        self._cleanup_interval = cleanup_interval_seconds

    def register(
        self,
        agent_card: AgentCard,
        ttl_seconds: int = 3600,
        tags: list[str] | None = None,
        priority: int = 0,
    ) -> RegistrationResponse:
        """
        Register an agent card in the registry.

        Args:
            agent_card: The agent card to register
            ttl_seconds: Time-to-live in seconds
            tags: Optional tags for categorization
            priority: Registration priority (higher = preferred)

        Returns:
            RegistrationResponse with success status and registration ID
        """
        request_id = str(uuid.uuid4())

        # Validate agent card
        if not agent_card.identity.agent_id:
            return RegistrationResponse.error_response(
                request_id, "INVALID_AGENT_ID", "Agent ID is required", "identity.agent_id"
            )

        with self._lock:
            # Check for existing registration
            agent_id = agent_card.identity.agent_id
            if agent_id in self._agent_id_to_reg_id:
                # Update existing registration
                old_reg_id = self._agent_id_to_reg_id[agent_id]
                self._remove_from_indices(old_reg_id)
                del self._entries[old_reg_id]

            # Create new registration
            registration_id = str(uuid.uuid4())
            now = datetime.now(timezone.utc)
            expires_at = datetime.fromtimestamp(
                now.timestamp() + ttl_seconds, tz=timezone.utc
            )

            entry = RegistryEntry(
                registration_id=registration_id,
                agent_card=agent_card,
                expires_at=expires_at,
                tags=tags or [],
                priority=priority,
                registered_at=now,
            )

            self._entries[registration_id] = entry
            self._agent_id_to_reg_id[agent_id] = registration_id
            self._add_to_indices(registration_id, agent_card)

            return RegistrationResponse.success_response(
                request_id, registration_id, expires_at.isoformat()
            )

    def deregister(self, registration_id: str, agent_id: str) -> DeregistrationResponse:
        """
        Remove an agent from the registry.

        Args:
            registration_id: The registration ID
            agent_id: The agent ID for verification

        Returns:
            DeregistrationResponse with success status
        """
        request_id = str(uuid.uuid4())

        with self._lock:
            if registration_id not in self._entries:
                return DeregistrationResponse(
                    request_id=request_id,
                    success=False,
                    message="Registration not found",
                )

            entry = self._entries[registration_id]
            if entry.agent_card.identity.agent_id != agent_id:
                return DeregistrationResponse(
                    request_id=request_id,
                    success=False,
                    message="Agent ID does not match registration",
                )

            self._remove_from_indices(registration_id)
            del self._entries[registration_id]
            if agent_id in self._agent_id_to_reg_id:
                del self._agent_id_to_reg_id[agent_id]

            return DeregistrationResponse(
                request_id=request_id,
                success=True,
                message="Agent deregistered successfully",
            )

    def update(
        self,
        registration_id: str,
        agent_card: AgentCard,
        extend_ttl: bool = False,
        new_ttl_seconds: int | None = None,
    ) -> RegistrationResponse:
        """
        Update an existing registration.

        Args:
            registration_id: The registration ID to update
            agent_card: Updated agent card
            extend_ttl: Whether to extend the TTL
            new_ttl_seconds: New TTL if extending

        Returns:
            RegistrationResponse with success status
        """
        request_id = str(uuid.uuid4())

        with self._lock:
            if registration_id not in self._entries:
                return RegistrationResponse.error_response(
                    request_id, "NOT_FOUND", "Registration not found"
                )

            entry = self._entries[registration_id]

            # Update indices
            self._remove_from_indices(registration_id)
            self._add_to_indices(registration_id, agent_card)

            # Update entry
            entry.agent_card = agent_card
            if extend_ttl and new_ttl_seconds:
                entry.expires_at = datetime.fromtimestamp(
                    datetime.now(timezone.utc).timestamp() + new_ttl_seconds,
                    tz=timezone.utc,
                )

            return RegistrationResponse.success_response(
                request_id, registration_id, entry.expires_at.isoformat()
            )

    def discover(self, request: DiscoveryRequest) -> DiscoveryResponse:
        """
        Discover agents matching the given criteria.

        Args:
            request: Discovery request with capabilities and constraints

        Returns:
            DiscoveryResponse with matching agents sorted by score
        """
        start_time = time.time()

        with self._lock:
            # Clean up expired entries
            self._cleanup_expired()

            # Get candidate agents from capability index
            candidates = self._get_candidates(request.required_capabilities)

            # Score and filter candidates
            matches: list[AgentMatch] = []
            for reg_id in candidates:
                entry = self._entries.get(reg_id)
                if not entry:
                    continue

                # Check if expired
                if entry.expires_at < datetime.now(timezone.utc):
                    continue

                # Calculate match
                match = self._score_agent(entry.agent_card, request)
                if match:
                    matches.append(match)

            # Sort by score descending
            matches.sort(key=lambda m: m.match_score, reverse=True)

            # Limit results
            total_count = len(matches)
            matches = matches[: request.max_results]

            elapsed_ms = int((time.time() - start_time) * 1000)

            return DiscoveryResponse(
                request_id=request.request_id,
                agents=matches,
                total_count=total_count,
                returned_count=len(matches),
                discovery_time_ms=elapsed_ms,
                source=DiscoverySource.REGISTRY,
                cached=False,
            )

    def get_agent(self, agent_id: str) -> AgentCard | None:
        """Get an agent card by agent ID."""
        with self._lock:
            reg_id = self._agent_id_to_reg_id.get(agent_id)
            if not reg_id:
                return None
            entry = self._entries.get(reg_id)
            if not entry:
                return None
            if entry.expires_at < datetime.now(timezone.utc):
                return None
            return entry.agent_card

    def get_status(self) -> RegistryStatus:
        """Get the current status of the registry."""
        with self._lock:
            now = datetime.now(timezone.utc)
            uptime = int((now - self._start_time).total_seconds())
            total_requests = self._cache_hits + self._cache_misses
            cache_hit_rate = (
                self._cache_hits / total_requests if total_requests > 0 else 0.0
            )

            return RegistryStatus(
                healthy=True,
                agent_count=len(self._entries),
                capability_count=len(self._capability_index),
                last_cleanup=self._last_cleanup.isoformat(),
                uptime_seconds=uptime,
                cache_hit_rate=cache_hit_rate,
            )

    def get_capability_stats(self, capability_id: str) -> CapabilityStats | None:
        """Get statistics for a specific capability."""
        with self._lock:
            agent_ids = self._capability_index.get(capability_id)
            if not agent_ids:
                return None

            protocols: set[ProtocolType] = set()
            versions: list[str] = []

            for reg_id in agent_ids:
                entry = self._entries.get(reg_id)
                if not entry:
                    continue

                for protocol in entry.agent_card.supported_protocols:
                    protocols.add(protocol.protocol)

                # Use agent card version since capabilities don't have version
                for cap in entry.agent_card.capabilities:
                    if cap.capability_id == capability_id:
                        versions.append(entry.agent_card.identity.version)

            # Calculate average version (simplified - just take the first)
            avg_version = versions[0] if versions else "0.0.0"

            return CapabilityStats(
                capability_id=capability_id,
                agent_count=len(agent_ids),
                average_version=avg_version,
                protocols=list(protocols),
            )

    def list_capabilities(self) -> list[str]:
        """List all registered capabilities."""
        with self._lock:
            return list(self._capability_index.keys())

    def list_agents(self) -> list[str]:
        """List all registered agent IDs."""
        with self._lock:
            return list(self._agent_id_to_reg_id.keys())

    def clear(self) -> None:
        """Clear all registrations."""
        with self._lock:
            self._entries.clear()
            self._agent_id_to_reg_id.clear()
            self._capability_index.clear()
            self._protocol_index.clear()
            self._provider_index.clear()

    # ============================================
    # Private Methods
    # ============================================

    def _add_to_indices(self, registration_id: str, agent_card: AgentCard) -> None:
        """Add an agent to all indices."""
        # Capability index
        for capability in agent_card.capabilities:
            cap_id = capability.capability_id
            if cap_id not in self._capability_index:
                self._capability_index[cap_id] = set()
            self._capability_index[cap_id].add(registration_id)

        # Protocol index
        for protocol in agent_card.supported_protocols:
            if protocol.protocol not in self._protocol_index:
                self._protocol_index[protocol.protocol] = set()
            self._protocol_index[protocol.protocol].add(registration_id)

        # Provider index
        provider = agent_card.identity.provider
        if provider:
            if provider not in self._provider_index:
                self._provider_index[provider] = set()
            self._provider_index[provider].add(registration_id)

    def _remove_from_indices(self, registration_id: str) -> None:
        """Remove an agent from all indices."""
        entry = self._entries.get(registration_id)
        if not entry:
            return

        agent_card = entry.agent_card

        # Capability index
        for capability in agent_card.capabilities:
            cap_id = capability.capability_id
            if cap_id in self._capability_index:
                self._capability_index[cap_id].discard(registration_id)
                if not self._capability_index[cap_id]:
                    del self._capability_index[cap_id]

        # Protocol index
        for protocol in agent_card.supported_protocols:
            if protocol.protocol in self._protocol_index:
                self._protocol_index[protocol.protocol].discard(registration_id)
                if not self._protocol_index[protocol.protocol]:
                    del self._protocol_index[protocol.protocol]

        # Provider index
        provider = agent_card.identity.provider
        if provider and provider in self._provider_index:
            self._provider_index[provider].discard(registration_id)
            if not self._provider_index[provider]:
                del self._provider_index[provider]

    def _get_candidates(self, required_capabilities: list[str]) -> set[str]:
        """Get candidate registration IDs from capability index."""
        if not required_capabilities:
            return set(self._entries.keys())

        # Start with agents that have the first capability
        first_cap = required_capabilities[0]
        candidates = self._capability_index.get(first_cap, set()).copy()

        # Intersect with agents that have remaining capabilities
        for cap_id in required_capabilities[1:]:
            cap_agents = self._capability_index.get(cap_id, set())
            candidates &= cap_agents

        return candidates

    def _score_agent(
        self, agent_card: AgentCard, request: DiscoveryRequest
    ) -> AgentMatch | None:
        """Score an agent against the discovery request."""
        # Get agent capabilities
        agent_cap_ids = {cap.capability_id for cap in agent_card.capabilities}

        # Calculate capability coverage
        required = set(request.required_capabilities)
        matched = required & agent_cap_ids
        missing = required - agent_cap_ids

        if missing and not request.include_inactive:
            # Missing required capabilities
            return None

        capability_coverage = len(matched) / len(required) if required else 1.0

        # Calculate constraint satisfaction
        constraint_score, notes = self._evaluate_constraints(
            agent_card, request.constraints
        )

        # Check if required constraints are met
        for constraint in request.constraints:
            if constraint.required:
                if not self._evaluate_single_constraint(agent_card, constraint):
                    return None

        # Calculate optional capability bonus
        optional = set(request.optional_capabilities)
        optional_matched = optional & agent_cap_ids
        optional_bonus = (
            len(optional_matched) / len(optional) * 0.1 if optional else 0.0
        )

        # Calculate overall score
        match_score = (
            capability_coverage * 0.6 + constraint_score * 0.3 + optional_bonus + 0.1
        )
        match_score = min(1.0, match_score)

        return AgentMatch(
            agent=agent_card,
            match_score=match_score,
            capability_coverage=capability_coverage,
            constraint_satisfaction=constraint_score,
            matched_capabilities=list(matched),
            missing_capabilities=list(missing),
            compatibility_notes=notes,
        )

    def _evaluate_constraints(
        self, agent_card: AgentCard, constraints: list[DiscoveryConstraint]
    ) -> tuple[float, list[str]]:
        """Evaluate all constraints and return score and notes."""
        if not constraints:
            return 1.0, []

        total_weight = sum(c.weight for c in constraints)
        satisfied_weight = 0.0
        notes: list[str] = []

        for constraint in constraints:
            if self._evaluate_single_constraint(agent_card, constraint):
                satisfied_weight += constraint.weight
            else:
                notes.append(
                    f"Constraint not met: {constraint.field} {constraint.operator.value} {constraint.value}"
                )

        score = satisfied_weight / total_weight if total_weight > 0 else 1.0
        return score, notes

    def _evaluate_single_constraint(
        self, agent_card: AgentCard, constraint: DiscoveryConstraint
    ) -> bool:
        """Evaluate a single constraint against an agent card."""
        # Get the field value
        value = self._get_field_value(agent_card, constraint.field)
        if value is None:
            return False

        target = constraint.value
        op = constraint.operator

        # String comparison
        if isinstance(value, str):
            if op == ConstraintOperator.EQUALS:
                return value == target
            elif op == ConstraintOperator.NOT_EQUALS:
                return value != target
            elif op == ConstraintOperator.CONTAINS:
                return target in value
            elif op == ConstraintOperator.REGEX:
                return bool(re.match(target, value))

        # List comparison
        if isinstance(value, list):
            if op == ConstraintOperator.IN:
                return target in value
            elif op == ConstraintOperator.NOT_IN:
                return target not in value
            elif op == ConstraintOperator.CONTAINS:
                return any(target in str(v) for v in value)

        # Numeric comparison
        try:
            num_value = float(str(value))
            num_target = float(target)
            if op == ConstraintOperator.GREATER_THAN:
                return num_value > num_target
            elif op == ConstraintOperator.LESS_THAN:
                return num_value < num_target
            elif op == ConstraintOperator.GREATER_OR_EQUAL:
                return num_value >= num_target
            elif op == ConstraintOperator.LESS_OR_EQUAL:
                return num_value <= num_target
        except (ValueError, TypeError):
            pass

        return False

    def _get_field_value(self, agent_card: AgentCard, field_path: str) -> Any:
        """Get a field value from agent card using dot notation."""
        parts = field_path.split(".")
        obj: Any = agent_card

        for part in parts:
            if hasattr(obj, part):
                obj = getattr(obj, part)
            elif isinstance(obj, dict) and part in obj:
                obj = obj[part]
            else:
                return None

        return obj

    def _cleanup_expired(self) -> None:
        """Remove expired registrations."""
        now = datetime.now(timezone.utc)
        expired = [
            reg_id
            for reg_id, entry in self._entries.items()
            if entry.expires_at < now
        ]

        for reg_id in expired:
            entry = self._entries[reg_id]
            agent_id = entry.agent_card.identity.agent_id
            self._remove_from_indices(reg_id)
            del self._entries[reg_id]
            if agent_id in self._agent_id_to_reg_id:
                del self._agent_id_to_reg_id[agent_id]

        self._last_cleanup = now
