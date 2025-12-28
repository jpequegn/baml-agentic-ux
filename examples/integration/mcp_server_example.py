"""
Integration example: Create an MCP server from a LUI schema.

This example shows how to generate MCP tool definitions and create
a simple server implementation that can be used with Claude or other
MCP-compatible clients.
"""

import json
from pathlib import Path
import sys
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lui_simulator.simulator import load_schema_from_dict
from lui_schema_export import MCPToolsExporter


def create_mcp_server_config(schema_path: str) -> dict[str, Any]:
    """Create an MCP server configuration from a LUI schema.

    This generates the server capabilities and tool definitions that
    can be used to implement an MCP server.

    Args:
        schema_path: Path to the LUI schema JSON file

    Returns:
        MCP server configuration dictionary
    """
    # Load schema
    with open(schema_path) as f:
        schema_data = json.load(f)

    schema = load_schema_from_dict(schema_data)

    # Create exporter with custom settings
    exporter = MCPToolsExporter(
        include_annotations=True,
        include_examples=True,
        tool_name_prefix="",  # No prefix for cleaner names
    )

    # Export as full server capabilities
    return exporter.export_as_server_capabilities(schema)


def generate_tool_handlers_stub(schema_path: str) -> str:
    """Generate Python stub code for tool handlers.

    This creates a skeleton implementation that developers can fill in
    with actual business logic.

    Args:
        schema_path: Path to the LUI schema JSON file

    Returns:
        Python code as a string
    """
    with open(schema_path) as f:
        schema_data = json.load(f)

    schema = load_schema_from_dict(schema_data)

    lines = [
        '"""',
        f"MCP Tool Handlers for {schema.name}",
        "",
        "Auto-generated from LUI schema. Implement the TODO sections.",
        '"""',
        "",
        "from typing import Any",
        "",
        "",
        "class ToolHandlers:",
        f'    """Handlers for {schema.name} tools."""',
        "",
    ]

    for component in schema.components:
        # Convert component_id to snake_case method name
        method_name = component.component_id.replace("-", "_")

        # Build method signature
        params = ["self"]
        for param in component.parameters:
            param_name = param.name.replace("-", "_")
            type_hint = _get_python_type(param.param_type.value)
            if param.required:
                params.append(f"{param_name}: {type_hint}")
            else:
                params.append(f"{param_name}: {type_hint} | None = None")

        params_str = ", ".join(params)

        lines.extend([
            f"    def {method_name}({params_str}) -> dict[str, Any]:",
            f'        """',
            f"        {component.intent}",
            f"        ",
            f'        Invocation: "{component.invocation.primary_phrase}"',
            f'        """',
            f"        # TODO: Implement {component.intent}",
            f"        return {{",
            f'            "success": True,',
            f'            "message": "{component.feedback.success_template}",',
            f'            "data": None,',
            f"        }}",
            "",
        ])

    return "\n".join(lines)


def _get_python_type(param_type: str) -> str:
    """Convert LUI parameter type to Python type hint."""
    type_map = {
        "STRING": "str",
        "NUMBER": "float",
        "BOOLEAN": "bool",
        "DATE": "str",
        "ENUM": "str",
        "ENTITY": "str",
        "LIST": "list[str]",
    }
    return type_map.get(param_type, "Any")


def main():
    """Run the MCP server example."""
    schema_path = Path(__file__).parent.parent / "task_manager_schema.json"

    print(f"Creating MCP server config from: {schema_path}")
    print()

    # Generate server config
    config = create_mcp_server_config(str(schema_path))

    print("Server Info:")
    print(f"  Name: {config['serverInfo']['name']}")
    print(f"  Version: {config['serverInfo']['version']}")
    print(f"  Protocol: {config['protocolVersion']}")
    print()

    print(f"Tools ({len(config['tools'])}):")
    for tool in config["tools"]:
        print(f"  - {tool['name']}: {tool['description'].split(chr(10))[0]}")
    print()

    # Save config
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    config_path = output_dir / "mcp_server_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"Server config saved to: {config_path}")

    # Generate handler stubs
    handlers_code = generate_tool_handlers_stub(str(schema_path))
    handlers_path = output_dir / "tool_handlers.py"
    with open(handlers_path, "w") as f:
        f.write(handlers_code)
    print(f"Handler stubs saved to: {handlers_path}")


if __name__ == "__main__":
    main()
