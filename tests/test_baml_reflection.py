"""
Tests for BAML Runtime Type Reflection module.
"""

import pytest
from enum import Enum

from src.baml_reflection import (
    get_type_info,
    get_fields,
    get_enum_values,
    get_all_classes,
    get_all_enums,
    validate_data,
    TypeInfo,
    FieldInfo,
    EnumInfo,
    ValidationResult,
)
from src.baml_reflection.reflection import (
    generate_markdown_docs,
    generate_typescript_interface,
    get_enum_info,
)


class TestGetFields:
    """Tests for get_fields function."""

    def test_get_fields_lui_component(self):
        """Test getting fields from LUIComponent class."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)

        assert len(fields) > 0

        # Check for expected fields
        field_names = [f.name for f in fields]
        assert "component_id" in field_names
        assert "component_type" in field_names
        assert "intent" in field_names
        assert "parameters" in field_names
        assert "feedback" in field_names

    def test_get_fields_interface_schema(self):
        """Test getting fields from InterfaceSchema class."""
        from baml_client.types import InterfaceSchema

        fields = get_fields(InterfaceSchema)

        field_names = [f.name for f in fields]
        assert "schema_id" in field_names
        assert "name" in field_names
        assert "description" in field_names
        assert "version" in field_names
        assert "components" in field_names

    def test_field_info_attributes(self):
        """Test that FieldInfo has correct attributes."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)
        component_id_field = next(f for f in fields if f.name == "component_id")

        assert component_id_field.name == "component_id"
        assert "str" in component_id_field.type_name.lower()
        assert component_id_field.is_optional is False

    def test_optional_field_detection(self):
        """Test that optional fields are correctly detected."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)
        accessibility_field = next(f for f in fields if f.name == "accessibility")

        assert accessibility_field.is_optional is True

    def test_list_field_detection(self):
        """Test that list fields are correctly detected."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)
        parameters_field = next(f for f in fields if f.name == "parameters")

        assert parameters_field.is_list is True
        assert "List" in parameters_field.type_name

    def test_enum_field_detection(self):
        """Test that enum fields are correctly detected."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)
        component_type_field = next(f for f in fields if f.name == "component_type")

        assert component_type_field.is_enum is True

    def test_nested_class_detection(self):
        """Test that nested class fields are correctly detected."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)
        feedback_field = next(f for f in fields if f.name == "feedback")

        assert feedback_field.is_nested_class is True

    def test_field_to_dict(self):
        """Test FieldInfo.to_dict() serialization."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)
        field_dict = fields[0].to_dict()

        assert "name" in field_dict
        assert "type_name" in field_dict
        assert "is_optional" in field_dict
        assert "is_list" in field_dict

    def test_invalid_type_raises_error(self):
        """Test that non-BAML types raise TypeError."""
        with pytest.raises(TypeError):
            get_fields(str)

        with pytest.raises(TypeError):
            get_fields(dict)


class TestGetEnumValues:
    """Tests for get_enum_values function."""

    def test_get_enum_values_component_type(self):
        """Test getting values from LUIComponentType enum."""
        from baml_client.types import LUIComponentType

        values = get_enum_values(LUIComponentType)

        assert len(values) > 0
        assert "ACTION" in values
        assert "QUERY" in values
        assert "NAVIGATION" in values

    def test_get_enum_values_parameter_type(self):
        """Test getting values from ParameterType enum."""
        from baml_client.types import ParameterType

        values = get_enum_values(ParameterType)

        assert "STRING" in values
        assert "NUMBER" in values
        assert "BOOLEAN" in values

    def test_invalid_enum_raises_error(self):
        """Test that non-enum types raise TypeError."""
        from baml_client.types import LUIComponent

        with pytest.raises(TypeError):
            get_enum_values(LUIComponent)

        with pytest.raises(TypeError):
            get_enum_values(str)


class TestGetEnumInfo:
    """Tests for get_enum_info function."""

    def test_get_enum_info(self):
        """Test getting complete enum info."""
        from baml_client.types import LUIComponentType

        info = get_enum_info(LUIComponentType)

        assert isinstance(info, EnumInfo)
        assert info.name == "LUIComponentType"
        assert len(info.values) > 0
        assert "ACTION" in info.values

    def test_enum_info_to_dict(self):
        """Test EnumInfo.to_dict() serialization."""
        from baml_client.types import LUIComponentType

        info = get_enum_info(LUIComponentType)
        info_dict = info.to_dict()

        assert "name" in info_dict
        assert "values" in info_dict
        assert info_dict["name"] == "LUIComponentType"


class TestGetTypeInfo:
    """Tests for get_type_info function."""

    def test_get_type_info_class(self):
        """Test getting type info for a class."""
        from baml_client.types import LUIComponent

        info = get_type_info(LUIComponent)

        assert isinstance(info, TypeInfo)
        assert info.name == "LUIComponent"
        assert info.is_class is True
        assert info.is_enum is False
        assert len(info.fields) > 0

    def test_get_type_info_enum(self):
        """Test getting type info for an enum."""
        from baml_client.types import LUIComponentType

        info = get_type_info(LUIComponentType)

        assert isinstance(info, TypeInfo)
        assert info.name == "LUIComponentType"
        assert info.is_class is False
        assert info.is_enum is True
        assert len(info.enum_values) > 0

    def test_type_info_to_dict(self):
        """Test TypeInfo.to_dict() serialization."""
        from baml_client.types import LUIComponent

        info = get_type_info(LUIComponent)
        info_dict = info.to_dict()

        assert "name" in info_dict
        assert "is_enum" in info_dict
        assert "is_class" in info_dict
        assert "fields" in info_dict
        assert isinstance(info_dict["fields"], list)

    def test_invalid_type_raises_error(self):
        """Test that non-BAML types raise TypeError."""
        with pytest.raises(TypeError):
            get_type_info(str)


class TestGetAllTypes:
    """Tests for get_all_classes and get_all_enums functions."""

    def test_get_all_classes(self):
        """Test getting all BAML classes."""
        classes = get_all_classes()

        assert isinstance(classes, dict)
        assert len(classes) > 0
        assert "LUIComponent" in classes
        assert "InterfaceSchema" in classes

    def test_get_all_enums(self):
        """Test getting all BAML enums."""
        enums = get_all_enums()

        assert isinstance(enums, dict)
        assert len(enums) > 0
        assert "LUIComponentType" in enums
        assert "ParameterType" in enums

    def test_all_classes_are_valid(self):
        """Test that all returned classes are valid BAML types."""
        classes = get_all_classes()

        for name, cls in classes.items():
            info = get_type_info(cls)
            assert info.is_class is True
            assert info.name == name

    def test_all_enums_are_valid(self):
        """Test that all returned enums are valid BAML types."""
        enums = get_all_enums()

        for name, enum_cls in enums.items():
            info = get_type_info(enum_cls)
            assert info.is_enum is True
            assert info.name == name


class TestValidateData:
    """Tests for validate_data function."""

    def test_validate_valid_data(self):
        """Test validating correct data."""
        from baml_client.types import FeedbackConfig

        valid_data = {
            "success_template": "Success!",
            "error_template": "Error occurred",
            "confirmation_required": False,
        }

        result = validate_data(valid_data, FeedbackConfig)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_data(self):
        """Test validating incorrect data."""
        from baml_client.types import FeedbackConfig

        invalid_data = {
            "success_template": "Success!",
            # Missing required fields
        }

        result = validate_data(invalid_data, FeedbackConfig)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validation_result_to_dict(self):
        """Test ValidationResult.to_dict() serialization."""
        from baml_client.types import FeedbackConfig

        result = validate_data({}, FeedbackConfig)
        result_dict = result.to_dict()

        assert "is_valid" in result_dict
        assert "errors" in result_dict
        assert "warnings" in result_dict


class TestDocGeneration:
    """Tests for documentation generation functions."""

    def test_generate_markdown_docs_class(self):
        """Test generating Markdown docs for a class."""
        from baml_client.types import LUIComponent

        markdown = generate_markdown_docs(LUIComponent)

        assert isinstance(markdown, str)
        assert "# LUIComponent" in markdown
        assert "## Fields" in markdown
        assert "component_id" in markdown

    def test_generate_markdown_docs_enum(self):
        """Test generating Markdown docs for an enum."""
        from baml_client.types import LUIComponentType

        markdown = generate_markdown_docs(LUIComponentType)

        assert isinstance(markdown, str)
        assert "# LUIComponentType" in markdown
        assert "## Values" in markdown
        assert "ACTION" in markdown

    def test_generate_typescript_interface(self):
        """Test generating TypeScript interface."""
        from baml_client.types import FeedbackConfig

        typescript = generate_typescript_interface(FeedbackConfig)

        assert isinstance(typescript, str)
        assert "interface FeedbackConfig" in typescript
        assert "success_template" in typescript
        assert "string" in typescript


class TestRealWorldUseCases:
    """Tests for real-world use cases mentioned in Issue #34."""

    def test_generate_help_text(self):
        """Test use case: generating help text from types."""
        from baml_client.types import LUIComponent

        fields = get_fields(LUIComponent)
        help_lines = [f"- {f.name}: {f.type_name}" for f in fields]
        help_text = "\n".join(help_lines)

        assert "component_id" in help_text
        assert "component_type" in help_text

    def test_schema_export_introspection(self):
        """Test use case: schema export using introspection."""
        from baml_client.types import InterfaceSchema

        info = get_type_info(InterfaceSchema)

        # Build a simple JSON schema-like structure
        schema = {
            "title": info.name,
            "type": "object",
            "properties": {},
            "required": [],
        }

        for field in info.fields:
            schema["properties"][field.name] = {
                "type": field.type_name,
                "description": field.description,
            }
            if not field.is_optional:
                schema["required"].append(field.name)

        assert schema["title"] == "InterfaceSchema"
        assert len(schema["properties"]) > 0
        assert len(schema["required"]) > 0

    def test_form_generation(self):
        """Test use case: UI form generation from types."""
        from baml_client.types import ComponentParameter

        fields = get_fields(ComponentParameter)

        form_fields = []
        for field in fields:
            form_field = {
                "name": field.name,
                "label": field.name.replace("_", " ").title(),
                "type": "text" if "str" in field.type_name.lower() else "other",
                "required": not field.is_optional,
            }
            form_fields.append(form_field)

        assert len(form_fields) > 0
        assert any(f["name"] == "name" for f in form_fields)
