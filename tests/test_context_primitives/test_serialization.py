"""
Tests for Context Serialization

Tests round-trip serialization for all formats and performance benchmarks.

Part of Phase 7: BAML Context Primitives Implementation
Issue #105 - Task 7.5: Context Serialization
"""

import gzip
import json
import time
import pytest
from datetime import datetime, timezone, timedelta

from src.context_primitives.provider import (
    ExecutionContext,
    SessionContext,
    ConversationHistory,
    ConversationTurn,
    ContextVariables,
    ContextValue,
    ContextValueType,
)
from src.context_primitives.serialization import (
    SerializationFormat,
    ContextSerializer,
    JSONSerializer,
    CompressedSerializer,
    SerializerFactory,
    create_serializer,
)


def create_test_context(
    num_turns: int = 5,
    num_variables: int = 3,
    with_metadata: bool = True,
) -> ExecutionContext:
    """Create a test ExecutionContext with specified complexity."""
    now = datetime.now(timezone.utc)

    session = SessionContext(
        session_id="test_session_123",
        user_id="user_456",
        created_at=now - timedelta(hours=1),
        last_activity=now,
        metadata={"channel": "web", "locale": "en-US"} if with_metadata else {},
        ttl_seconds=3600,
        is_active=True,
    )

    turns = []
    for i in range(num_turns):
        turn = ConversationTurn(
            turn_id=i + 1,
            timestamp=now - timedelta(minutes=num_turns - i),
            user_input=f"User question {i + 1}",
            assistant_response=f"Assistant answer {i + 1} with some longer text to simulate real responses.",
            detected_intent=f"intent_{i % 3}",
            extracted_entities={"entity_a": f"value_{i}", "entity_b": str(i * 10)},
            confidence=0.85 + (i * 0.02),
            component_id=f"component_{i % 2}",
            duration_ms=100 + i * 50,
        )
        turns.append(turn)

    history = ConversationHistory(
        session_id="test_session_123",
        turns=turns,
        max_turns=20,
        total_turns=num_turns,
        summary="Previous conversation about scheduling and tasks.",
        summary_updated_at=now - timedelta(minutes=30),
        token_count=500,
    )

    variables = ContextVariables(
        session_id="test_session_123",
        updated_at=now,
    )
    for i in range(num_variables):
        if i % 4 == 0:
            variables.set(f"var_{i}", f"string_value_{i}")
        elif i % 4 == 1:
            variables.set(f"var_{i}", i * 100)
        elif i % 4 == 2:
            variables.set(f"var_{i}", i % 2 == 0)
        else:
            variables.set(f"var_{i}", {"nested": f"object_{i}", "count": i})

    return ExecutionContext(
        session=session,
        history=history,
        variables=variables,
        current_intent="test_intent",
        current_entities={"key": "value"},
    )


class TestJSONSerializer:
    """Tests for JSONSerializer."""

    def test_serialize_returns_bytes(self):
        """Test that serialize returns bytes."""
        serializer = JSONSerializer()
        context = create_test_context()

        result = serializer.serialize(context)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_deserialize_returns_context(self):
        """Test that deserialize returns ExecutionContext."""
        serializer = JSONSerializer()
        context = create_test_context()

        data = serializer.serialize(context)
        result = serializer.deserialize(data)

        assert isinstance(result, ExecutionContext)

    def test_round_trip_preserves_session(self):
        """Test that session data survives round-trip."""
        serializer = JSONSerializer()
        context = create_test_context()

        data = serializer.serialize(context)
        restored = serializer.deserialize(data)

        assert restored.session.session_id == context.session.session_id
        assert restored.session.user_id == context.session.user_id
        assert restored.session.ttl_seconds == context.session.ttl_seconds
        assert restored.session.is_active == context.session.is_active
        assert restored.session.metadata == context.session.metadata

    def test_round_trip_preserves_history(self):
        """Test that history data survives round-trip."""
        serializer = JSONSerializer()
        context = create_test_context(num_turns=10)

        data = serializer.serialize(context)
        restored = serializer.deserialize(data)

        assert len(restored.history.turns) == len(context.history.turns)
        assert restored.history.total_turns == context.history.total_turns
        assert restored.history.summary == context.history.summary
        assert restored.history.token_count == context.history.token_count

        # Check individual turns
        for i, (orig, rest) in enumerate(
            zip(context.history.turns, restored.history.turns)
        ):
            assert rest.turn_id == orig.turn_id, f"Turn {i} turn_id mismatch"
            assert rest.user_input == orig.user_input, f"Turn {i} user_input mismatch"
            assert (
                rest.assistant_response == orig.assistant_response
            ), f"Turn {i} assistant_response mismatch"
            assert (
                rest.detected_intent == orig.detected_intent
            ), f"Turn {i} detected_intent mismatch"
            assert (
                rest.extracted_entities == orig.extracted_entities
            ), f"Turn {i} extracted_entities mismatch"

    def test_round_trip_preserves_variables(self):
        """Test that variables data survives round-trip."""
        serializer = JSONSerializer()
        context = create_test_context(num_variables=10)

        data = serializer.serialize(context)
        restored = serializer.deserialize(data)

        # Check all variable keys exist
        orig_keys = set(context.variables.keys())
        rest_keys = set(restored.variables.keys())
        assert rest_keys == orig_keys

        # Check variable values
        for key in orig_keys:
            orig_val = context.variables.get(key)
            rest_val = restored.variables.get(key)
            assert rest_val == orig_val, f"Variable {key} mismatch"

    def test_round_trip_preserves_datetime(self):
        """Test that datetime objects are correctly serialized and restored."""
        serializer = JSONSerializer()
        context = create_test_context()

        data = serializer.serialize(context)
        restored = serializer.deserialize(data)

        # Session datetimes
        assert restored.session.created_at == context.session.created_at
        assert restored.session.last_activity == context.session.last_activity

        # History datetimes
        assert (
            restored.history.summary_updated_at == context.history.summary_updated_at
        )

        # Turn timestamps
        for orig, rest in zip(context.history.turns, restored.history.turns):
            assert rest.timestamp == orig.timestamp

    def test_format_property(self):
        """Test format property returns JSON."""
        serializer = JSONSerializer()
        assert serializer.format == SerializationFormat.JSON

    def test_content_type_property(self):
        """Test content_type property returns application/json."""
        serializer = JSONSerializer()
        assert serializer.content_type == "application/json"

    def test_json_is_valid(self):
        """Test that serialized output is valid JSON."""
        serializer = JSONSerializer()
        context = create_test_context()

        data = serializer.serialize(context)

        # Should parse without error
        parsed = json.loads(data.decode("utf-8"))
        assert isinstance(parsed, dict)
        assert "session" in parsed
        assert "history" in parsed
        assert "variables" in parsed

    def test_indented_output(self):
        """Test that indent parameter works."""
        compact = JSONSerializer()
        indented = JSONSerializer(indent=2)
        context = create_test_context()

        compact_data = compact.serialize(context)
        indented_data = indented.serialize(context)

        # Indented should be larger due to whitespace
        assert len(indented_data) > len(compact_data)

    def test_empty_context(self):
        """Test serializing context with minimal data."""
        serializer = JSONSerializer()

        session = SessionContext(session_id="empty")
        history = ConversationHistory(session_id="empty")
        variables = ContextVariables(session_id="empty")
        context = ExecutionContext(
            session=session,
            history=history,
            variables=variables,
        )

        data = serializer.serialize(context)
        restored = serializer.deserialize(data)

        assert restored.session.session_id == "empty"
        assert len(restored.history.turns) == 0
        assert len(restored.variables.keys()) == 0


class TestMessagePackSerializer:
    """Tests for MessagePackSerializer."""

    @pytest.fixture
    def serializer(self):
        """Create MessagePack serializer if available."""
        try:
            from src.context_primitives.serialization import MessagePackSerializer

            return MessagePackSerializer()
        except ImportError:
            pytest.skip("msgpack not installed")

    def test_serialize_returns_bytes(self, serializer):
        """Test that serialize returns bytes."""
        context = create_test_context()

        result = serializer.serialize(context)

        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_round_trip_preserves_data(self, serializer):
        """Test complete round-trip."""
        context = create_test_context(num_turns=5, num_variables=5)

        data = serializer.serialize(context)
        restored = serializer.deserialize(data)

        assert restored.session.session_id == context.session.session_id
        assert len(restored.history.turns) == len(context.history.turns)
        assert restored.variables.keys() == context.variables.keys()

    def test_format_property(self, serializer):
        """Test format property returns MSGPACK."""
        assert serializer.format == SerializationFormat.MSGPACK

    def test_smaller_than_json(self, serializer):
        """Test that MessagePack output is smaller than JSON."""
        json_serializer = JSONSerializer()
        context = create_test_context(num_turns=20, num_variables=10)

        json_data = json_serializer.serialize(context)
        msgpack_data = serializer.serialize(context)

        # MessagePack should be smaller
        assert len(msgpack_data) < len(json_data)

    def test_import_error_message(self):
        """Test helpful error message when msgpack not installed."""
        import sys

        # Temporarily remove msgpack if present
        msgpack_module = sys.modules.get("msgpack")
        if msgpack_module:
            sys.modules["msgpack"] = None

        try:
            # This should raise ImportError
            from src.context_primitives.serialization import MessagePackSerializer

            # Force reimport to trigger check
            try:
                # Create instance which triggers the import check
                MessagePackSerializer()
            except (ImportError, TypeError):
                pass  # Expected
        finally:
            if msgpack_module:
                sys.modules["msgpack"] = msgpack_module


class TestCompressedSerializer:
    """Tests for CompressedSerializer."""

    def test_serialize_is_compressed(self):
        """Test that output is gzip compressed."""
        inner = JSONSerializer()
        compressed = CompressedSerializer(inner)
        context = create_test_context()

        data = compressed.serialize(context)

        # Gzip magic number
        assert data[:2] == b"\x1f\x8b"

        # Should decompress
        decompressed = gzip.decompress(data)
        assert len(decompressed) > len(data)

    def test_round_trip_preserves_data(self):
        """Test complete round-trip with compression."""
        inner = JSONSerializer()
        compressed = CompressedSerializer(inner)
        context = create_test_context(num_turns=10)

        data = compressed.serialize(context)
        restored = compressed.deserialize(data)

        assert restored.session.session_id == context.session.session_id
        assert len(restored.history.turns) == len(context.history.turns)

    def test_format_property_json(self):
        """Test format property for compressed JSON."""
        inner = JSONSerializer()
        compressed = CompressedSerializer(inner)

        assert compressed.format == SerializationFormat.COMPRESSED_JSON

    def test_format_property_msgpack(self):
        """Test format property for compressed MessagePack."""
        try:
            from src.context_primitives.serialization import MessagePackSerializer

            inner = MessagePackSerializer()
            compressed = CompressedSerializer(inner)
            assert compressed.format == SerializationFormat.COMPRESSED_MSGPACK
        except ImportError:
            pytest.skip("msgpack not installed")

    def test_compression_ratio(self):
        """Test that compression achieves good ratio on large contexts."""
        inner = JSONSerializer()
        compressed = CompressedSerializer(inner)
        # Large context with repetitive data
        context = create_test_context(num_turns=50, num_variables=20)

        uncompressed = inner.serialize(context)
        compressed_data = compressed.serialize(context)

        ratio = len(compressed_data) / len(uncompressed)
        # Should achieve at least 30% reduction
        assert ratio < 0.7, f"Compression ratio {ratio:.2%} is too high"

    def test_compression_level(self):
        """Test different compression levels."""
        inner = JSONSerializer()
        low = CompressedSerializer(inner, compression_level=1)
        high = CompressedSerializer(inner, compression_level=9)
        context = create_test_context(num_turns=20)

        low_data = low.serialize(context)
        high_data = high.serialize(context)

        # Higher compression should be smaller or equal
        assert len(high_data) <= len(low_data)

    def test_inner_serializer_property(self):
        """Test inner_serializer property."""
        inner = JSONSerializer()
        compressed = CompressedSerializer(inner)

        assert compressed.inner_serializer is inner


class TestSerializerFactory:
    """Tests for SerializerFactory."""

    def test_get_json_serializer(self):
        """Test getting JSON serializer."""
        factory = SerializerFactory()

        serializer = factory.get(SerializationFormat.JSON)

        assert isinstance(serializer, JSONSerializer)

    def test_get_compressed_json_serializer(self):
        """Test getting compressed JSON serializer."""
        factory = SerializerFactory()

        serializer = factory.get(SerializationFormat.COMPRESSED_JSON)

        assert isinstance(serializer, CompressedSerializer)
        assert serializer.format == SerializationFormat.COMPRESSED_JSON

    def test_get_caches_serializer(self):
        """Test that factory caches serializers."""
        factory = SerializerFactory()

        first = factory.get(SerializationFormat.JSON)
        second = factory.get(SerializationFormat.JSON)

        assert first is second

    def test_create_does_not_cache(self):
        """Test that create returns fresh instances."""
        factory = SerializerFactory()

        first = factory.create(SerializationFormat.JSON)
        second = factory.create(SerializationFormat.JSON)

        assert first is not second

    def test_create_with_options(self):
        """Test create with custom options."""
        factory = SerializerFactory()

        serializer = factory.create(SerializationFormat.JSON, indent=4)

        assert isinstance(serializer, JSONSerializer)
        # Verify indent is applied by checking output
        context = create_test_context(num_turns=1)
        data = serializer.serialize(context)
        # Indented JSON will have newlines
        assert b"\n" in data

    def test_clear_cache(self):
        """Test cache clearing."""
        factory = SerializerFactory()

        first = factory.get(SerializationFormat.JSON)
        factory.clear_cache()
        second = factory.get(SerializationFormat.JSON)

        assert first is not second

    def test_available_formats(self):
        """Test available_formats returns list."""
        formats = SerializerFactory.available_formats()

        assert isinstance(formats, list)
        assert SerializationFormat.JSON in formats
        assert SerializationFormat.COMPRESSED_JSON in formats


class TestCreateSerializer:
    """Tests for create_serializer factory function."""

    def test_create_json(self):
        """Test creating JSON serializer."""
        serializer = create_serializer(SerializationFormat.JSON)
        assert isinstance(serializer, JSONSerializer)

    def test_create_compressed_json(self):
        """Test creating compressed JSON serializer."""
        serializer = create_serializer(SerializationFormat.COMPRESSED_JSON)
        assert isinstance(serializer, CompressedSerializer)

    def test_create_with_compression_level(self):
        """Test creating with custom compression level."""
        serializer = create_serializer(
            SerializationFormat.COMPRESSED_JSON, compression_level=9
        )
        assert isinstance(serializer, CompressedSerializer)

    def test_create_msgpack_if_available(self):
        """Test creating MessagePack serializer if available."""
        try:
            from src.context_primitives.serialization import MessagePackSerializer

            serializer = create_serializer(SerializationFormat.MSGPACK)
            assert isinstance(serializer, MessagePackSerializer)
        except ImportError:
            pytest.skip("msgpack not installed")

    def test_invalid_format(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises((ValueError, KeyError)):
            create_serializer("invalid_format")


class TestPerformanceBenchmarks:
    """Performance benchmarks for serialization formats."""

    @pytest.fixture
    def large_context(self):
        """Create a large context for benchmarking."""
        return create_test_context(num_turns=100, num_variables=50)

    def test_json_performance(self, large_context):
        """Benchmark JSON serialization."""
        serializer = JSONSerializer()
        iterations = 100

        # Serialize
        start = time.perf_counter()
        for _ in range(iterations):
            data = serializer.serialize(large_context)
        serialize_time = (time.perf_counter() - start) / iterations * 1000

        # Deserialize
        start = time.perf_counter()
        for _ in range(iterations):
            serializer.deserialize(data)
        deserialize_time = (time.perf_counter() - start) / iterations * 1000

        print(f"\nJSON Benchmark ({iterations} iterations):")
        print(f"  Serialize: {serialize_time:.3f}ms avg")
        print(f"  Deserialize: {deserialize_time:.3f}ms avg")
        print(f"  Size: {len(data):,} bytes")

    def test_msgpack_performance(self, large_context):
        """Benchmark MessagePack serialization."""
        try:
            from src.context_primitives.serialization import MessagePackSerializer

            serializer = MessagePackSerializer()
        except ImportError:
            pytest.skip("msgpack not installed")

        iterations = 100

        # Serialize
        start = time.perf_counter()
        for _ in range(iterations):
            data = serializer.serialize(large_context)
        serialize_time = (time.perf_counter() - start) / iterations * 1000

        # Deserialize
        start = time.perf_counter()
        for _ in range(iterations):
            serializer.deserialize(data)
        deserialize_time = (time.perf_counter() - start) / iterations * 1000

        print(f"\nMessagePack Benchmark ({iterations} iterations):")
        print(f"  Serialize: {serialize_time:.3f}ms avg")
        print(f"  Deserialize: {deserialize_time:.3f}ms avg")
        print(f"  Size: {len(data):,} bytes")

    def test_compressed_json_performance(self, large_context):
        """Benchmark compressed JSON serialization."""
        serializer = create_serializer(SerializationFormat.COMPRESSED_JSON)
        iterations = 50  # Fewer iterations due to compression cost

        # Serialize
        start = time.perf_counter()
        for _ in range(iterations):
            data = serializer.serialize(large_context)
        serialize_time = (time.perf_counter() - start) / iterations * 1000

        # Deserialize
        start = time.perf_counter()
        for _ in range(iterations):
            serializer.deserialize(data)
        deserialize_time = (time.perf_counter() - start) / iterations * 1000

        print(f"\nCompressed JSON Benchmark ({iterations} iterations):")
        print(f"  Serialize: {serialize_time:.3f}ms avg")
        print(f"  Deserialize: {deserialize_time:.3f}ms avg")
        print(f"  Size: {len(data):,} bytes")

    def test_format_comparison(self, large_context):
        """Compare all available formats."""
        json_serializer = JSONSerializer()
        compressed_json = create_serializer(SerializationFormat.COMPRESSED_JSON)

        json_data = json_serializer.serialize(large_context)
        compressed_data = compressed_json.serialize(large_context)

        print("\n=== Format Comparison ===")
        print(f"JSON size:            {len(json_data):,} bytes")
        print(f"Compressed JSON size: {len(compressed_data):,} bytes")
        print(
            f"Compression ratio:    {len(compressed_data) / len(json_data):.1%}"
        )

        try:
            from src.context_primitives.serialization import MessagePackSerializer

            msgpack_serializer = MessagePackSerializer()
            compressed_msgpack = create_serializer(
                SerializationFormat.COMPRESSED_MSGPACK
            )

            msgpack_data = msgpack_serializer.serialize(large_context)
            compressed_msgpack_data = compressed_msgpack.serialize(large_context)

            print(f"MessagePack size:     {len(msgpack_data):,} bytes")
            print(f"Compressed MsgPack:   {len(compressed_msgpack_data):,} bytes")
            print(f"MsgPack vs JSON:      {len(msgpack_data) / len(json_data):.1%}")
        except ImportError:
            print("MessagePack: not available (install msgpack)")
