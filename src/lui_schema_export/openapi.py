"""OpenAPI exporter for LUI schemas."""

from dataclasses import dataclass, field
from typing import Any

from baml_client.types import (
    InterfaceSchema,
    LUIComponent,
    ParameterType,
    ComponentParameter,
)


def param_type_to_json_schema(param_type: ParameterType) -> dict[str, Any]:
    """Convert a LUI parameter type to JSON Schema type."""
    type_mapping = {
        ParameterType.STRING: {"type": "string"},
        ParameterType.NUMBER: {"type": "number"},
        ParameterType.BOOLEAN: {"type": "boolean"},
        ParameterType.DATE: {"type": "string", "format": "date-time"},
        ParameterType.ENUM: {"type": "string"},
        ParameterType.ENTITY: {"type": "string"},
        ParameterType.LIST: {"type": "array", "items": {"type": "string"}},
    }
    return type_mapping.get(param_type, {"type": "string"})


def build_parameter_schema(param: ComponentParameter) -> dict[str, Any]:
    """Build a JSON Schema for a component parameter."""
    schema = param_type_to_json_schema(param.param_type)
    schema["description"] = param.description

    if param.default_value is not None:
        schema["default"] = param.default_value

    # Add extraction hints as examples
    if param.extraction_hints:
        schema["examples"] = param.extraction_hints

    return schema


@dataclass
class OpenAPIExporter:
    """Exports LUI schemas to OpenAPI 3.0 specification."""

    base_path: str = "/actions"
    include_examples: bool = True
    include_feedback_templates: bool = True
    server_url: str = field(default="http://localhost:8000")

    def export(self, schema: InterfaceSchema) -> dict[str, Any]:
        """Export the schema to OpenAPI format."""
        paths = {}
        tags = []

        # Group components by type for tags
        component_types = set()
        for component in schema.components:
            component_types.add(component.component_type.value)

        for comp_type in sorted(component_types):
            tags.append({
                "name": comp_type.lower(),
                "description": f"{comp_type} components",
            })

        # Build paths for each component
        for component in schema.components:
            path = f"{self.base_path}/{component.component_id}"
            paths[path] = self._build_path_item(component)

        # Build the full OpenAPI spec
        spec: dict[str, Any] = {
            "openapi": "3.0.3",
            "info": {
                "title": schema.name,
                "description": schema.description,
                "version": schema.version,
            },
            "servers": [{"url": self.server_url}],
            "tags": tags,
            "paths": paths,
        }

        # Add domain info as extension
        if schema.domain:
            spec["info"]["x-domain"] = {
                "name": schema.domain.domain_name,
                "subdomain": schema.domain.subdomain,
                "description": schema.domain.description,
                "key_concepts": schema.domain.key_concepts,
            }

        return spec

    def _build_path_item(self, component: LUIComponent) -> dict[str, Any]:
        """Build an OpenAPI path item for a component."""
        operation: dict[str, Any] = {
            "operationId": component.component_id,
            "summary": component.intent,
            "description": self._build_description(component),
            "tags": [component.component_type.value.lower()],
        }

        # Build request body if there are parameters
        if component.parameters:
            properties = {}
            required = []

            for param in component.parameters:
                properties[param.name] = build_parameter_schema(param)
                if param.required:
                    required.append(param.name)

            operation["requestBody"] = {
                "required": True,
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": properties,
                            "required": required if required else None,
                        }
                    }
                }
            }

        # Build responses
        operation["responses"] = self._build_responses(component)

        return {"post": operation}

    def _build_description(self, component: LUIComponent) -> str:
        """Build a detailed description for the component."""
        lines = []

        lines.append(f"**Primary Invocation:** {component.invocation.primary_phrase}")

        if component.invocation.alternate_phrases:
            lines.append(f"\n**Alternate Phrases:** {', '.join(component.invocation.alternate_phrases)}")

        if self.include_examples and component.invocation.examples:
            lines.append("\n**Examples:**")
            for example in component.invocation.examples:
                lines.append(f"- {example}")

        return "\n".join(lines)

    def _build_responses(self, component: LUIComponent) -> dict[str, Any]:
        """Build response definitions for the component."""
        responses: dict[str, Any] = {
            "200": {
                "description": "Successful execution",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "success": {"type": "boolean"},
                                "message": {"type": "string"},
                                "data": {"type": "object"},
                            }
                        }
                    }
                }
            },
            "400": {
                "description": "Invalid parameters or request",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "error": {"type": "string"},
                                "details": {"type": "object"},
                            }
                        }
                    }
                }
            }
        }

        if self.include_feedback_templates:
            responses["200"]["x-success-template"] = component.feedback.success_template
            responses["400"]["x-error-template"] = component.feedback.error_template

        # Add confirmation response if required
        if component.feedback.confirmation_required:
            responses["202"] = {
                "description": "Confirmation required",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {
                                "requires_confirmation": {"type": "boolean"},
                                "confirmation_prompt": {"type": "string"},
                            }
                        }
                    }
                }
            }
            if component.feedback.confirmation_prompt:
                responses["202"]["x-confirmation-prompt"] = component.feedback.confirmation_prompt

        return responses


def export_to_openapi(
    schema: InterfaceSchema,
    base_path: str = "/actions",
    server_url: str = "http://localhost:8000",
) -> dict[str, Any]:
    """Export a LUI schema to OpenAPI 3.0 specification.

    Args:
        schema: The LUI interface schema to export
        base_path: Base path for all operations (default: /actions)
        server_url: Server URL for the API (default: http://localhost:8000)

    Returns:
        A dictionary containing the OpenAPI specification
    """
    exporter = OpenAPIExporter(base_path=base_path, server_url=server_url)
    return exporter.export(schema)
