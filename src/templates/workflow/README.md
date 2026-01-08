# {{PROJECT_NAME_TITLE}} - Workflow Template

This template demonstrates multi-step conversational workflow patterns using BAML and LUI.

## What You'll Learn

1. **State Management** - Tracking workflow progress and user data across steps
2. **Step Transitions** - Moving between workflow stages with validation
3. **Branching Logic** - Conditional paths based on user choices
4. **Rollback & Recovery** - Handling errors and allowing users to go back
5. **Completion States** - Properly finishing and cleaning up workflows

## When to Use Workflow Patterns

Workflow patterns are ideal for:

- **Checkout Flows** - Multi-step purchase processes (cart -> shipping -> payment -> confirm)
- **Onboarding Wizards** - Step-by-step user registration and setup
- **Approval Processes** - Request submission, review, and decision flows
- **Form Completion** - Complex forms broken into conversational steps
- **Guided Troubleshooting** - Interactive problem diagnosis and resolution

## Quick Start

```bash
# Load the schema
python integration.py

# Run tests
pytest test_integration.py -v
```

## Schema Structure

### Components

| Component | Type | Purpose |
|-----------|------|---------|
| `start-process` | ACTION | Initialize a workflow with initial state |
| `collect-info` | ACTION | Gather information step-by-step |
| `confirm-action` | ACTION | Confirmation before proceeding |
| `branch-decision` | ACTION | Handle conditional workflow paths |
| `complete-process` | FEEDBACK | Finalize and cleanup workflow |

## Key Workflow Concepts

### 1. State Management

Workflows maintain state across multiple conversational turns:

```json
"metadata": {
  "state_changes": {
    "workflow_status": "in_progress",
    "current_step": 1,
    "collected_data": {}
  }
}
```

Track:
- Current step in the process
- Data collected so far
- Selected paths/branches
- Validation status

### 2. Step Transitions

Control which steps can follow each other:

```json
"metadata": {
  "next_steps": ["collect-info", "confirm-action"]
}
```

This ensures:
- Users don't skip required steps
- Validation happens at the right time
- Clear progress indication

### 3. Branching Logic

Different paths based on user choices:

```json
"metadata": {
  "conditional_paths": {
    "express": ["collect-payment-info", "confirm-action"],
    "standard": ["confirm-action"],
    "premium": ["setup-account", "collect-payment-info", "confirm-action"]
  }
}
```

Use cases:
- Shipping options (express vs. standard)
- Pricing tiers (free vs. premium)
- Account types (personal vs. business)

### 4. Data Collection Pattern

Gather information conversationally:

```
User: "I want to start checkout"
System: "Great! Let's begin. What's your shipping address?"
User: "123 Main St, Springfield"
System: "Got it! And your email?"
User: "user@example.com"
System: "Perfect. Review your order..."
```

The `collect-info` component handles incremental data gathering with validation.

### 5. Confirmation Before Commitment

Always confirm before irreversible actions:

```json
"feedback": {
  "confirmation_required": true,
  "confirmation_prompt": "Please review the details before confirming. Continue?"
}
```

### 6. Rollback & Error Handling

Allow users to correct mistakes:

```json
"metadata": {
  "can_retry": true,
  "validation_required": true
}
```

Support commands like:
- "Go back"
- "Change my email"
- "Start over"

## Implementation Patterns

### Pattern 1: Linear Workflow

Simple step-by-step progression:
```
start-process -> collect-info -> collect-info -> confirm-action -> complete-process
```

### Pattern 2: Branching Workflow

Conditional paths based on choices:
```
start-process -> branch-decision -> [Path A or Path B] -> complete-process
```

### Pattern 3: Iterative Collection

Collect multiple items:
```
start-process -> collect-info -> [repeat] -> confirm-action -> complete-process
```

## Customization Guide

### 1. Add Your Domain Logic

Replace template variables:
- `{{PROJECT_NAME}}` - Your project name
- `{{PROJECT_NAME_TITLE}}` - Title-cased version
- `{{PROJECT_NAME_LOWER}}` - Lowercase version

### 2. Define Your Steps

Modify components to match your workflow:
```json
{
  "component_id": "collect-shipping-address",
  "component_type": "ACTION",
  "intent": "Collect shipping address",
  ...
}
```

### 3. Specify State Requirements

Define what data each step needs:
```json
"metadata": {
  "requires_complete_state": true,
  "required_fields": ["email", "address", "payment"]
}
```

### 4. Configure Transitions

Set valid next steps:
```json
"metadata": {
  "next_steps": ["review-order", "add-promo-code"]
}
```

## Example Use Cases

### E-commerce Checkout

```
1. start-process (type: "checkout")
2. collect-info (shipping address)
3. collect-info (payment info)
4. branch-decision (shipping speed)
5. confirm-action (review order)
6. complete-process (order confirmation)
```

### User Onboarding

```
1. start-process (type: "onboarding")
2. collect-info (name, email)
3. branch-decision (account type)
4. collect-info (additional details based on type)
5. confirm-action (create account)
6. complete-process (welcome message)
```

### Approval Workflow

```
1. start-process (type: "approval_request")
2. collect-info (request details)
3. confirm-action (submit for review)
4. [System: route to approver]
5. branch-decision (approve/reject)
6. complete-process (notify outcome)
```

## Files

- `schema.json` - The LUI workflow schema definition
- `integration.py` - Python code with state management
- `test_integration.py` - Tests for workflow behavior
- `README.md` - This file

## Best Practices

1. **Keep Steps Small** - Each step should collect 1-3 related pieces of information
2. **Validate Early** - Check data validity as it's collected, not at the end
3. **Show Progress** - Let users know where they are in the workflow
4. **Enable Rollback** - Always allow users to go back and change things
5. **Confirm Before Commit** - Final confirmation before irreversible actions
6. **Handle Abandonment** - Save state so users can resume later
7. **Provide Summaries** - Show what was collected before confirmation

## Next Steps

1. Map out your workflow steps on paper first
2. Identify branching points and conditional logic
3. Define the data collected at each step
4. Implement state management in your application
5. Add validation and error handling
6. Test with real users to refine the flow

Generated on: {{CREATED_DATE}}
