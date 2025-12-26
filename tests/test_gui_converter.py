"""Tests for GUI to LUI Converter Types."""

import pytest
from baml_client.types import (
    # GUI Specification types
    GUISpecification,
    GUIComponent,
    GUIComponentType,
    GUIProperty,
    GUIPropertyType,
    GUIEvent,
    GUIEventType,
    GUIValidation,
    # Navigation types
    NavigationStructure,
    NavigationType,
    NavigationItem,
    # Form types
    FormDefinition,
    FormField,
    SelectOption,
    ValidationMode,
    # Action types
    ActionDefinition,
    ActionType,
    ActionParameter,
    ParameterSource,
    # State types
    StateDefinition,
    StateTransition,
    # Conversion types
    ConversionOptions,
    ConversionApproach,
    ConversionResult,
    ConversionNote,
    ConversionNoteType,
    # Analysis types
    GUIAnalysisResult,
    NavigationConversionResult,
    KeyboardShortcut,
    DifferenceAnalysis,
    FunctionalityChange,
    # Interface schema for integration
    InterfaceSchema,
    DomainInfo,
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
)


class TestGUIComponentTypeEnums:
    """Test GUI component type enums."""

    def test_gui_component_type_has_input_types(self):
        """Verify input component types exist."""
        input_types = {
            "BUTTON",
            "INPUT_TEXT",
            "INPUT_NUMBER",
            "INPUT_EMAIL",
            "INPUT_PASSWORD",
            "INPUT_DATE",
            "INPUT_FILE",
            "TEXTAREA",
            "SELECT",
            "MULTISELECT",
            "CHECKBOX",
            "CHECKBOX_GROUP",
            "RADIO_GROUP",
            "TOGGLE",
            "SLIDER",
            "COLOR_PICKER",
        }
        actual = {t.name for t in GUIComponentType}
        assert input_types.issubset(actual)

    def test_gui_component_type_has_navigation_types(self):
        """Verify navigation component types exist."""
        nav_types = {"LINK", "MENU", "TAB", "BREADCRUMB", "PAGINATION"}
        actual = {t.name for t in GUIComponentType}
        assert nav_types.issubset(actual)

    def test_gui_component_type_has_container_types(self):
        """Verify container component types exist."""
        container_types = {
            "MODAL",
            "DRAWER",
            "ACCORDION",
            "CARD",
            "FORM",
            "TABLE",
            "LIST",
            "GRID",
        }
        actual = {t.name for t in GUIComponentType}
        assert container_types.issubset(actual)

    def test_action_type_enum_values(self):
        """Verify all action types exist."""
        expected = {
            "CREATE",
            "READ",
            "UPDATE",
            "DELETE",
            "NAVIGATE",
            "DOWNLOAD",
            "UPLOAD",
            "SHARE",
            "EXPORT",
            "IMPORT",
            "PRINT",
            "REFRESH",
            "SEARCH",
            "FILTER",
            "SORT",
        }
        actual = {t.name for t in ActionType}
        assert actual == expected

    def test_conversion_approach_enum_values(self):
        """Verify conversion approach values."""
        expected = {"LITERAL", "OPTIMIZED", "HYBRID", "MINIMAL", "COMPREHENSIVE"}
        actual = {a.name for a in ConversionApproach}
        assert actual == expected

    def test_navigation_type_enum_values(self):
        """Verify navigation type values."""
        expected = {"SIDEBAR", "TOP_BAR", "BOTTOM_BAR", "HAMBURGER", "TAB_BAR", "BREADCRUMB"}
        actual = {t.name for t in NavigationType}
        assert actual == expected


class TestGUIComponent:
    """Test GUIComponent creation."""

    def test_create_button_component(self):
        """Test creating a button component."""
        event = GUIEvent(
            event_type=GUIEventType.CLICK,
            handler_description="Submit the form",
            navigates_to=None,
            api_call="POST /api/submit",
        )

        button = GUIComponent(
            component_id="submit-btn",
            component_type=GUIComponentType.BUTTON,
            label="Submit",
            placeholder=None,
            children=None,
            properties=None,
            events=[event],
            validation=None,
        )

        assert button.component_id == "submit-btn"
        assert button.component_type == GUIComponentType.BUTTON
        assert button.events is not None
        assert len(button.events) == 1

    def test_create_input_with_validation(self):
        """Test creating an input with validation."""
        validation = GUIValidation(
            rule_type="pattern",
            constraint="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
            error_message="Please enter a valid email address",
        )

        input_field = GUIComponent(
            component_id="email-input",
            component_type=GUIComponentType.INPUT_EMAIL,
            label="Email Address",
            placeholder="you@example.com",
            children=None,
            properties=None,
            events=None,
            validation=[validation],
        )

        assert input_field.component_type == GUIComponentType.INPUT_EMAIL
        assert input_field.validation is not None
        assert len(input_field.validation) == 1

    def test_create_nested_components(self):
        """Test creating nested component hierarchy."""
        email_input = GUIComponent(
            component_id="email",
            component_type=GUIComponentType.INPUT_EMAIL,
            label="Email",
            placeholder=None,
            children=None,
            properties=None,
            events=None,
            validation=None,
        )

        password_input = GUIComponent(
            component_id="password",
            component_type=GUIComponentType.INPUT_PASSWORD,
            label="Password",
            placeholder=None,
            children=None,
            properties=None,
            events=None,
            validation=None,
        )

        form = GUIComponent(
            component_id="login-form",
            component_type=GUIComponentType.FORM,
            label="Login",
            placeholder=None,
            children=[email_input, password_input],
            properties=None,
            events=None,
            validation=None,
        )

        assert form.component_type == GUIComponentType.FORM
        assert form.children is not None
        assert len(form.children) == 2
        assert form.children[0].component_type == GUIComponentType.INPUT_EMAIL


class TestGUISpecification:
    """Test GUISpecification creation."""

    def test_create_minimal_gui_spec(self):
        """Test creating a minimal GUI specification."""
        button = GUIComponent(
            component_id="btn-1",
            component_type=GUIComponentType.BUTTON,
            label="Click Me",
            placeholder=None,
            children=None,
            properties=None,
            events=None,
            validation=None,
        )

        spec = GUISpecification(
            name="Simple App",
            description="A simple application",
            component_tree=[button],
            navigation=None,
            forms=None,
            actions=None,
            states=None,
        )

        assert spec.name == "Simple App"
        assert len(spec.component_tree) == 1

    def test_create_full_gui_spec(self):
        """Test creating a complete GUI specification."""
        # Navigation
        nav = NavigationStructure(
            nav_type=NavigationType.SIDEBAR,
            items=[
                NavigationItem(
                    item_id="home",
                    label="Home",
                    route="/",
                    icon="home",
                    children=None,
                    badge_count=None,
                    requires_auth=False,
                ),
                NavigationItem(
                    item_id="settings",
                    label="Settings",
                    route="/settings",
                    icon="cog",
                    children=None,
                    badge_count=None,
                    requires_auth=True,
                ),
            ],
            default_route="/",
            auth_required_routes=["/settings"],
        )

        # Form
        form = FormDefinition(
            form_id="contact-form",
            form_name="Contact Us",
            purpose="Allow users to send messages",
            fields=[
                FormField(
                    field_id="name",
                    field_label="Your Name",
                    field_type=GUIComponentType.INPUT_TEXT,
                    required=True,
                    default_value=None,
                    options=None,
                    depends_on=None,
                ),
                FormField(
                    field_id="message",
                    field_label="Message",
                    field_type=GUIComponentType.TEXTAREA,
                    required=True,
                    default_value=None,
                    options=None,
                    depends_on=None,
                ),
            ],
            submit_action="send-message",
            validation_mode=ValidationMode.ON_SUBMIT,
        )

        # Action
        action = ActionDefinition(
            action_id="send-message",
            action_name="Send Message",
            action_type=ActionType.CREATE,
            description="Send a contact message",
            requires_confirmation=True,
            permission_required=None,
            parameters=[
                ActionParameter(
                    param_name="name",
                    param_type="string",
                    required=True,
                    source=ParameterSource.USER_INPUT,
                ),
                ActionParameter(
                    param_name="message",
                    param_type="string",
                    required=True,
                    source=ParameterSource.USER_INPUT,
                ),
            ],
        )

        # State
        state = StateDefinition(
            state_id="form-state",
            state_name="Form View",
            description="Showing the contact form",
            visible_components=["contact-form"],
            enabled_actions=["send-message"],
            transitions=[
                StateTransition(
                    trigger="message sent",
                    target_state="success-state",
                    condition=None,
                )
            ],
        )

        # Component tree
        component = GUIComponent(
            component_id="main",
            component_type=GUIComponentType.FORM,
            label="Contact",
            placeholder=None,
            children=None,
            properties=None,
            events=None,
            validation=None,
        )

        spec = GUISpecification(
            name="Contact App",
            description="Application for contacting support",
            component_tree=[component],
            navigation=nav,
            forms=[form],
            actions=[action],
            states=[state],
        )

        assert spec.name == "Contact App"
        assert spec.navigation is not None
        assert spec.navigation.nav_type == NavigationType.SIDEBAR
        assert spec.forms is not None
        assert len(spec.forms) == 1
        assert spec.actions is not None
        assert spec.actions[0].action_type == ActionType.CREATE


class TestConversionOptions:
    """Test ConversionOptions creation."""

    def test_create_literal_conversion_options(self):
        """Test creating literal conversion options."""
        options = ConversionOptions(
            approach=ConversionApproach.LITERAL,
            preserve_structure=True,
            add_confirmations=False,
            generate_help=False,
            optimize_for_voice=False,
            include_shortcuts=False,
            group_related_actions=False,
            max_flow_depth=None,
        )

        assert options.approach == ConversionApproach.LITERAL
        assert options.preserve_structure is True

    def test_create_optimized_conversion_options(self):
        """Test creating optimized conversion options."""
        options = ConversionOptions(
            approach=ConversionApproach.OPTIMIZED,
            preserve_structure=False,
            add_confirmations=True,
            generate_help=True,
            optimize_for_voice=True,
            include_shortcuts=True,
            group_related_actions=True,
            max_flow_depth=5,
        )

        assert options.approach == ConversionApproach.OPTIMIZED
        assert options.max_flow_depth == 5
        assert options.optimize_for_voice is True


class TestConversionResult:
    """Test ConversionResult creation."""

    def test_create_conversion_result(self):
        """Test creating a conversion result."""
        # Create minimal schema
        domain = DomainInfo(
            domain_name="test",
            subdomain=None,
            description="Test domain",
            key_concepts=["test"],
            terminology=None,
        )

        component = LUIComponent(
            component_id="test-component",
            component_type=LUIComponentType.ACTION,
            intent="Test action",
            invocation=InvocationPattern(
                primary_phrase="test",
                alternate_phrases=[],
                examples=[],
                context_requirements=None,
            ),
            parameters=[],
            feedback=FeedbackConfig(
                success_template="Done",
                error_template="Failed",
                progress_template=None,
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
        )

        schema = InterfaceSchema(
            schema_id="converted-v1",
            name="Converted Schema",
            description="Converted from GUI",
            version="1.0.0",
            domain=domain,
            components=[component],
            flows=[],
            entities=[],
            global_context=None,
        )

        note = ConversionNote(
            source_element="submit-button",
            target_element="components[0]",
            conversion_type=ConversionNoteType.DIRECT_MAP,
            rationale="Button directly maps to ACTION component",
        )

        result = ConversionResult(
            lui_schema=schema,
            conversion_notes=[note],
            warnings=["Some hover effects lost in conversion"],
            unmapped_elements=["decorative-icon"],
            suggestions=["Consider adding voice shortcuts"],
        )

        assert result.lui_schema.schema_id == "converted-v1"
        assert len(result.conversion_notes) == 1
        assert result.conversion_notes[0].conversion_type == ConversionNoteType.DIRECT_MAP
        assert len(result.warnings) == 1
        assert len(result.unmapped_elements) == 1


class TestGUIAnalysisResult:
    """Test GUIAnalysisResult creation."""

    def test_create_gui_analysis_result(self):
        """Test creating a GUI analysis result from image analysis."""
        component = GUIComponent(
            component_id="detected-1",
            component_type=GUIComponentType.BUTTON,
            label="Sign In",
            placeholder=None,
            children=None,
            properties=None,
            events=None,
            validation=None,
        )

        spec = GUISpecification(
            name="Detected UI",
            description="UI extracted from screenshot",
            component_tree=[component],
            navigation=None,
            forms=None,
            actions=None,
            states=None,
        )

        result = GUIAnalysisResult(
            extracted_spec=spec,
            confidence=0.85,
            ambiguities=["Button color might indicate state"],
            assumptions=["Assumed English language"],
            recommended_verification=["Verify button action"],
        )

        assert result.confidence == 0.85
        assert len(result.ambiguities) == 1
        assert result.extracted_spec.name == "Detected UI"


class TestNavigationConversion:
    """Test navigation conversion types."""

    def test_create_keyboard_shortcut(self):
        """Test creating a keyboard shortcut."""
        shortcut = KeyboardShortcut(
            key_combination="Ctrl+S",
            action="save",
            description="Save the current document",
        )

        assert shortcut.key_combination == "Ctrl+S"
        assert shortcut.action == "save"

    def test_create_navigation_conversion_result(self):
        """Test creating a navigation conversion result."""
        component = LUIComponent(
            component_id="nav-home",
            component_type=LUIComponentType.NAVIGATION,
            intent="Navigate to home page",
            invocation=InvocationPattern(
                primary_phrase="go home",
                alternate_phrases=["take me home", "home page"],
                examples=["Go to the home page"],
                context_requirements=None,
            ),
            parameters=[],
            feedback=FeedbackConfig(
                success_template="Navigating to home",
                error_template="Couldn't navigate",
                progress_template=None,
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
        )

        shortcut = KeyboardShortcut(
            key_combination="Alt+H",
            action="navigate-home",
            description="Go to home page",
        )

        result = NavigationConversionResult(
            components=[component],
            navigation_flow=None,
            shortcuts=[shortcut],
            voice_commands=["go home", "navigate home", "take me to home"],
        )

        assert len(result.components) == 1
        assert result.shortcuts is not None
        assert len(result.shortcuts) == 1
        assert len(result.voice_commands) == 3


class TestDifferenceAnalysis:
    """Test difference analysis types."""

    def test_create_functionality_change(self):
        """Test creating a functionality change record."""
        change = FunctionalityChange(
            feature="Data filtering",
            gui_behavior="Click filter icon, select from dropdown",
            lui_behavior="Say 'filter by status active'",
            change_type="improved",
            impact="Faster filtering with voice, but no visual filter preview",
        )

        assert change.feature == "Data filtering"
        assert change.change_type == "improved"

    def test_create_difference_analysis(self):
        """Test creating a complete difference analysis."""
        change = FunctionalityChange(
            feature="Navigation",
            gui_behavior="Click menu items",
            lui_behavior="Voice or text commands",
            change_type="different",
            impact="More accessible but less discoverable",
        )

        analysis = DifferenceAnalysis(
            gui_only_features=["Drag and drop", "Hover tooltips"],
            lui_only_features=["Voice commands", "Natural language queries"],
            functionality_changes=[change],
            ux_improvements=["Faster task completion", "Better accessibility"],
            potential_issues=["Learning curve for voice commands"],
            recommendations=["Add tutorial for voice commands"],
            parity_score=0.82,
        )

        assert len(analysis.gui_only_features) == 2
        assert len(analysis.lui_only_features) == 2
        assert analysis.parity_score == 0.82
        assert len(analysis.functionality_changes) == 1
