"""
BAML Type Reflection Implementation

Provides runtime introspection for BAML-generated Pydantic models and enums.
"""

import typing
import inspect
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    Union,
    get_type_hints,
    get_origin,
    get_args,
)

from pydantic import BaseModel


@dataclass
class FieldInfo:
    """Information about a single field in a BAML class."""

    name: str
    type_name: str
    type_class: Optional[Type] = None
    is_optional: bool = False
    is_list: bool = False
    is_enum: bool = False
    is_nested_class: bool = False
    default_value: Any = None
    has_default: bool = False
    description: Optional[str] = None
    inner_type_name: Optional[str] = None  # For List[X], this is "X"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "type_name": self.type_name,
            "is_optional": self.is_optional,
            "is_list": self.is_list,
            "is_enum": self.is_enum,
            "is_nested_class": self.is_nested_class,
            "has_default": self.has_default,
            "default_value": str(self.default_value) if self.has_default else None,
            "description": self.description,
            "inner_type_name": self.inner_type_name,
        }


@dataclass
class EnumInfo:
    """Information about a BAML enum type."""

    name: str
    values: List[str]
    descriptions: Dict[str, Optional[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "values": self.values,
            "descriptions": self.descriptions,
        }


@dataclass
class TypeInfo:
    """Complete information about a BAML type (class or enum)."""

    name: str
    is_enum: bool
    is_class: bool
    fields: List[FieldInfo] = field(default_factory=list)
    enum_values: List[str] = field(default_factory=list)
    description: Optional[str] = None
    base_classes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "is_enum": self.is_enum,
            "is_class": self.is_class,
            "fields": [f.to_dict() for f in self.fields],
            "enum_values": self.enum_values,
            "description": self.description,
            "base_classes": self.base_classes,
        }


@dataclass
class ValidationError:
    """A single validation error."""

    path: str
    message: str
    expected: Optional[str] = None
    actual: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating data against a BAML type."""

    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "is_valid": self.is_valid,
            "errors": [
                {
                    "path": e.path,
                    "message": e.message,
                    "expected": e.expected,
                    "actual": e.actual,
                }
                for e in self.errors
            ],
            "warnings": self.warnings,
        }


def _get_type_name(type_hint: Any) -> str:
    """Get a human-readable name for a type hint."""
    origin = get_origin(type_hint)

    if origin is Union:
        args = get_args(type_hint)
        # Check for Optional (Union[X, None])
        if len(args) == 2 and type(None) in args:
            non_none_type = [a for a in args if a is not type(None)][0]
            return f"Optional[{_get_type_name(non_none_type)}]"
        return f"Union[{', '.join(_get_type_name(a) for a in args)}]"

    if origin is list or origin is typing.List:
        args = get_args(type_hint)
        if args:
            return f"List[{_get_type_name(args[0])}]"
        return "List"

    if origin is dict or origin is typing.Dict:
        args = get_args(type_hint)
        if len(args) == 2:
            return f"Dict[{_get_type_name(args[0])}, {_get_type_name(args[1])}]"
        return "Dict"

    if hasattr(type_hint, "__name__"):
        return type_hint.__name__

    return str(type_hint)


def _get_inner_type(type_hint: Any) -> Optional[Type]:
    """Get the inner type for container types like List[X] or Optional[X]."""
    origin = get_origin(type_hint)

    if origin is Union:
        args = get_args(type_hint)
        if len(args) == 2 and type(None) in args:
            return [a for a in args if a is not type(None)][0]
        return None

    if origin is list or origin is typing.List:
        args = get_args(type_hint)
        if args:
            return args[0]
    return None


def _is_optional(type_hint: Any) -> bool:
    """Check if a type hint is Optional[X]."""
    origin = get_origin(type_hint)
    if origin is Union:
        args = get_args(type_hint)
        return len(args) == 2 and type(None) in args
    return False


def _is_list(type_hint: Any) -> bool:
    """Check if a type hint is List[X]."""
    origin = get_origin(type_hint)
    return origin is list or origin is typing.List


def _is_baml_enum(type_class: Type) -> bool:
    """Check if a type is a BAML-generated enum."""
    return (
        inspect.isclass(type_class)
        and issubclass(type_class, Enum)
        and issubclass(type_class, str)
    )


def _is_baml_class(type_class: Type) -> bool:
    """Check if a type is a BAML-generated class (Pydantic model)."""
    return inspect.isclass(type_class) and issubclass(type_class, BaseModel)


def _extract_description_from_docstring(type_class: Type) -> Optional[str]:
    """Extract description from docstring comment."""
    if hasattr(type_class, "__doc__") and type_class.__doc__:
        doc = type_class.__doc__.strip()
        # Skip if it's just the class name
        if doc and doc != type_class.__name__:
            return doc
    return None


def get_fields(type_class: Type[BaseModel]) -> List[FieldInfo]:
    """
    Get detailed information about all fields in a BAML class.

    Args:
        type_class: A BAML-generated Pydantic model class

    Returns:
        List of FieldInfo objects describing each field

    Example:
        from baml_client.types import LUIComponent

        for field in get_fields(LUIComponent):
            print(f"{field.name}: {field.type_name}")
            print(f"  Optional: {field.is_optional}")
    """
    if not _is_baml_class(type_class):
        raise TypeError(f"{type_class} is not a BAML class (Pydantic model)")

    fields = []
    type_hints = get_type_hints(type_class)
    model_fields = type_class.model_fields

    for field_name, type_hint in type_hints.items():
        pydantic_field = model_fields.get(field_name)

        is_optional = _is_optional(type_hint)
        is_list = _is_list(type_hint)

        # Get the actual type (unwrap Optional/List)
        actual_type = type_hint
        if is_optional:
            actual_type = _get_inner_type(type_hint)
        if is_list and actual_type:
            inner = _get_inner_type(actual_type if not is_optional else type_hint)
            if inner:
                actual_type = inner

        # Check if it's a nested class or enum
        is_enum = False
        is_nested = False
        type_class_ref = None

        if actual_type and hasattr(actual_type, "__mro__"):
            is_enum = _is_baml_enum(actual_type)
            is_nested = _is_baml_class(actual_type)
            type_class_ref = actual_type

        # Get default value
        has_default = False
        default_value = None
        if pydantic_field:
            if pydantic_field.default is not None:
                has_default = True
                default_value = pydantic_field.default
            elif pydantic_field.default_factory is not None:
                has_default = True
                default_value = "(factory)"

        # Get description from Pydantic field
        description = None
        if pydantic_field and pydantic_field.description:
            description = pydantic_field.description

        # Get inner type name for lists
        inner_type_name = None
        if is_list:
            inner = _get_inner_type(type_hint if not is_optional else _get_inner_type(type_hint))
            if inner:
                inner_type_name = _get_type_name(inner)

        fields.append(
            FieldInfo(
                name=field_name,
                type_name=_get_type_name(type_hint),
                type_class=type_class_ref,
                is_optional=is_optional,
                is_list=is_list,
                is_enum=is_enum,
                is_nested_class=is_nested,
                default_value=default_value,
                has_default=has_default,
                description=description,
                inner_type_name=inner_type_name,
            )
        )

    return fields


def get_enum_values(enum_class: Type[Enum]) -> List[str]:
    """
    Get all values from a BAML enum.

    Args:
        enum_class: A BAML-generated enum class

    Returns:
        List of enum value strings

    Example:
        from baml_client.types import LUIComponentType

        values = get_enum_values(LUIComponentType)
        # ['ACTION', 'QUERY', 'NAVIGATION', 'INPUT', 'CONFIRMATION', 'FEEDBACK']
    """
    if not _is_baml_enum(enum_class):
        raise TypeError(f"{enum_class} is not a BAML enum")

    return [member.value for member in enum_class]


def get_enum_info(enum_class: Type[Enum]) -> EnumInfo:
    """
    Get detailed information about a BAML enum.

    Args:
        enum_class: A BAML-generated enum class

    Returns:
        EnumInfo with values and descriptions
    """
    if not _is_baml_enum(enum_class):
        raise TypeError(f"{enum_class} is not a BAML enum")

    values = get_enum_values(enum_class)

    # Try to extract descriptions from docstring
    descriptions = {}
    doc = enum_class.__doc__
    if doc:
        # Parse docstring for member descriptions
        for member in enum_class:
            descriptions[member.value] = None  # BAML doesn't preserve @description in enums

    return EnumInfo(
        name=enum_class.__name__,
        values=values,
        descriptions=descriptions,
    )


def get_type_info(type_class: Type) -> TypeInfo:
    """
    Get complete information about a BAML type (class or enum).

    Args:
        type_class: A BAML-generated class or enum

    Returns:
        TypeInfo with all details about the type

    Example:
        from baml_client.types import InterfaceSchema

        info = get_type_info(InterfaceSchema)
        print(info.name)  # "InterfaceSchema"
        print(info.is_class)  # True
        for field in info.fields:
            print(f"  {field.name}: {field.type_name}")
    """
    is_enum = _is_baml_enum(type_class)
    is_class = _is_baml_class(type_class)

    if not is_enum and not is_class:
        raise TypeError(f"{type_class} is not a BAML type (class or enum)")

    description = _extract_description_from_docstring(type_class)
    base_classes = [b.__name__ for b in type_class.__bases__ if b not in (Enum, str, BaseModel, object)]

    if is_enum:
        return TypeInfo(
            name=type_class.__name__,
            is_enum=True,
            is_class=False,
            enum_values=get_enum_values(type_class),
            description=description,
            base_classes=base_classes,
        )
    else:
        return TypeInfo(
            name=type_class.__name__,
            is_enum=False,
            is_class=True,
            fields=get_fields(type_class),
            description=description,
            base_classes=base_classes,
        )


def get_all_classes() -> Dict[str, Type[BaseModel]]:
    """
    Get all BAML-generated classes.

    Returns:
        Dictionary mapping class names to class types

    Example:
        classes = get_all_classes()
        for name, cls in classes.items():
            print(f"{name}: {len(get_fields(cls))} fields")
    """
    try:
        from baml_client import types as baml_types
    except ImportError:
        raise ImportError("baml_client not found. Run 'baml-cli generate' first.")

    classes = {}
    for name in dir(baml_types):
        if name.startswith("_"):
            continue
        obj = getattr(baml_types, name)
        if _is_baml_class(obj):
            classes[name] = obj

    return classes


def get_all_enums() -> Dict[str, Type[Enum]]:
    """
    Get all BAML-generated enums.

    Returns:
        Dictionary mapping enum names to enum types

    Example:
        enums = get_all_enums()
        for name, enum_cls in enums.items():
            values = get_enum_values(enum_cls)
            print(f"{name}: {len(values)} values")
    """
    try:
        from baml_client import types as baml_types
    except ImportError:
        raise ImportError("baml_client not found. Run 'baml-cli generate' first.")

    enums = {}
    for name in dir(baml_types):
        if name.startswith("_"):
            continue
        obj = getattr(baml_types, name)
        if _is_baml_enum(obj):
            enums[name] = obj

    return enums


def validate_data(data: Dict[str, Any], type_class: Type[BaseModel]) -> ValidationResult:
    """
    Validate external data against a BAML type.

    Args:
        data: Dictionary of data to validate
        type_class: BAML class to validate against

    Returns:
        ValidationResult with is_valid flag and any errors

    Example:
        from baml_client.types import LUIComponent

        data = {"component_id": "test", "intent": "Do something"}
        result = validate_data(data, LUIComponent)
        if not result.is_valid:
            for error in result.errors:
                print(f"{error.path}: {error.message}")
    """
    if not _is_baml_class(type_class):
        raise TypeError(f"{type_class} is not a BAML class")

    errors = []

    try:
        # Use Pydantic's validation
        type_class.model_validate(data)
        return ValidationResult(is_valid=True)
    except Exception as e:
        # Parse Pydantic validation errors
        error_str = str(e)
        errors.append(
            ValidationError(
                path="root",
                message=error_str,
            )
        )
        return ValidationResult(is_valid=False, errors=errors)


def generate_markdown_docs(type_class: Type) -> str:
    """
    Generate Markdown documentation for a BAML type.

    Args:
        type_class: A BAML-generated class or enum

    Returns:
        Markdown string documenting the type
    """
    info = get_type_info(type_class)

    lines = [f"# {info.name}", ""]

    if info.description:
        lines.extend([info.description, ""])

    if info.is_enum:
        lines.extend(["## Values", ""])
        for value in info.enum_values:
            lines.append(f"- `{value}`")
    else:
        lines.extend(["## Fields", "", "| Field | Type | Required | Description |", "|-------|------|----------|-------------|"])
        for field_info in info.fields:
            required = "No" if field_info.is_optional else "Yes"
            desc = field_info.description or "-"
            lines.append(f"| `{field_info.name}` | `{field_info.type_name}` | {required} | {desc} |")

    return "\n".join(lines)


def generate_typescript_interface(type_class: Type[BaseModel]) -> str:
    """
    Generate TypeScript interface definition for a BAML class.

    Args:
        type_class: A BAML-generated class

    Returns:
        TypeScript interface string
    """
    if not _is_baml_class(type_class):
        raise TypeError(f"{type_class} is not a BAML class")

    info = get_type_info(type_class)

    lines = [f"interface {info.name} {{"]

    type_map = {
        "str": "string",
        "int": "number",
        "float": "number",
        "bool": "boolean",
        "Any": "any",
    }

    for field_info in info.fields:
        ts_type = field_info.type_name

        # Convert Python types to TypeScript
        for py_type, ts_equiv in type_map.items():
            ts_type = ts_type.replace(py_type, ts_equiv)

        ts_type = ts_type.replace("List[", "Array<").replace("]", ">")
        ts_type = ts_type.replace("Optional[", "").rstrip(">")

        optional = "?" if field_info.is_optional else ""
        comment = f"  // {field_info.description}" if field_info.description else ""
        lines.append(f"  {field_info.name}{optional}: {ts_type};{comment}")

    lines.append("}")

    return "\n".join(lines)
