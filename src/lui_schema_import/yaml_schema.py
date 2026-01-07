"""YAML Schema parser and importer for LUI schemas.

This module provides functionality to parse YAML schema files (including
OpenAPI specs) and convert them into LUI-compatible InterfaceSchema objects.
"""

from __future__ import annotations

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
)

from .json_schema import JsonSchemaParser, ParsedSchema, _slugify
from .type_mapper import JsonSchemaToLUIMapper


def _load_yaml(file_path: str | Path) -> dict[str, Any]:
    """Load a YAML file.

    Args:
        file_path: Path to the YAML file

    Returns:
        Parsed YAML as a dictionary

    Raises:
        ImportError: If PyYAML is not installed
        FileNotFoundError: If the file doesn't exist
    """
    try:
        import yaml
    except ImportError:
        raise ImportError(
            "PyYAML is required for YAML schema import. "
            "Install it with: pip install pyyaml"
        )

    path = Path(file_path)
    with open(path) as f:
        return yaml.safe_load(f)


class YamlSchemaParser(JsonSchemaParser):
    """Parses YAML schema files into intermediate representations.

    This parser extends JsonSchemaParser to support YAML format and
    OpenAPI specifications. It can handle:

    - Standard JSON Schema in YAML format
    - OpenAPI 3.x specifications
    - Custom YAML schema definitions

    Example:
        parser = YamlSchemaParser()
        parsed = parser.parse_file("api/openapi.yaml")
        lui_schema = parser.to_interface_schema(parsed)
    """

    def parse_file(self, file_path: str | Path) -> ParsedSchema:
        """Parse a YAML schema file.

        Args:
            file_path: Path to the YAML schema file

        Returns:
            ParsedSchema intermediate representation
        """
        schema = _load_yaml(file_path)
        return self.parse(schema)

    def parse(self, schema: dict[str, Any]) -> ParsedSchema:
        """Parse a YAML schema dictionary.

        Handles both standard JSON Schema and OpenAPI formats.

        Args:
            schema: A YAML schema as a dictionary

        Returns:
            ParsedSchema intermediate representation
        """
        # Check if this is an OpenAPI spec
        if "openapi" in schema or "swagger" in schema:
            return self._parse_openapi(schema)

        # Otherwise, parse as standard JSON Schema
        return super().parse(schema)

    def _parse_openapi(self, spec: dict[str, Any]) -> ParsedSchema:
        """Parse an OpenAPI specification.

        Extracts schema information from OpenAPI paths and components.

        Args:
            spec: An OpenAPI specification dictionary

        Returns:
            ParsedSchema with OpenAPI-derived properties
        """
        info = spec.get("info", {})
        title = info.get("title", "OpenAPI Schema")
        description = info.get("description")

        # Extract definitions from components/schemas
        components = spec.get("components", {})
        definitions = components.get("schemas", {})
        self.type_mapper.definitions = definitions

        # Parse all request body schemas from paths
        properties = []
        paths = spec.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if isinstance(operation, dict):
                    props = self._extract_operation_parameters(
                        operation, path, method
                    )
                    properties.extend(props)

        return ParsedSchema(
            title=title,
            description=description,
            schema_type="object",
            properties=properties,
            definitions=definitions,
            raw_schema=spec,
        )

    def _extract_operation_parameters(
        self,
        operation: dict[str, Any],
        path: str,
        method: str,
    ) -> list:
        """Extract parameters from an OpenAPI operation."""
        from .json_schema import ParsedProperty

        properties = []

        # Extract path/query parameters
        for param in operation.get("parameters", []):
            schema = param.get("schema", {"type": "string"})
            mapping = self.type_mapper.map_schema(schema)

            properties.append(
                ParsedProperty(
                    name=param.get("name", "unknown"),
                    parameter_type=mapping.parameter_type,
                    description=param.get("description"),
                    required=param.get("required", False),
                    enum_values=mapping.enum_values,
                    constraints=mapping.constraints,
                )
            )

        # Extract request body parameters
        request_body = operation.get("requestBody", {})
        content = request_body.get("content", {})

        for media_type, media_schema in content.items():
            schema = media_schema.get("schema", {})
            if schema.get("type") == "object":
                required_props = set(schema.get("required", []))
                for prop_name, prop_schema in schema.get("properties", {}).items():
                    mapping = self.type_mapper.map_schema(prop_schema)
                    properties.append(
                        ParsedProperty(
                            name=prop_name,
                            parameter_type=mapping.parameter_type,
                            description=prop_schema.get("description"),
                            required=prop_name in required_props,
                            default_value=prop_schema.get("default"),
                            enum_values=mapping.enum_values,
                            constraints=mapping.constraints,
                        )
                    )

        return properties

    def to_interface_schema(
        self,
        parsed: ParsedSchema,
        schema_id: str | None = None,
        domain_name: str = "imported",
    ) -> InterfaceSchema:
        """Convert a ParsedSchema to an InterfaceSchema.

        For OpenAPI specs, this creates components for each endpoint.
        """
        # Check if this was an OpenAPI spec
        if "openapi" in parsed.raw_schema or "swagger" in parsed.raw_schema:
            return self._openapi_to_interface_schema(
                parsed, schema_id, domain_name
            )

        # Otherwise, use standard conversion
        return super().to_interface_schema(parsed, schema_id, domain_name)

    def _openapi_to_interface_schema(
        self,
        parsed: ParsedSchema,
        schema_id: str | None = None,
        domain_name: str = "imported",
    ) -> InterfaceSchema:
        """Convert an OpenAPI-derived ParsedSchema to InterfaceSchema."""
        spec = parsed.raw_schema

        if schema_id is None:
            schema_id = _slugify(parsed.title)

        # Create domain info
        domain = DomainInfo(
            domain_name=domain_name,
            subdomain=None,
            description=parsed.description or f"Imported from OpenAPI: {parsed.title}",
            key_concepts=[],
            terminology=None,
        )

        # Create components from OpenAPI paths
        components = []
        paths = spec.get("paths", {})

        for path, methods in paths.items():
            for method, operation in methods.items():
                if isinstance(operation, dict):
                    component = self._operation_to_component(
                        path, method, operation
                    )
                    if component:
                        components.append(component)

        # If no components were created, create a default one
        if not components:
            components.append(
                LUIComponent(
                    component_id=f"{schema_id}_default",
                    component_type=LUIComponentType.ACTION,
                    intent="Default action",
                    invocation=InvocationPattern(
                        primary_phrase="execute action",
                        alternate_phrases=[],
                        examples=[],
                        context_requirements=None,
                    ),
                    parameters=[],
                    feedback=FeedbackConfig(
                        success_template="Action completed.",
                        error_template="Action failed: {error}",
                        progress_template=None,
                        confirmation_required=False,
                        confirmation_prompt=None,
                    ),
                    accessibility=None,
                    execution=None,
                    context=None,
                )
            )

        return InterfaceSchema(
            schema_id=schema_id,
            name=parsed.title,
            description=parsed.description or f"Imported from OpenAPI: {parsed.title}",
            version=spec.get("info", {}).get("version", "1.0.0"),
            domain=domain,
            components=components,
            flows=[],
            entities=[],
            global_context=None,
            accessibility=None,
        )

    def _operation_to_component(
        self,
        path: str,
        method: str,
        operation: dict[str, Any],
    ) -> LUIComponent | None:
        """Convert an OpenAPI operation to a LUIComponent."""
        operation_id = operation.get("operationId")
        if not operation_id:
            # Generate operation ID from path and method
            operation_id = f"{method}_{path.replace('/', '_').strip('_')}"

        summary = operation.get("summary", f"{method.upper()} {path}")
        description = operation.get("description", summary)

        # Create parameters
        parameters = []
        for param in operation.get("parameters", []):
            schema = param.get("schema", {"type": "string"})
            mapping = self.type_mapper.map_schema(schema)

            parameters.append(
                ComponentParameter(
                    name=param.get("name", "param"),
                    param_type=mapping.parameter_type,
                    description=param.get("description", ""),
                    required=param.get("required", False),
                    default_value=None,
                    extraction_hints=mapping.enum_values or [],
                    validation=None,
                )
            )

        # Extract request body parameters
        request_body = operation.get("requestBody", {})
        content = request_body.get("content", {})
        for media_type, media_schema in content.items():
            schema = media_schema.get("schema", {})
            if schema.get("type") == "object":
                required_props = set(schema.get("required", []))
                for prop_name, prop_schema in schema.get("properties", {}).items():
                    mapping = self.type_mapper.map_schema(prop_schema)
                    parameters.append(
                        ComponentParameter(
                            name=prop_name,
                            param_type=mapping.parameter_type,
                            description=prop_schema.get("description", ""),
                            required=prop_name in required_props,
                            default_value=str(prop_schema.get("default")) if prop_schema.get("default") else None,
                            extraction_hints=mapping.enum_values or [],
                            validation=None,
                        )
                    )

        # Determine component type based on HTTP method
        component_type = LUIComponentType.ACTION
        if method.lower() == "get":
            component_type = LUIComponentType.QUERY

        return LUIComponent(
            component_id=_slugify(operation_id),
            component_type=component_type,
            intent=summary,
            invocation=InvocationPattern(
                primary_phrase=summary.lower(),
                alternate_phrases=[description.lower()] if description != summary else [],
                examples=[],
                context_requirements=None,
            ),
            parameters=parameters,
            feedback=FeedbackConfig(
                success_template=f"{summary} completed successfully.",
                error_template=f"Failed to {summary.lower()}: {{error}}",
                progress_template=f"Processing {summary.lower()}...",
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
            execution=None,
            context=None,
        )


def parse_yaml_schema(schema: dict[str, Any]) -> ParsedSchema:
    """Parse a YAML schema dictionary.

    Convenience function that creates a parser and parses the schema.

    Args:
        schema: A YAML schema dictionary

    Returns:
        ParsedSchema intermediate representation
    """
    parser = YamlSchemaParser()
    return parser.parse(schema)


def import_yaml_schema(
    source: str | Path | dict[str, Any],
    schema_id: str | None = None,
    domain_name: str = "imported",
) -> InterfaceSchema:
    """Import a YAML schema and convert to InterfaceSchema.

    This is the main entry point for importing YAML schema files.
    Supports both standard JSON Schema in YAML format and OpenAPI specs.

    Args:
        source: Path to YAML file, or a schema dictionary
        schema_id: Optional schema ID (auto-generated if not provided)
        domain_name: Domain name for the schema

    Returns:
        An InterfaceSchema object

    Examples:
        # From OpenAPI file
        schema = import_yaml_schema("api/openapi.yaml")

        # From dictionary
        schema = import_yaml_schema({"openapi": "3.0.0", ...})
    """
    parser = YamlSchemaParser()

    if isinstance(source, dict):
        parsed = parser.parse(source)
    else:
        parsed = parser.parse_file(source)

    return parser.to_interface_schema(
        parsed,
        schema_id=schema_id,
        domain_name=domain_name,
    )
