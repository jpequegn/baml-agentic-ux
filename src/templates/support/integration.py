"""{{PROJECT_NAME_TITLE}} - Integration Example.

This module demonstrates how to use a LUI schema for support operations with the BAML client.
Generated from the Support template on {{CREATED_DATE}}.
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


def load_schema() -> dict:
    """Load the LUI schema from schema.json.

    Returns:
        The parsed schema dictionary
    """
    schema_path = Path(__file__).parent / "schema.json"
    with open(schema_path) as f:
        return json.load(f)


def find_component(schema: dict, component_id: str) -> dict | None:
    """Find a component by ID in the schema.

    Args:
        schema: The loaded schema
        component_id: ID of the component to find

    Returns:
        The component dictionary or None if not found
    """
    for component in schema.get("components", []):
        if component.get("component_id") == component_id:
            return component
    return None


def search_faq(query: str, category: Optional[str] = None) -> List[Dict]:
    """Search FAQ with relevance scoring.

    This is a simplified implementation. In production, use:
    - Vector embeddings for semantic search
    - Full-text search engines (Elasticsearch, etc.)
    - Machine learning models for intent classification

    Args:
        query: The search query
        category: Optional category filter

    Returns:
        List of FAQ results with relevance scores
    """
    # Mock FAQ database
    faq_database = [
        {
            "id": "faq-001",
            "category": "account",
            "question": "How do I reset my password?",
            "answer": "Click 'Forgot Password' on the login page and follow the email instructions.",
            "relevance": 0.95 if "password" in query.lower() else 0.2,
        },
        {
            "id": "faq-002",
            "category": "billing",
            "question": "How do I update my payment method?",
            "answer": "Go to Settings > Billing > Payment Methods and add or update your card.",
            "relevance": 0.9 if "payment" in query.lower() or "billing" in query.lower() else 0.15,
        },
        {
            "id": "faq-003",
            "category": "technical",
            "question": "Why is the app running slowly?",
            "answer": "Clear your browser cache and cookies. If that doesn't help, try using a different browser.",
            "relevance": 0.85 if "slow" in query.lower() or "performance" in query.lower() else 0.1,
        },
    ]

    # Filter by category if provided
    results = faq_database
    if category:
        results = [faq for faq in results if faq["category"] == category]

    # Sort by relevance score
    results = sorted(results, key=lambda x: x["relevance"], reverse=True)

    # Return top 3 results with score > 0.5
    return [faq for faq in results if faq["relevance"] > 0.5][:3]


class TicketManager:
    """Manages support ticket lifecycle."""

    def __init__(self):
        self.tickets = {}
        self.ticket_counter = 1000

    def create_ticket(
        self,
        subject: str,
        description: str,
        priority: str = "medium",
        category: Optional[str] = None,
    ) -> Dict:
        """Create a new support ticket.

        Args:
            subject: Brief subject line
            description: Detailed description
            priority: Priority level (low, medium, high, urgent)
            category: Issue category

        Returns:
            Created ticket dictionary
        """
        ticket_id = str(self.ticket_counter)
        self.ticket_counter += 1

        ticket = {
            "ticket_id": ticket_id,
            "subject": subject,
            "description": description,
            "priority": priority,
            "category": category or "general",
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        self.tickets[ticket_id] = ticket
        return ticket

    def get_ticket_status(self, ticket_id: Optional[str] = None) -> Dict:
        """Get status of a ticket.

        Args:
            ticket_id: ID of ticket to check, or None for latest

        Returns:
            Ticket status information
        """
        if ticket_id is None:
            # Return latest ticket
            if not self.tickets:
                return {"error": "No tickets found"}
            ticket_id = max(self.tickets.keys())

        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}

        return ticket

    def escalate_ticket(
        self, ticket_id: Optional[str] = None, reason: Optional[str] = None
    ) -> Dict:
        """Escalate ticket to human agent.

        Args:
            ticket_id: ID of ticket to escalate, or None for latest
            reason: Optional reason for escalation

        Returns:
            Escalation result
        """
        if ticket_id is None:
            if not self.tickets:
                return {"error": "No tickets found"}
            ticket_id = max(self.tickets.keys())

        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return {"error": f"Ticket {ticket_id} not found"}

        ticket["status"] = "escalated"
        ticket["escalation_reason"] = reason
        ticket["escalated_at"] = datetime.now().isoformat()
        ticket["updated_at"] = datetime.now().isoformat()

        # Calculate expected response time based on priority
        response_times = {
            "urgent": "1 hour",
            "high": "4 hours",
            "medium": "1 business day",
            "low": "3 business days",
        }

        return {
            "ticket_id": ticket_id,
            "status": "escalated",
            "response_time": response_times.get(ticket["priority"], "1 business day"),
        }


class FeedbackCollector:
    """Collects and tracks customer feedback."""

    def __init__(self):
        self.feedback = []

    def submit_feedback(
        self, rating: int, ticket_id: Optional[str] = None, comment: Optional[str] = None
    ) -> Dict:
        """Submit customer feedback.

        Args:
            rating: Rating from 1-5 stars
            ticket_id: Associated ticket ID
            comment: Optional feedback comment

        Returns:
            Feedback submission result
        """
        if not (1 <= rating <= 5):
            return {"error": "Rating must be between 1 and 5"}

        feedback_entry = {
            "feedback_id": len(self.feedback) + 1,
            "ticket_id": ticket_id,
            "rating": rating,
            "comment": comment,
            "submitted_at": datetime.now().isoformat(),
        }

        self.feedback.append(feedback_entry)
        return {
            "success": True,
            "rating": rating,
            "message": "Thank you for your feedback!",
        }

    def get_average_rating(self) -> float:
        """Calculate average customer satisfaction rating.

        Returns:
            Average rating across all feedback
        """
        if not self.feedback:
            return 0.0
        return sum(f["rating"] for f in self.feedback) / len(self.feedback)


def main():
    """Demonstrate support schema usage."""
    schema = load_schema()
    print(f"Loaded schema: {schema['name']}")
    print(f"Domain: {schema['domain']['subdomain']}")
    print(f"Components: {len(schema['components'])}")
    print()

    # Demo 1: FAQ Search
    print("=== Demo 1: FAQ Search ===")
    search_component = find_component(schema, "search-faq")
    if search_component:
        query = "How do I reset my password?"
        results = search_faq(query)
        print(f"Query: {query}")
        print(f"Found {len(results)} relevant articles:")
        for result in results:
            print(f"  - {result['question']} (relevance: {result['relevance']:.2f})")
    print()

    # Demo 2: Ticket Creation
    print("=== Demo 2: Ticket Creation ===")
    ticket_manager = TicketManager()
    ticket = ticket_manager.create_ticket(
        subject="Cannot login to account",
        description="Getting error 'Invalid credentials' even with correct password",
        priority="high",
        category="technical",
    )
    print(f"Created Ticket #{ticket['ticket_id']}")
    print(f"  Subject: {ticket['subject']}")
    print(f"  Priority: {ticket['priority']}")
    print(f"  Status: {ticket['status']}")
    print()

    # Demo 3: Ticket Escalation
    print("=== Demo 3: Ticket Escalation ===")
    escalation = ticket_manager.escalate_ticket(
        ticket_id=ticket["ticket_id"], reason="User frustrated, needs immediate help"
    )
    print(f"Escalated Ticket #{escalation['ticket_id']}")
    print(f"  Status: {escalation['status']}")
    print(f"  Expected response: {escalation['response_time']}")
    print()

    # Demo 4: Feedback Collection
    print("=== Demo 4: Feedback Collection ===")
    feedback_collector = FeedbackCollector()
    feedback = feedback_collector.submit_feedback(
        rating=4, ticket_id=ticket["ticket_id"], comment="Agent was helpful and quick"
    )
    print(f"Feedback submitted: {feedback['rating']}/5 stars")
    print(f"Average rating: {feedback_collector.get_average_rating():.1f}/5")


if __name__ == "__main__":
    main()
