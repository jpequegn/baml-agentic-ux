"""JSON Schema parser and importer for LUI schemas.

This module provides functionality to parse JSON Schema files and convert
them into LUI-compatible InterfaceSchema objects.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from baml_client.types import (
    ComponentParameter,
    DomainInfo,
    FeedbackConfig,
    InterfaceSchema,
    InvocationPattern,
    LUIComponent,
    LUIComponentType,
    ParameterType,
)

from .type_mapper import JsonSchemaToLUIMapper, json_schema_type_to_parameter_type


@dataclass
class ParsedProperty:
    """A parsed property from JSON Schema."""

    name: str
    parameter_type: ParameterType
    description: str | None = None
    required: bool = False
    default_value: Any = None
    enum_values: list[str] | None = None
    constraints: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedSchema:
    """Intermediate representation of a parsed JSON Schema."""

    title: str
    description: str | None = None
    schema_type: str = "object"
    properties: list[ParsedProperty] = field(default_factory=list)
    definitions: dict[str, dict[str, Any]] = field(default_factory=dict)
    required: list[str] = field(default_factory=list)
    raw_schema: dict[str, Any] = field(default_factory=dict)


class JsonSchemaParser:
    """Parses JSON Schema files into intermediate representations.

    This parser supports JSON Schema draft-07 and later, including:
    - Basic types (string, number, integer, boolean, array, object)
    - Formats (date-time, email, uri, etc.)
    - Enums and const values
    - $ref references
    - Definitions/$defs
    - Composition (allOf, oneOf, anyOf)

    Example:
        parser = JsonSchemaParser()
        parsed = parser.parse_file("schema.json")
        lui_schema = parser.to_interface_schema(parsed)
    """

    def __init__(self) -> None:
        self.type_mapper = JsonSchemaToLUIMapper()

    def parse_file(self, file_path: str | Path) -> ParsedSchema:
        """Parse a JSON Schema file.

        Args:
            file_path: Path to the JSON Schema file

        Returns:
            ParsedSchema intermediate representation

        Raises:
            FileNotFoundError: If the file doesn't exist
            json.JSONDecodeError: If the file is not valid JSON
        """
        path = Path(file_path)
        with open(path) as f:
            schema = json.load(f)
        return self.parse(schema)

    def parse(self, schema: dict[str, Any]) -> ParsedSchema:
        """Parse a JSON Schema dictionary.

        Args:
            schema: A JSON Schema as a dictionary

        Returns:
            ParsedSchema intermediate representation
        """
        # Extract definitions for reference resolution
        definitions = schema.get("definitions", schema.get("$defs", {}))
        self.type_mapper.definitions = definitions

        # Parse basic info
        title = schema.get("title", "Imported Schema")
        description = schema.get("description")
        schema_type = schema.get("type", "object")

        # Parse properties
        properties = []
        required_props = set(schema.get("required", []))

        if schema_type == "object" and "properties" in schema:
            for prop_name, prop_schema in schema["properties"].items():
                parsed_prop = self._parse_property(
                    prop_name,
                    prop_schema,
                    is_required=prop_name in required_props,
                )
                properties.append(parsed_prop)

        return ParsedSchema(
            title=title,
            description=description,
            schema_type=schema_type,
            properties=properties,
            definitions=definitions,
            required=list(required_props),
            raw_schema=schema,
        )

    def _parse_property(
        self,
        name: str,
        schema: dict[str, Any],
        is_required: bool = False,
    ) -> ParsedProperty:
        """Parse a single property from JSON Schema."""
        mapping = self.type_mapper.map_schema(schema)

        return ParsedProperty(
            name=name,
            parameter_type=mapping.parameter_type,
            description=mapping.description or schema.get("description"),
            required=is_required,
            default_value=schema.get("default"),
            enum_values=mapping.enum_values,
            constraints=mapping.constraints,
        )

    def to_interface_schema(
        self,
        parsed: ParsedSchema,
        schema_id: str | None = None,
        domain_name: str = "imported",
    ) -> InterfaceSchema:
        """Convert a ParsedSchema to an InterfaceSchema.

        This creates a basic InterfaceSchema with a single component
        representing the schema's structure.

        Args:
            parsed: The parsed JSON Schema
            schema_id: Optional schema ID (auto-generated if not provided)
            domain_name: Domain name for the schema

        Returns:
            An InterfaceSchema object
        """
        # Generate schema ID from title if not provided
        if schema_id is None:
            schema_id = _slugify(parsed.title)

        # Create domain info
        domain = DomainInfo(
            domain_name=domain_name,
            subdomain=None,
            description=parsed.description or f"Imported from JSON Schema: {parsed.title}",
            key_concepts=[prop.name for prop in parsed.properties[:5]],
            terminology=None,
        )

        # Create component parameters from properties
        parameters = []
        for prop in parsed.properties:
            param = ComponentParameter(
                name=prop.name,
                param_type=prop.parameter_type,
                description=prop.description or f"Parameter: {prop.name}",
                required=prop.required,
                default_value=str(prop.default_value) if prop.default_value else None,
                extraction_hints=prop.enum_values or [],
                validation=None,
            )
            parameters.append(param)

        # Create a single component for the schema
        component = LUIComponent(
            component_id=f"{schema_id}_action",
            component_type=LUIComponentType.ACTION,
            intent=f"Execute {parsed.title} operation",
            invocation=InvocationPattern(
                primary_phrase=f"run {parsed.title.lower()}",
                alternate_phrases=[
                    f"execute {parsed.title.lower()}",
                    f"perform {parsed.title.lower()}",
                ],
                examples=[],
                context_requirements=None,
            ),
            parameters=parameters,
            feedback=FeedbackConfig(
                success_template=f"{parsed.title} completed successfully.",
                error_template=f"Failed to execute {parsed.title}: {{error}}",
                progress_template=f"Processing {parsed.title}...",
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
            execution=None,
            context=None,
        )

        return InterfaceSchema(
            schema_id=schema_id,
            name=parsed.title,
            description=parsed.description or f"Schema imported from JSON Schema",
            version="1.0.0",
            domain=domain,
            components=[component],
            flows=[],
            entities=[],
            global_context=None,
            accessibility=None,
        )


def parse_json_schema(schema: dict[str, Any]) -> ParsedSchema:
    """Parse a JSON Schema dictionary.

    Convenience function that creates a parser and parses the schema.

    Args:
        schema: A JSON Schema dictionary

    Returns:
        ParsedSchema intermediate representation
    """
    parser = JsonSchemaParser()
    return parser.parse(schema)


def import_json_schema(
    source: str | Path | dict[str, Any],
    schema_id: str | None = None,
    domain_name: str = "imported",
) -> InterfaceSchema:
    """Import a JSON Schema and convert to InterfaceSchema.

    This is the main entry point for importing JSON Schema files.

    Args:
        source: Path to JSON file, or a schema dictionary
        schema_id: Optional schema ID (auto-generated if not provided)
        domain_name: Domain name for the schema

    Returns:
        An InterfaceSchema object

    Examples:
        # From file path
        schema = import_json_schema("api/schema.json")

        # From dictionary
        schema = import_json_schema({"type": "object", "properties": {...}})
    """
    parser = JsonSchemaParser()

    if isinstance(source, dict):
        parsed = parser.parse(source)
    else:
        parsed = parser.parse_file(source)

    return parser.to_interface_schema(
        parsed,
        schema_id=schema_id,
        domain_name=domain_name,
    )


def _slugify(text: str) -> str:
    """Convert text to a valid schema ID."""
    import re

    # Convert to lowercase and replace spaces/special chars with underscores
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[-\s]+", "_", slug)
    return slug.strip("_")
