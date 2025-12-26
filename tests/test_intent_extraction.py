"""Tests for Intent Extraction and Routing Types."""

import pytest
from baml_client.types import (
    # Intent types
    Intent,
    IntentCategory,
    IntentExtraction,
    AmbiguityInfo,
    # Context types
    ConversationContext,
    ConversationMessage,
    MessageRole,
    UserPreferences,
    VerbosityPreference,
    # Multi-intent types
    MultiIntentExtraction,
    ExecutionStrategy,
    IntentDependency,
    DependencyType,
    # Routing types
    RoutingResult,
    ComponentMatch,
    ParameterBinding,
    MissingParameter,
    # Shared types
    ExtractedParameter,
    # Interface types for integration
    InterfaceSchema,
    DomainInfo,
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
)


class TestIntentCategoryEnum:
    """Test IntentCategory enum values."""

    def test_intent_category_has_crud_operations(self):
        """Verify CRUD operation categories exist."""
        crud_categories = {"CREATE", "READ", "UPDATE", "DELETE"}
        actual = {c.name for c in IntentCategory}
        assert crud_categories.issubset(actual)

    def test_intent_category_has_all_values(self):
        """Verify all expected intent categories exist."""
        expected = {
            "CREATE",
            "READ",
            "UPDATE",
            "DELETE",
            "NAVIGATE",
            "QUERY",
            "CONFIGURE",
            "HELP",
        }
        actual = {c.name for c in IntentCategory}
        assert actual == expected


class TestMessageRoleEnum:
    """Test MessageRole enum values."""

    def test_message_role_values(self):
        """Verify all message roles exist."""
        expected = {"USER", "ASSISTANT", "SYSTEM"}
        actual = {r.name for r in MessageRole}
        assert actual == expected


class TestExecutionStrategyEnum:
    """Test ExecutionStrategy enum values."""

    def test_execution_strategy_values(self):
        """Verify all execution strategies exist."""
        expected = {"SEQUENTIAL", "PARALLEL", "CONDITIONAL", "USER_CHOICE"}
        actual = {s.name for s in ExecutionStrategy}
        assert actual == expected


class TestDependencyTypeEnum:
    """Test DependencyType enum values."""

    def test_dependency_type_values(self):
        """Verify all dependency types exist."""
        expected = {"REQUIRES_COMPLETION", "REQUIRES_SUCCESS", "SHARES_PARAMETER"}
        actual = {d.name for d in DependencyType}
        assert actual == expected


class TestVerbosityPreferenceEnum:
    """Test VerbosityPreference enum values."""

    def test_verbosity_preference_values(self):
        """Verify all verbosity preferences exist."""
        expected = {"BRIEF", "STANDARD", "DETAILED"}
        actual = {v.name for v in VerbosityPreference}
        assert actual == expected


class TestIntent:
    """Test Intent type creation."""

    def test_create_simple_intent(self):
        """Test creating a simple intent."""
        intent = Intent(
            intent_name="Create Task",
            intent_category=IntentCategory.CREATE,
            target_component="create-task",
            action_verb="create",
        )

        assert intent.intent_name == "Create Task"
        assert intent.intent_category == IntentCategory.CREATE
        assert intent.target_component == "create-task"
        assert intent.action_verb == "create"

    def test_create_query_intent(self):
        """Test creating a query intent."""
        intent = Intent(
            intent_name="Search Products",
            intent_category=IntentCategory.QUERY,
            target_component="search-products",
            action_verb="search",
        )

        assert intent.intent_category == IntentCategory.QUERY
        assert intent.action_verb == "search"


class TestExtractedParameter:
    """Test ExtractedParameter type creation."""

    def test_create_extracted_parameter(self):
        """Test creating an extracted parameter."""
        param = ExtractedParameter(
            parameter_name="title",
            extracted_value="Review PR #42",
            source_text="called Review PR #42",
            confidence=0.95,
        )

        assert param.parameter_name == "title"
        assert param.extracted_value == "Review PR #42"
        assert param.source_text == "called Review PR #42"
        assert param.confidence == 0.95

    def test_create_parameter_without_source(self):
        """Test creating a parameter without source text."""
        param = ExtractedParameter(
            parameter_name="assignee",
            extracted_value="John",
            source_text=None,
            confidence=0.8,
        )

        assert param.parameter_name == "assignee"
        assert param.source_text is None


class TestAmbiguityInfo:
    """Test AmbiguityInfo type creation."""

    def test_create_ambiguous_info(self):
        """Test creating ambiguity information."""
        intent1 = Intent(
            intent_name="Create Task",
            intent_category=IntentCategory.CREATE,
            target_component="create-task",
            action_verb="create",
        )
        intent2 = Intent(
            intent_name="Create Note",
            intent_category=IntentCategory.CREATE,
            target_component="create-note",
            action_verb="create",
        )

        ambiguity = AmbiguityInfo(
            is_ambiguous=True,
            possible_intents=[intent1, intent2],
            disambiguation_question="Did you want to create a task or a note?",
        )

        assert ambiguity.is_ambiguous is True
        assert len(ambiguity.possible_intents) == 2
        assert "task or a note" in ambiguity.disambiguation_question

    def test_create_non_ambiguous_info(self):
        """Test creating non-ambiguous info."""
        ambiguity = AmbiguityInfo(
            is_ambiguous=False,
            possible_intents=[],
            disambiguation_question="",
        )

        assert ambiguity.is_ambiguous is False
        assert len(ambiguity.possible_intents) == 0


class TestIntentExtraction:
    """Test IntentExtraction type creation."""

    def test_create_clear_intent_extraction(self):
        """Test creating a clear intent extraction result."""
        intent = Intent(
            intent_name="Create Task",
            intent_category=IntentCategory.CREATE,
            target_component="create-task",
            action_verb="create",
        )
        param = ExtractedParameter(
            parameter_name="title",
            extracted_value="Review code",
            source_text="called Review code",
            confidence=0.9,
        )

        extraction = IntentExtraction(
            detected_intent=intent,
            confidence=0.95,
            extracted_parameters=[param],
            ambiguity=None,
            suggested_clarification=None,
        )

        assert extraction.confidence == 0.95
        assert extraction.detected_intent.intent_name == "Create Task"
        assert len(extraction.extracted_parameters) == 1
        assert extraction.ambiguity is None

    def test_create_ambiguous_intent_extraction(self):
        """Test creating an ambiguous intent extraction."""
        intent = Intent(
            intent_name="Create Item",
            intent_category=IntentCategory.CREATE,
            target_component="create-task",
            action_verb="create",
        )
        ambiguity = AmbiguityInfo(
            is_ambiguous=True,
            possible_intents=[intent],
            disambiguation_question="What type of item?",
        )

        extraction = IntentExtraction(
            detected_intent=intent,
            confidence=0.5,
            extracted_parameters=[],
            ambiguity=ambiguity,
            suggested_clarification="Could you specify what type of item you want to create?",
        )

        assert extraction.confidence == 0.5
        assert extraction.ambiguity is not None
        assert extraction.ambiguity.is_ambiguous is True
        assert extraction.suggested_clarification is not None


class TestConversationContext:
    """Test ConversationContext type creation."""

    def test_create_simple_context(self):
        """Test creating a simple conversation context."""
        message = ConversationMessage(
            role=MessageRole.USER,
            content="Show me task #123",
            timestamp="2025-01-15T10:00:00Z",
            extracted_intent=None,
        )

        context = ConversationContext(
            recent_messages=[message],
            current_state="viewing-tasks",
            active_entity="task-123",
            user_preferences=None,
        )

        assert len(context.recent_messages) == 1
        assert context.current_state == "viewing-tasks"
        assert context.active_entity == "task-123"

    def test_create_context_with_preferences(self):
        """Test creating context with user preferences."""
        prefs = UserPreferences(
            preferred_language="en-US",
            verbosity_preference=VerbosityPreference.BRIEF,
            shortcuts={"new": "create-task", "done": "complete-task"},
        )

        context = ConversationContext(
            recent_messages=[],
            current_state=None,
            active_entity=None,
            user_preferences=prefs,
        )

        assert context.user_preferences is not None
        assert context.user_preferences.preferred_language == "en-US"
        assert context.user_preferences.verbosity_preference == VerbosityPreference.BRIEF


class TestMultiIntentExtraction:
    """Test MultiIntentExtraction type creation."""

    def test_create_sequential_multi_intent(self):
        """Test creating a sequential multi-intent extraction."""
        intent1 = Intent(
            intent_name="Create Task",
            intent_category=IntentCategory.CREATE,
            target_component="create-task",
            action_verb="create",
        )
        intent2 = Intent(
            intent_name="Assign Task",
            intent_category=IntentCategory.UPDATE,
            target_component="assign-task",
            action_verb="assign",
        )

        extraction1 = IntentExtraction(
            detected_intent=intent1,
            confidence=0.9,
            extracted_parameters=[],
            ambiguity=None,
            suggested_clarification=None,
        )
        extraction2 = IntentExtraction(
            detected_intent=intent2,
            confidence=0.85,
            extracted_parameters=[],
            ambiguity=None,
            suggested_clarification=None,
        )

        dependency = IntentDependency(
            dependent_intent_index=1,
            depends_on_index=0,
            dependency_type=DependencyType.REQUIRES_SUCCESS,
        )

        multi = MultiIntentExtraction(
            intents=[extraction1, extraction2],
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
            dependencies=[dependency],
        )

        assert len(multi.intents) == 2
        assert multi.execution_strategy == ExecutionStrategy.SEQUENTIAL
        assert multi.dependencies is not None
        assert len(multi.dependencies) == 1
        assert multi.dependencies[0].dependency_type == DependencyType.REQUIRES_SUCCESS

    def test_create_parallel_multi_intent(self):
        """Test creating a parallel multi-intent extraction."""
        intent1 = Intent(
            intent_name="Search Products",
            intent_category=IntentCategory.QUERY,
            target_component="search-products",
            action_verb="search",
        )
        intent2 = Intent(
            intent_name="Search Orders",
            intent_category=IntentCategory.QUERY,
            target_component="search-orders",
            action_verb="search",
        )

        extraction1 = IntentExtraction(
            detected_intent=intent1,
            confidence=0.9,
            extracted_parameters=[],
            ambiguity=None,
            suggested_clarification=None,
        )
        extraction2 = IntentExtraction(
            detected_intent=intent2,
            confidence=0.9,
            extracted_parameters=[],
            ambiguity=None,
            suggested_clarification=None,
        )

        multi = MultiIntentExtraction(
            intents=[extraction1, extraction2],
            execution_strategy=ExecutionStrategy.PARALLEL,
            dependencies=None,
        )

        assert multi.execution_strategy == ExecutionStrategy.PARALLEL
        assert multi.dependencies is None


class TestRoutingResult:
    """Test RoutingResult type creation."""

    def test_create_ready_routing_result(self):
        """Test creating a routing result ready for execution."""
        match = ComponentMatch(
            component_id="create-task",
            component_type=LUIComponentType.ACTION,
            match_confidence=0.95,
            match_reason="Direct match to 'create task' invocation",
        )

        param = ExtractedParameter(
            parameter_name="title",
            extracted_value="Review code",
            source_text=None,
            confidence=0.9,
        )

        binding = ParameterBinding(
            parameter_name="title",
            bound_value="Review code",
            source=param,
            requires_validation=False,
        )

        result = RoutingResult(
            matched_component=match,
            parameter_bindings=[binding],
            missing_required=None,
            execution_ready=True,
        )

        assert result.execution_ready is True
        assert result.matched_component.component_id == "create-task"
        assert len(result.parameter_bindings) == 1
        assert result.missing_required is None

    def test_create_incomplete_routing_result(self):
        """Test creating a routing result with missing parameters."""
        match = ComponentMatch(
            component_id="create-task",
            component_type=LUIComponentType.ACTION,
            match_confidence=0.9,
            match_reason="Matched create intent",
        )

        missing = MissingParameter(
            parameter_name="title",
            parameter_type="string",
            prompt_for_value="What would you like to call this task?",
            has_default=False,
        )

        result = RoutingResult(
            matched_component=match,
            parameter_bindings=[],
            missing_required=[missing],
            execution_ready=False,
        )

        assert result.execution_ready is False
        assert result.missing_required is not None
        assert len(result.missing_required) == 1
        assert result.missing_required[0].parameter_name == "title"


class TestComponentMatch:
    """Test ComponentMatch type creation."""

    def test_create_high_confidence_match(self):
        """Test creating a high confidence component match."""
        match = ComponentMatch(
            component_id="search-products",
            component_type=LUIComponentType.QUERY,
            match_confidence=0.98,
            match_reason="Exact phrase match with 'search products'",
        )

        assert match.component_id == "search-products"
        assert match.component_type == LUIComponentType.QUERY
        assert match.match_confidence == 0.98

    def test_create_low_confidence_match(self):
        """Test creating a low confidence component match."""
        match = ComponentMatch(
            component_id="help",
            component_type=LUIComponentType.FEEDBACK,
            match_confidence=0.4,
            match_reason="Fallback match - no clear intent detected",
        )

        assert match.match_confidence == 0.4
        assert "Fallback" in match.match_reason


class TestIntegrationWithInterfaceSchema:
    """Test integration with InterfaceSchema types."""

    def test_create_intent_for_schema_component(self):
        """Test creating intent that targets a schema component."""
        # Create a minimal interface schema
        domain = DomainInfo(
            domain_name="task-management",
            subdomain=None,
            description="Task tracking",
            key_concepts=["tasks", "assignments"],
            terminology=None,
        )

        component = LUIComponent(
            component_id="create-task",
            component_type=LUIComponentType.ACTION,
            intent="Create a new task",
            invocation=InvocationPattern(
                primary_phrase="create task",
                alternate_phrases=["add task", "new task"],
                examples=["Create a task to review code"],
                context_requirements=None,
            ),
            parameters=[],
            feedback=FeedbackConfig(
                success_template="Task created",
                error_template="Failed",
                progress_template=None,
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
        )

        schema = InterfaceSchema(
            schema_id="task-manager-v1",
            name="Task Manager",
            description="Task management interface",
            version="1.0.0",
            domain=domain,
            components=[component],
            flows=[],
            entities=[],
            global_context=None,
        )

        # Create intent that targets the component
        intent = Intent(
            intent_name="Create Task",
            intent_category=IntentCategory.CREATE,
            target_component=schema.components[0].component_id,
            action_verb="create",
        )

        assert intent.target_component == "create-task"
        assert intent.target_component == component.component_id
