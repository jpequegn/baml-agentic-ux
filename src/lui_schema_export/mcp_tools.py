"""MCP (Model Context Protocol) tools exporter for LUI schemas."""

from dataclasses import dataclass, field
from typing import Any

from baml_client.types import (
    InterfaceSchema,
    LUIComponent,
    ParameterType,
    ComponentParameter,
)


def param_type_to_json_type(param_type: ParameterType) -> str:
    """Convert a LUI parameter type to JSON Schema type string."""
    type_mapping = {
        ParameterType.STRING: "string",
        ParameterType.NUMBER: "number",
        ParameterType.BOOLEAN: "boolean",
        ParameterType.DATE: "string",
        ParameterType.ENUM: "string",
        ParameterType.ENTITY: "string",
        ParameterType.LIST: "array",
    }
    return type_mapping.get(param_type, "string")


def build_mcp_property(param: ComponentParameter) -> dict[str, Any]:
    """Build an MCP tool property from a component parameter."""
    prop: dict[str, Any] = {
        "type": param_type_to_json_type(param.param_type),
        "description": param.description,
    }

    # Handle array type
    if param.param_type == ParameterType.LIST:
        prop["items"] = {"type": "string"}

    # Add format for date
    if param.param_type == ParameterType.DATE:
        prop["format"] = "date-time"

    # Add default value
    if param.default_value is not None:
        prop["default"] = param.default_value

    return prop


@dataclass
class MCPToolsExporter:
    """Exports LUI schemas to MCP tool definitions."""

    include_annotations: bool = True
    include_examples: bool = True
    tool_name_prefix: str = ""

    def export(self, schema: InterfaceSchema) -> list[dict[str, Any]]:
        """Export the schema to MCP tool definitions."""
        tools = []

        for component in schema.components:
            tool = self._build_tool(component, schema)
            tools.append(tool)

        return tools

    def _build_tool(
        self,
        component: LUIComponent,
        schema: InterfaceSchema,
    ) -> dict[str, Any]:
        """Build an MCP tool definition for a component."""
        tool_name = f"{self.tool_name_prefix}{component.component_id}"

        # Build input schema
        properties: dict[str, Any] = {}
        required: list[str] = []

        for param in component.parameters:
            properties[param.name] = build_mcp_property(param)
            if param.required:
                required.append(param.name)

        input_schema: dict[str, Any] = {
            "type": "object",
            "properties": properties,
        }

        if required:
            input_schema["required"] = required

        tool: dict[str, Any] = {
            "name": tool_name,
            "description": self._build_description(component),
            "inputSchema": input_schema,
        }

        # Add annotations if enabled
        if self.include_annotations:
            tool["annotations"] = self._build_annotations(component, schema)

        return tool

    def _build_description(self, component: LUIComponent) -> str:
        """Build a description for the MCP tool."""
        lines = [component.intent]

        lines.append(f"\nInvoke with: \"{component.invocation.primary_phrase}\"")

        if component.invocation.alternate_phrases:
            alt = ", ".join(f'"{p}"' for p in component.invocation.alternate_phrases[:3])
            lines.append(f"Also: {alt}")

        if self.include_examples and component.invocation.examples:
            lines.append("\nExamples:")
            for example in component.invocation.examples[:3]:
                lines.append(f"  - {example}")

        return "\n".join(lines)

    def _build_annotations(
        self,
        component: LUIComponent,
        schema: InterfaceSchema,
    ) -> dict[str, Any]:
        """Build MCP annotations for the tool."""
        annotations: dict[str, Any] = {
            "component_type": component.component_type.value,
            "domain": schema.domain.domain_name if schema.domain else None,
            "confirmation_required": component.feedback.confirmation_required,
        }

        # Add accessibility info if available
        if component.accessibility:
            annotations["accessibility"] = {
                "screen_reader_label": component.accessibility.screen_reader_label,
                "keyboard_shortcut": component.accessibility.keyboard_shortcut,
            }

        return annotations

    def export_as_server_capabilities(
        self,
        schema: InterfaceSchema,
    ) -> dict[str, Any]:
        """Export as MCP server capabilities format."""
        tools = self.export(schema)

        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {
                    "listChanged": True,
                }
            },
            "serverInfo": {
                "name": schema.name,
                "version": schema.version,
            },
            "tools": tools,
        }


def export_to_mcp_tools(
    schema: InterfaceSchema,
    include_annotations: bool = True,
    tool_name_prefix: str = "",
) -> list[dict[str, Any]]:
    """Export a LUI schema to MCP tool definitions.

    Args:
        schema: The LUI interface schema to export
        include_annotations: Whether to include MCP annotations (default: True)
        tool_name_prefix: Prefix to add to tool names (default: "")

    Returns:
        A list of MCP tool definitions
    """
    exporter = MCPToolsExporter(
        include_annotations=include_annotations,
        tool_name_prefix=tool_name_prefix,
    )
    return exporter.export(schema)
