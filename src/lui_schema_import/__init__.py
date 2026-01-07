"""LUI Schema Import - Native JSON/YAML schema import for BAML.

This module provides functionality to import JSON Schema and YAML schemas
into BAML-compatible LUI types, enabling interoperability with existing
API specifications and schema definitions.

Usage:
    from lui_schema_import import import_json_schema, import_yaml_schema

    # Import from JSON Schema
    schema = import_json_schema("path/to/schema.json")

    # Import from YAML
    schema = import_yaml_schema("path/to/schema.yaml")

    # Generate BAML code
    baml_code = generate_baml_types(schema)
"""

from .json_schema import (
    import_json_schema,
    parse_json_schema,
    JsonSchemaParser,
)
from .yaml_schema import (
    import_yaml_schema,
    parse_yaml_schema,
)
from .type_mapper import (
    JsonSchemaToLUIMapper,
    json_schema_type_to_parameter_type,
)
from .generator import (
    generate_baml_types,
    generate_baml_class,
    BAMLGenerator,
)

__all__ = [
    # JSON Schema
    "import_json_schema",
    "parse_json_schema",
    "JsonSchemaParser",
    # YAML Schema
    "import_yaml_schema",
    "parse_yaml_schema",
    # Type Mapping
    "JsonSchemaToLUIMapper",
    "json_schema_type_to_parameter_type",
    # Code Generation
    "generate_baml_types",
    "generate_baml_class",
    "BAMLGenerator",
]
