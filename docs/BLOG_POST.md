# Building Type-Safe Language User Interfaces with BAML

*A deep dive into designing, generating, and validating conversational AI interfaces*

---

## The Problem with Conversational AI

Building conversational interfaces is hard. Not because understanding language is hard (LLMs handle that), but because the **structure around language** is messy:

- How do you define what your interface can do?
- How do you handle ambiguous user intent?
- How do you ensure consistent responses?
- How do you test conversations?

Most teams solve this with brittle pattern matching, custom NLU pipelines, or prayer. There's a better way.

## Enter BAML: Type-Safe AI Interactions

[BAML](https://github.com/BoundaryML/baml) (Boundary AI Markup Language) brings type safety to AI applications. Originally designed for structured data extraction, we explored whether its principles could transform Language User Interface (LUI) development.

**Spoiler**: They can.

## What We Built

Over 12 implementation tasks, we developed a complete LUI framework:

```
┌─────────────────────────────────────────────────────────┐
│                    LUI FRAMEWORK                        │
├─────────────────────────────────────────────────────────┤
│  Schema Definition  →  LUI Generator  →  Simulator      │
│         ↓                   ↓               ↓           │
│  Intent Extraction  →  Response Gen  →  Usability       │
│         ↓                   ↓               ↓           │
│  OpenAPI / MCP / TypeScript / Markdown Export           │
└─────────────────────────────────────────────────────────┘
```

## Key Insight #1: Invocation Patterns

Every conversational command needs multiple entry points:

```baml
class InvocationPattern {
  primary_phrase string    // "create task"
  alternate_phrases string[] // ["add task", "new task"]
  examples string[]        // ["Create a task called review code"]
}
```

Users don't speak in commands. They say "add something for tomorrow" or "I need to remember to call John." Your interface must recognize all these as the same intent.

## Key Insight #2: Ambiguity is Normal

"Show me my tasks" could mean:
- List all tasks
- Search for something specific
- Filter by some criteria

We built explicit ambiguity handling:

```baml
class Ambiguity {
  is_ambiguous bool
  alternatives IntentAlternative[]
  disambiguation_question string // "Did you mean list all tasks or search?"
}
```

Instead of guessing, **ask**. Users prefer clarification over wrong actions.

## Key Insight #3: Context Changes Everything

Conversational interfaces need memory:

```baml
class GlobalContext {
  session_variables string[]     // ["current_project_id"]
  persistent_variables string[]  // ["preferred_theme"]
  context_hints string[]         // ["Remember the selected task"]
}
```

"Delete it" only makes sense if the system knows what "it" refers to.

## Key Insight #4: Feedback Templates

Structured responses feel more reliable:

```baml
class FeedbackConfig {
  success_template string  // "Task '{title}' created (ID: {id})"
  error_template string    // "Could not create task: {error}"
  confirmation_prompt string? // "Delete '{title}'? Cannot be undone."
}
```

Users learn the patterns and trust the system more.

## The Real Test: P3 Podcast Processor

We applied this framework to a real application—a CLI tool for processing podcasts:

**Before (CLI)**:
```bash
p3 fetch --max-episodes 5
p3 transcribe --episode-id 42
p3 digest --provider ollama
p3 export --format markdown
```

**After (LUI)**:
```
User: "Process today's podcasts and give me a summary"
System: "I'll fetch, transcribe, and summarize new episodes. Continue?"
User: "Yes"
System: "Processing... Found 3 new episodes from All-In and Lex Friedman..."
```

The LUI version:
- Fewer steps (1 vs 4)
- Natural language
- Confirmation for safety
- Progress feedback

But the CLI is better for batch scripting. **The answer is hybrid interfaces**.

## What BAML Does Well

1. **Type-Safe Outputs**: AI responses are parsed into structured types
2. **Declarative Prompts**: Clean separation of prompt logic from types
3. **Generated Clients**: Auto-generated Python/TypeScript with full type hints
4. **Error Handling**: Clear errors when outputs don't match schemas

## What Needs Improvement

1. **State Management**: Functions are stateless; context must be passed explicitly
2. **Schema Import**: No native JSON/YAML schema loading
3. **Streaming**: Complex types require full response before parsing

## The Patterns That Work

After building this framework, we identified six patterns every LUI needs:

| Pattern | Description |
|---------|-------------|
| **Invocation Triad** | Primary phrase + alternates + examples |
| **Feedback Templates** | Parameterized success/error messages |
| **Confirmation Gates** | Required confirmation for destructive actions |
| **Entity Resolution** | Multiple ways to reference entities (ID, name, "latest") |
| **Composite Actions** | Single invocations for common workflows |
| **Weighted Scoring** | Category-based usability assessment |

## Future Directions

This research opens several paths:

1. **Multi-Modal LUI**: Voice + text + visual in one interface
2. **Adaptive Interfaces**: Behavior adapts to user expertise
3. **Agent-to-Agent Negotiation**: AI systems negotiating shared interfaces
4. **LUI Accessibility Standards**: WCAG equivalents for conversations

## Try It Yourself

The complete framework is open source:

```bash
git clone https://github.com/jpequegn/baml-agentic-ux
cd baml-agentic-ux
uv sync
uv run pytest  # 254 tests
```

Explore the schemas, generate your own LUI, and run usability analysis.

## Conclusion

BAML's type-safe approach transforms LUI development from ad-hoc scripting to structured engineering. The patterns we discovered—invocation triads, ambiguity handling, context management—apply whether you're building chatbots, voice assistants, or AI agents.

The future of human-computer interaction is conversational. Make it type-safe.

---

*This research was conducted as part of exploring agentic UX patterns with BAML. Full documentation at [docs/RESEARCH_SYNTHESIS.md](./RESEARCH_SYNTHESIS.md).*
