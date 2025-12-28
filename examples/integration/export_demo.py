"""
Integration example: Export LUI schemas to multiple formats.

This example demonstrates how to use the lui_schema_export module to convert
a LUI schema into OpenAPI, MCP tools, Markdown, and TypeScript formats.
"""

import json
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lui_simulator.simulator import load_schema_from_dict
from lui_schema_export import (
    export_to_openapi,
    export_to_mcp_tools,
    export_to_markdown,
    export_to_typescript,
)


def main():
    """Run the export demo."""
    # Load the example schema
    schema_path = Path(__file__).parent.parent / "task_manager_schema.json"

    print(f"Loading schema from: {schema_path}")

    with open(schema_path) as f:
        schema_data = json.load(f)

    schema = load_schema_from_dict(schema_data)
    print(f"Loaded schema: {schema.name} (v{schema.version})")
    print(f"Components: {len(schema.components)}")
    print()

    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    # Export to OpenAPI
    print("Exporting to OpenAPI...")
    openapi_spec = export_to_openapi(
        schema,
        base_path="/api/v1",
        server_url="https://api.taskmanager.example.com",
    )
    openapi_path = output_dir / "openapi.json"
    with open(openapi_path, "w") as f:
        json.dump(openapi_spec, f, indent=2)
    print(f"  -> Saved to {openapi_path}")

    # Export to MCP tools
    print("Exporting to MCP tools...")
    mcp_tools = export_to_mcp_tools(schema, tool_name_prefix="task_")
    mcp_path = output_dir / "mcp_tools.json"
    with open(mcp_path, "w") as f:
        json.dump(mcp_tools, f, indent=2)
    print(f"  -> Saved to {mcp_path}")

    # Export to Markdown
    print("Exporting to Markdown...")
    markdown_doc = export_to_markdown(schema)
    markdown_path = output_dir / "documentation.md"
    with open(markdown_path, "w") as f:
        f.write(markdown_doc)
    print(f"  -> Saved to {markdown_path}")

    # Export to TypeScript
    print("Exporting to TypeScript...")
    typescript_types = export_to_typescript(schema, namespace="TaskManager")
    typescript_path = output_dir / "types.ts"
    with open(typescript_path, "w") as f:
        f.write(typescript_types)
    print(f"  -> Saved to {typescript_path}")

    print()
    print("Export complete!")
    print(f"All files saved to: {output_dir}")


if __name__ == "__main__":
    main()
