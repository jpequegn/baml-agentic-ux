"""BAML code generator for imported schemas.

This module provides functionality to generate BAML type definitions
from imported JSON/YAML schemas, enabling full round-trip schema support.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from baml_client.types import (
    InterfaceSchema,
    LUIComponent,
    ParameterType,
)

from .json_schema import ParsedProperty, ParsedSchema


# BAML type name mapping
PARAMETER_TYPE_TO_BAML: dict[ParameterType, str] = {
    ParameterType.STRING: "string",
    ParameterType.NUMBER: "float",
    ParameterType.BOOLEAN: "bool",
    ParameterType.DATE: "string",  # BAML doesn't have native date type
    ParameterType.ENUM: "string",  # Will be converted to enum class
    ParameterType.ENTITY: "string",  # Will be converted to class
    ParameterType.LIST: "string[]",  # Will be typed based on items
}


@dataclass
class BAMLGenerator:
    """Generates BAML code from parsed schemas.

    This generator creates valid BAML type definitions including:
    - Class definitions with typed fields
    - Enum definitions
    - Function signatures
    - Description annotations

    Example:
        generator = BAMLGenerator()
        baml_code = generator.generate(parsed_schema)
    """

    indent: str = "  "
    include_descriptions: bool = True
    include_comments: bool = True
    generated_enums: set[str] = field(default_factory=set)

    def generate(self, parsed: ParsedSchema) -> str:
        """Generate BAML code from a ParsedSchema.

        Args:
            parsed: The parsed schema

        Returns:
            Generated BAML code as a string
        """
        lines = []

        # Add header comment
        if self.include_comments:
            lines.append(f"// Auto-generated from: {parsed.title}")
            lines.append(f"// Schema type: {parsed.schema_type}")
            if parsed.description:
                lines.append(f"// Description: {parsed.description}")
            lines.append("")

        # Generate enums first
        enum_code = self._generate_enums(parsed.properties)
        if enum_code:
            lines.append(enum_code)
            lines.append("")

        # Generate main class
        class_code = self._generate_class(parsed)
        lines.append(class_code)

        return "\n".join(lines)

    def generate_from_interface_schema(self, schema: InterfaceSchema) -> str:
        """Generate BAML code from an InterfaceSchema.

        Args:
            schema: An InterfaceSchema object

        Returns:
            Generated BAML code as a string
        """
        lines = []

        # Add header
        if self.include_comments:
            lines.append(f"// Auto-generated LUI Schema: {schema.name}")
            lines.append(f"// Version: {schema.version}")
            if schema.description:
                lines.append(f"// {schema.description}")
            lines.append("")

        # Generate component parameter types
        for component in schema.components:
            component_code = self._generate_component_class(component)
            lines.append(component_code)
            lines.append("")

        return "\n".join(lines)

    def _generate_enums(self, properties: list[ParsedProperty]) -> str:
        """Generate enum definitions for properties with enum values."""
        lines = []

        for prop in properties:
            if prop.enum_values and prop.name not in self.generated_enums:
                enum_name = _to_pascal_case(prop.name) + "Type"
                self.generated_enums.add(prop.name)

                if self.include_descriptions and prop.description:
                    lines.append(f"/// {prop.description}")

                lines.append(f"enum {enum_name} {{")
                for value in prop.enum_values:
                    # Sanitize enum value for BAML
                    safe_value = _to_enum_value(value)
                    lines.append(f"{self.indent}{safe_value}")
                lines.append("}")
                lines.append("")

        return "\n".join(lines) if lines else ""

    def _generate_class(self, parsed: ParsedSchema) -> str:
        """Generate a BAML class definition."""
        lines = []

        class_name = _to_pascal_case(parsed.title)

        # Add class description
        if self.include_descriptions and parsed.description:
            lines.append(f"/// {parsed.description}")

        lines.append(f"class {class_name} {{")

        # Generate fields
        for prop in parsed.properties:
            field_code = self._generate_field(prop)
            lines.append(f"{self.indent}{field_code}")

        lines.append("}")

        return "\n".join(lines)

    def _generate_field(self, prop: ParsedProperty) -> str:
        """Generate a field definition for a property."""
        # Determine BAML type
        if prop.enum_values:
            baml_type = _to_pascal_case(prop.name) + "Type"
        else:
            baml_type = PARAMETER_TYPE_TO_BAML.get(
                prop.parameter_type, "string"
            )

        # Make optional if not required
        if not prop.required:
            baml_type = f"{baml_type}?"

        # Build field line
        field_name = _to_snake_case(prop.name)
        field_line = f"{field_name} {baml_type}"

        # Add description annotation
        if self.include_descriptions and prop.description:
            # Escape description for BAML
            desc = prop.description.replace('"', '\\"')
            field_line += f' @description("{desc}")'

        return field_line

    def _generate_component_class(self, component: LUIComponent) -> str:
        """Generate a BAML class for a LUIComponent's parameters."""
        lines = []

        class_name = _to_pascal_case(component.component_id) + "Params"

        # Add description
        if self.include_descriptions:
            lines.append(f"/// Parameters for: {component.intent}")

        lines.append(f"class {class_name} {{")

        # Generate fields for each parameter
        if component.parameters:
            for param in component.parameters:
                baml_type = PARAMETER_TYPE_TO_BAML.get(
                    param.param_type, "string"
                )

                if not param.required:
                    baml_type = f"{baml_type}?"

                field_name = _to_snake_case(param.name)
                field_line = f"{self.indent}{field_name} {baml_type}"

                if self.include_descriptions and param.description:
                    desc = param.description.replace('"', '\\"')
                    field_line += f' @description("{desc}")'

                lines.append(field_line)

        lines.append("}")

        return "\n".join(lines)


def generate_baml_types(
    source: ParsedSchema | InterfaceSchema,
    include_descriptions: bool = True,
) -> str:
    """Generate BAML type definitions from a schema.

    Main entry point for BAML code generation.

    Args:
        source: A ParsedSchema or InterfaceSchema
        include_descriptions: Whether to include @description annotations

    Returns:
        Generated BAML code as a string

    Examples:
        # From parsed JSON Schema
        parsed = parse_json_schema(schema_dict)
        baml_code = generate_baml_types(parsed)

        # From InterfaceSchema
        lui_schema = import_json_schema("schema.json")
        baml_code = generate_baml_types(lui_schema)
    """
    generator = BAMLGenerator(include_descriptions=include_descriptions)

    if isinstance(source, ParsedSchema):
        return generator.generate(source)
    elif isinstance(source, InterfaceSchema):
        return generator.generate_from_interface_schema(source)
    else:
        raise TypeError(f"Expected ParsedSchema or InterfaceSchema, got {type(source)}")


def generate_baml_class(
    name: str,
    properties: dict[str, Any],
    description: str | None = None,
) -> str:
    """Generate a single BAML class definition.

    Convenience function for generating a class from a dictionary
    of properties.

    Args:
        name: Class name
        properties: Dictionary of property_name -> type_or_schema
        description: Optional class description

    Returns:
        Generated BAML class code

    Examples:
        code = generate_baml_class(
            "UserProfile",
            {
                "name": "string",
                "age": "int",
                "email": {"type": "string", "format": "email"}
            },
            description="User profile information"
        )
    """
    lines = []

    if description:
        lines.append(f"/// {description}")

    lines.append(f"class {name} {{")

    for prop_name, prop_type in properties.items():
        if isinstance(prop_type, str):
            # Simple type
            lines.append(f"  {prop_name} {prop_type}")
        elif isinstance(prop_type, dict):
            # JSON Schema-like definition
            from .type_mapper import json_schema_type_to_parameter_type

            mapping = json_schema_type_to_parameter_type(prop_type)
            baml_type = PARAMETER_TYPE_TO_BAML.get(
                mapping.parameter_type, "string"
            )
            field_line = f"  {prop_name} {baml_type}"

            if mapping.description:
                desc = mapping.description.replace('"', '\\"')
                field_line += f' @description("{desc}")'

            lines.append(field_line)

    lines.append("}")

    return "\n".join(lines)


def _to_pascal_case(text: str) -> str:
    """Convert text to PascalCase."""
    import re

    # Split on non-alphanumeric characters
    words = re.split(r"[^a-zA-Z0-9]+", text)
    # Capitalize each word and join
    return "".join(word.capitalize() for word in words if word)


def _to_snake_case(text: str) -> str:
    """Convert text to snake_case."""
    import re

    # Insert underscore before uppercase letters
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    # Insert underscore before uppercase letters followed by lowercase
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    # Replace non-alphanumeric with underscore and lowercase
    s3 = re.sub(r"[^a-zA-Z0-9]", "_", s2)
    return s3.lower()


def _to_enum_value(text: str) -> str:
    """Convert text to a valid BAML enum value."""
    import re

    # Convert to SCREAMING_SNAKE_CASE
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", str(text))
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1)
    s3 = re.sub(r"[^a-zA-Z0-9]", "_", s2)
    return s3.upper()
