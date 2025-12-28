"""
Integration example: Generate an API client from LUI schema's OpenAPI export.

This example demonstrates how to use the OpenAPI export to create
type-safe API client code that can be used to interact with a LUI-based
service.
"""

import json
from pathlib import Path
import sys
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from lui_simulator.simulator import load_schema_from_dict
from lui_schema_export import OpenAPIExporter


def generate_python_client(schema_path: str) -> str:
    """Generate a Python API client from a LUI schema.

    Args:
        schema_path: Path to the LUI schema JSON file

    Returns:
        Python code for an API client
    """
    with open(schema_path) as f:
        schema_data = json.load(f)

    schema = load_schema_from_dict(schema_data)

    # Get the OpenAPI spec
    exporter = OpenAPIExporter(
        base_path="/api/v1",
        server_url="https://api.example.com",
    )
    openapi_spec = exporter.export(schema)

    # Generate client code
    lines = [
        '"""',
        f"Python API Client for {schema.name}",
        "",
        f"Version: {schema.version}",
        "Auto-generated from LUI schema.",
        '"""',
        "",
        "import httpx",
        "from dataclasses import dataclass",
        "from typing import Any",
        "",
        "",
        "@dataclass",
        "class APIResponse:",
        '    """Standard API response."""',
        "    success: bool",
        "    message: str",
        "    data: Any | None = None",
        "",
        "",
        f"class {_to_class_name(schema.name)}Client:",
        f'    """API client for {schema.name}."""',
        "",
        f'    def __init__(self, base_url: str = "{openapi_spec["servers"][0]["url"]}"):'
        "",
        "        self.base_url = base_url.rstrip('/')",
        "        self.client = httpx.Client()",
        "",
        "    def close(self):",
        '        """Close the HTTP client."""',
        "        self.client.close()",
        "",
        "    def __enter__(self):",
        "        return self",
        "",
        "    def __exit__(self, *args):",
        "        self.close()",
        "",
    ]

    # Generate methods for each component
    for component in schema.components:
        method_name = component.component_id.replace("-", "_")
        endpoint = f"/api/v1/{component.component_id}"

        # Build method parameters
        params = ["self"]
        param_docs = []

        for param in component.parameters:
            param_name = param.name.replace("-", "_")
            type_hint = _get_type_hint(param.param_type.value)

            if param.required:
                params.append(f"{param_name}: {type_hint}")
            else:
                params.append(f"{param_name}: {type_hint} | None = None")

            param_docs.append(f"            {param_name}: {param.description}")

        params_str = ", ".join(params)

        # Build request body
        body_items = []
        for param in component.parameters:
            param_name = param.name.replace("-", "_")
            body_items.append(f'"{param.name}": {param_name}')
        body_str = ", ".join(body_items) if body_items else ""

        lines.extend([
            f"    def {method_name}({params_str}) -> APIResponse:",
            f'        """',
            f"        {component.intent}",
            f"        ",
            f'        Invoke by saying: "{component.invocation.primary_phrase}"',
        ])

        if param_docs:
            lines.append("        ")
            lines.append("        Args:")
            lines.extend(param_docs)

        lines.extend([
            f'        """',
        ])

        if body_items:
            lines.append(f"        data = {{{body_str}}}")
            lines.append(f"        # Remove None values")
            lines.append(f"        data = {{k: v for k, v in data.items() if v is not None}}")
            lines.append(f"        response = self.client.post(f\"{{self.base_url}}{endpoint}\", json=data)")
        else:
            lines.append(f"        response = self.client.post(f\"{{self.base_url}}{endpoint}\")")

        lines.extend([
            f"        response.raise_for_status()",
            f"        result = response.json()",
            f"        return APIResponse(",
            f"            success=result.get('success', True),",
            f"            message=result.get('message', ''),",
            f"            data=result.get('data'),",
            f"        )",
            "",
        ])

    return "\n".join(lines)


def _to_class_name(name: str) -> str:
    """Convert a name to a valid Python class name."""
    # Remove special characters and convert to PascalCase
    words = name.replace("-", " ").replace("_", " ").split()
    return "".join(word.capitalize() for word in words)


def _get_type_hint(param_type: str) -> str:
    """Get Python type hint for a parameter type."""
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
    """Run the OpenAPI client example."""
    schema_path = Path(__file__).parent.parent / "task_manager_schema.json"

    print(f"Generating Python API client from: {schema_path}")
    print()

    # Generate client code
    client_code = generate_python_client(str(schema_path))

    # Save to file
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)

    client_path = output_dir / "api_client.py"
    with open(client_path, "w") as f:
        f.write(client_code)

    print(f"Client saved to: {client_path}")
    print()
    print("Usage example:")
    print()
    print("    from api_client import TaskManagerLuiClient")
    print()
    print("    with TaskManagerLuiClient() as client:")
    print('        result = client.create_task(title="Review PR")')
    print("        print(result.message)")


if __name__ == "__main__":
    main()
