# Agentic UX Design Principles

Design principles for Language User Interfaces (LUI) and agent-first design.

## Core Paradigm Shift: GUI → LUI

| Traditional GUI | Modern LUI |
|-----------------|-----------|
| User controls, masters interface | System interprets intent |
| Interface-centric navigation | Intent-centric interaction |
| Explicit commands | Natural language |
| Menu hierarchies | Conversational flow |

**Key Insight**: Hybrid approaches win—blend GUI and LUI elements based on task requirements.

---

## 1. Interface Discovery Patterns

### Dynamic Capability Discovery
Agents should discover available capabilities at runtime, not rely on hardcoded configurations.

**Patterns:**
- **Schema Exposure**: Publish OpenAPI/JSON Schema at known endpoints (`/openapi.json`)
- **Self-Describing Interfaces**: Include metadata, versioning, examples, constraints
- **MCP (Model Context Protocol)**: Standardized tool discovery via JSON-RPC

### Progressive Loading Strategy
Based on Anthropic's Agent Skills framework:

| Level | Content | When Loaded |
|-------|---------|-------------|
| 1. Metadata | Name, description, triggers | Always |
| 2. Core Instructions | Full capability details | When relevant |
| 3. Supplementary | Examples, references | On-demand |

---

## 2. Action Capability Declaration

### Machine-Readable Actions
Every action an agent can perform must be:
- **Discoverable**: Published in schema
- **Documented**: Parameters, operations, responses, semantics
- **Typed**: Clear input/output schemas
- **Contextual**: When and why to use

### Schema Components
```
Operation:
  - name: descriptive identifier
  - description: what it does and when to use
  - parameters: typed inputs with descriptions
  - returns: typed output with examples
  - errors: possible failure modes
```

---

## 3. Feedback Loop Design

### User Feedback Mechanisms
- Thumbs up/down on responses
- "Incorrect" flagging buttons
- Inline correction capability
- Detailed feedback forms

### Self-Improvement Cycle
```
User interaction → Feedback collection → Pattern analysis →
Model/prompt adjustment → Improved responses → Monitor
```

### Confidence Visualization
- Explicit confidence scores where appropriate
- Uncertainty acknowledgment ("I'm not sure, but...")
- Source citations for trust

---

## 4. Error Handling in Conversational UI

### Philosophy: Recovery > Perfection

**Graceful Failure Pattern:**
```
Error occurs
→ Show user-friendly message
→ Preserve user context/data
→ Offer specific recovery actions
→ Provide escalation path
```

### Error Types
| Type | Response |
|------|----------|
| User Error | Guidance + correction |
| System Error | Apologize + explain + retry |
| External Error | Explain dependency + alternatives |

### Human Handoff
When agent confidence < threshold:
1. Inform user of limitation
2. Offer human assistance
3. Transfer full context
4. Continue monitoring for learning

---

## 5. Progressive Disclosure for Agents

### Principles
- Start simple, reveal complexity gradually
- Load capabilities on-demand, not upfront
- Treat agent as intelligent information forager

### Layered Architecture
```
Level 1: Essential capabilities (always visible)
Level 2: Common options (one interaction away)
Level 3: Advanced features (two interactions away)
Level 4: Expert settings (discoverable but hidden)
```

### Benefits
- Context efficiency (fewer tokens)
- Faster responses
- Scalable capability addition
- Better maintainability

---

## 6. Machine-Readable Interface Patterns

### API Design for Agents

**Requirements:**
- Rich, structured data (no parsing needed)
- Context preservation across interactions
- High efficiency (minimize round trips)
- Robust error handling

**Best Practices:**
| Practice | Bad | Good |
|----------|-----|------|
| Naming | `userId`, `user_id`, `uid` | Single convention |
| Structure | Deeply nested | Flat, simple |
| Auth | Interactive login | OAuth 2.0, API keys |
| Errors | Generic | Structured + actionable |

---

## 7. Conversational UX Patterns

### Three Interaction Modes

**1. Collaborative (Synchronous)**
- User and agent work together in real-time
- Best for: Complex tasks, creative work
- Example: Cursor Chat

**2. Embedded (Automatic)**
- Agent provides suggestions without request
- Best for: Repetitive tasks, completions
- Example: Tab autocomplete

**3. Asynchronous (Background)**
- Agent works independently, reports back
- Best for: Time-consuming operations
- Example: Background processing

### Conversation Principles
- Humanize responses (user's language, not jargon)
- Remember past interactions
- Keep responses concise
- Allow interruptions and direction changes
- Confirm understanding of ambiguous requests

---

## 8. Agent-First Design Considerations

### Intent-First Architecture
```
Traditional: User journey → Interface design → Features
Agentic: Intent mapping → Agent behaviors → UX affordances
```

### Design Questions
- What does the user want to accomplish?
- What agent capabilities enable this intent?
- How does interface adapt to both user intent and agent capabilities?

### Key Principles
1. Design around outcomes, not flows
2. Start with user goals → agent behaviors → UX
3. Agent autonomy with human oversight
4. Adaptive experiences responding to context

---

## 9. Trust & Transparency

### Transparency Dashboard Components
- Reasoning panels (show thought process)
- Action cards (planned/completed actions)
- Confidence indicators
- Source attribution
- Decision visualization

### Control Mechanisms
- User preferences and customization
- Ability to reset agent knowledge
- Override mechanisms for suggestions
- Audit trails of decisions

---

## 10. Implementation Checklist

### Starting a New Agentic Feature
- [ ] Define user intents (not just features)
- [ ] Design capability schema (OpenAPI/JSON Schema)
- [ ] Plan progressive disclosure levels
- [ ] Design feedback collection mechanisms
- [ ] Plan error handling and recovery
- [ ] Consider transparency requirements
- [ ] Test with actual agent interactions

### API Readiness for Agents
- [ ] Schema exposed at known endpoint
- [ ] Consistent naming conventions
- [ ] Flat, simple data structures
- [ ] Machine-friendly authentication
- [ ] Structured error responses
- [ ] Rate limiting designed for automation

---

## References

- [Anthropic: Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic: Agent Skills Framework](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Microsoft: UX Design for Agents](https://microsoft.design/articles/ux-design-for-agents/)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Full Research Document](../research/agentic-ux-design-principles.md)
