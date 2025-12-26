// Interface Schema Types
// Defines complete agent-friendly interface schemas for LUI applications

/// Complete interface schema for an agent-friendly application
class InterfaceSchema {
  schema_id string @description("Unique identifier for this schema")
  name string @description("Human-readable name of the interface")
  description string @description("What this interface enables")
  version string @description("Semantic version (e.g., 1.0.0)")
  domain DomainInfo
  components LUIComponent[] @description("Available UI components")
  flows ConversationalFlow[] @description("Conversational interaction patterns")
  entities EntityDefinition[] @description("Domain entities and their structure")
  global_context GlobalContext? @description("Shared context across the interface")
}

/// Information about the domain this interface serves
class DomainInfo {
  domain_name string @description("Primary domain (e.g., 'e-commerce', 'healthcare')")
  subdomain string? @description("Specific subdomain (e.g., 'order-management')")
  description string @description("Description of the domain context")
  key_concepts string[] @description("Important domain concepts users should know")
  terminology Terminology[]? @description("Domain-specific terms and definitions")
}

/// Domain-specific terminology for agent understanding
class Terminology {
  term string
  definition string
  synonyms string[]?
  usage_examples string[]?
}

/// Global context shared across the entire interface
class GlobalContext {
  supported_locales string[] @description("Supported language/locale codes")
  default_locale string
  timezone string?
  currency string?
  authentication_required bool
  rate_limits RateLimitConfig?
  feature_flags string[]
}

/// Rate limiting configuration
class RateLimitConfig {
  requests_per_minute int
  requests_per_hour int?
  burst_limit int?
}
