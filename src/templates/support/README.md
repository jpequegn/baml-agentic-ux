# {{PROJECT_NAME_TITLE}} - Support Template

This template demonstrates customer support and help desk LUI patterns using BAML.

## What You'll Learn

1. **Knowledge Base Search** - FAQ matching with semantic search and relevance scoring
2. **Ticket Lifecycle** - Creating, tracking, and managing support tickets
3. **Escalation Patterns** - When and how to handoff to human agents
4. **Satisfaction Tracking** - Collecting feedback and ratings
5. **Multi-tier Support** - Self-service to human escalation flow

## Quick Start

```bash
# Load the schema
python integration.py

# Run tests
pytest test_integration.py -v
```

## When to Use This Template

The Support template is ideal for:
- **Help Desk Systems** - Customer service and technical support
- **FAQ Bots** - Self-service knowledge base search
- **Ticket Management** - Issue tracking and resolution workflows
- **Customer Service** - Multi-channel support interfaces
- **IT Support** - Internal helpdesk and ticketing systems

## Schema Structure

### Components

| Component | Type | Purpose |
|-----------|------|---------|
| `search-faq` | QUERY | Find answers in knowledge base |
| `create-ticket` | ACTION | Submit new support ticket |
| `check-status` | QUERY | Track ticket status |
| `escalate-ticket` | ACTION | Handoff to human agent |
| `provide-feedback` | FEEDBACK | Rate support interaction |

## Key Concepts

### 1. Knowledge Base Matching

The `search-faq` component demonstrates semantic search:
- **Flexible queries**: Natural questions like "How do I reset my password?"
- **Category filtering**: Optional filters to narrow results
- **Relevance scoring**: Ranking results by match quality

```json
{
  "query": "reset password",
  "category": "account"
}
```

### 2. Ticket Lifecycle

Support tickets flow through states:
1. **Created** - Initial submission
2. **In Progress** - Agent working on it
3. **Waiting** - Awaiting customer response
4. **Resolved** - Issue fixed
5. **Closed** - Confirmed resolution

The `create-ticket` component captures:
- Subject and detailed description
- Priority levels (low, medium, high, urgent)
- Category for routing

### 3. Escalation Triggers

The `escalate-ticket` component handles handoff when:
- Self-service options don't resolve the issue
- Customer explicitly requests human help
- Issue complexity exceeds automated handling
- Timeout or repeated failures occur

**Best Practice**: Use confirmation before escalation to set expectations about response time.

### 4. Satisfaction Tracking

The `provide-feedback` component collects:
- **Rating**: 1-5 stars for quantitative metrics
- **Comment**: Optional qualitative feedback
- **Ticket association**: Links feedback to specific interactions

This data drives:
- Agent performance metrics
- Process improvement
- Customer satisfaction (CSAT) scores

## Key Patterns Demonstrated

### Semantic Search with Relevance

```json
"feedback": {
  "success_template": "Found {count} relevant articles for '{query}'"
}
```

Dynamic count shows search effectiveness.

### Priority Classification

```json
"parameters": [
  {
    "name": "priority",
    "type": "string",
    "description": "Priority level: low, medium, high, urgent"
  }
]
```

Structured priority helps with ticket routing and SLA management.

### Escalation with Confirmation

```json
"feedback": {
  "confirmation_required": true,
  "confirmation_prompt": "Escalating to a human agent may take longer to respond. Continue?"
}
```

Sets expectations before handoff to prevent frustration.

### Optional Parameters for Flexibility

Most components use optional parameters for ease of use:
- `check-status` without ticket_id shows recent tickets
- `escalate-ticket` without ticket_id escalates latest ticket
- `provide-feedback` without ticket_id uses latest resolved ticket

## Customization Guide

### Adding New FAQ Categories

Edit the `search-faq` component to add domain-specific categories:

```json
"parameters": [
  {
    "name": "category",
    "type": "string",
    "description": "Category: billing, technical, account, shipping, returns"
  }
]
```

### Extending Ticket Properties

Add custom fields to `create-ticket`:

```json
"parameters": [
  {
    "name": "affected_feature",
    "type": "string",
    "description": "Which feature is affected"
  },
  {
    "name": "browser",
    "type": "string",
    "description": "Browser for web issues"
  }
]
```

### Multi-language Support

Add language parameter for international support:

```json
{
  "name": "language",
  "type": "string",
  "description": "Preferred language: en, es, fr, de"
}
```

## Example Use Cases

1. **SaaS Customer Support** - Users get instant answers from FAQ, create tickets for complex issues
2. **E-commerce Help Desk** - Order tracking, return requests, shipping questions
3. **IT Internal Support** - Employee helpdesk for technical issues and access requests
4. **Healthcare Patient Support** - Appointment scheduling, billing questions, prescription refills
5. **Financial Services** - Account inquiries, transaction disputes, fraud reporting

## Files

- `schema.json` - The LUI schema definition
- `integration.py` - Python code demonstrating schema usage
- `test_integration.py` - Tests showing expected behavior
- `README.md` - This file

## Next Steps

1. Customize components for your support domain
2. Add your FAQ data and search logic
3. Integrate with your ticketing system (Zendesk, Freshdesk, etc.)
4. Implement escalation rules and SLA tracking
5. Test with real customer queries
6. Monitor satisfaction metrics

Generated on: {{CREATED_DATE}}
