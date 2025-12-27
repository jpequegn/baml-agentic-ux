"""Core LUI Simulator implementation."""

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from baml_client import b
from baml_client.types import (
    InterfaceSchema,
    LUIComponent,
    ActionResult,
    ResultStatus,
    ResultMetadata,
    GeneratedResponse,
    ResponseType,
    IntentExtraction,
)

from .context import SimulatorContext, SimulatorConfig, SimulatorMode
from .logger import ConversationLogger


@dataclass
class SimulationResult:
    """Result of processing a user input."""

    response_text: str
    response_type: ResponseType
    intent_extracted: IntentExtraction | None = None
    action_result: ActionResult | None = None
    follow_up_suggestion: str | None = None
    processing_time_ms: int = 0
    was_ambiguous: bool = False
    required_clarification: bool = False


class LUISimulator:
    """Interactive simulator for testing LUI schemas."""

    def __init__(
        self,
        schema: InterfaceSchema,
        config: SimulatorConfig | None = None,
    ):
        """Initialize the simulator with a schema and optional config."""
        self.config = config or SimulatorConfig()
        self.context = SimulatorContext(schema=schema, config=self.config)
        log_path = Path(self.config.log_file_path) if self.config.log_to_file and self.config.log_file_path else None
        self.logger = ConversationLogger(
            session_id=self.context.session_id,
            log_file_path=log_path,
        )

        # Log session start
        self.logger.log_system(f"Simulator started with schema: {schema.name}")

    @property
    def schema(self) -> InterfaceSchema:
        """Get the loaded schema."""
        return self.context.schema

    def process_input(self, user_input: str) -> SimulationResult:
        """Process a user input and generate a response."""
        start_time = datetime.now()
        self.context.interaction_count += 1

        # Log user input
        self.logger.log_user_input(user_input)
        self.context.add_user_message(user_input)

        try:
            # Extract intent
            intent = self._extract_intent(user_input)

            if self.config.mode == SimulatorMode.VERBOSE:
                self.logger.log_debug(
                    f"Intent extracted: {intent.detected_intent.intent_name}",
                    {"confidence": intent.confidence},
                )

            # Check for ambiguity
            if intent.ambiguity and intent.ambiguity.is_ambiguous:
                clarification = intent.suggested_clarification or intent.ambiguity.disambiguation_question
                self.context.add_assistant_message(clarification)
                self.logger.log_response(clarification, "CLARIFICATION")

                return SimulationResult(
                    response_text=clarification,
                    response_type=ResponseType.CLARIFICATION,
                    intent_extracted=intent,
                    was_ambiguous=True,
                    required_clarification=True,
                    processing_time_ms=self._calc_time_ms(start_time),
                )

            # Log intent
            self.logger.log_intent(
                intent.detected_intent.intent_name,
                intent.confidence,
                intent.detected_intent.target_component,
                {p.parameter_name: p.extracted_value for p in intent.extracted_parameters},
            )

            # Get target component
            component = self._get_component(intent.detected_intent.target_component)

            if not component:
                error_response = f"I couldn't find the component '{intent.detected_intent.target_component}' to handle that request."
                self.context.add_assistant_message(error_response)
                self.logger.log_error(f"Component not found: {intent.detected_intent.target_component}")

                return SimulationResult(
                    response_text=error_response,
                    response_type=ResponseType.ERROR,
                    intent_extracted=intent,
                    processing_time_ms=self._calc_time_ms(start_time),
                )

            # Simulate action execution
            action_result = self._simulate_action(intent, component)
            self.logger.log_action(
                component.component_id,
                action_result.status.value,
                action_result.data,
            )

            # Generate response
            response = self._generate_response(action_result, component)

            # Update context
            self.context.add_assistant_message(response.response_text)
            self.context.current_state = f"after_{component.component_id}"

            # Log response
            self.logger.log_response(
                response.response_text,
                response.response_type.value,
                response.follow_up is not None,
            )

            return SimulationResult(
                response_text=response.response_text,
                response_type=response.response_type,
                intent_extracted=intent,
                action_result=action_result,
                follow_up_suggestion=response.follow_up.suggested_action if response.follow_up else None,
                processing_time_ms=self._calc_time_ms(start_time),
            )

        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.logger.log_error(error_message, e)

            return SimulationResult(
                response_text=error_message,
                response_type=ResponseType.ERROR,
                processing_time_ms=self._calc_time_ms(start_time),
            )

    def _extract_intent(self, user_input: str) -> IntentExtraction:
        """Extract intent from user input using BAML."""
        return b.ExtractIntent(
            user_input=user_input,
            interface_schema=self.schema,
            conversation_context=self.context.get_conversation_context(),
        )

    def _get_component(self, component_id: str) -> LUIComponent | None:
        """Find a component by ID in the schema."""
        for component in self.schema.components:
            if component.component_id == component_id:
                return component
        return None

    def _simulate_action(
        self,
        intent: IntentExtraction,
        component: LUIComponent,
    ) -> ActionResult:
        """Simulate executing an action based on the intent."""
        # Simulate latency if configured
        if self.config.simulate_latency:
            time.sleep(self.config.latency_ms / 1000)

        # Build simulated result based on intent
        params = {p.parameter_name: p.extracted_value for p in intent.extracted_parameters}

        # Generate simulated data based on component type
        simulated_data = self._generate_simulated_data(component, params)

        return ActionResult(
            status=ResultStatus.SUCCESS,
            data=simulated_data,
            error_message=None,
            metadata=ResultMetadata(
                timestamp=datetime.now().isoformat(),
                affected_count=1,
                warnings=None,
                debug_info=f"Simulated execution of {component.component_id}",
                related_actions=None,
            ),
            affected_entities=[f"simulated-{component.component_id}-result"],
            execution_time_ms=self.config.latency_ms if self.config.simulate_latency else 50,
        )

    def _generate_simulated_data(
        self,
        component: LUIComponent,
        params: dict[str, str],
    ) -> str:
        """Generate simulated result data based on component and parameters."""
        component_type = component.component_type.value

        if component_type == "ACTION":
            if params:
                param_str = ", ".join(f"{k}='{v}'" for k, v in params.items())
                return f"Action '{component.intent}' completed successfully with {param_str}"
            return f"Action '{component.intent}' completed successfully"

        elif component_type == "QUERY":
            return f"Found 5 results matching your query for '{component.intent}'"

        elif component_type == "NAVIGATION":
            return f"Navigated to {component.intent}"

        elif component_type == "INPUT":
            if params:
                return f"Input received: {params}"
            return "Awaiting input..."

        elif component_type == "CONFIRMATION":
            return "Confirmed"

        else:
            return f"Simulated result for {component.component_id}"

    def _generate_response(
        self,
        action_result: ActionResult,
        component: LUIComponent,
    ) -> GeneratedResponse:
        """Generate a natural language response using BAML."""
        return b.GenerateResponse(
            action_result=action_result,
            component=component,
            user_context=self.config.get_user_context(self.context.interaction_count),
            style=self.config.get_response_style(),
        )

    def _calc_time_ms(self, start_time: datetime) -> int:
        """Calculate elapsed time in milliseconds."""
        return int((datetime.now() - start_time).total_seconds() * 1000)

    def get_debug_info(self) -> dict[str, Any]:
        """Get debug information about the simulator state."""
        return {
            "context": self.context.get_debug_info(),
            "config": {
                "mode": self.config.mode.value,
                "tone": self.config.tone.value,
                "formality": self.config.formality.value,
                "simulate_latency": self.config.simulate_latency,
            },
            "log_summary": self.logger.get_summary(),
        }

    def get_transcript(self) -> str:
        """Get a transcript of the conversation."""
        return self.logger.get_conversation_transcript()

    def reset(self) -> None:
        """Reset the simulator to initial state."""
        self.context.reset()
        self.logger.log_system("Simulator reset")

    def save_session(self) -> str:
        """Save the current session and return the file path."""
        path = self.logger.save_session()
        return str(path)


def load_schema_from_dict(data: dict[str, Any]) -> InterfaceSchema:
    """Load an InterfaceSchema from a dictionary."""
    from baml_client.types import (
        DomainInfo,
        LUIComponent,
        LUIComponentType,
        InvocationPattern,
        FeedbackConfig,
    )

    # Parse domain
    domain_data = data.get("domain", {})
    domain = DomainInfo(
        domain_name=domain_data.get("domain_name", "unknown"),
        subdomain=domain_data.get("subdomain"),
        description=domain_data.get("description", ""),
        key_concepts=domain_data.get("key_concepts", []),
        terminology=None,
    )

    # Parse components
    components = []
    for comp_data in data.get("components", []):
        invocation = InvocationPattern(
            primary_phrase=comp_data.get("invocation", {}).get("primary_phrase", ""),
            alternate_phrases=comp_data.get("invocation", {}).get("alternate_phrases", []),
            examples=comp_data.get("invocation", {}).get("examples", []),
            context_requirements=None,
        )

        feedback = FeedbackConfig(
            success_template=comp_data.get("feedback", {}).get("success_template", "Done"),
            error_template=comp_data.get("feedback", {}).get("error_template", "Failed"),
            progress_template=comp_data.get("feedback", {}).get("progress_template"),
            confirmation_required=comp_data.get("feedback", {}).get("confirmation_required", False),
            confirmation_prompt=comp_data.get("feedback", {}).get("confirmation_prompt"),
        )

        component = LUIComponent(
            component_id=comp_data.get("component_id", ""),
            component_type=LUIComponentType[comp_data.get("component_type", "ACTION")],
            intent=comp_data.get("intent", ""),
            invocation=invocation,
            parameters=[],
            feedback=feedback,
            accessibility=None,
        )
        components.append(component)

    return InterfaceSchema(
        schema_id=data.get("schema_id", "unknown"),
        name=data.get("name", "Unknown Schema"),
        description=data.get("description", ""),
        version=data.get("version", "1.0.0"),
        domain=domain,
        components=components,
        flows=[],
        entities=[],
        global_context=None,
    )
