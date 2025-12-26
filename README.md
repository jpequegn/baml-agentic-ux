# BAML Agentic UX

Exploring Language User Interfaces (LUI) and agent-first design patterns using BAML.

## Project Overview

This project investigates the paradigm shift from traditional GUIs to LUIs (Language User Interfaces) for AI agents. Using BAML (Boundary AI Markup Language), we explore how to design interfaces that are optimized for both human users and AI agents.

### Goals

1. **Generate LUI Schemas from Requirements** - Create machine-readable interface definitions from natural language requirements
2. **Create Agent-Friendly Interface Definitions** - Design APIs and schemas optimized for AI agent consumption
3. **Compare with Traditional UI Components** - Analyze differences between GUI and LUI design patterns

### Key Concepts

- **Intent-Based Design**: Shifting from interface-centric to intent-centric design
- **Progressive Disclosure**: Loading capabilities on-demand rather than all at once
- **Dynamic Capability Discovery**: Agents discover available actions at runtime
- **Feedback Loops**: Continuous improvement through user and agent feedback

## Project Structure

```
baml-agentic-ux/
├── baml_src/           # BAML definitions
│   ├── clients.baml    # LLM client configurations
│   ├── generators.baml # Code generation settings
│   └── resume.baml     # Example BAML function
├── docs/               # Documentation
│   └── design_principles.md  # Agentic UX design principles
├── research/           # Research materials
│   └── agentic-ux-design-principles.md  # Comprehensive research
├── main.py            # Entry point
└── pyproject.toml     # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) package manager
- [BAML CLI](https://docs.boundaryml.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/jpequegn/baml-agentic-ux.git
cd baml-agentic-ux

# Install dependencies
uv sync

# Generate BAML client code
baml-cli generate
```

### Running

```bash
# Activate virtual environment
source .venv/bin/activate

# Run the main script
python main.py
```

## Design Principles

See [docs/design_principles.md](docs/design_principles.md) for the complete set of agentic UX design principles including:

- Interface discovery patterns
- Action capability declaration
- Feedback loop design
- Error handling in conversational UI
- Progressive disclosure for agents
- Machine-readable interface patterns

## Research

Comprehensive research on agentic UX is available in [research/agentic-ux-design-principles.md](research/agentic-ux-design-principles.md), covering:

- GUI → LUI paradigm shift
- Language User Interface patterns
- Model Context Protocol (MCP)
- Industry adoption trends
- Implementation best practices

## Tech Stack

- **BAML** - Type-safe AI function definitions
- **Python** - Primary language
- **Pydantic** - Data validation
- **uv** - Package management

## License

MIT
