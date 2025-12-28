"""Markdown documentation exporter for LUI schemas."""

from dataclasses import dataclass
from typing import Any

from baml_client.types import (
    InterfaceSchema,
    LUIComponent,
    LUIComponentType,
    ComponentParameter,
)


@dataclass
class MarkdownExporter:
    """Exports LUI schemas to Markdown documentation."""

    include_toc: bool = True
    include_examples: bool = True
    include_parameters: bool = True
    include_feedback: bool = True
    heading_level: int = 1

    def export(self, schema: InterfaceSchema) -> str:
        """Export the schema to Markdown format."""
        lines: list[str] = []
        h = "#" * self.heading_level

        # Title and description
        lines.append(f"{h} {schema.name}\n")
        lines.append(f"{schema.description}\n")

        # Metadata
        lines.append(f"**Version:** {schema.version}\n")

        # Domain info
        if schema.domain:
            lines.append(f"{h}# Domain Information\n")
            lines.append(f"- **Domain:** {schema.domain.domain_name}")
            if schema.domain.subdomain:
                lines.append(f"- **Subdomain:** {schema.domain.subdomain}")
            lines.append(f"- **Description:** {schema.domain.description}")
            if schema.domain.key_concepts:
                concepts = ", ".join(schema.domain.key_concepts)
                lines.append(f"- **Key Concepts:** {concepts}")
            lines.append("")

        # Table of contents
        if self.include_toc and schema.components:
            lines.append(f"{h}# Table of Contents\n")
            for component in schema.components:
                anchor = component.component_id.lower().replace(" ", "-")
                lines.append(f"- [{component.intent}](#{anchor})")
            lines.append("")

        # Components by type
        components_by_type = self._group_by_type(schema.components)

        lines.append(f"{h}# Available Commands\n")

        for comp_type, components in components_by_type.items():
            lines.append(f"{h}## {comp_type.value.title()} Commands\n")

            for component in components:
                lines.extend(self._render_component(component))

        # Entities if available
        if schema.entities:
            lines.append(f"{h}# Domain Entities\n")
            for entity in schema.entities:
                lines.append(f"{h}## {entity.entity_name}\n")
                lines.append(f"{entity.description}\n")
                if entity.attributes:
                    lines.append("| Attribute | Type | Description |")
                    lines.append("|-----------|------|-------------|")
                    for attr in entity.attributes:
                        lines.append(f"| {attr.attribute_name} | {attr.attribute_type.value} | {attr.description} |")
                    lines.append("")

        # Flows if available
        if schema.flows:
            lines.append(f"{h}# Conversational Flows\n")
            for flow in schema.flows:
                lines.append(f"{h}## {flow.name}\n")
                if flow.description:
                    lines.append(f"{flow.description}\n")
                if flow.steps:
                    lines.append("**Steps:**\n")
                    for i, step in enumerate(flow.steps, 1):
                        step_desc = step.prompt_template or step.component_ref or step.step_type.value
                        lines.append(f"{i}. {step.step_id}: {step_desc}")
                    lines.append("")

        return "\n".join(lines)

    def _group_by_type(
        self,
        components: list[LUIComponent],
    ) -> dict[LUIComponentType, list[LUIComponent]]:
        """Group components by their type."""
        groups: dict[LUIComponentType, list[LUIComponent]] = {}
        for component in components:
            if component.component_type not in groups:
                groups[component.component_type] = []
            groups[component.component_type].append(component)
        return groups

    def _render_component(self, component: LUIComponent) -> list[str]:
        """Render a single component to Markdown."""
        h = "#" * (self.heading_level + 2)
        lines: list[str] = []

        # Component header with anchor
        lines.append(f"<a id=\"{component.component_id.lower()}\"></a>")
        lines.append(f"{h} {component.intent}\n")

        # Invocation
        lines.append(f"**Say:** \"{component.invocation.primary_phrase}\"\n")

        if component.invocation.alternate_phrases:
            phrases = ", ".join(f'"{p}"' for p in component.invocation.alternate_phrases)
            lines.append(f"**Also works with:** {phrases}\n")

        # Examples
        if self.include_examples and component.invocation.examples:
            lines.append("**Examples:**\n")
            for example in component.invocation.examples:
                lines.append(f"- \"{example}\"")
            lines.append("")

        # Parameters
        if self.include_parameters and component.parameters:
            lines.append("**Parameters:**\n")
            lines.append("| Name | Type | Required | Description |")
            lines.append("|------|------|----------|-------------|")
            for param in component.parameters:
                required = "Yes" if param.required else "No"
                lines.append(f"| `{param.name}` | {param.param_type.value} | {required} | {param.description} |")
            lines.append("")

        # Feedback templates
        if self.include_feedback:
            lines.append("**Responses:**\n")
            lines.append(f"- ✅ Success: \"{component.feedback.success_template}\"")
            lines.append(f"- ❌ Error: \"{component.feedback.error_template}\"")
            if component.feedback.confirmation_required:
                prompt = component.feedback.confirmation_prompt or "Are you sure?"
                lines.append(f"- ⚠️ Confirmation: \"{prompt}\"")
            lines.append("")

        lines.append("---\n")

        return lines

    def export_quick_reference(self, schema: InterfaceSchema) -> str:
        """Export a quick reference card in Markdown format."""
        lines: list[str] = []
        h = "#" * self.heading_level

        lines.append(f"{h} {schema.name} - Quick Reference\n")

        # Commands table
        lines.append("| Command | What to say | Type |")
        lines.append("|---------|-------------|------|")

        for component in schema.components:
            lines.append(
                f"| {component.intent} | "
                f"\"{component.invocation.primary_phrase}\" | "
                f"{component.component_type.value} |"
            )

        lines.append("")

        # Key concepts
        if schema.domain and schema.domain.key_concepts:
            lines.append(f"{h}# Key Concepts\n")
            for concept in schema.domain.key_concepts:
                lines.append(f"- {concept}")
            lines.append("")

        return "\n".join(lines)


def export_to_markdown(
    schema: InterfaceSchema,
    include_toc: bool = True,
    include_examples: bool = True,
) -> str:
    """Export a LUI schema to Markdown documentation.

    Args:
        schema: The LUI interface schema to export
        include_toc: Whether to include table of contents (default: True)
        include_examples: Whether to include invocation examples (default: True)

    Returns:
        A Markdown formatted string
    """
    exporter = MarkdownExporter(
        include_toc=include_toc,
        include_examples=include_examples,
    )
    return exporter.export(schema)
