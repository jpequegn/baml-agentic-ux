"""
Capability Matching Algorithms

Schema matching for determining capability compatibility between agents.
Implements Cupid-style multi-factor matching with schema compatibility scoring.

Issue #56 - Phase 3: Agent-to-Agent Interface Negotiation
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import difflib
import re
import time
import uuid

from src.lui_simulator.agent_types import (
    AgentCapability,
    CapabilityType,
    SchemaDefinition,
    SchemaType,
)


# ============================================
# Schema Compatibility Types
# ============================================


class TransformationDirection(Enum):
    """Direction of schema transformation."""

    INPUT_TO_REQUIRED = "input_to_required"
    OUTPUT_TO_REQUIRED = "output_to_required"
    BIDIRECTIONAL = "bidirectional"


class TransformationType(Enum):
    """Type of schema transformation needed."""

    TYPE_COERCION = "type_coercion"
    PROPERTY_RENAME = "property_rename"
    PROPERTY_ADD = "property_add"
    PROPERTY_REMOVE = "property_remove"
    FORMAT_CONVERSION = "format_conversion"
    ARRAY_WRAP = "array_wrap"
    ARRAY_UNWRAP = "array_unwrap"
    OPTIONAL_TO_REQUIRED = "optional_to_required"
    ENUM_MAPPING = "enum_mapping"
    NESTED_TRANSFORM = "nested_transform"


class TransformationComplexity(Enum):
    """Complexity level of a transformation."""

    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    RISKY = "risky"


class SuggestionType(Enum):
    """Types of adaptation suggestions."""

    SCHEMA_TRANSFORM = "schema_transform"
    ADD_WRAPPER = "add_wrapper"
    PROTOCOL_BRIDGE = "protocol_bridge"
    TYPE_CONVERTER = "type_converter"
    DEFAULT_VALUES = "default_values"
    VALIDATION_LAYER = "validation_layer"
    CACHING_LAYER = "caching_layer"
    FALLBACK = "fallback"
    COMPOSITION = "composition"
    CUSTOM_ADAPTER = "custom_adapter"


class SuggestionPriority(Enum):
    """Priority levels for suggestions."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    OPTIONAL = "optional"


class EffortLevel(Enum):
    """Effort levels for implementation."""

    TRIVIAL = "trivial"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


# ============================================
# Schema Transformation
# ============================================


@dataclass
class SchemaTransformation:
    """A specific schema transformation that can be applied."""

    transformation_type: TransformationType
    direction: TransformationDirection
    source_path: str
    target_path: str
    complexity: TransformationComplexity
    reversible: bool
    description: str
    example_before: str | None = None
    example_after: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "transformation_type": self.transformation_type.value,
            "direction": self.direction.value,
            "source_path": self.source_path,
            "target_path": self.target_path,
            "complexity": self.complexity.value,
            "reversible": self.reversible,
            "description": self.description,
        }
        if self.example_before:
            result["example_before"] = self.example_before
        if self.example_after:
            result["example_after"] = self.example_after
        return result


@dataclass
class PropertyMatch:
    """Match result for a single property."""

    required_property: str
    offered_property: str | None
    match_score: float
    match_reason: str
    type_compatible: bool
    transformation_needed: SchemaTransformation | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result: dict[str, Any] = {
            "required_property": self.required_property,
            "offered_property": self.offered_property,
            "match_score": self.match_score,
            "match_reason": self.match_reason,
            "type_compatible": self.type_compatible,
        }
        if self.transformation_needed:
            result["transformation_needed"] = self.transformation_needed.to_dict()
        return result


@dataclass
class SchemaCompatibility:
    """Compatibility assessment between two schemas."""

    input_compatible: bool
    output_compatible: bool
    input_score: float
    output_score: float
    overall_score: float
    transformations_needed: list[SchemaTransformation] = field(default_factory=list)
    property_matches: list[PropertyMatch] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "input_compatible": self.input_compatible,
            "output_compatible": self.output_compatible,
            "input_score": self.input_score,
            "output_score": self.output_score,
            "overall_score": self.overall_score,
            "transformations_needed": [t.to_dict() for t in self.transformations_needed],
            "property_matches": [p.to_dict() for p in self.property_matches],
            "warnings": self.warnings,
        }


# ============================================
# Constraint Satisfaction
# ============================================


@dataclass
class ConstraintSatisfaction:
    """Status of constraint satisfaction."""

    all_satisfied: bool
    satisfied_constraints: list[str] = field(default_factory=list)
    unsatisfied_constraints: list[str] = field(default_factory=list)
    partially_satisfied: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "all_satisfied": self.all_satisfied,
            "satisfied_constraints": self.satisfied_constraints,
            "unsatisfied_constraints": self.unsatisfied_constraints,
            "partially_satisfied": self.partially_satisfied,
            "notes": self.notes,
        }


# ============================================
# Adaptation Suggestions
# ============================================


@dataclass
class AdaptationSuggestion:
    """Suggestion for adapting capabilities to improve compatibility."""

    suggestion_type: SuggestionType
    priority: SuggestionPriority
    description: str
    effort_estimate: EffortLevel
    compatibility_improvement: float
    suggestion_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    implementation_hints: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "suggestion_id": self.suggestion_id,
            "suggestion_type": self.suggestion_type.value,
            "priority": self.priority.value,
            "description": self.description,
            "effort_estimate": self.effort_estimate.value,
            "compatibility_improvement": self.compatibility_improvement,
            "implementation_hints": self.implementation_hints,
            "risks": self.risks,
        }


# ============================================
# Capability Matching Types
# ============================================


@dataclass
class CapabilityDetailedMatch:
    """Detailed match information for a single capability pair."""

    required_capability: str
    matched_capability: str
    compatibility_score: float
    schema_compatibility: SchemaCompatibility
    constraint_satisfaction: ConstraintSatisfaction
    performance_adequate: bool = True
    trust_adequate: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "required_capability": self.required_capability,
            "matched_capability": self.matched_capability,
            "compatibility_score": self.compatibility_score,
            "schema_compatibility": self.schema_compatibility.to_dict(),
            "constraint_satisfaction": self.constraint_satisfaction.to_dict(),
            "performance_adequate": self.performance_adequate,
            "trust_adequate": self.trust_adequate,
        }


@dataclass
class CapabilityMatchResult:
    """Result of matching capabilities."""

    overall_compatibility: float
    type_score: float
    name_score: float
    description_score: float
    schema_score: float
    compatible: bool
    confidence: float
    matches: list[CapabilityDetailedMatch] = field(default_factory=list)
    unmatched_requirements: list[str] = field(default_factory=list)
    adaptation_suggestions: list[AdaptationSuggestion] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "overall_compatibility": self.overall_compatibility,
            "type_score": self.type_score,
            "name_score": self.name_score,
            "description_score": self.description_score,
            "schema_score": self.schema_score,
            "compatible": self.compatible,
            "confidence": self.confidence,
            "matches": [m.to_dict() for m in self.matches],
            "unmatched_requirements": self.unmatched_requirements,
            "adaptation_suggestions": [s.to_dict() for s in self.adaptation_suggestions],
        }


# ============================================
# Match Options
# ============================================


@dataclass
class MatchOptions:
    """Options for the matching algorithm."""

    minimum_compatibility: float = 0.5
    type_weight: float = 0.4
    name_weight: float = 0.2
    description_weight: float = 0.2
    schema_weight: float = 0.2
    include_transformations: bool = True
    include_suggestions: bool = True
    fuzzy_matching: bool = True
    semantic_matching: bool = False  # Requires external service

    def __post_init__(self) -> None:
        """Validate weights sum to 1.0."""
        total = self.type_weight + self.name_weight + self.description_weight + self.schema_weight
        if abs(total - 1.0) > 0.001:
            # Normalize weights
            self.type_weight /= total
            self.name_weight /= total
            self.description_weight /= total
            self.schema_weight /= total


@dataclass
class BestMatch:
    """Best match for a single required capability."""

    required_capability_id: str
    best_match_id: str | None
    match_score: float
    alternatives: list[tuple[str, float, list[str]]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "required_capability_id": self.required_capability_id,
            "best_match_id": self.best_match_id,
            "match_score": self.match_score,
            "alternatives": [
                {"capability_id": alt[0], "match_score": alt[1], "trade_offs": alt[2]}
                for alt in self.alternatives
            ],
        }


@dataclass
class CapabilityMatchResponse:
    """Response from capability matching."""

    request_id: str
    overall_result: CapabilityMatchResult
    best_matches: list[BestMatch]
    match_time_ms: int
    algorithm_version: str = "1.0.0"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "request_id": self.request_id,
            "overall_result": self.overall_result.to_dict(),
            "best_matches": [m.to_dict() for m in self.best_matches],
            "match_time_ms": self.match_time_ms,
            "algorithm_version": self.algorithm_version,
        }


# ============================================
# Capability Matcher
# ============================================


class CapabilityMatcher:
    """
    Capability matching algorithm implementing Cupid-style multi-factor matching.

    Scoring Components:
    - Type Matching (40%): Capability type alignment
    - Name Similarity (20%): Jaccard/fuzzy string matching
    - Description Similarity (20%): Text similarity
    - Schema Compatibility (20%): Input/output schema alignment
    """

    # Type compatibility matrix
    TYPE_COMPATIBILITY: dict[CapabilityType, set[CapabilityType]] = {
        CapabilityType.ACTION: {CapabilityType.ACTION, CapabilityType.COMPOSITE},
        CapabilityType.QUERY: {CapabilityType.QUERY, CapabilityType.COMPOSITE},
        CapabilityType.TRANSFORM: {CapabilityType.TRANSFORM, CapabilityType.COMPOSITE},
        CapabilityType.COMPOSITE: {
            CapabilityType.COMPOSITE,
            CapabilityType.ACTION,
            CapabilityType.QUERY,
            CapabilityType.TRANSFORM,
        },
        CapabilityType.DELEGATION: {CapabilityType.DELEGATION, CapabilityType.COMPOSITE},
        CapabilityType.STREAMING: {CapabilityType.STREAMING, CapabilityType.COMPOSITE},
        CapabilityType.INTERACTIVE: {CapabilityType.INTERACTIVE, CapabilityType.COMPOSITE},
    }

    # Schema type coercion possibilities
    TYPE_COERCION: dict[SchemaType, set[SchemaType]] = {
        SchemaType.INTEGER: {SchemaType.INTEGER, SchemaType.NUMBER, SchemaType.STRING},
        SchemaType.NUMBER: {SchemaType.NUMBER, SchemaType.STRING},
        SchemaType.BOOLEAN: {SchemaType.BOOLEAN, SchemaType.STRING},
        SchemaType.STRING: {SchemaType.STRING},
        SchemaType.ARRAY: {SchemaType.ARRAY},
        SchemaType.OBJECT: {SchemaType.OBJECT},
        SchemaType.NULL: {SchemaType.NULL, SchemaType.ANY},
        SchemaType.ANY: {
            SchemaType.ANY,
            SchemaType.STRING,
            SchemaType.NUMBER,
            SchemaType.INTEGER,
            SchemaType.BOOLEAN,
            SchemaType.ARRAY,
            SchemaType.OBJECT,
            SchemaType.NULL,
        },
        SchemaType.UNION: {SchemaType.UNION, SchemaType.ANY},
        SchemaType.ENUM: {SchemaType.ENUM, SchemaType.STRING},
        SchemaType.REFERENCE: {SchemaType.REFERENCE},
    }

    def __init__(self, options: MatchOptions | None = None):
        """Initialize the capability matcher."""
        self.options = options or MatchOptions()

    def match(
        self,
        required: list[AgentCapability],
        offered: list[AgentCapability],
        options: MatchOptions | None = None,
    ) -> CapabilityMatchResponse:
        """
        Match required capabilities against offered capabilities.

        Args:
            required: List of required capabilities
            offered: List of offered capabilities
            options: Optional matching options (overrides instance options)

        Returns:
            CapabilityMatchResponse with detailed match results
        """
        start_time = time.time()
        opts = options or self.options
        request_id = str(uuid.uuid4())

        matches: list[CapabilityDetailedMatch] = []
        best_matches: list[BestMatch] = []
        unmatched: list[str] = []

        total_type_score = 0.0
        total_name_score = 0.0
        total_desc_score = 0.0
        total_schema_score = 0.0

        for req_cap in required:
            # Find best match for this required capability
            best_score = 0.0
            best_match: AgentCapability | None = None
            best_detail: CapabilityDetailedMatch | None = None
            alternatives: list[tuple[str, float, list[str]]] = []

            for off_cap in offered:
                score, detail = self._score_capability_pair(req_cap, off_cap, opts)

                if score > best_score:
                    if best_match is not None:
                        # Previous best becomes an alternative
                        trade_offs = self._get_trade_offs(best_match, off_cap)
                        alternatives.append(
                            (best_match.capability_id, best_score, trade_offs)
                        )
                    best_score = score
                    best_match = off_cap
                    best_detail = detail
                elif score >= opts.minimum_compatibility:
                    trade_offs = self._get_trade_offs(off_cap, best_match)
                    alternatives.append((off_cap.capability_id, score, trade_offs))

            if best_match is not None and best_score >= opts.minimum_compatibility:
                matches.append(best_detail)
                total_type_score += self._type_score(req_cap, best_match)
                total_name_score += self._name_similarity(req_cap.name, best_match.name)
                total_desc_score += self._description_similarity(
                    req_cap.description, best_match.description
                )
                total_schema_score += best_detail.schema_compatibility.overall_score

                best_matches.append(
                    BestMatch(
                        required_capability_id=req_cap.capability_id,
                        best_match_id=best_match.capability_id,
                        match_score=best_score,
                        alternatives=alternatives[:3],  # Top 3 alternatives
                    )
                )
            else:
                unmatched.append(req_cap.capability_id)
                best_matches.append(
                    BestMatch(
                        required_capability_id=req_cap.capability_id,
                        best_match_id=None,
                        match_score=0.0,
                        alternatives=[],
                    )
                )

        # Calculate overall scores
        n = len(required)
        avg_type = total_type_score / n if n > 0 else 0.0
        avg_name = total_name_score / n if n > 0 else 0.0
        avg_desc = total_desc_score / n if n > 0 else 0.0
        avg_schema = total_schema_score / n if n > 0 else 0.0

        overall = (
            opts.type_weight * avg_type
            + opts.name_weight * avg_name
            + opts.description_weight * avg_desc
            + opts.schema_weight * avg_schema
        )

        # Generate suggestions if enabled
        suggestions: list[AdaptationSuggestion] = []
        if opts.include_suggestions and unmatched:
            suggestions = self._generate_suggestions(unmatched, required, offered)

        # Calculate confidence based on match quality
        matched_ratio = len(matches) / n if n > 0 else 0.0
        avg_match_score = (
            sum(m.compatibility_score for m in matches) / len(matches)
            if matches
            else 0.0
        )
        confidence = matched_ratio * avg_match_score

        result = CapabilityMatchResult(
            overall_compatibility=overall,
            type_score=avg_type,
            name_score=avg_name,
            description_score=avg_desc,
            schema_score=avg_schema,
            compatible=overall >= opts.minimum_compatibility and not unmatched,
            confidence=confidence,
            matches=matches,
            unmatched_requirements=unmatched,
            adaptation_suggestions=suggestions,
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        return CapabilityMatchResponse(
            request_id=request_id,
            overall_result=result,
            best_matches=best_matches,
            match_time_ms=elapsed_ms,
        )

    def match_single(
        self,
        required: AgentCapability,
        offered: AgentCapability,
        options: MatchOptions | None = None,
    ) -> tuple[float, CapabilityDetailedMatch]:
        """
        Match a single required capability against a single offered capability.

        Args:
            required: Required capability
            offered: Offered capability
            options: Optional matching options

        Returns:
            Tuple of (score, detailed match)
        """
        opts = options or self.options
        return self._score_capability_pair(required, offered, opts)

    def compare_schemas(
        self,
        required: SchemaDefinition,
        offered: SchemaDefinition,
        direction: TransformationDirection = TransformationDirection.INPUT_TO_REQUIRED,
    ) -> SchemaCompatibility:
        """
        Compare two schemas for compatibility.

        Args:
            required: Required schema
            offered: Offered schema
            direction: Direction of comparison

        Returns:
            SchemaCompatibility with detailed analysis
        """
        return self._schema_compatibility(required, offered, direction)

    # ============================================
    # Private Methods - Scoring
    # ============================================

    def _score_capability_pair(
        self,
        required: AgentCapability,
        offered: AgentCapability,
        opts: MatchOptions,
    ) -> tuple[float, CapabilityDetailedMatch]:
        """Score a single capability pair."""
        # Calculate component scores
        type_score = self._type_score(required, offered)
        name_score = (
            self._name_similarity(required.name, offered.name)
            if opts.fuzzy_matching
            else float(required.name.lower() == offered.name.lower())
        )
        desc_score = self._description_similarity(
            required.description, offered.description
        )

        # Schema compatibility
        input_compat = self._schema_compatibility(
            required.input_schema,
            offered.input_schema,
            TransformationDirection.INPUT_TO_REQUIRED,
        )
        output_compat = self._schema_compatibility(
            offered.output_schema,
            required.output_schema,
            TransformationDirection.OUTPUT_TO_REQUIRED,
        )

        schema_score = (input_compat.overall_score + output_compat.overall_score) / 2

        # Combine all transformations
        all_transformations = (
            input_compat.transformations_needed + output_compat.transformations_needed
        )
        all_property_matches = (
            input_compat.property_matches + output_compat.property_matches
        )
        all_warnings = input_compat.warnings + output_compat.warnings

        schema_compat = SchemaCompatibility(
            input_compatible=input_compat.input_compatible,
            output_compatible=output_compat.output_compatible,
            input_score=input_compat.overall_score,
            output_score=output_compat.overall_score,
            overall_score=schema_score,
            transformations_needed=all_transformations,
            property_matches=all_property_matches,
            warnings=all_warnings,
        )

        # Constraint satisfaction
        constraint_sat = self._check_constraints(required, offered)

        # Calculate overall score
        overall_score = (
            opts.type_weight * type_score
            + opts.name_weight * name_score
            + opts.description_weight * desc_score
            + opts.schema_weight * schema_score
        )

        detail = CapabilityDetailedMatch(
            required_capability=required.capability_id,
            matched_capability=offered.capability_id,
            compatibility_score=overall_score,
            schema_compatibility=schema_compat,
            constraint_satisfaction=constraint_sat,
            performance_adequate=True,  # Simplified for now
            trust_adequate=True,
        )

        return overall_score, detail

    def _type_score(self, required: AgentCapability, offered: AgentCapability) -> float:
        """Calculate type compatibility score."""
        if required.capability_type == offered.capability_type:
            return 1.0

        compatible = self.TYPE_COMPATIBILITY.get(required.capability_type, set())
        if offered.capability_type in compatible:
            return 0.8  # Compatible but not exact

        return 0.0

    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity using Jaccard and sequence matching."""
        # Normalize names
        n1 = self._normalize_name(name1)
        n2 = self._normalize_name(name2)

        if n1 == n2:
            return 1.0

        # Jaccard similarity on tokens
        tokens1 = set(n1.split())
        tokens2 = set(n2.split())

        if not tokens1 or not tokens2:
            return 0.0

        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        jaccard = len(intersection) / len(union)

        # Sequence matching
        seq_ratio = difflib.SequenceMatcher(None, n1, n2).ratio()

        # Combine both measures
        return 0.6 * jaccard + 0.4 * seq_ratio

    def _description_similarity(self, desc1: str, desc2: str) -> float:
        """Calculate description similarity."""
        # Normalize descriptions
        d1 = desc1.lower().strip()
        d2 = desc2.lower().strip()

        if d1 == d2:
            return 1.0

        # Tokenize and remove stop words
        tokens1 = self._tokenize(d1)
        tokens2 = self._tokenize(d2)

        if not tokens1 or not tokens2:
            return 0.0

        # Jaccard similarity
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        return len(intersection) / len(union)

    def _normalize_name(self, name: str) -> str:
        """Normalize a name for comparison."""
        # Convert camelCase and PascalCase to spaces
        name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
        # Convert snake_case and kebab-case to spaces
        name = re.sub(r"[_-]", " ", name)
        # Lowercase and strip
        return name.lower().strip()

    def _tokenize(self, text: str) -> set[str]:
        """Tokenize text, removing stop words."""
        stop_words = {
            "a", "an", "the", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "must", "shall",
            "can", "need", "to", "of", "in", "for", "on", "with", "at",
            "by", "from", "as", "into", "through", "during", "before",
            "after", "above", "below", "between", "under", "again", "further",
            "then", "once", "here", "there", "when", "where", "why", "how",
            "all", "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "and", "but", "if", "or", "because", "until",
            "while", "this", "that", "these", "those",
        }
        words = re.findall(r"\b\w+\b", text.lower())
        return {w for w in words if w not in stop_words and len(w) > 2}

    # ============================================
    # Private Methods - Schema Comparison
    # ============================================

    def _schema_compatibility(
        self,
        required: SchemaDefinition,
        offered: SchemaDefinition,
        direction: TransformationDirection,
    ) -> SchemaCompatibility:
        """Compare two schemas for compatibility."""
        transformations: list[SchemaTransformation] = []
        property_matches: list[PropertyMatch] = []
        warnings: list[str] = []

        # Check type compatibility
        type_score = self._schema_type_score(required.type, offered.type)

        if type_score == 0.0:
            # Check if coercion is possible
            if self._can_coerce(offered.type, required.type):
                type_score = 0.7
                transformations.append(
                    SchemaTransformation(
                        transformation_type=TransformationType.TYPE_COERCION,
                        direction=direction,
                        source_path="$",
                        target_path="$",
                        complexity=TransformationComplexity.SIMPLE,
                        reversible=False,
                        description=f"Coerce {offered.type.value} to {required.type.value}",
                    )
                )

        # For objects, compare properties
        property_score = 1.0
        if required.type == SchemaType.OBJECT and offered.type == SchemaType.OBJECT:
            property_score, prop_matches, prop_transforms, prop_warnings = (
                self._compare_object_schemas(required, offered, direction)
            )
            property_matches.extend(prop_matches)
            transformations.extend(prop_transforms)
            warnings.extend(prop_warnings)

        # For arrays, compare item schemas
        if required.type == SchemaType.ARRAY and offered.type == SchemaType.ARRAY:
            if required.items and offered.items:
                item_compat = self._schema_compatibility(
                    required.items, offered.items, direction
                )
                property_score = item_compat.overall_score
                transformations.extend(item_compat.transformations_needed)
                warnings.extend(item_compat.warnings)

        overall_score = (type_score + property_score) / 2

        return SchemaCompatibility(
            input_compatible=overall_score >= 0.5,
            output_compatible=overall_score >= 0.5,
            input_score=overall_score,
            output_score=overall_score,
            overall_score=overall_score,
            transformations_needed=transformations,
            property_matches=property_matches,
            warnings=warnings,
        )

    def _schema_type_score(
        self, required: SchemaType, offered: SchemaType
    ) -> float:
        """Score compatibility between schema types."""
        if required == offered:
            return 1.0

        if required == SchemaType.ANY:
            return 1.0  # ANY accepts anything

        if offered == SchemaType.ANY:
            return 0.8  # ANY can provide anything, but less certain

        return 0.0

    def _can_coerce(self, from_type: SchemaType, to_type: SchemaType) -> bool:
        """Check if a type can be coerced to another type."""
        coercible = self.TYPE_COERCION.get(from_type, set())
        return to_type in coercible

    def _compare_object_schemas(
        self,
        required: SchemaDefinition,
        offered: SchemaDefinition,
        direction: TransformationDirection,
    ) -> tuple[float, list[PropertyMatch], list[SchemaTransformation], list[str]]:
        """Compare object schemas property by property."""
        property_matches: list[PropertyMatch] = []
        transformations: list[SchemaTransformation] = []
        warnings: list[str] = []

        req_props = {p.name: p for p in (required.properties or [])}
        off_props = {p.name: p for p in (offered.properties or [])}
        required_names = set(required.required or [])

        total_score = 0.0
        prop_count = len(req_props)

        if prop_count == 0:
            return 1.0, [], [], []

        for req_name, req_prop in req_props.items():
            # Try exact match first
            if req_name in off_props:
                off_prop = off_props[req_name]
                type_compat = self._schema_type_score(
                    req_prop.schema.type, off_prop.schema.type
                )
                property_matches.append(
                    PropertyMatch(
                        required_property=req_name,
                        offered_property=req_name,
                        match_score=type_compat,
                        match_reason="exact name match",
                        type_compatible=type_compat >= 0.7,
                    )
                )
                total_score += type_compat
                continue

            # Try fuzzy matching on name
            best_match = None
            best_similarity = 0.0
            for off_name in off_props:
                sim = self._name_similarity(req_name, off_name)
                if sim > best_similarity and sim >= 0.7:
                    best_similarity = sim
                    best_match = off_name

            if best_match:
                off_prop = off_props[best_match]
                type_compat = self._schema_type_score(
                    req_prop.schema.type, off_prop.schema.type
                )
                score = best_similarity * type_compat

                transformations.append(
                    SchemaTransformation(
                        transformation_type=TransformationType.PROPERTY_RENAME,
                        direction=direction,
                        source_path=f"$.{best_match}",
                        target_path=f"$.{req_name}",
                        complexity=TransformationComplexity.TRIVIAL,
                        reversible=True,
                        description=f"Rename property '{best_match}' to '{req_name}'",
                    )
                )

                property_matches.append(
                    PropertyMatch(
                        required_property=req_name,
                        offered_property=best_match,
                        match_score=score,
                        match_reason=f"fuzzy name match ({best_similarity:.2f})",
                        type_compatible=type_compat >= 0.7,
                        transformation_needed=transformations[-1],
                    )
                )
                total_score += score
            else:
                # No match found
                is_required = req_name in required_names
                if is_required:
                    warnings.append(f"Required property '{req_name}' has no match")

                    transformations.append(
                        SchemaTransformation(
                            transformation_type=TransformationType.PROPERTY_ADD,
                            direction=direction,
                            source_path="",
                            target_path=f"$.{req_name}",
                            complexity=TransformationComplexity.MODERATE,
                            reversible=False,
                            description=f"Add missing required property '{req_name}'",
                        )
                    )

                property_matches.append(
                    PropertyMatch(
                        required_property=req_name,
                        offered_property=None,
                        match_score=0.0,
                        match_reason="no match found",
                        type_compatible=False,
                    )
                )
                # Score penalty for missing required properties
                if is_required:
                    total_score -= 0.2

        # Check for extra properties in offered
        for off_name in off_props:
            if off_name not in req_props:
                # Check if fuzzy matched
                matched = any(
                    pm.offered_property == off_name for pm in property_matches
                )
                if not matched:
                    warnings.append(f"Extra property '{off_name}' in offered schema")

        avg_score = max(0.0, min(1.0, total_score / prop_count))
        return avg_score, property_matches, transformations, warnings

    # ============================================
    # Private Methods - Constraints
    # ============================================

    def _check_constraints(
        self,
        required: AgentCapability,
        offered: AgentCapability,
    ) -> ConstraintSatisfaction:
        """Check if offered capability satisfies required constraints."""
        satisfied: list[str] = []
        unsatisfied: list[str] = []
        partial: list[str] = []
        notes: list[str] = []

        req_constraints = required.constraints or []
        off_constraints = {c.constraint_id: c for c in (offered.constraints or [])}

        for req_c in req_constraints:
            if req_c.constraint_id in off_constraints:
                # Both have the constraint - check compatibility
                off_c = off_constraints[req_c.constraint_id]
                if req_c.constraint_type == off_c.constraint_type:
                    satisfied.append(req_c.constraint_id)
                else:
                    partial.append(req_c.constraint_id)
                    notes.append(
                        f"Constraint {req_c.constraint_id} has different type"
                    )
            else:
                # Required constraint not present in offered
                unsatisfied.append(req_c.constraint_id)
                notes.append(
                    f"Required constraint {req_c.constraint_id} not found"
                )

        return ConstraintSatisfaction(
            all_satisfied=len(unsatisfied) == 0 and len(partial) == 0,
            satisfied_constraints=satisfied,
            unsatisfied_constraints=unsatisfied,
            partially_satisfied=partial,
            notes=notes,
        )

    # ============================================
    # Private Methods - Suggestions
    # ============================================

    def _generate_suggestions(
        self,
        unmatched: list[str],
        required: list[AgentCapability],
        offered: list[AgentCapability],
    ) -> list[AdaptationSuggestion]:
        """Generate adaptation suggestions for unmatched requirements."""
        suggestions: list[AdaptationSuggestion] = []

        unmatched_caps = {
            cap.capability_id: cap
            for cap in required
            if cap.capability_id in unmatched
        }

        for cap_id, cap in unmatched_caps.items():
            # Find closest partial match
            best_score = 0.0
            best_offered: AgentCapability | None = None
            for off in offered:
                score = self._type_score(cap, off) * 0.5 + self._name_similarity(
                    cap.name, off.name
                ) * 0.5
                if score > best_score:
                    best_score = score
                    best_offered = off

            if best_offered and best_score >= 0.3:
                # Suggest schema transform
                suggestions.append(
                    AdaptationSuggestion(
                        suggestion_type=SuggestionType.SCHEMA_TRANSFORM,
                        priority=SuggestionPriority.HIGH,
                        description=(
                            f"Transform '{best_offered.name}' to match '{cap.name}' "
                            f"requirements (partial match: {best_score:.0%})"
                        ),
                        effort_estimate=EffortLevel.MEDIUM,
                        compatibility_improvement=0.3,
                        implementation_hints=[
                            f"Map input schema from {best_offered.name} format",
                            f"Convert output to {cap.name} expected format",
                        ],
                        risks=["Data loss possible during transformation"],
                    )
                )
            else:
                # Suggest fallback or custom adapter
                suggestions.append(
                    AdaptationSuggestion(
                        suggestion_type=SuggestionType.CUSTOM_ADAPTER,
                        priority=SuggestionPriority.CRITICAL,
                        description=(
                            f"Implement custom adapter for '{cap.name}' - "
                            f"no suitable match found"
                        ),
                        effort_estimate=EffortLevel.HIGH,
                        compatibility_improvement=0.5,
                        implementation_hints=[
                            f"Create wrapper that implements {cap.capability_id} interface",
                            "May require external service integration",
                        ],
                        risks=[
                            "Significant development effort",
                            "May not achieve full compatibility",
                        ],
                    )
                )

        return suggestions

    def _get_trade_offs(
        self,
        alternative: AgentCapability | None,
        best: AgentCapability | None,
    ) -> list[str]:
        """Get trade-offs of using alternative instead of best match."""
        trade_offs: list[str] = []

        if not alternative or not best:
            return trade_offs

        if alternative.capability_type != best.capability_type:
            trade_offs.append(
                f"Different type: {alternative.capability_type.value} vs {best.capability_type.value}"
            )

        # Compare performance hints if available
        if alternative.performance_hints and best.performance_hints:
            alt_latency = alternative.performance_hints.typical_latency_ms
            best_latency = best.performance_hints.typical_latency_ms
            if alt_latency > best_latency * 1.5:
                trade_offs.append(f"Higher latency: {alt_latency}ms vs {best_latency}ms")

        return trade_offs
