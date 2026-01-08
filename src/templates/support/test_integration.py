"""Tests for {{PROJECT_NAME_TITLE}} support integration.

These tests demonstrate expected behavior and serve as documentation.
Generated from the Support template on {{CREATED_DATE}}.
"""

import pytest
from integration import (
    load_schema,
    find_component,
    search_faq,
    TicketManager,
    FeedbackCollector,
)


class TestSchemaLoading:
    """Test schema loading functionality."""

    def test_loads_schema(self):
        """Test that schema loads successfully."""
        schema = load_schema()
        assert schema is not None
        assert "schema_id" in schema
        assert "components" in schema

    def test_schema_has_support_components(self):
        """Test that schema has expected support components."""
        schema = load_schema()
        assert len(schema["components"]) == 5

        component_ids = [c["component_id"] for c in schema["components"]]
        assert "search-faq" in component_ids
        assert "create-ticket" in component_ids
        assert "check-status" in component_ids
        assert "escalate-ticket" in component_ids
        assert "provide-feedback" in component_ids

    def test_schema_domain_is_support(self):
        """Test that schema domain is support-operations."""
        schema = load_schema()
        assert schema["domain"]["subdomain"] == "support-operations"


class TestComponentFinding:
    """Test component finding functionality."""

    def test_finds_search_faq_component(self):
        """Test finding the search-faq component."""
        schema = load_schema()
        component = find_component(schema, "search-faq")
        assert component is not None
        assert component["component_type"] == "QUERY"

    def test_finds_create_ticket_component(self):
        """Test finding the create-ticket component."""
        schema = load_schema()
        component = find_component(schema, "create-ticket")
        assert component is not None
        assert component["component_type"] == "ACTION"

    def test_returns_none_for_missing(self):
        """Test that missing components return None."""
        schema = load_schema()
        component = find_component(schema, "nonexistent")
        assert component is None


class TestFAQSearch:
    """Test FAQ search functionality."""

    def test_search_returns_relevant_results(self):
        """Test that FAQ search returns relevant results."""
        results = search_faq("password reset")
        assert len(results) > 0
        assert results[0]["relevance"] > 0.5

    def test_search_filters_by_category(self):
        """Test category filtering in FAQ search."""
        results = search_faq("payment", category="billing")
        assert len(results) > 0
        assert all(r["category"] == "billing" for r in results)

    def test_search_sorts_by_relevance(self):
        """Test that results are sorted by relevance score."""
        results = search_faq("password")
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i]["relevance"] >= results[i + 1]["relevance"]

    def test_search_returns_top_matches_only(self):
        """Test that only high-relevance matches are returned."""
        results = search_faq("completely unrelated query xyz123")
        # Should return empty or only matches above threshold
        assert all(r["relevance"] > 0.5 for r in results)


class TestTicketManagement:
    """Test ticket lifecycle operations."""

    def test_creates_ticket_with_all_fields(self):
        """Test creating a ticket with all parameters."""
        manager = TicketManager()
        ticket = manager.create_ticket(
            subject="Login issue",
            description="Cannot access my account",
            priority="high",
            category="technical",
        )

        assert ticket["ticket_id"] is not None
        assert ticket["subject"] == "Login issue"
        assert ticket["description"] == "Cannot access my account"
        assert ticket["priority"] == "high"
        assert ticket["category"] == "technical"
        assert ticket["status"] == "created"

    def test_creates_ticket_with_defaults(self):
        """Test creating a ticket with minimal parameters."""
        manager = TicketManager()
        ticket = manager.create_ticket(
            subject="Question",
            description="Need help",
        )

        assert ticket["priority"] == "medium"
        assert ticket["category"] == "general"

    def test_ticket_ids_are_unique(self):
        """Test that each ticket gets a unique ID."""
        manager = TicketManager()
        ticket1 = manager.create_ticket("Issue 1", "Description 1")
        ticket2 = manager.create_ticket("Issue 2", "Description 2")

        assert ticket1["ticket_id"] != ticket2["ticket_id"]

    def test_get_ticket_status_by_id(self):
        """Test retrieving ticket status by ID."""
        manager = TicketManager()
        ticket = manager.create_ticket("Test", "Description")

        status = manager.get_ticket_status(ticket["ticket_id"])
        assert status["ticket_id"] == ticket["ticket_id"]
        assert status["status"] == "created"

    def test_get_latest_ticket_status(self):
        """Test retrieving latest ticket when no ID provided."""
        manager = TicketManager()
        manager.create_ticket("Old ticket", "Old description")
        latest_ticket = manager.create_ticket("Latest ticket", "Latest description")

        status = manager.get_ticket_status()
        assert status["ticket_id"] == latest_ticket["ticket_id"]

    def test_get_status_handles_missing_ticket(self):
        """Test error handling for non-existent ticket."""
        manager = TicketManager()
        status = manager.get_ticket_status("99999")

        assert "error" in status


class TestTicketEscalation:
    """Test escalation trigger functionality."""

    def test_escalates_ticket_to_human(self):
        """Test escalating a ticket to human agent."""
        manager = TicketManager()
        ticket = manager.create_ticket("Need help", "Urgent issue", priority="urgent")

        result = manager.escalate_ticket(ticket["ticket_id"], "Customer frustrated")

        assert result["ticket_id"] == ticket["ticket_id"]
        assert result["status"] == "escalated"
        assert "response_time" in result

    def test_escalation_response_time_by_priority(self):
        """Test that escalation response time varies by priority."""
        manager = TicketManager()

        urgent_ticket = manager.create_ticket("Urgent", "Description", priority="urgent")
        low_ticket = manager.create_ticket("Low", "Description", priority="low")

        urgent_result = manager.escalate_ticket(urgent_ticket["ticket_id"])
        low_result = manager.escalate_ticket(low_ticket["ticket_id"])

        # Urgent should have faster response time
        assert urgent_result["response_time"] != low_result["response_time"]

    def test_escalate_latest_ticket_without_id(self):
        """Test escalating latest ticket when no ID provided."""
        manager = TicketManager()
        ticket = manager.create_ticket("Issue", "Description")

        result = manager.escalate_ticket()

        assert result["ticket_id"] == ticket["ticket_id"]
        assert result["status"] == "escalated"

    def test_escalation_updates_ticket_status(self):
        """Test that escalation updates the ticket in the manager."""
        manager = TicketManager()
        ticket = manager.create_ticket("Issue", "Description")

        manager.escalate_ticket(ticket["ticket_id"])

        status = manager.get_ticket_status(ticket["ticket_id"])
        assert status["status"] == "escalated"
        assert "escalated_at" in status


class TestFeedbackCollection:
    """Test feedback handling functionality."""

    def test_submits_feedback_with_rating(self):
        """Test submitting feedback with rating."""
        collector = FeedbackCollector()
        result = collector.submit_feedback(rating=5, comment="Excellent service")

        assert result["success"] is True
        assert result["rating"] == 5

    def test_submits_feedback_with_ticket_id(self):
        """Test associating feedback with ticket."""
        collector = FeedbackCollector()
        result = collector.submit_feedback(rating=4, ticket_id="1000")

        assert result["success"] is True

    def test_validates_rating_range(self):
        """Test that rating must be between 1-5."""
        collector = FeedbackCollector()

        invalid_low = collector.submit_feedback(rating=0)
        invalid_high = collector.submit_feedback(rating=6)

        assert "error" in invalid_low
        assert "error" in invalid_high

    def test_calculates_average_rating(self):
        """Test calculating average satisfaction rating."""
        collector = FeedbackCollector()
        collector.submit_feedback(rating=5)
        collector.submit_feedback(rating=3)
        collector.submit_feedback(rating=4)

        average = collector.get_average_rating()
        assert average == 4.0

    def test_average_rating_with_no_feedback(self):
        """Test average rating returns 0 when no feedback."""
        collector = FeedbackCollector()
        average = collector.get_average_rating()
        assert average == 0.0


class TestEscalationConfirmation:
    """Test escalation confirmation pattern."""

    def test_escalate_component_requires_confirmation(self):
        """Test that escalate-ticket component requires confirmation."""
        schema = load_schema()
        component = find_component(schema, "escalate-ticket")

        assert component["feedback"]["confirmation_required"] is True
        assert "confirmation_prompt" in component["feedback"]
        assert "longer to respond" in component["feedback"]["confirmation_prompt"]
