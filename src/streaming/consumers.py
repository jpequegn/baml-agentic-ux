"""
Streaming consumers for BAML functions.

Provides high-level wrappers for consuming streaming BAML responses
with progress tracking and callback support.
"""

from typing import Any, Callable, Optional, TypeVar

from baml_client import b
from baml_client import types
from baml_client import stream_types

from src.streaming.types import StreamProgress, StreamResult, PartialFieldTracker

T = TypeVar("T")
P = TypeVar("P")


async def stream_with_callback(
    stream: Any,
    on_partial: Optional[Callable[[Any], None]] = None,
    field_names: Optional[list[str]] = None,
) -> StreamResult[Any, Any]:
    """Generic streaming consumer with callback support.

    Args:
        stream: A BAML stream object
        on_partial: Optional callback for each partial result
        field_names: Optional field names to track for progress

    Returns:
        StreamResult with final result and progress info
    """
    progress = StreamProgress()
    last_partial = None

    async for partial in stream:
        progress.update(partial, field_names)
        last_partial = partial

        if on_partial:
            on_partial(partial)

    final = await stream.get_final_response()

    return StreamResult(
        final=final,
        last_partial=last_partial,
        progress=progress,
    )


async def stream_intent_extraction(
    user_input: str,
    interface_schema: types.InterfaceSchema,
    conversation_context: Optional[types.ConversationContext] = None,
    on_partial: Optional[Callable[[stream_types.IntentExtraction], None]] = None,
    on_intent_detected: Optional[Callable[[types.Intent], None]] = None,
    on_parameter_extracted: Optional[Callable[[types.ExtractedParameter], None]] = None,
) -> StreamResult[types.IntentExtraction, stream_types.IntentExtraction]:
    """Stream intent extraction with specialized callbacks.

    Args:
        user_input: User's input text
        interface_schema: Available components
        conversation_context: Optional conversation context
        on_partial: General callback for each partial
        on_intent_detected: Callback when intent is first detected
        on_parameter_extracted: Callback for each new parameter

    Returns:
        StreamResult with complete IntentExtraction and progress info
    """
    stream = b.stream.ExtractIntent(
        user_input=user_input,
        interface_schema=interface_schema,
        conversation_context=conversation_context,
    )

    progress = StreamProgress()
    last_partial: Optional[stream_types.IntentExtraction] = None
    tracker = PartialFieldTracker()
    seen_params: set[str] = set()

    async for partial in stream:
        progress.update(
            partial,
            ["detected_intent", "confidence", "extracted_parameters", "ambiguity"],
        )
        last_partial = partial

        changes = tracker.update(partial)

        # Call specialized callbacks
        if on_intent_detected and "detected_intent" in changes.new_fields:
            if partial.detected_intent:
                on_intent_detected(partial.detected_intent)

        if on_parameter_extracted and partial.extracted_parameters:
            for param in partial.extracted_parameters:
                param_key = f"{param.parameter_name}:{param.extracted_value}"
                if param_key not in seen_params:
                    seen_params.add(param_key)
                    on_parameter_extracted(param)

        if on_partial:
            on_partial(partial)

    final = await stream.get_final_response()

    return StreamResult(
        final=final,
        last_partial=last_partial,
        progress=progress,
    )


async def stream_multiple_intents(
    user_input: str,
    interface_schema: types.InterfaceSchema,
    conversation_context: Optional[types.ConversationContext] = None,
    on_partial: Optional[
        Callable[[stream_types.MultiIntentExtraction], None]
    ] = None,
    on_strategy_detected: Optional[Callable[[types.ExecutionStrategy], None]] = None,
    on_intent_added: Optional[Callable[[types.IntentExtraction, int], None]] = None,
) -> StreamResult[types.MultiIntentExtraction, stream_types.MultiIntentExtraction]:
    """Stream multi-intent extraction with specialized callbacks.

    Args:
        user_input: User's input text
        interface_schema: Available components
        conversation_context: Optional conversation context
        on_partial: General callback for each partial
        on_strategy_detected: Callback when execution strategy is determined
        on_intent_added: Callback when a new intent is fully detected (intent, index)

    Returns:
        StreamResult with complete MultiIntentExtraction and progress info
    """
    stream = b.stream.ExtractMultipleIntents(
        user_input=user_input,
        interface_schema=interface_schema,
        conversation_context=conversation_context,
    )

    progress = StreamProgress()
    last_partial: Optional[stream_types.MultiIntentExtraction] = None
    tracker = PartialFieldTracker()
    seen_intent_count = 0

    async for partial in stream:
        progress.update(
            partial,
            ["execution_strategy", "intents", "dependencies"],
        )
        last_partial = partial

        changes = tracker.update(partial)

        # Call specialized callbacks
        if on_strategy_detected and "execution_strategy" in changes.new_fields:
            if partial.execution_strategy:
                on_strategy_detected(partial.execution_strategy)

        if on_intent_added and partial.intents:
            current_count = len(partial.intents)
            for i in range(seen_intent_count, current_count):
                intent = partial.intents[i]
                # Check if intent is complete (has detected_intent)
                if intent.detected_intent:
                    on_intent_added(intent, i)
            seen_intent_count = current_count

        if on_partial:
            on_partial(partial)

    final = await stream.get_final_response()

    return StreamResult(
        final=final,
        last_partial=last_partial,
        progress=progress,
    )


async def stream_response_generation(
    action_result: types.ActionResult,
    component: types.LUIComponent,
    style: types.ResponseStyle,
    user_context: Optional[types.UserContext] = None,
    on_partial: Optional[Callable[[stream_types.GeneratedResponse], None]] = None,
    on_response_type_known: Optional[Callable[[types.ResponseType], None]] = None,
    on_text_chunk: Optional[Callable[[str], None]] = None,
) -> StreamResult[types.GeneratedResponse, stream_types.GeneratedResponse]:
    """Stream response generation with specialized callbacks.

    Args:
        action_result: The result of the action
        component: The LUI component
        style: Response style settings
        user_context: Optional user context
        on_partial: General callback for each partial
        on_response_type_known: Callback when response type is determined
        on_text_chunk: Callback for each new text chunk (incremental text)

    Returns:
        StreamResult with complete GeneratedResponse and progress info
    """
    stream = b.stream.GenerateResponse(
        action_result=action_result,
        component=component,
        style=style,
        user_context=user_context,
    )

    progress = StreamProgress()
    last_partial: Optional[stream_types.GeneratedResponse] = None
    tracker = PartialFieldTracker()
    last_text_length = 0

    async for partial in stream:
        progress.update(
            partial,
            ["response_type", "response_text", "follow_up", "visual_elements"],
        )
        last_partial = partial

        changes = tracker.update(partial)

        # Call specialized callbacks
        if on_response_type_known and "response_type" in changes.new_fields:
            if partial.response_type:
                on_response_type_known(partial.response_type)

        if on_text_chunk and partial.response_text:
            new_text = partial.response_text[last_text_length:]
            if new_text:
                on_text_chunk(new_text)
                last_text_length = len(partial.response_text)

        if on_partial:
            on_partial(partial)

    final = await stream.get_final_response()

    return StreamResult(
        final=final,
        last_partial=last_partial,
        progress=progress,
    )


async def stream_usability_analysis(
    schema: types.InterfaceSchema,
    target_users: Optional[list[types.UserPersona]] = None,
    on_partial: Optional[Callable[[stream_types.UsabilityAnalysis], None]] = None,
    on_grade_known: Optional[Callable[[types.UsabilityGrade], None]] = None,
    on_issue_found: Optional[Callable[[types.UsabilityIssue], None]] = None,
    on_recommendation_added: Optional[
        Callable[[types.UsabilityRecommendation], None]
    ] = None,
) -> StreamResult[types.UsabilityAnalysis, stream_types.UsabilityAnalysis]:
    """Stream usability analysis with specialized callbacks.

    Args:
        schema: The interface schema to analyze
        target_users: Optional target user personas
        on_partial: General callback for each partial
        on_grade_known: Callback when grade is determined
        on_issue_found: Callback for each new issue found
        on_recommendation_added: Callback for each new recommendation

    Returns:
        StreamResult with complete UsabilityAnalysis and progress info
    """
    stream = b.stream.AnalyzeLUIUsability(
        schema=schema,
        target_users=target_users,
    )

    progress = StreamProgress()
    last_partial: Optional[stream_types.UsabilityAnalysis] = None
    tracker = PartialFieldTracker()
    seen_issues: set[str] = set()
    seen_recommendations: set[str] = set()

    async for partial in stream:
        progress.update(
            partial,
            ["grade", "overall_score", "issues", "recommendations", "summary"],
        )
        last_partial = partial

        changes = tracker.update(partial)

        # Call specialized callbacks
        if on_grade_known and "grade" in changes.new_fields:
            if partial.grade:
                on_grade_known(partial.grade)

        if on_issue_found and partial.issues:
            for issue in partial.issues:
                if issue.issue_id and issue.issue_id not in seen_issues:
                    seen_issues.add(issue.issue_id)
                    on_issue_found(issue)

        if on_recommendation_added and partial.recommendations:
            for rec in partial.recommendations:
                if rec.recommendation_id and rec.recommendation_id not in seen_recommendations:
                    seen_recommendations.add(rec.recommendation_id)
                    on_recommendation_added(rec)

        if on_partial:
            on_partial(partial)

    final = await stream.get_final_response()

    return StreamResult(
        final=final,
        last_partial=last_partial,
        progress=progress,
    )
