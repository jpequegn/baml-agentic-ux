"""Tests for Interface Schema Types."""

import pytest
from baml_client.types import (
    # Interface Schema types
    InterfaceSchema,
    DomainInfo,
    Terminology,
    GlobalContext,
    RateLimitConfig,
    # Conversational Flow types
    ConversationalFlow,
    FlowStep,
    FlowStepType,
    ActionConfig,
    ParameterMapping,
    ParameterSourceType,
    BranchConfig,
    BranchCondition,
    BranchEvaluationType,
    StepTransition,
    StepErrorHandling,
    ErrorAction,
    FlowExecutionState,
    FlowContext,
    FlowHistoryEntry,
    FlowStatus,
    # Entity types
    EntityDefinition,
    EntityType,
    EntityAttribute,
    AttributeType,
    AttributeConstraint,
    ConstraintType,
    AttributeDisplayConfig,
    InputType,
    EntityRelationship,
    RelationshipType,
    EntityValidation,
    ValidationSeverity,
    EntityExample,
    EntityInstance,
    # Validation types
    SchemaValidationResult,
    SchemaError,
    SchemaWarning,
    # LUI types from previous issue
    LUIComponent,
    LUIComponentType,
    InvocationPattern,
    FeedbackConfig,
    ContextRequirement,
    ContextType,
)


class TestInterfaceSchemaTypes:
    """Test interface schema type definitions."""

    def test_flow_step_type_enum_values(self):
        """Verify all expected flow step types exist."""
        expected_types = {
            "PROMPT",
            "ACTION",
            "BRANCH",
            "CONFIRM",
            "VALIDATE",
            "TRANSFORM",
            "COMPLETE",
            "CANCEL",
        }
        actual_types = {t.name for t in FlowStepType}
        assert actual_types == expected_types

    def test_entity_type_enum_values(self):
        """Verify all expected entity types exist."""
        expected_types = {
            "USER",
            "RESOURCE",
            "ACTION",
            "STATE",
            "CONFIGURATION",
            "EVENT",
            "AGGREGATE",
        }
        actual_types = {t.name for t in EntityType}
        assert actual_types == expected_types

    def test_relationship_type_enum_values(self):
        """Verify all expected relationship types exist."""
        expected_types = {
            "ONE_TO_ONE",
            "ONE_TO_MANY",
            "MANY_TO_ONE",
            "MANY_TO_MANY",
        }
        actual_types = {t.name for t in RelationshipType}
        assert actual_types == expected_types

    def test_flow_status_enum_values(self):
        """Verify all expected flow status values exist."""
        expected_statuses = {
            "ACTIVE",
            "WAITING_USER_INPUT",
            "PROCESSING",
            "COMPLETED",
            "CANCELLED",
            "TIMED_OUT",
            "ERROR",
        }
        actual_statuses = {s.name for s in FlowStatus}
        assert actual_statuses == expected_statuses


class TestDomainInfo:
    """Test DomainInfo creation."""

    def test_create_domain_info(self):
        """Test creating domain information."""
        term = Terminology(
            term="SKU",
            definition="Stock Keeping Unit - unique product identifier",
            synonyms=["product code", "item number"],
            usage_examples=["The SKU for this item is ABC-123"],
        )

        domain = DomainInfo(
            domain_name="e-commerce",
            subdomain="inventory-management",
            description="Managing product inventory for online store",
            key_concepts=["products", "stock levels", "warehouses", "orders"],
            terminology=[term],
        )

        assert domain.domain_name == "e-commerce"
        assert domain.subdomain == "inventory-management"
        assert len(domain.key_concepts) == 4
        assert domain.terminology is not None
        assert len(domain.terminology) == 1


class TestGlobalContext:
    """Test GlobalContext creation."""

    def test_create_global_context(self):
        """Test creating global context."""
        rate_limits = RateLimitConfig(
            requests_per_minute=60,
            requests_per_hour=1000,
            burst_limit=10,
        )

        ctx = GlobalContext(
            supported_locales=["en-US", "es-ES", "fr-FR"],
            default_locale="en-US",
            timezone="America/New_York",
            currency="USD",
            authentication_required=True,
            rate_limits=rate_limits,
            feature_flags=["new-checkout", "beta-search"],
        )

        assert ctx.default_locale == "en-US"
        assert ctx.authentication_required is True
        assert ctx.rate_limits is not None
        assert ctx.rate_limits.requests_per_minute == 60


class TestConversationalFlow:
    """Test ConversationalFlow creation."""

    def test_create_simple_flow(self):
        """Test creating a simple conversational flow."""
        transition = StepTransition(
            transition_id="t1",
            condition=None,
            next_step="step-2",
            transition_message="Great! Let me help you with that.",
        )

        step1 = FlowStep(
            step_id="step-1",
            step_type=FlowStepType.PROMPT,
            component_ref=None,
            prompt_template="What would you like to search for?",
            action_config=None,
            branch_config=None,
            transitions=[transition],
            error_handling=None,
        )

        step2 = FlowStep(
            step_id="step-2",
            step_type=FlowStepType.ACTION,
            component_ref="search-products",
            prompt_template=None,
            action_config=ActionConfig(
                component_id="search-products",
                parameter_mapping=[
                    ParameterMapping(
                        parameter_name="query",
                        source_type=ParameterSourceType.USER_INPUT,
                        source_value="$last_input",
                    )
                ],
                store_result_as="search_results",
                retry_on_failure=True,
                max_retries=2,
            ),
            branch_config=None,
            transitions=[
                StepTransition(
                    transition_id="t2",
                    condition=None,
                    next_step="step-3",
                    transition_message=None,
                )
            ],
            error_handling=StepErrorHandling(
                on_error=ErrorAction.ASK_USER,
                retry_count=2,
                fallback_step=None,
                error_message_template="Sorry, I couldn't complete the search. Would you like to try again?",
            ),
        )

        step3 = FlowStep(
            step_id="step-3",
            step_type=FlowStepType.COMPLETE,
            component_ref=None,
            prompt_template="Here are your results: {search_results}",
            action_config=None,
            branch_config=None,
            transitions=[],
            error_handling=None,
        )

        flow = ConversationalFlow(
            flow_id="product-search",
            name="Product Search Flow",
            description="Helps users search for products",
            trigger_intents=["search products", "find items", "look for"],
            entry_conditions=None,
            steps=[step1, step2, step3],
            fallback_responses=[
                "I'm sorry, I didn't understand. Could you rephrase?",
                "Let me connect you with a human agent.",
            ],
            timeout_seconds=300,
            on_timeout_action="cancel",
        )

        assert flow.flow_id == "product-search"
        assert len(flow.steps) == 3
        assert flow.steps[0].step_type == FlowStepType.PROMPT
        assert flow.steps[1].step_type == FlowStepType.ACTION
        assert flow.steps[2].step_type == FlowStepType.COMPLETE

    def test_create_branching_flow(self):
        """Test creating a flow with branching logic."""
        branch_config = BranchConfig(
            evaluation_type=BranchEvaluationType.FIRST_MATCH,
            conditions=[
                BranchCondition(
                    condition_id="c1",
                    expression="user.is_premium == true",
                    description="User is a premium member",
                    target_step="premium-path",
                ),
                BranchCondition(
                    condition_id="c2",
                    expression="cart.total > 100",
                    description="Large order discount eligible",
                    target_step="discount-path",
                ),
            ],
            default_transition="standard-path",
        )

        step = FlowStep(
            step_id="check-eligibility",
            step_type=FlowStepType.BRANCH,
            component_ref=None,
            prompt_template=None,
            action_config=None,
            branch_config=branch_config,
            transitions=[],
            error_handling=None,
        )

        assert step.step_type == FlowStepType.BRANCH
        assert step.branch_config is not None
        assert len(step.branch_config.conditions) == 2
        assert step.branch_config.evaluation_type == BranchEvaluationType.FIRST_MATCH


class TestEntityDefinition:
    """Test EntityDefinition creation."""

    def test_create_entity_definition(self):
        """Test creating an entity definition."""
        attributes = [
            EntityAttribute(
                attribute_name="name",
                attribute_type=AttributeType.STRING,
                description="Full name of the customer",
                required=True,
                default_value=None,
                constraints=[
                    AttributeConstraint(
                        constraint_type=ConstraintType.MIN_LENGTH,
                        value="2",
                        error_message="Name must be at least 2 characters",
                    ),
                    AttributeConstraint(
                        constraint_type=ConstraintType.MAX_LENGTH,
                        value="100",
                        error_message="Name cannot exceed 100 characters",
                    ),
                ],
                display_config=AttributeDisplayConfig(
                    display_name="Customer Name",
                    placeholder="Enter full name",
                    help_text="First and last name",
                    input_type=InputType.TEXT,
                    display_order=1,
                    group_name="basic-info",
                ),
            ),
            EntityAttribute(
                attribute_name="email",
                attribute_type=AttributeType.EMAIL,
                description="Customer email address",
                required=True,
                default_value=None,
                constraints=None,
                display_config=None,
            ),
            EntityAttribute(
                attribute_name="status",
                attribute_type=AttributeType.ENUM,
                description="Customer account status",
                required=True,
                default_value="active",
                constraints=[
                    AttributeConstraint(
                        constraint_type=ConstraintType.ENUM_VALUES,
                        value="active,inactive,suspended",
                        error_message="Invalid status value",
                    )
                ],
                display_config=None,
            ),
        ]

        relationships = [
            EntityRelationship(
                relationship_name="orders",
                relationship_type=RelationshipType.ONE_TO_MANY,
                target_entity="Order",
                inverse_name="customer",
                required=False,
                cascade_delete=False,
                description="Orders placed by this customer",
            )
        ]

        validations = [
            EntityValidation(
                validation_name="valid-email-domain",
                expression="email.endsWith('@company.com') or !is_employee",
                error_message="Employees must use company email",
                severity=ValidationSeverity.ERROR,
            )
        ]

        examples = [
            EntityExample(
                example_name="regular-customer",
                description="A typical active customer",
                attribute_values={
                    "name": "John Smith",
                    "email": "john@example.com",
                    "status": "active",
                },
                use_case="Standard customer lookup",
            )
        ]

        entity = EntityDefinition(
            entity_name="Customer",
            entity_type=EntityType.USER,
            description="A customer who can place orders",
            attributes=attributes,
            relationships=relationships,
            validations=validations,
            examples=examples,
        )

        assert entity.entity_name == "Customer"
        assert entity.entity_type == EntityType.USER
        assert len(entity.attributes) == 3
        assert len(entity.relationships) == 1
        assert entity.relationships[0].relationship_type == RelationshipType.ONE_TO_MANY


class TestFlowExecutionState:
    """Test flow execution state tracking."""

    def test_create_flow_execution_state(self):
        """Test creating a flow execution state."""
        context = FlowContext(
            variables={"query": "laptop", "category": "electronics"},
            user_inputs=["I want to find a laptop", "Something under $1000"],
            extracted_entities=[],
        )

        history = [
            FlowHistoryEntry(
                step_id="step-1",
                timestamp="2025-01-15T10:30:00Z",
                action_taken="prompted user for search query",
                result="received: laptop",
            ),
            FlowHistoryEntry(
                step_id="step-2",
                timestamp="2025-01-15T10:30:05Z",
                action_taken="executed search",
                result="found 15 results",
            ),
        ]

        state = FlowExecutionState(
            flow_id="product-search",
            current_step_id="step-3",
            started_at="2025-01-15T10:29:55Z",
            context=context,
            history=history,
            status=FlowStatus.ACTIVE,
        )

        assert state.flow_id == "product-search"
        assert state.status == FlowStatus.ACTIVE
        assert len(state.history) == 2
        assert state.context.variables["query"] == "laptop"


class TestInterfaceSchemaCreation:
    """Test complete InterfaceSchema creation."""

    def test_create_minimal_interface_schema(self):
        """Test creating a minimal interface schema."""
        domain = DomainInfo(
            domain_name="task-management",
            subdomain=None,
            description="Simple task tracking",
            key_concepts=["tasks", "projects", "deadlines"],
            terminology=None,
        )

        # Create a simple component
        component = LUIComponent(
            component_id="create-task",
            component_type=LUIComponentType.ACTION,
            intent="Create a new task",
            invocation=InvocationPattern(
                primary_phrase="create task",
                alternate_phrases=["add task", "new task"],
                examples=["Create a task to review the document"],
                context_requirements=None,
            ),
            parameters=[],
            feedback=FeedbackConfig(
                success_template="Task created successfully",
                error_template="Failed to create task: {error}",
                progress_template=None,
                confirmation_required=False,
                confirmation_prompt=None,
            ),
            accessibility=None,
        )

        # Create a simple flow
        flow = ConversationalFlow(
            flow_id="quick-add-task",
            name="Quick Add Task",
            description=None,
            trigger_intents=["add task", "create task"],
            entry_conditions=None,
            steps=[
                FlowStep(
                    step_id="get-title",
                    step_type=FlowStepType.PROMPT,
                    component_ref=None,
                    prompt_template="What would you like to name the task?",
                    action_config=None,
                    branch_config=None,
                    transitions=[],
                    error_handling=None,
                )
            ],
            fallback_responses=["I didn't catch that. What's the task name?"],
            timeout_seconds=None,
            on_timeout_action=None,
        )

        # Create a simple entity
        entity = EntityDefinition(
            entity_name="Task",
            entity_type=EntityType.RESOURCE,
            description="A task to be completed",
            attributes=[
                EntityAttribute(
                    attribute_name="title",
                    attribute_type=AttributeType.STRING,
                    description="Task title",
                    required=True,
                    default_value=None,
                    constraints=None,
                    display_config=None,
                )
            ],
            relationships=[],
            validations=None,
            examples=None,
        )

        schema = InterfaceSchema(
            schema_id="task-manager-v1",
            name="Task Manager",
            description="Simple task management interface",
            version="1.0.0",
            domain=domain,
            components=[component],
            flows=[flow],
            entities=[entity],
            global_context=None,
        )

        assert schema.schema_id == "task-manager-v1"
        assert schema.version == "1.0.0"
        assert len(schema.components) == 1
        assert len(schema.flows) == 1
        assert len(schema.entities) == 1
        assert schema.domain.domain_name == "task-management"


class TestSchemaValidation:
    """Test schema validation types."""

    def test_create_validation_result(self):
        """Test creating a schema validation result."""
        error = SchemaError(
            error_code="MISSING_COMPONENT",
            message="Flow references non-existent component 'send-email'",
            location="flows[0].steps[2].component_ref",
            severity="error",
        )

        warning = SchemaWarning(
            warning_code="MISSING_FALLBACK",
            message="Flow has no fallback responses",
            location="flows[1]",
            suggestion="Add at least one fallback response",
        )

        result = SchemaValidationResult(
            is_valid=False,
            errors=[error],
            warnings=[warning],
            suggestions=[
                "Consider adding more alternate phrases to components",
                "Add entity examples for better agent understanding",
            ],
            coverage_score=0.75,
        )

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert result.coverage_score == 0.75
