"""Type mapping between JSON Schema and LUI/BAML types.

This module provides bidirectional mapping between JSON Schema types
and LUI ParameterTypes, enabling seamless conversion of schema definitions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from baml_client.types import ParameterType


class JsonSchemaType(str, Enum):
    """Standard JSON Schema types."""

    STRING = "string"
    NUMBER = "number"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    NULL = "null"


@dataclass
class TypeMappingResult:
    """Result of a type mapping operation."""

    parameter_type: ParameterType
    is_array: bool = False
    is_optional: bool = False
    enum_values: list[str] | None = None
    format_hint: str | None = None
    constraints: dict[str, Any] = field(default_factory=dict)
    nested_type: TypeMappingResult | None = None
    description: str | None = None


# JSON Schema type to LUI ParameterType mapping
JSON_SCHEMA_TO_LUI_TYPE: dict[str, ParameterType] = {
    "string": ParameterType.STRING,
    "number": ParameterType.NUMBER,
    "integer": ParameterType.NUMBER,
    "boolean": ParameterType.BOOLEAN,
    "array": ParameterType.LIST,
    "object": ParameterType.ENTITY,
}

# JSON Schema format to LUI ParameterType mapping (for string formats)
JSON_SCHEMA_FORMAT_TO_LUI_TYPE: dict[str, ParameterType] = {
    "date": ParameterType.DATE,
    "date-time": ParameterType.DATE,
    "time": ParameterType.DATE,
    "email": ParameterType.STRING,
    "uri": ParameterType.STRING,
    "uuid": ParameterType.STRING,
}

# Reverse mapping: LUI ParameterType to JSON Schema type
LUI_TYPE_TO_JSON_SCHEMA: dict[ParameterType, dict[str, Any]] = {
    ParameterType.STRING: {"type": "string"},
    ParameterType.NUMBER: {"type": "number"},
    ParameterType.BOOLEAN: {"type": "boolean"},
    ParameterType.DATE: {"type": "string", "format": "date-time"},
    ParameterType.ENUM: {"type": "string"},
    ParameterType.ENTITY: {"type": "object"},
    ParameterType.LIST: {"type": "array"},
}


def json_schema_type_to_parameter_type(
    schema: dict[str, Any],
) -> TypeMappingResult:
    """Convert a JSON Schema type definition to a LUI ParameterType.

    Args:
        schema: A JSON Schema definition dict

    Returns:
        TypeMappingResult with the mapped type and metadata

    Examples:
        >>> json_schema_type_to_parameter_type({"type": "string"})
        TypeMappingResult(parameter_type=ParameterType.STRING, ...)

        >>> json_schema_type_to_parameter_type({"type": "string", "enum": ["a", "b"]})
        TypeMappingResult(parameter_type=ParameterType.ENUM, enum_values=["a", "b"], ...)
    """
    schema_type = schema.get("type", "string")
    format_hint = schema.get("format")
    description = schema.get("description")

    # Handle enum types
    if "enum" in schema:
        return TypeMappingResult(
            parameter_type=ParameterType.ENUM,
            enum_values=schema["enum"],
            description=description,
        )

    # Handle const (single value enum)
    if "const" in schema:
        return TypeMappingResult(
            parameter_type=ParameterType.ENUM,
            enum_values=[schema["const"]],
            description=description,
        )

    # Handle array types
    if schema_type == "array":
        items_schema = schema.get("items", {"type": "string"})
        nested = json_schema_type_to_parameter_type(items_schema)
        return TypeMappingResult(
            parameter_type=ParameterType.LIST,
            is_array=True,
            nested_type=nested,
            description=description,
            constraints=_extract_array_constraints(schema),
        )

    # Handle string with format
    if schema_type == "string" and format_hint:
        param_type = JSON_SCHEMA_FORMAT_TO_LUI_TYPE.get(
            format_hint, ParameterType.STRING
        )
        return TypeMappingResult(
            parameter_type=param_type,
            format_hint=format_hint,
            description=description,
            constraints=_extract_string_constraints(schema),
        )

    # Handle basic types
    param_type = JSON_SCHEMA_TO_LUI_TYPE.get(schema_type, ParameterType.STRING)

    # Extract type-specific constraints
    constraints = {}
    if schema_type == "string":
        constraints = _extract_string_constraints(schema)
    elif schema_type in ("number", "integer"):
        constraints = _extract_number_constraints(schema)

    return TypeMappingResult(
        parameter_type=param_type,
        format_hint=format_hint,
        description=description,
        constraints=constraints,
    )


def _extract_string_constraints(schema: dict[str, Any]) -> dict[str, Any]:
    """Extract string validation constraints from JSON Schema."""
    constraints = {}
    if "minLength" in schema:
        constraints["min_length"] = schema["minLength"]
    if "maxLength" in schema:
        constraints["max_length"] = schema["maxLength"]
    if "pattern" in schema:
        constraints["pattern"] = schema["pattern"]
    return constraints


def _extract_number_constraints(schema: dict[str, Any]) -> dict[str, Any]:
    """Extract number validation constraints from JSON Schema."""
    constraints = {}
    if "minimum" in schema:
        constraints["minimum"] = schema["minimum"]
    if "maximum" in schema:
        constraints["maximum"] = schema["maximum"]
    if "exclusiveMinimum" in schema:
        constraints["exclusive_minimum"] = schema["exclusiveMinimum"]
    if "exclusiveMaximum" in schema:
        constraints["exclusive_maximum"] = schema["exclusiveMaximum"]
    if "multipleOf" in schema:
        constraints["multiple_of"] = schema["multipleOf"]
    return constraints


def _extract_array_constraints(schema: dict[str, Any]) -> dict[str, Any]:
    """Extract array validation constraints from JSON Schema."""
    constraints = {}
    if "minItems" in schema:
        constraints["min_items"] = schema["minItems"]
    if "maxItems" in schema:
        constraints["max_items"] = schema["maxItems"]
    if "uniqueItems" in schema:
        constraints["unique_items"] = schema["uniqueItems"]
    return constraints


@dataclass
class JsonSchemaToLUIMapper:
    """Maps JSON Schema definitions to LUI types.

    This class provides comprehensive mapping from JSON Schema to LUI types,
    including support for complex nested structures, references, and
    composition keywords (allOf, oneOf, anyOf).
    """

    definitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    resolved_refs: dict[str, TypeMappingResult] = field(default_factory=dict)

    def map_schema(self, schema: dict[str, Any]) -> TypeMappingResult:
        """Map a JSON Schema to LUI type.

        Args:
            schema: A JSON Schema definition

        Returns:
            TypeMappingResult with the mapped type
        """
        # Handle $ref
        if "$ref" in schema:
            return self._resolve_ref(schema["$ref"])

        # Handle composition keywords
        if "allOf" in schema:
            return self._handle_all_of(schema["allOf"])
        if "oneOf" in schema:
            return self._handle_one_of(schema["oneOf"])
        if "anyOf" in schema:
            return self._handle_any_of(schema["anyOf"])

        # Standard type mapping
        return json_schema_type_to_parameter_type(schema)

    def _resolve_ref(self, ref: str) -> TypeMappingResult:
        """Resolve a JSON Schema $ref."""
        # Check cache
        if ref in self.resolved_refs:
            return self.resolved_refs[ref]

        # Parse reference path
        if ref.startswith("#/definitions/"):
            def_name = ref.replace("#/definitions/", "")
            if def_name in self.definitions:
                result = self.map_schema(self.definitions[def_name])
                self.resolved_refs[ref] = result
                return result

        if ref.startswith("#/$defs/"):
            def_name = ref.replace("#/$defs/", "")
            if def_name in self.definitions:
                result = self.map_schema(self.definitions[def_name])
                self.resolved_refs[ref] = result
                return result

        # Unresolved reference - treat as entity
        return TypeMappingResult(
            parameter_type=ParameterType.ENTITY,
            description=f"Unresolved reference: {ref}",
        )

    def _handle_all_of(
        self, schemas: list[dict[str, Any]]
    ) -> TypeMappingResult:
        """Handle allOf composition - merge all schemas."""
        # For simplicity, return the first schema's type
        # In a full implementation, we'd merge properties
        if schemas:
            return self.map_schema(schemas[0])
        return TypeMappingResult(parameter_type=ParameterType.ENTITY)

    def _handle_one_of(
        self, schemas: list[dict[str, Any]]
    ) -> TypeMappingResult:
        """Handle oneOf composition - union type."""
        # Map to ENUM if all are string enums, otherwise ENTITY
        all_enum_values = []
        for schema in schemas:
            if "const" in schema:
                all_enum_values.append(schema["const"])
            elif "enum" in schema:
                all_enum_values.extend(schema["enum"])

        if all_enum_values:
            return TypeMappingResult(
                parameter_type=ParameterType.ENUM,
                enum_values=all_enum_values,
            )

        return TypeMappingResult(parameter_type=ParameterType.ENTITY)

    def _handle_any_of(
        self, schemas: list[dict[str, Any]]
    ) -> TypeMappingResult:
        """Handle anyOf composition - similar to oneOf for our purposes."""
        return self._handle_one_of(schemas)


def parameter_type_to_json_schema(param_type: ParameterType) -> dict[str, Any]:
    """Convert a LUI ParameterType to JSON Schema type definition.

    This is the reverse of json_schema_type_to_parameter_type.

    Args:
        param_type: A LUI ParameterType

    Returns:
        A JSON Schema type definition dict
    """
    return LUI_TYPE_TO_JSON_SCHEMA.get(param_type, {"type": "string"})
