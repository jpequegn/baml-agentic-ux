# {{PROJECT_NAME_TITLE}} - CRUD Template

This template demonstrates fundamental LUI (Language User Interface) patterns using BAML.

## What You'll Learn

1. **Component Types** - ACTION, QUERY, and FEEDBACK components
2. **Invocation Patterns** - Primary phrases, alternates, and examples
3. **Feedback Templates** - Success, error, and confirmation messages
4. **Destructive Action Confirmation** - Protecting users from accidents

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
| `create-item` | ACTION | Create new items |
| `list-items` | QUERY | Retrieve items |
| `update-item` | ACTION | Modify existing items |
| `delete-item` | ACTION | Remove items (with confirmation) |
| `help` | FEEDBACK | Discoverability |

### Key Patterns Demonstrated

#### 1. Invocation Triad
Every component defines three levels of invocation:
- `primary_phrase`: The main way to invoke ("create item")
- `alternate_phrases`: Common variations ("add item", "new item")
- `examples`: Full example sentences for intent matching

#### 2. Feedback Templates
Use template variables for dynamic responses:
```json
"success_template": "Created item '{title}' successfully"
```
The `{title}` placeholder is filled from extracted parameters.

#### 3. Confirmation for Destructive Actions
The delete component sets:
```json
"confirmation_required": true,
"confirmation_prompt": "Are you sure...?"
```
This prevents accidental data loss.

## Files

- `schema.json` - The LUI schema definition
- `integration.py` - Python code demonstrating schema usage
- `test_integration.py` - Tests showing expected behavior
- `README.md` - This file

## Next Steps

1. Modify the schema to match your domain
2. Add more components as needed
3. Test with the LUI simulator
4. Export to OpenAPI or MCP format

Generated on: {{CREATED_DATE}}
