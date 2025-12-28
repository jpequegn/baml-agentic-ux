"""TypeScript types exporter for LUI schemas."""

from dataclasses import dataclass
from typing import Any

from baml_client.types import (
    InterfaceSchema,
    LUIComponent,
    ParameterType,
    ComponentParameter,
    LUIComponentType,
)


def param_type_to_ts_type(param_type: ParameterType) -> str:
    """Convert a LUI parameter type to TypeScript type."""
    type_mapping = {
        ParameterType.STRING: "string",
        ParameterType.NUMBER: "number",
        ParameterType.BOOLEAN: "boolean",
        ParameterType.DATE: "Date",
        ParameterType.ENUM: "string",
        ParameterType.ENTITY: "string",
        ParameterType.LIST: "string[]",
    }
    return type_mapping.get(param_type, "unknown")


def to_pascal_case(s: str) -> str:
    """Convert a string to PascalCase."""
    parts = s.replace("-", "_").split("_")
    return "".join(word.capitalize() for word in parts)


def to_camel_case(s: str) -> str:
    """Convert a string to camelCase."""
    pascal = to_pascal_case(s)
    return pascal[0].lower() + pascal[1:] if pascal else ""


@dataclass
class TypeScriptExporter:
    """Exports LUI schemas to TypeScript type definitions."""

    include_jsdoc: bool = True
    include_enums: bool = True
    namespace: str | None = None
    export_style: str = "interface"  # "interface" or "type"

    def export(self, schema: InterfaceSchema) -> str:
        """Export the schema to TypeScript type definitions."""
        lines: list[str] = []

        # Header comment
        lines.append("/**")
        lines.append(f" * {schema.name}")
        lines.append(f" * {schema.description}")
        lines.append(f" * Version: {schema.version}")
        lines.append(" * ")
        lines.append(" * Auto-generated from LUI schema. Do not edit manually.")
        lines.append(" */")
        lines.append("")

        # Enums
        if self.include_enums:
            lines.extend(self._generate_enums())
            lines.append("")

        # Start namespace if specified
        if self.namespace:
            lines.append(f"export namespace {self.namespace} {{")
            indent = "  "
        else:
            indent = ""

        # Component types
        for component in schema.components:
            lines.extend(self._generate_component_types(component, indent))
            lines.append("")

        # Main schema interface
        lines.extend(self._generate_schema_interface(schema, indent))
        lines.append("")

        # Action dispatcher type
        lines.extend(self._generate_action_types(schema, indent))

        # Close namespace
        if self.namespace:
            lines.append("}")

        return "\n".join(lines)

    def _generate_enums(self) -> list[str]:
        """Generate TypeScript enums for component types and parameter types."""
        lines: list[str] = []

        # Component type enum
        lines.append("export enum LUIComponentType {")
        for comp_type in LUIComponentType:
            lines.append(f"  {comp_type.name} = '{comp_type.value}',")
        lines.append("}")
        lines.append("")

        # Parameter type enum
        lines.append("export enum ParameterType {")
        for param_type in ParameterType:
            lines.append(f"  {param_type.name} = '{param_type.value}',")
        lines.append("}")

        return lines

    def _generate_component_types(
        self,
        component: LUIComponent,
        indent: str,
    ) -> list[str]:
        """Generate TypeScript types for a component."""
        lines: list[str] = []
        type_name = to_pascal_case(component.component_id)

        # Input params type
        if component.parameters:
            lines.extend(self._generate_params_interface(component, type_name, indent))
            lines.append("")

        # Result type
        lines.extend(self._generate_result_interface(component, type_name, indent))

        return lines

    def _generate_params_interface(
        self,
        component: LUIComponent,
        type_name: str,
        indent: str,
    ) -> list[str]:
        """Generate TypeScript interface for component parameters."""
        lines: list[str] = []

        if self.include_jsdoc:
            lines.append(f"{indent}/**")
            lines.append(f"{indent} * Parameters for {component.intent}")
            lines.append(f"{indent} */")

        keyword = "interface" if self.export_style == "interface" else "type"
        eq = "" if keyword == "interface" else " ="

        lines.append(f"{indent}export {keyword} {type_name}Params{eq} {{")

        for param in component.parameters:
            if self.include_jsdoc:
                lines.append(f"{indent}  /** {param.description} */")

            optional = "" if param.required else "?"
            ts_type = param_type_to_ts_type(param.param_type)
            lines.append(f"{indent}  {to_camel_case(param.name)}{optional}: {ts_type};")

        lines.append(f"{indent}}}")

        return lines

    def _generate_result_interface(
        self,
        component: LUIComponent,
        type_name: str,
        indent: str,
    ) -> list[str]:
        """Generate TypeScript interface for component result."""
        lines: list[str] = []

        if self.include_jsdoc:
            lines.append(f"{indent}/**")
            lines.append(f"{indent} * Result of {component.intent}")
            lines.append(f"{indent} */")

        keyword = "interface" if self.export_style == "interface" else "type"
        eq = "" if keyword == "interface" else " ="

        lines.append(f"{indent}export {keyword} {type_name}Result{eq} {{")
        lines.append(f"{indent}  success: boolean;")
        lines.append(f"{indent}  message: string;")
        lines.append(f"{indent}  data?: unknown;")

        if component.feedback.confirmation_required:
            lines.append(f"{indent}  requiresConfirmation?: boolean;")
            lines.append(f"{indent}  confirmationPrompt?: string;")

        lines.append(f"{indent}}}")

        return lines

    def _generate_schema_interface(
        self,
        schema: InterfaceSchema,
        indent: str,
    ) -> list[str]:
        """Generate the main schema interface."""
        lines: list[str] = []
        schema_name = to_pascal_case(schema.schema_id.replace("-", "_"))

        if self.include_jsdoc:
            lines.append(f"{indent}/**")
            lines.append(f"{indent} * {schema.name} interface schema")
            lines.append(f"{indent} * {schema.description}")
            lines.append(f"{indent} */")

        lines.append(f"{indent}export interface {schema_name}Schema {{")
        lines.append(f"{indent}  schemaId: '{schema.schema_id}';")
        lines.append(f"{indent}  name: '{schema.name}';")
        lines.append(f"{indent}  version: '{schema.version}';")

        # Component IDs
        component_ids = [f"'{c.component_id}'" for c in schema.components]
        lines.append(f"{indent}  componentIds: [{', '.join(component_ids)}];")

        lines.append(f"{indent}}}")

        return lines

    def _generate_action_types(
        self,
        schema: InterfaceSchema,
        indent: str,
    ) -> list[str]:
        """Generate action dispatcher types."""
        lines: list[str] = []

        if self.include_jsdoc:
            lines.append(f"{indent}/**")
            lines.append(f"{indent} * Union type for all action names")
            lines.append(f"{indent} */")

        action_names = [f"'{c.component_id}'" for c in schema.components]
        lines.append(f"{indent}export type ActionName = {' | '.join(action_names)};")
        lines.append("")

        # Action handlers interface
        if self.include_jsdoc:
            lines.append(f"{indent}/**")
            lines.append(f"{indent} * Action handler interface for implementing LUI actions")
            lines.append(f"{indent} */")

        lines.append(f"{indent}export interface ActionHandlers {{")

        for component in schema.components:
            type_name = to_pascal_case(component.component_id)
            handler_name = to_camel_case(component.component_id)

            if component.parameters:
                lines.append(f"{indent}  {handler_name}(params: {type_name}Params): Promise<{type_name}Result>;")
            else:
                lines.append(f"{indent}  {handler_name}(): Promise<{type_name}Result>;")

        lines.append(f"{indent}}}")

        return lines

    def export_declaration_file(self, schema: InterfaceSchema) -> str:
        """Export as a .d.ts declaration file."""
        content = self.export(schema)
        return f"// Type definitions for {schema.name}\n// Project: LUI Schema Export\n\n{content}"


def export_to_typescript(
    schema: InterfaceSchema,
    include_jsdoc: bool = True,
    namespace: str | None = None,
) -> str:
    """Export a LUI schema to TypeScript type definitions.

    Args:
        schema: The LUI interface schema to export
        include_jsdoc: Whether to include JSDoc comments (default: True)
        namespace: Optional namespace to wrap types in

    Returns:
        A TypeScript type definitions string
    """
    exporter = TypeScriptExporter(
        include_jsdoc=include_jsdoc,
        namespace=namespace,
    )
    return exporter.export(schema)
