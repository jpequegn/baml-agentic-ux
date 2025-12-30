"""
BAML Runtime Type Reflection

Provides runtime introspection capabilities for BAML-generated types.

This module enables:
- Listing all fields of BAML classes
- Getting field types programmatically
- Enumerating enum values
- Generating documentation from types
- Validating external data against BAML types

Example usage:
    from src.baml_reflection import get_type_info, get_fields, get_enum_values
    from baml_client.types import InterfaceSchema, LUIComponentType

    # Type introspection
    type_info = get_type_info(InterfaceSchema)
    print(type_info.name)  # "InterfaceSchema"
    print(type_info.fields)  # [FieldInfo(...), ...]

    # Field details
    for field in get_fields(LUIComponent):
        print(f"{field.name}: {field.type_name}")
        print(f"  Optional: {field.is_optional}")
        print(f"  Description: {field.description}")

    # Enum values
    values = get_enum_values(LUIComponentType)
    # ['ACTION', 'QUERY', 'NAVIGATION', 'INPUT', 'CONFIRMATION', 'FEEDBACK']
"""

from .reflection import (
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

__all__ = [
    "get_type_info",
    "get_fields",
    "get_enum_values",
    "get_all_classes",
    "get_all_enums",
    "validate_data",
    "TypeInfo",
    "FieldInfo",
    "EnumInfo",
    "ValidationResult",
]
