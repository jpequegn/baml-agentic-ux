// Visual Element Types (Adaptive Cards)
// Rich visual responses using Adaptive Cards-compatible format
// Issue #37 - Phase 1: Multi-Modal LUI Support

// ============================================
// Spacing and Layout Enums
// ============================================

/// Spacing between elements
enum Spacing {
  NONE @description("No spacing")
  SMALL @description("Small spacing (8px)")
  DEFAULT @description("Default spacing (12px)")
  MEDIUM @description("Medium spacing (16px)")
  LARGE @description("Large spacing (24px)")
  EXTRA_LARGE @description("Extra large spacing (32px)")
  PADDING @description("Padding amount")
}

/// Horizontal alignment
enum HorizontalAlignment {
  LEFT @description("Left aligned")
  CENTER @description("Center aligned")
  RIGHT @description("Right aligned")
}

/// Vertical alignment for columns
enum VerticalContentAlignment {
  TOP @description("Top aligned")
  CENTER @description("Center aligned")
  BOTTOM @description("Bottom aligned")
}

/// Container style
enum ContainerStyle {
  DEFAULT @description("Default container style")
  EMPHASIS @description("Emphasized container")
  GOOD @description("Positive/success style")
  ATTENTION @description("Warning/attention style")
  WARNING @description("Warning style")
  ACCENT @description("Accent color style")
}

// ============================================
// Text Styling Enums
// ============================================

/// Text sizes
enum TextSize {
  SMALL @description("Small text")
  DEFAULT @description("Default text size")
  MEDIUM @description("Medium text")
  LARGE @description("Large text")
  EXTRA_LARGE @description("Extra large text")
}

/// Text weights
enum TextWeight {
  LIGHTER @description("Lighter weight")
  DEFAULT @description("Default weight")
  BOLDER @description("Bold weight")
}

/// Text colors
enum TextColor {
  DEFAULT @description("Default text color")
  DARK @description("Dark text")
  LIGHT @description("Light text")
  ACCENT @description("Accent color")
  GOOD @description("Positive/success color")
  WARNING @description("Warning color")
  ATTENTION @description("Attention/error color")
}

/// Font type
enum FontType {
  DEFAULT @description("Default font")
  MONOSPACE @description("Monospace font for code")
}

// ============================================
// Image Types
// ============================================

/// Image sizes
enum ImageSize {
  AUTO @description("Automatic sizing")
  STRETCH @description("Stretch to fill")
  SMALL @description("Small image (40x40)")
  MEDIUM @description("Medium image (80x80)")
  LARGE @description("Large image (160x160)")
}

/// Image styles
enum ImageStyle {
  DEFAULT @description("Default rectangular style")
  PERSON @description("Circular style for avatars")
}

/// Background image fill mode
enum ImageFillMode {
  COVER @description("Cover the container")
  REPEAT_HORIZONTALLY @description("Repeat horizontally")
  REPEAT_VERTICALLY @description("Repeat vertically")
  REPEAT @description("Repeat both directions")
}

// ============================================
// Card Element Types
// ============================================

/// Types of card elements
enum CardElementType {
  TEXT_BLOCK @description("Text content block")
  IMAGE @description("Image element")
  RICH_TEXT_BLOCK @description("Rich formatted text")
  FACT_SET @description("Key-value pairs display")
  CONTAINER @description("Container for grouping elements")
  COLUMN_SET @description("Horizontal columns layout")
  COLUMN @description("Single column in a column set")
  TABLE @description("Table element")
  TABLE_ROW @description("Row in a table")
  TABLE_CELL @description("Cell in a table row")
  IMAGE_SET @description("Set of images")
  MEDIA @description("Media player element")
  ACTION_SET @description("Inline action buttons")
  // Input elements
  INPUT_TEXT @description("Text input field")
  INPUT_NUMBER @description("Number input field")
  INPUT_DATE @description("Date picker input")
  INPUT_TIME @description("Time picker input")
  INPUT_TOGGLE @description("Toggle switch input")
  INPUT_CHOICE_SET @description("Choice set (dropdown/radio/checkbox)")
}

// ============================================
// Card Action Types
// ============================================

/// Types of card actions
enum CardActionType {
  OPEN_URL @description("Open a URL")
  SUBMIT @description("Submit form data")
  SHOW_CARD @description("Show an embedded card")
  TOGGLE_VISIBILITY @description("Toggle element visibility")
  EXECUTE @description("Execute server-side action")
}

// ============================================
// Input Types
// ============================================

/// Text input style
enum TextInputStyle {
  TEXT @description("Single line text")
  TEL @description("Telephone number")
  URL @description("URL input")
  EMAIL @description("Email address")
  PASSWORD @description("Password (masked)")
}

/// Choice input style
enum ChoiceInputStyle {
  COMPACT @description("Dropdown select")
  EXPANDED @description("Radio buttons or checkboxes")
  FILTERED @description("Searchable dropdown")
}

// ============================================
// Supporting Classes
// ============================================

/// A fact (key-value pair) for FactSet
class Fact {
  title string @description("The label/key")
  value string @description("The value")
}

/// A choice option for choice inputs
class Choice {
  title string @description("Display text")
  value string @description("Value to submit")
}

/// A table cell definition
class TableCell {
  type string @description("Always 'TableCell'")
  items CardElement[]? @description("Elements in the cell")
}

/// A table row definition
class TableRow {
  type string @description("Always 'TableRow'")
  cells TableCell[] @description("Cells in the row")
}

/// Table column definition
class TableColumnDefinition {
  width string? @description("Column width (px, weight, or auto)")
  horizontal_alignment HorizontalAlignment? @description("Content alignment")
  vertical_alignment VerticalContentAlignment? @description("Vertical alignment")
}

/// Background image for containers
class BackgroundImage {
  url string @description("Image URL")
  fill_mode ImageFillMode? @description("How to fill the container")
  horizontal_alignment HorizontalAlignment? @description("Horizontal position")
  vertical_alignment VerticalContentAlignment? @description("Vertical position")
}

/// Rich text inline element
class TextRun {
  type string @description("Always 'TextRun'")
  text string @description("Text content")
  size TextSize? @description("Text size")
  weight TextWeight? @description("Text weight")
  color TextColor? @description("Text color")
  italic bool? @description("Italic style")
  strikethrough bool? @description("Strikethrough style")
  underline bool? @description("Underline style")
  highlight bool? @description("Highlight style")
  font_type FontType? @description("Font type")
  select_action CardAction? @description("Action on click")
}

/// Target element for toggle visibility action
class TargetElement {
  element_id string @description("ID of element to toggle")
  is_visible bool? @description("Target visibility state")
}

// ============================================
// Card Element Class
// ============================================

/// A single card element
class CardElement {
  element_type CardElementType @description("Type of element")
  id string? @description("Unique element ID")
  spacing Spacing? @description("Spacing above element")
  separator bool? @description("Show separator above")
  is_visible bool? @description("Element visibility")
  height string? @description("Element height (auto or stretch)")

  // TextBlock properties
  text string? @description("Text content")
  size TextSize? @description("Text size")
  weight TextWeight? @description("Text weight")
  color TextColor? @description("Text color")
  wrap bool? @description("Wrap long text")
  max_lines int? @description("Maximum lines to show")
  font_type FontType? @description("Font type")
  horizontal_alignment HorizontalAlignment? @description("Text alignment")
  is_subtle bool? @description("Subtle/muted appearance")

  // Image properties
  url string? @description("Image URL")
  alt_text string? @description("Image alt text for accessibility")
  image_size ImageSize? @description("Image size")
  image_style ImageStyle? @description("Image style (default/person)")
  width string? @description("Explicit width (e.g., '100px')")
  background_color string? @description("Background color for transparent images")
  select_action CardAction? @description("Action on click")

  // Container properties
  items CardElement[]? @description("Child elements")
  style ContainerStyle? @description("Container style")
  bleed bool? @description("Bleed to parent edges")
  min_height string? @description("Minimum height")
  vertical_content_alignment VerticalContentAlignment? @description("Vertical alignment")
  background_image BackgroundImage? @description("Background image")

  // ColumnSet properties
  columns Column[]? @description("Columns in set")

  // FactSet properties
  facts Fact[]? @description("Facts to display")

  // Table properties
  columns_def TableColumnDefinition[]? @description("Column definitions")
  rows TableRow[]? @description("Table rows")
  first_row_as_header bool? @description("First row is header")
  show_grid_lines bool? @description("Show grid lines")
  grid_style ContainerStyle? @description("Grid style")
  horizontal_cell_content_alignment HorizontalAlignment? @description("Cell horizontal alignment")
  vertical_cell_content_alignment VerticalContentAlignment? @description("Cell vertical alignment")

  // RichTextBlock properties
  inlines TextRun[]? @description("Inline text runs")

  // ImageSet properties
  images CardElement[]? @description("Images in set")
  image_set_size ImageSize? @description("Size for all images")

  // Media properties
  poster string? @description("Poster image URL")
  sources MediaSource[]? @description("Media sources")

  // ActionSet properties
  actions CardAction[]? @description("Actions to display")

  // Input properties
  input_id string? @description("Input field ID for form submission")
  label string? @description("Input label")
  is_required bool? @description("Required field")
  error_message string? @description("Error message for validation")
  placeholder string? @description("Placeholder text")
  value string? @description("Default value")
  input_style TextInputStyle? @description("Text input style")
  is_multiline bool? @description("Multi-line text input")
  max_length int? @description("Maximum character length")
  regex string? @description("Validation regex")

  // Number input properties
  min_value float? @description("Minimum value")
  max_value float? @description("Maximum value")

  // Date/Time input properties
  min_date string? @description("Minimum date (YYYY-MM-DD)")
  max_date string? @description("Maximum date (YYYY-MM-DD)")

  // Toggle properties
  title_for_true string? @description("Label when on")
  title_for_false string? @description("Label when off")
  value_on string? @description("Value when on")
  value_off string? @description("Value when off")

  // ChoiceSet properties
  choices Choice[]? @description("Available choices")
  choice_style ChoiceInputStyle? @description("Choice input style")
  is_multi_select bool? @description("Allow multiple selection")
  wrap_choices bool? @description("Wrap choice labels")
}

/// A column in a ColumnSet
class Column {
  type string @description("Always 'Column'")
  width string @description("Column width (auto, stretch, or weight)")
  items CardElement[]? @description("Elements in column")
  id string? @description("Column ID")
  spacing Spacing? @description("Spacing before column")
  separator bool? @description("Show separator before")
  style ContainerStyle? @description("Column style")
  vertical_content_alignment VerticalContentAlignment? @description("Vertical alignment")
  background_image BackgroundImage? @description("Background image")
  min_height string? @description("Minimum height")
  bleed bool? @description("Bleed to edges")
  select_action CardAction? @description("Action on click")
  is_visible bool? @description("Visibility")
}

/// Media source definition
class MediaSource {
  mime_type string @description("MIME type (e.g., video/mp4)")
  url string @description("Media URL")
}

// ============================================
// Card Action Class
// ============================================

/// A card action
class CardAction {
  action_type CardActionType @description("Type of action")
  id string? @description("Action ID")
  title string @description("Button/action title")
  icon_url string? @description("Icon URL")
  style string? @description("Action style (default, positive, destructive)")
  tooltip string? @description("Tooltip text")
  is_enabled bool? @description("Whether action is enabled")
  mode string? @description("Mode (primary, secondary)")

  // OpenUrl properties
  url string? @description("URL to open")

  // Submit/Execute properties
  data string? @description("Data to submit (JSON string)")
  associated_inputs string? @description("Which inputs to include (auto, none)")
  verb string? @description("Action verb for execute")

  // ShowCard properties
  card AdaptiveCard? @description("Card to show")

  // ToggleVisibility properties
  target_elements TargetElement[]? @description("Elements to toggle")

  // Fallback
  fallback string? @description("Fallback action type")
}

// ============================================
// Adaptive Card Class
// ============================================

/// A complete Adaptive Card
class AdaptiveCard {
  type string @description("Always 'AdaptiveCard'")
  schema_version string @description("Schema version (e.g., '1.5')")
  version string @description("Card version")
  body CardElement[] @description("Card body elements")
  actions CardAction[]? @description("Card-level actions")
  select_action CardAction? @description("Action on card click")
  fallback_text string @description("Screen reader fallback text")
  background_image BackgroundImage? @description("Card background image")
  min_height string? @description("Minimum card height")
  speak string? @description("Speech text (SSML)")
  lang string? @description("Language code")
  vertical_content_alignment VerticalContentAlignment? @description("Vertical alignment")
  rtl bool? @description("Right-to-left layout")
  refresh CardRefresh? @description("Auto-refresh configuration")
  authentication CardAuthentication? @description("Authentication config")
  metadata CardMetadata? @description("Card metadata")
}

/// Card refresh configuration
class CardRefresh {
  action CardAction @description("Action to invoke on refresh")
  expires string? @description("ISO timestamp when card expires")
  user_ids string[]? @description("User IDs that can refresh")
}

/// Card authentication configuration
class CardAuthentication {
  text string @description("Sign-in prompt text")
  connection_name string @description("OAuth connection name")
  token_exchange_resource TokenExchangeResource? @description("Token exchange config")
  buttons CardAction[]? @description("Authentication buttons")
}

/// Token exchange resource for SSO
class TokenExchangeResource {
  id string @description("Resource ID")
  uri string @description("Resource URI")
  provider_id string @description("Provider ID")
}

/// Card metadata
class CardMetadata {
  web_url string? @description("Web URL for card content")
}

// ============================================
// Validation Types
// ============================================

/// Result of Adaptive Card validation
class AdaptiveCardValidationResult {
  is_valid bool @description("Whether the card is valid")
  errors AdaptiveCardValidationError[]? @description("Validation errors")
  warnings AdaptiveCardValidationWarning[]? @description("Validation warnings")
  schema_version string? @description("Detected schema version")
  compatibility AdaptiveCardCompatibility? @description("Platform compatibility")
}

/// Validation error
class AdaptiveCardValidationError {
  code string @description("Error code")
  message string @description("Error message")
  path string? @description("JSON path to error")
  element_type string? @description("Element type that caused error")
}

/// Validation warning
class AdaptiveCardValidationWarning {
  code string @description("Warning code")
  message string @description("Warning message")
  suggestion string? @description("Suggested fix")
  path string? @description("JSON path to warning")
}

/// Platform compatibility information
class AdaptiveCardCompatibility {
  teams bool @description("Compatible with Microsoft Teams")
  outlook bool @description("Compatible with Microsoft Outlook")
  windows bool @description("Compatible with Windows Widgets")
  web bool @description("Compatible with web SDK")
  unsupported_features string[]? @description("Features not supported on some platforms")
}

// ============================================
// Exporter Options
// ============================================

/// Options for Adaptive Card export
class AdaptiveCardExportOptions {
  schema_version string @description("Target schema version (1.0-1.5)")
  include_fallback_text bool @description("Always include fallback text")
  target_platform AdaptiveCardPlatform? @description("Target platform for optimization")
  minify bool @description("Minify JSON output")
  validate bool @description("Validate before export")
}

/// Target platforms for Adaptive Cards
enum AdaptiveCardPlatform {
  GENERIC @description("Generic/all platforms")
  TEAMS @description("Microsoft Teams")
  OUTLOOK @description("Microsoft Outlook")
  WINDOWS @description("Windows Widgets")
  WEB @description("Web SDK")
  BOT_FRAMEWORK @description("Bot Framework")
}

// ============================================
// Helper Functions
// ============================================

/// Convert visual elements to an Adaptive Card
function CreateAdaptiveCard(
  elements: MultiModalVisualElement[],
  actions: MultiModalAction[]?,
  fallback_text: string
) -> AdaptiveCard {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Create an Adaptive Card from the given visual elements.

    ## Visual Elements
    {{ elements }}

    {% if actions %}
    ## Actions
    {{ actions }}
    {% endif %}

    ## Fallback Text
    {{ fallback_text }}

    ## Requirements
    1. Convert each visual element to appropriate Adaptive Card element
    2. Use proper element types and properties
    3. Include all actions as card actions
    4. Set appropriate spacing and styling
    5. Ensure fallback_text is set for accessibility

    {{ ctx.output_format }}
  "#
}

/// Validate an Adaptive Card
function ValidateAdaptiveCard(
  card: AdaptiveCard,
  target_platform: AdaptiveCardPlatform?
) -> AdaptiveCardValidationResult {
  client "anthropic/claude-sonnet-4-20250514"
  prompt #"
    Validate the given Adaptive Card.

    ## Card
    {{ card }}

    {% if target_platform %}
    ## Target Platform
    {{ target_platform }}
    {% endif %}

    ## Validation Steps
    1. Check required properties
    2. Validate element types and properties
    3. Check for deprecated features
    4. Verify platform compatibility
    5. Check accessibility (fallback_text present)

    {{ ctx.output_format }}
  "#
}

// ============================================
// Test Cases
// ============================================

test create_simple_card {
  functions [CreateAdaptiveCard]
  args {
    elements []
    actions null
    fallback_text "A simple adaptive card"
  }
}

test validate_card {
  functions [ValidateAdaptiveCard]
  args {
    card {
      type "AdaptiveCard"
      schema_version "1.5"
      version "1.5"
      body []
      actions null
      select_action null
      fallback_text "Test card"
      background_image null
      min_height null
      speak null
      lang "en-US"
      vertical_content_alignment null
      rtl null
      refresh null
      authentication null
      metadata null
    }
    target_platform TEAMS
  }
}
