"""Tests for the schema import module.

Tests the JSON Schema and YAML/OpenAPI import functionality.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from baml_client.types import (
    InterfaceSchema,
    LUIComponentType,
    ParameterType,
)

from lui_schema_import import (
    import_json_schema,
    parse_json_schema,
    JsonSchemaParser,
    generate_baml_types,
    generate_baml_class,
)
from lui_schema_import.type_mapper import (
    JsonSchemaToLUIMapper,
    TypeMappingResult,
    json_schema_type_to_parameter_type,
)


# ============================================
# Type Mapper Tests
# ============================================


class TestJsonSchemaTypeMapper:
    """Tests for JSON Schema to LUI type mapping."""

    def test_map_string_type(self) -> None:
        """Test mapping string type."""
        result = json_schema_type_to_parameter_type({"type": "string"})
        assert result.parameter_type == ParameterType.STRING

    def test_map_number_type(self) -> None:
        """Test mapping number type."""
        result = json_schema_type_to_parameter_type({"type": "number"})
        assert result.parameter_type == ParameterType.NUMBER

    def test_map_integer_type(self) -> None:
        """Test mapping integer type (maps to NUMBER)."""
        result = json_schema_type_to_parameter_type({"type": "integer"})
        assert result.parameter_type == ParameterType.NUMBER

    def test_map_boolean_type(self) -> None:
        """Test mapping boolean type."""
        result = json_schema_type_to_parameter_type({"type": "boolean"})
        assert result.parameter_type == ParameterType.BOOLEAN

    def test_map_array_type(self) -> None:
        """Test mapping array type."""
        result = json_schema_type_to_parameter_type({
            "type": "array",
            "items": {"type": "string"}
        })
        assert result.parameter_type == ParameterType.LIST
        assert result.is_array is True
        assert result.nested_type is not None
        assert result.nested_type.parameter_type == ParameterType.STRING

    def test_map_object_type(self) -> None:
        """Test mapping object type."""
        result = json_schema_type_to_parameter_type({"type": "object"})
        assert result.parameter_type == ParameterType.ENTITY

    def test_map_enum_type(self) -> None:
        """Test mapping enum type."""
        result = json_schema_type_to_parameter_type({
            "type": "string",
            "enum": ["active", "inactive", "pending"]
        })
        assert result.parameter_type == ParameterType.ENUM
        assert result.enum_values == ["active", "inactive", "pending"]

    def test_map_const_type(self) -> None:
        """Test mapping const type (single-value enum)."""
        result = json_schema_type_to_parameter_type({
            "type": "string",
            "const": "fixed_value"
        })
        assert result.parameter_type == ParameterType.ENUM
        assert result.enum_values == ["fixed_value"]

    def test_map_date_format(self) -> None:
        """Test mapping date-time format."""
        result = json_schema_type_to_parameter_type({
            "type": "string",
            "format": "date-time"
        })
        assert result.parameter_type == ParameterType.DATE

    def test_map_with_description(self) -> None:
        """Test that description is preserved."""
        result = json_schema_type_to_parameter_type({
            "type": "string",
            "description": "A test field"
        })
        assert result.description == "A test field"

    def test_extract_string_constraints(self) -> None:
        """Test extraction of string constraints."""
        result = json_schema_type_to_parameter_type({
            "type": "string",
            "minLength": 1,
            "maxLength": 100,
            "pattern": "^[a-z]+$"
        })
        assert result.constraints.get("min_length") == 1
        assert result.constraints.get("max_length") == 100
        assert result.constraints.get("pattern") == "^[a-z]+$"

    def test_extract_number_constraints(self) -> None:
        """Test extraction of number constraints."""
        result = json_schema_type_to_parameter_type({
            "type": "number",
            "minimum": 0,
            "maximum": 100,
            "multipleOf": 0.5
        })
        assert result.constraints.get("minimum") == 0
        assert result.constraints.get("maximum") == 100
        assert result.constraints.get("multiple_of") == 0.5


class TestJsonSchemaToLUIMapper:
    """Tests for the full schema mapper with refs."""

    def test_resolve_definition_ref(self) -> None:
        """Test resolving $ref to definitions."""
        mapper = JsonSchemaToLUIMapper()
        mapper.definitions = {
            "Status": {
                "type": "string",
                "enum": ["active", "inactive"]
            }
        }

        result = mapper.map_schema({"$ref": "#/definitions/Status"})
        assert result.parameter_type == ParameterType.ENUM
        assert result.enum_values == ["active", "inactive"]

    def test_resolve_defs_ref(self) -> None:
        """Test resolving $ref to $defs (draft 2019-09+)."""
        mapper = JsonSchemaToLUIMapper()
        mapper.definitions = {
            "Priority": {
                "type": "string",
                "enum": ["low", "medium", "high"]
            }
        }

        result = mapper.map_schema({"$ref": "#/$defs/Priority"})
        assert result.parameter_type == ParameterType.ENUM

    def test_handle_one_of_with_enums(self) -> None:
        """Test oneOf with const values."""
        mapper = JsonSchemaToLUIMapper()
        result = mapper.map_schema({
            "oneOf": [
                {"const": "option1"},
                {"const": "option2"},
                {"const": "option3"}
            ]
        })
        assert result.parameter_type == ParameterType.ENUM
        assert "option1" in result.enum_values
        assert "option2" in result.enum_values
        assert "option3" in result.enum_values


# ============================================
# JSON Schema Parser Tests
# ============================================


class TestJsonSchemaParser:
    """Tests for the JSON Schema parser."""

    def test_parse_simple_schema(self) -> None:
        """Test parsing a simple object schema."""
        schema = {
            "title": "User",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }

        parser = JsonSchemaParser()
        parsed = parser.parse(schema)

        assert parsed.title == "User"
        assert parsed.schema_type == "object"
        assert len(parsed.properties) == 2

        # Check name property
        name_prop = next(p for p in parsed.properties if p.name == "name")
        assert name_prop.parameter_type == ParameterType.STRING
        assert name_prop.required is True

        # Check age property
        age_prop = next(p for p in parsed.properties if p.name == "age")
        assert age_prop.parameter_type == ParameterType.NUMBER
        assert age_prop.required is False

    def test_parse_schema_with_enums(self) -> None:
        """Test parsing schema with enum properties."""
        schema = {
            "title": "Task",
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "in_progress", "done"],
                    "description": "Task status"
                }
            }
        }

        parser = JsonSchemaParser()
        parsed = parser.parse(schema)

        status_prop = parsed.properties[0]
        assert status_prop.name == "status"
        assert status_prop.parameter_type == ParameterType.ENUM
        assert status_prop.enum_values == ["pending", "in_progress", "done"]

    def test_parse_with_definitions(self) -> None:
        """Test parsing schema that uses definitions."""
        schema = {
            "title": "Order",
            "type": "object",
            "definitions": {
                "Address": {
                    "type": "object",
                    "properties": {
                        "street": {"type": "string"},
                        "city": {"type": "string"}
                    }
                }
            },
            "properties": {
                "shipping": {"$ref": "#/definitions/Address"}
            }
        }

        parser = JsonSchemaParser()
        parsed = parser.parse(schema)

        assert "Address" in parsed.definitions
        assert len(parsed.properties) == 1

    def test_to_interface_schema(self) -> None:
        """Test conversion to InterfaceSchema."""
        schema = {
            "title": "Product Catalog",
            "description": "API for managing products",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Product name"},
                "price": {"type": "number", "description": "Price in USD"},
                "category": {
                    "type": "string",
                    "enum": ["electronics", "clothing", "food"]
                }
            },
            "required": ["name", "price"]
        }

        parser = JsonSchemaParser()
        parsed = parser.parse(schema)
        lui_schema = parser.to_interface_schema(parsed, domain_name="products")

        assert isinstance(lui_schema, InterfaceSchema)
        assert lui_schema.name == "Product Catalog"
        assert lui_schema.domain.domain_name == "products"
        assert len(lui_schema.components) == 1

        # Check component
        component = lui_schema.components[0]
        assert component.component_type == LUIComponentType.ACTION
        assert len(component.parameters) == 3

        # Check parameters
        name_param = next(p for p in component.parameters if p.name == "name")
        assert name_param.required is True
        assert name_param.param_type == ParameterType.STRING


class TestImportJsonSchema:
    """Tests for the import_json_schema function."""

    def test_import_from_dict(self) -> None:
        """Test importing from a dictionary."""
        schema = {
            "title": "TestSchema",
            "type": "object",
            "properties": {
                "field1": {"type": "string"}
            }
        }

        result = import_json_schema(schema)
        assert isinstance(result, InterfaceSchema)
        assert result.name == "TestSchema"

    def test_import_from_file(self) -> None:
        """Test importing from a JSON file."""
        schema = {
            "title": "FileSchema",
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "name": {"type": "string"}
            }
        }

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(schema, f)
            f.flush()

            result = import_json_schema(f.name)
            assert result.name == "FileSchema"

            # Cleanup
            Path(f.name).unlink()

    def test_import_with_custom_schema_id(self) -> None:
        """Test importing with custom schema ID."""
        schema = {
            "title": "CustomID",
            "type": "object",
            "properties": {}
        }

        result = import_json_schema(schema, schema_id="my_custom_id")
        assert result.schema_id == "my_custom_id"

    def test_import_with_custom_domain(self) -> None:
        """Test importing with custom domain name."""
        schema = {
            "title": "DomainTest",
            "type": "object",
            "properties": {}
        }

        result = import_json_schema(schema, domain_name="my_domain")
        assert result.domain.domain_name == "my_domain"


# ============================================
# BAML Generator Tests
# ============================================


class TestBAMLGenerator:
    """Tests for BAML code generation."""

    def test_generate_simple_class(self) -> None:
        """Test generating a simple BAML class."""
        schema = {
            "title": "Person",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }

        parsed = parse_json_schema(schema)
        baml_code = generate_baml_types(parsed)

        assert "class Person" in baml_code
        assert "name string" in baml_code
        assert "age float" in baml_code  # integer maps to float in BAML

    def test_generate_with_optional_fields(self) -> None:
        """Test generating class with optional fields."""
        schema = {
            "title": "Contact",
            "type": "object",
            "properties": {
                "email": {"type": "string"},
                "phone": {"type": "string"}
            },
            "required": ["email"]
        }

        parsed = parse_json_schema(schema)
        baml_code = generate_baml_types(parsed)

        assert "email string" in baml_code  # Required - no ?
        assert "phone string?" in baml_code  # Optional - has ?

    def test_generate_with_enums(self) -> None:
        """Test generating enums for enum properties."""
        schema = {
            "title": "Task",
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["PENDING", "ACTIVE", "DONE"]
                }
            }
        }

        parsed = parse_json_schema(schema)
        baml_code = generate_baml_types(parsed)

        assert "enum StatusType" in baml_code
        assert "PENDING" in baml_code
        assert "ACTIVE" in baml_code
        assert "DONE" in baml_code

    def test_generate_with_descriptions(self) -> None:
        """Test generating with @description annotations."""
        schema = {
            "title": "Item",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The item name"
                }
            }
        }

        parsed = parse_json_schema(schema)
        baml_code = generate_baml_types(parsed, include_descriptions=True)

        assert '@description("The item name")' in baml_code


class TestGenerateBAMLClass:
    """Tests for the generate_baml_class helper."""

    def test_generate_class_from_dict(self) -> None:
        """Test generating class from simple dict."""
        code = generate_baml_class(
            "UserProfile",
            {
                "username": "string",
                "email": "string",
                "score": "int"
            }
        )

        assert "class UserProfile" in code
        assert "username string" in code
        assert "email string" in code
        assert "score int" in code

    def test_generate_class_with_description(self) -> None:
        """Test generating class with description."""
        code = generate_baml_class(
            "Config",
            {"key": "string"},
            description="Application configuration"
        )

        assert "/// Application configuration" in code


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for the full import workflow."""

    def test_full_json_schema_workflow(self) -> None:
        """Test complete workflow: JSON Schema -> LUI -> BAML."""
        schema = {
            "title": "API Request",
            "description": "Standard API request format",
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "API endpoint URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE"]
                },
                "body": {
                    "type": "object",
                    "description": "Request body"
                }
            },
            "required": ["endpoint", "method"]
        }

        # Step 1: Import JSON Schema
        lui_schema = import_json_schema(schema, domain_name="api")

        # Verify LUI schema
        assert lui_schema.name == "API Request"
        assert lui_schema.domain.domain_name == "api"
        assert len(lui_schema.components) == 1

        component = lui_schema.components[0]
        assert len(component.parameters) == 3

        # Step 2: Generate BAML code
        baml_code = generate_baml_types(lui_schema)

        # Verify BAML output contains component params class
        assert "ApiRequestActionParams" in baml_code or "api_request" in baml_code.lower()

    def test_complex_nested_schema(self) -> None:
        """Test importing a complex nested schema."""
        schema = {
            "title": "E-commerce Order",
            "type": "object",
            "definitions": {
                "LineItem": {
                    "type": "object",
                    "properties": {
                        "product_id": {"type": "string"},
                        "quantity": {"type": "integer"},
                        "unit_price": {"type": "number"}
                    }
                }
            },
            "properties": {
                "order_id": {"type": "string"},
                "customer_email": {"type": "string", "format": "email"},
                "items": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/LineItem"}
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "processing", "shipped", "delivered"]
                },
                "total": {"type": "number"}
            },
            "required": ["order_id", "items", "status"]
        }

        lui_schema = import_json_schema(schema)

        assert lui_schema.name == "E-commerce Order"
        assert len(lui_schema.components) == 1

        # Check that parameters were created
        params = lui_schema.components[0].parameters
        param_names = {p.name for p in params}
        assert "order_id" in param_names
        assert "items" in param_names
        assert "status" in param_names


# ============================================
# Edge Cases
# ============================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_schema(self) -> None:
        """Test handling of empty schema."""
        result = import_json_schema({})
        assert result.name == "Imported Schema"  # Default title
        assert len(result.components) == 1

    def test_schema_without_properties(self) -> None:
        """Test schema with no properties."""
        schema = {
            "title": "EmptyObject",
            "type": "object"
        }
        result = import_json_schema(schema)
        assert result.name == "EmptyObject"
        assert len(result.components[0].parameters) == 0

    def test_schema_with_unknown_type(self) -> None:
        """Test handling of unknown type defaults to string."""
        schema = {
            "title": "UnknownType",
            "type": "object",
            "properties": {
                "weird": {"type": "custom_type"}
            }
        }
        result = import_json_schema(schema)
        param = result.components[0].parameters[0]
        assert param.param_type == ParameterType.STRING  # Default fallback

    def test_slugify_special_characters(self) -> None:
        """Test schema ID generation handles special characters."""
        schema = {
            "title": "My Super Schema! (v2.0)",
            "type": "object",
            "properties": {}
        }
        result = import_json_schema(schema)
        # Should be slugified without special chars
        assert "_" not in result.schema_id or "!" not in result.schema_id
