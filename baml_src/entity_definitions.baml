// Entity Definition Types
// Defines domain entities, their attributes, and relationships

/// Definition of a domain entity
class EntityDefinition {
  entity_name string @description("Name of the entity (e.g., 'User', 'Order')")
  entity_type EntityType
  description string @description("What this entity represents")
  attributes EntityAttribute[] @description("Properties of this entity")
  relationships EntityRelationship[] @description("Relationships to other entities")
  validations EntityValidation[]? @description("Entity-level validations")
  examples EntityExample[]? @description("Example instances for agent understanding")
}

/// Types of domain entities
enum EntityType {
  USER @description("Represents a user or actor in the system")
  RESOURCE @description("A manageable resource (document, item, etc.)")
  ACTION @description("An action or operation that can be performed")
  STATE @description("A state or status value")
  CONFIGURATION @description("System or user configuration")
  EVENT @description("An event or occurrence")
  AGGREGATE @description("A composite entity containing other entities")
}

/// An attribute of an entity
class EntityAttribute {
  attribute_name string
  attribute_type AttributeType
  description string
  required bool
  default_value string?
  constraints AttributeConstraint[]?
  display_config AttributeDisplayConfig?
}

/// Types for entity attributes
enum AttributeType {
  STRING
  NUMBER
  INTEGER
  BOOLEAN
  DATE
  DATETIME
  ENUM
  REFERENCE @description("Reference to another entity")
  LIST
  OBJECT @description("Nested object/map")
  FILE
  URL
  EMAIL
  PHONE
}

/// Constraints on attribute values
class AttributeConstraint {
  constraint_type EntityConstraintType
  value string
  error_message string
}

enum EntityConstraintType {
  MIN_LENGTH
  MAX_LENGTH
  MIN_VALUE
  MAX_VALUE
  PATTERN
  ENUM_VALUES
  UNIQUE
  IMMUTABLE
  COMPUTED
}

/// How an attribute should be displayed/collected
class AttributeDisplayConfig {
  display_name string @description("User-friendly label")
  placeholder string?
  help_text string?
  input_type InputType?
  display_order int?
  group_name string? @description("Group related attributes")
}

enum InputType {
  TEXT
  TEXTAREA
  NUMBER
  SELECT
  MULTISELECT
  CHECKBOX
  RADIO
  DATE_PICKER
  FILE_UPLOAD
  AUTOCOMPLETE
  HIDDEN
}

/// Relationship between entities
class EntityRelationship {
  relationship_name string
  relationship_type RelationshipType
  target_entity string @description("Name of related entity")
  inverse_name string? @description("Name from the other side")
  required bool
  cascade_delete bool?
  description string?
}

enum RelationshipType {
  ONE_TO_ONE
  ONE_TO_MANY
  MANY_TO_ONE
  MANY_TO_MANY
}

/// Entity-level validation rules
class EntityValidation {
  validation_name string
  expression string @description("Validation expression")
  error_message string
  severity ValidationSeverity
}

enum ValidationSeverity {
  ERROR @description("Blocks saving")
  WARNING @description("Shows warning but allows saving")
  INFO @description("Informational only")
}

/// Example instance of an entity for agent understanding
class EntityExample {
  example_name string
  description string?
  attribute_values map<string, string>
  use_case string? @description("When this example is relevant")
}

/// Runtime entity instance
class EntityInstance {
  entity_type string
  entity_id string
  attributes map<string, string>
  created_at string
  updated_at string
  version int?
}
