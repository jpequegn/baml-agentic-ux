"""Tests for LUI Schema Export module."""

import json
import pytest
from pathlib import Path

from baml_client.types import (
    InterfaceSchema,
    DomainInfo,
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
    ComponentParameter,
    ParameterType,
)

# Import exporters
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from lui_schema_export.openapi import (
    export_to_openapi,
    OpenAPIExporter,
    param_type_to_json_schema,
)
from lui_schema_export.mcp_tools import (
    export_to_mcp_tools,
    MCPToolsExporter,
    param_type_to_json_type,
)
from lui_schema_export.markdown import (
    export_to_markdown,
    MarkdownExporter,
)
from lui_schema_export.typescript import (
    export_to_typescript,
    TypeScriptExporter,
    to_pascal_case,
    to_camel_case,
)


# ============================================
# Test Fixtures
# ============================================

@pytest.fixture
def sample_parameter() -> ComponentParameter:
    """Create a sample component parameter."""
    return ComponentParameter(
        name="task_title",
        param_type=ParameterType.STRING,
        description="The title of the task",
        required=True,
        default_value=None,
        extraction_hints=["task called", "task named"],
        validation=None,
    )


@pytest.fixture
def sample_component(sample_parameter: ComponentParameter) -> LUIComponent:
    """Create a sample LUI component."""
    return LUIComponent(
        component_id="create-task",
        component_type=LUIComponentType.ACTION,
        intent="Create a new task",
        invocation=InvocationPattern(
            primary_phrase="create task",
            alternate_phrases=["add task", "new task"],
            examples=["Create a task to review code", "Add task called finish report"],
            context_requirements=None,
        ),
        parameters=[sample_parameter],
        feedback=FeedbackConfig(
            success_template="Task '{title}' created successfully",
            error_template="Could not create task: {error}",
            progress_template=None,
            confirmation_required=False,
            confirmation_prompt=None,
        ),
        accessibility=None,
    )


@pytest.fixture
def sample_schema(sample_component: LUIComponent) -> InterfaceSchema:
    """Create a sample interface schema."""
    domain = DomainInfo(
        domain_name="task-management",
        subdomain="personal-productivity",
        description="Task and project management",
        key_concepts=["tasks", "projects", "deadlines"],
        terminology=None,
    )

    query_component = LUIComponent(
        component_id="list-tasks",
        component_type=LUIComponentType.QUERY,
        intent="List all tasks",
        invocation=InvocationPattern(
            primary_phrase="list tasks",
            alternate_phrases=["show tasks", "my tasks"],
            examples=["Show me my tasks"],
            context_requirements=None,
        ),
        parameters=[],
        feedback=FeedbackConfig(
            success_template="Here are your tasks",
            error_template="Could not list tasks",
            progress_template=None,
            confirmation_required=False,
            confirmation_prompt=None,
        ),
        accessibility=None,
    )

    confirm_component = LUIComponent(
        component_id="delete-task",
        component_type=LUIComponentType.ACTION,
        intent="Delete a task",
        invocation=InvocationPattern(
            primary_phrase="delete task",
            alternate_phrases=["remove task"],
            examples=["Delete task 123"],
            context_requirements=None,
        ),
        parameters=[],
        feedback=FeedbackConfig(
            success_template="Task deleted",
            error_template="Could not delete task",
            progress_template=None,
            confirmation_required=True,
            confirmation_prompt="Are you sure you want to delete this task?",
        ),
        accessibility=None,
    )

    return InterfaceSchema(
        schema_id="test-schema-v1",
        name="Test Task Manager",
        description="A test task management schema",
        version="1.0.0",
        domain=domain,
        components=[sample_component, query_component, confirm_component],
        flows=[],
        entities=[],
        global_context=None,
    )


# ============================================
# Test OpenAPI Exporter
# ============================================

class TestOpenAPIExporter:
    """Test OpenAPI export functionality."""

    def test_param_type_to_json_schema_string(self):
        """Test string parameter type conversion."""
        result = param_type_to_json_schema(ParameterType.STRING)
        assert result == {"type": "string"}

    def test_param_type_to_json_schema_number(self):
        """Test number parameter type conversion."""
        result = param_type_to_json_schema(ParameterType.NUMBER)
        assert result == {"type": "number"}

    def test_param_type_to_json_schema_boolean(self):
        """Test boolean parameter type conversion."""
        result = param_type_to_json_schema(ParameterType.BOOLEAN)
        assert result == {"type": "boolean"}

    def test_param_type_to_json_schema_date(self):
        """Test date parameter type conversion."""
        result = param_type_to_json_schema(ParameterType.DATE)
        assert result == {"type": "string", "format": "date-time"}

    def test_param_type_to_json_schema_list(self):
        """Test list parameter type conversion."""
        result = param_type_to_json_schema(ParameterType.LIST)
        assert result == {"type": "array", "items": {"type": "string"}}

    def test_export_basic_structure(self, sample_schema: InterfaceSchema):
        """Test that export creates valid OpenAPI structure."""
        result = export_to_openapi(sample_schema)

        assert result["openapi"] == "3.0.3"
        assert "info" in result
        assert "paths" in result
        assert "tags" in result

    def test_export_info_section(self, sample_schema: InterfaceSchema):
        """Test that info section is populated correctly."""
        result = export_to_openapi(sample_schema)

        assert result["info"]["title"] == "Test Task Manager"
        assert result["info"]["description"] == "A test task management schema"
        assert result["info"]["version"] == "1.0.0"

    def test_export_domain_info(self, sample_schema: InterfaceSchema):
        """Test that domain info is included as extension."""
        result = export_to_openapi(sample_schema)

        assert "x-domain" in result["info"]
        assert result["info"]["x-domain"]["name"] == "task-management"

    def test_export_paths_for_components(self, sample_schema: InterfaceSchema):
        """Test that paths are created for each component."""
        result = export_to_openapi(sample_schema)

        assert "/actions/create-task" in result["paths"]
        assert "/actions/list-tasks" in result["paths"]
        assert "/actions/delete-task" in result["paths"]

    def test_export_custom_base_path(self, sample_schema: InterfaceSchema):
        """Test custom base path."""
        result = export_to_openapi(sample_schema, base_path="/api/v1")

        assert "/api/v1/create-task" in result["paths"]

    def test_export_server_url(self, sample_schema: InterfaceSchema):
        """Test server URL configuration."""
        result = export_to_openapi(
            sample_schema,
            server_url="https://api.example.com",
        )

        assert result["servers"][0]["url"] == "https://api.example.com"

    def test_export_request_body_for_params(self, sample_schema: InterfaceSchema):
        """Test that request body is created for components with parameters."""
        result = export_to_openapi(sample_schema)
        create_task = result["paths"]["/actions/create-task"]["post"]

        assert "requestBody" in create_task
        schema = create_task["requestBody"]["content"]["application/json"]["schema"]
        assert "task_title" in schema["properties"]

    def test_export_confirmation_response(self, sample_schema: InterfaceSchema):
        """Test confirmation response for components requiring confirmation."""
        result = export_to_openapi(sample_schema)
        delete_task = result["paths"]["/actions/delete-task"]["post"]

        assert "202" in delete_task["responses"]
        assert "x-confirmation-prompt" in delete_task["responses"]["202"]

    def test_exporter_class(self, sample_schema: InterfaceSchema):
        """Test OpenAPIExporter class directly."""
        exporter = OpenAPIExporter(
            base_path="/custom",
            include_examples=True,
            server_url="http://localhost:3000",
        )
        result = exporter.export(sample_schema)

        assert "/custom/create-task" in result["paths"]
        assert result["servers"][0]["url"] == "http://localhost:3000"


# ============================================
# Test MCP Tools Exporter
# ============================================

class TestMCPToolsExporter:
    """Test MCP tools export functionality."""

    def test_param_type_to_json_type(self):
        """Test parameter type to JSON type conversion."""
        assert param_type_to_json_type(ParameterType.STRING) == "string"
        assert param_type_to_json_type(ParameterType.NUMBER) == "number"
        assert param_type_to_json_type(ParameterType.BOOLEAN) == "boolean"
        assert param_type_to_json_type(ParameterType.LIST) == "array"

    def test_export_returns_list(self, sample_schema: InterfaceSchema):
        """Test that export returns a list of tools."""
        result = export_to_mcp_tools(sample_schema)

        assert isinstance(result, list)
        assert len(result) == 3

    def test_export_tool_structure(self, sample_schema: InterfaceSchema):
        """Test that each tool has required MCP fields."""
        result = export_to_mcp_tools(sample_schema)

        for tool in result:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool

    def test_export_tool_names(self, sample_schema: InterfaceSchema):
        """Test that tool names match component IDs."""
        result = export_to_mcp_tools(sample_schema)
        names = [t["name"] for t in result]

        assert "create-task" in names
        assert "list-tasks" in names
        assert "delete-task" in names

    def test_export_with_prefix(self, sample_schema: InterfaceSchema):
        """Test tool name prefix."""
        result = export_to_mcp_tools(sample_schema, tool_name_prefix="task_")
        names = [t["name"] for t in result]

        assert "task_create-task" in names

    def test_export_input_schema(self, sample_schema: InterfaceSchema):
        """Test that input schema includes parameters."""
        result = export_to_mcp_tools(sample_schema)
        create_task = next(t for t in result if t["name"] == "create-task")

        assert create_task["inputSchema"]["type"] == "object"
        assert "task_title" in create_task["inputSchema"]["properties"]
        assert "task_title" in create_task["inputSchema"]["required"]

    def test_export_annotations(self, sample_schema: InterfaceSchema):
        """Test that annotations are included."""
        result = export_to_mcp_tools(sample_schema, include_annotations=True)
        create_task = next(t for t in result if t["name"] == "create-task")

        assert "annotations" in create_task
        assert create_task["annotations"]["component_type"] == "ACTION"

    def test_export_without_annotations(self, sample_schema: InterfaceSchema):
        """Test that annotations can be excluded."""
        result = export_to_mcp_tools(sample_schema, include_annotations=False)
        create_task = next(t for t in result if t["name"] == "create-task")

        assert "annotations" not in create_task

    def test_exporter_server_capabilities(self, sample_schema: InterfaceSchema):
        """Test server capabilities export."""
        exporter = MCPToolsExporter()
        result = exporter.export_as_server_capabilities(sample_schema)

        assert "protocolVersion" in result
        assert "capabilities" in result
        assert "serverInfo" in result
        assert "tools" in result
        assert result["serverInfo"]["name"] == "Test Task Manager"


# ============================================
# Test Markdown Exporter
# ============================================

class TestMarkdownExporter:
    """Test Markdown export functionality."""

    def test_export_returns_string(self, sample_schema: InterfaceSchema):
        """Test that export returns a string."""
        result = export_to_markdown(sample_schema)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_includes_title(self, sample_schema: InterfaceSchema):
        """Test that title is included."""
        result = export_to_markdown(sample_schema)

        assert "# Test Task Manager" in result

    def test_export_includes_description(self, sample_schema: InterfaceSchema):
        """Test that description is included."""
        result = export_to_markdown(sample_schema)

        assert "A test task management schema" in result

    def test_export_includes_version(self, sample_schema: InterfaceSchema):
        """Test that version is included."""
        result = export_to_markdown(sample_schema)

        assert "1.0.0" in result

    def test_export_includes_domain_info(self, sample_schema: InterfaceSchema):
        """Test that domain info is included."""
        result = export_to_markdown(sample_schema)

        assert "task-management" in result

    def test_export_includes_toc(self, sample_schema: InterfaceSchema):
        """Test that table of contents is included."""
        result = export_to_markdown(sample_schema, include_toc=True)

        assert "Table of Contents" in result

    def test_export_without_toc(self, sample_schema: InterfaceSchema):
        """Test that TOC can be excluded."""
        result = export_to_markdown(sample_schema, include_toc=False)

        assert "Table of Contents" not in result

    def test_export_includes_commands(self, sample_schema: InterfaceSchema):
        """Test that commands are included."""
        result = export_to_markdown(sample_schema)

        assert "Create a new task" in result
        assert "create task" in result

    def test_export_includes_examples(self, sample_schema: InterfaceSchema):
        """Test that examples are included."""
        result = export_to_markdown(sample_schema, include_examples=True)

        assert "Create a task to review code" in result

    def test_export_includes_parameters(self, sample_schema: InterfaceSchema):
        """Test that parameters are included."""
        result = export_to_markdown(sample_schema)

        assert "task_title" in result

    def test_export_includes_feedback(self, sample_schema: InterfaceSchema):
        """Test that feedback templates are included."""
        result = export_to_markdown(sample_schema)

        assert "Task '{title}' created successfully" in result

    def test_export_quick_reference(self, sample_schema: InterfaceSchema):
        """Test quick reference export."""
        exporter = MarkdownExporter()
        result = exporter.export_quick_reference(sample_schema)

        assert "Quick Reference" in result
        assert "| Command |" in result


# ============================================
# Test TypeScript Exporter
# ============================================

class TestTypeScriptExporter:
    """Test TypeScript export functionality."""

    def test_to_pascal_case(self):
        """Test PascalCase conversion."""
        assert to_pascal_case("create-task") == "CreateTask"
        assert to_pascal_case("list_tasks") == "ListTasks"
        assert to_pascal_case("hello-world-test") == "HelloWorldTest"

    def test_to_camel_case(self):
        """Test camelCase conversion."""
        assert to_camel_case("create-task") == "createTask"
        assert to_camel_case("list_tasks") == "listTasks"

    def test_export_returns_string(self, sample_schema: InterfaceSchema):
        """Test that export returns a string."""
        result = export_to_typescript(sample_schema)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_export_includes_header(self, sample_schema: InterfaceSchema):
        """Test that header comment is included."""
        result = export_to_typescript(sample_schema)

        assert "Test Task Manager" in result
        assert "Auto-generated" in result

    def test_export_includes_enums(self, sample_schema: InterfaceSchema):
        """Test that enums are included."""
        exporter = TypeScriptExporter(include_enums=True)
        result = exporter.export(sample_schema)

        assert "export enum LUIComponentType" in result
        assert "export enum ParameterType" in result

    def test_export_includes_params_interface(self, sample_schema: InterfaceSchema):
        """Test that parameter interfaces are generated."""
        result = export_to_typescript(sample_schema)

        assert "CreateTaskParams" in result
        assert "taskTitle" in result

    def test_export_includes_result_interface(self, sample_schema: InterfaceSchema):
        """Test that result interfaces are generated."""
        result = export_to_typescript(sample_schema)

        assert "CreateTaskResult" in result
        assert "success: boolean" in result

    def test_export_includes_schema_interface(self, sample_schema: InterfaceSchema):
        """Test that schema interface is generated."""
        result = export_to_typescript(sample_schema)

        assert "TestSchemaV1Schema" in result
        assert "schemaId:" in result

    def test_export_includes_action_types(self, sample_schema: InterfaceSchema):
        """Test that action types are generated."""
        result = export_to_typescript(sample_schema)

        assert "ActionName" in result
        assert "ActionHandlers" in result

    def test_export_with_namespace(self, sample_schema: InterfaceSchema):
        """Test namespace wrapping."""
        result = export_to_typescript(sample_schema, namespace="TaskManager")

        assert "export namespace TaskManager" in result

    def test_export_jsdoc_comments(self, sample_schema: InterfaceSchema):
        """Test JSDoc comments."""
        result = export_to_typescript(sample_schema, include_jsdoc=True)

        assert "/**" in result
        assert "Create a new task" in result

    def test_exporter_declaration_file(self, sample_schema: InterfaceSchema):
        """Test declaration file export."""
        exporter = TypeScriptExporter()
        result = exporter.export_declaration_file(sample_schema)

        assert "// Type definitions for" in result


# ============================================
# Test Integration
# ============================================

class TestExportIntegration:
    """Test export integration with example schema."""

    def test_load_and_export_example_schema(self):
        """Test loading and exporting the example schema file."""
        schema_path = Path(__file__).parent.parent / "examples" / "task_manager_schema.json"

        if not schema_path.exists():
            pytest.skip("Example schema file not found")

        with open(schema_path) as f:
            schema_data = json.load(f)

        # Import here to avoid circular imports
        from lui_simulator.simulator import load_schema_from_dict

        schema = load_schema_from_dict(schema_data)

        # Test all exporters
        openapi = export_to_openapi(schema)
        assert openapi["info"]["title"] == "Task Manager LUI"
        assert len(openapi["paths"]) == 7

        mcp_tools = export_to_mcp_tools(schema)
        assert len(mcp_tools) == 7

        markdown = export_to_markdown(schema)
        assert "Task Manager LUI" in markdown

        typescript = export_to_typescript(schema)
        assert "TaskManagerV1Schema" in typescript

    def test_openapi_is_valid_json(self, sample_schema: InterfaceSchema):
        """Test that OpenAPI export produces valid JSON."""
        result = export_to_openapi(sample_schema)
        json_str = json.dumps(result)

        # Should not raise
        parsed = json.loads(json_str)
        assert parsed == result

    def test_mcp_is_valid_json(self, sample_schema: InterfaceSchema):
        """Test that MCP export produces valid JSON."""
        result = export_to_mcp_tools(sample_schema)
        json_str = json.dumps(result)

        # Should not raise
        parsed = json.loads(json_str)
        assert parsed == result
