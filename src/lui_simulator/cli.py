"""CLI interface for the LUI Simulator."""

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint

from .simulator import LUISimulator, load_schema_from_dict
from .context import SimulatorConfig, SimulatorMode
from baml_client.types import ResponseTone, FormalityLevel, ExpertiseLevel

# Import schema import functionality
from lui_schema_import import (
    import_json_schema,
    import_yaml_schema,
    generate_baml_types,
)

app = typer.Typer(
    name="lui-sim",
    help="Interactive LUI Simulator - Test Language User Interface schemas",
    add_completion=False,
)

console = Console()


def load_schema(schema_path: str) -> dict:
    """Load a schema from a JSON file."""
    path = Path(schema_path)
    if not path.exists():
        raise typer.BadParameter(f"Schema file not found: {schema_path}")

    with open(path) as f:
        return json.load(f)


@app.command()
def simulate(
    schema_path: str = typer.Argument(..., help="Path to the LUI schema JSON file"),
    tone: str = typer.Option("friendly", help="Response tone (professional, friendly, empathetic, direct)"),
    formality: str = typer.Option("neutral", help="Formality level (formal, neutral, casual)"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose mode"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode"),
    log_file: Optional[str] = typer.Option(None, "--log", "-l", help="Path to log file"),
):
    """Run an interactive simulation session with a LUI schema."""
    # Load schema
    try:
        schema_data = load_schema(schema_path)
        schema = load_schema_from_dict(schema_data)
    except Exception as e:
        console.print(f"[red]Error loading schema: {e}[/red]")
        raise typer.Exit(1)

    # Configure simulator
    tone_map = {
        "professional": ResponseTone.PROFESSIONAL,
        "friendly": ResponseTone.FRIENDLY,
        "empathetic": ResponseTone.EMPATHETIC,
        "direct": ResponseTone.DIRECT,
        "calm": ResponseTone.CALM,
        "enthusiastic": ResponseTone.ENTHUSIASTIC,
        "playful": ResponseTone.PLAYFUL,
    }

    formality_map = {
        "very_formal": FormalityLevel.VERY_FORMAL,
        "formal": FormalityLevel.FORMAL,
        "neutral": FormalityLevel.NEUTRAL,
        "casual": FormalityLevel.CASUAL,
        "very_casual": FormalityLevel.VERY_CASUAL,
    }

    mode = SimulatorMode.INTERACTIVE
    if verbose:
        mode = SimulatorMode.VERBOSE
    elif debug:
        mode = SimulatorMode.DEBUG

    config = SimulatorConfig(
        tone=tone_map.get(tone.lower(), ResponseTone.FRIENDLY),
        formality=formality_map.get(formality.lower(), FormalityLevel.NEUTRAL),
        mode=mode,
        log_to_file=log_file is not None,
        log_file_path=log_file,
    )

    # Create simulator
    simulator = LUISimulator(schema, config)

    # Print welcome message
    console.print(Panel.fit(
        f"[bold blue]LUI Simulator[/bold blue]\n"
        f"Schema: [green]{schema.name}[/green]\n"
        f"Components: {len(schema.components)}\n"
        f"Tone: {tone} | Formality: {formality}",
        title="Session Started",
    ))

    console.print("\n[dim]Commands: 'quit' to exit, 'debug' for state, 'reset' to clear, 'help' for commands[/dim]\n")

    # Interactive loop
    while True:
        try:
            user_input = console.input("[bold cyan]You:[/bold cyan] ")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Session ended.[/yellow]")
            break

        user_input = user_input.strip()

        if not user_input:
            continue

        # Handle special commands
        if user_input.lower() == "quit":
            console.print("[yellow]Goodbye![/yellow]")
            break

        if user_input.lower() == "debug":
            _show_debug_info(simulator)
            continue

        if user_input.lower() == "reset":
            simulator.reset()
            console.print("[yellow]Simulator reset.[/yellow]")
            continue

        if user_input.lower() == "help":
            _show_help()
            continue

        if user_input.lower() == "transcript":
            console.print(Panel(simulator.get_transcript(), title="Conversation Transcript"))
            continue

        if user_input.lower() == "components":
            _show_components(simulator)
            continue

        if user_input.lower() == "save":
            path = simulator.save_session()
            console.print(f"[green]Session saved to: {path}[/green]")
            continue

        # Process user input
        try:
            result = simulator.process_input(user_input)

            # Display response
            if result.response_type.value == "ERROR":
                console.print(f"[bold red]LUI:[/bold red] {result.response_text}\n")
            elif result.was_ambiguous:
                console.print(f"[bold yellow]LUI:[/bold yellow] {result.response_text}\n")
            else:
                console.print(f"[bold green]LUI:[/bold green] {result.response_text}\n")

            # Show follow-up if available
            if result.follow_up_suggestion:
                console.print(f"[dim]Suggestion: {result.follow_up_suggestion}[/dim]\n")

            # Verbose mode: show processing info
            if config.mode == SimulatorMode.VERBOSE and result.intent_extracted:
                console.print(f"[dim]Intent: {result.intent_extracted.detected_intent.intent_name} "
                            f"(confidence: {result.intent_extracted.confidence:.2f})[/dim]")
                console.print(f"[dim]Processing time: {result.processing_time_ms}ms[/dim]\n")

        except Exception as e:
            console.print(f"[red]Error: {e}[/red]\n")


def _show_debug_info(simulator: LUISimulator) -> None:
    """Display debug information."""
    info = simulator.get_debug_info()

    table = Table(title="Debug Information")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    # Context info
    ctx = info["context"]
    table.add_row("Session ID", ctx["session_id"])
    table.add_row("Started At", ctx["started_at"])
    table.add_row("Interactions", str(ctx["interaction_count"]))
    table.add_row("Messages", str(ctx["message_count"]))
    table.add_row("Current State", ctx["current_state"] or "None")
    table.add_row("Active Entity", ctx["active_entity"] or "None")
    table.add_row("Schema", ctx["schema_name"])
    table.add_row("Components", str(ctx["component_count"]))

    # Config info
    cfg = info["config"]
    table.add_row("Mode", cfg["mode"])
    table.add_row("Tone", cfg["tone"])
    table.add_row("Formality", cfg["formality"])

    console.print(table)


def _show_components(simulator: LUISimulator) -> None:
    """Display available components."""
    table = Table(title="Available Components")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Intent", style="green")
    table.add_column("Invocation", style="blue")

    for comp in simulator.schema.components:
        table.add_row(
            comp.component_id,
            comp.component_type.value,
            comp.intent[:40] + "..." if len(comp.intent) > 40 else comp.intent,
            comp.invocation.primary_phrase,
        )

    console.print(table)


def _show_help() -> None:
    """Display help information."""
    help_text = """
## Available Commands

| Command | Description |
|---------|-------------|
| `quit` | Exit the simulator |
| `debug` | Show debug information |
| `reset` | Clear conversation and reset state |
| `transcript` | Show conversation transcript |
| `components` | List available components |
| `save` | Save session to file |
| `help` | Show this help message |

## Tips

- Just type naturally to interact with the LUI
- The simulator will extract your intent and respond
- Use `debug` to see what's happening internally
"""
    console.print(Markdown(help_text))


@app.command()
def info(schema_path: str = typer.Argument(..., help="Path to the LUI schema JSON file")):
    """Display information about a LUI schema."""
    try:
        schema_data = load_schema(schema_path)
        schema = load_schema_from_dict(schema_data)
    except Exception as e:
        console.print(f"[red]Error loading schema: {e}[/red]")
        raise typer.Exit(1)

    console.print(Panel.fit(
        f"[bold]{schema.name}[/bold]\n"
        f"ID: {schema.schema_id}\n"
        f"Version: {schema.version}\n"
        f"Description: {schema.description}\n\n"
        f"Domain: {schema.domain.domain_name}\n"
        f"Components: {len(schema.components)}\n"
        f"Flows: {len(schema.flows) if schema.flows else 0}",
        title="Schema Information",
    ))

    if schema.components:
        _show_components_table(schema.components)


def _show_components_table(components) -> None:
    """Display components in a table."""
    table = Table(title="Components")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("Intent", style="green")

    for comp in components:
        table.add_row(
            comp.component_id,
            comp.component_type.value,
            comp.intent,
        )

    console.print(table)


@app.command(name="import")
def import_schema(
    source_path: str = typer.Argument(..., help="Path to JSON Schema or OpenAPI/YAML file"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (defaults to stdout)"),
    format: str = typer.Option("lui", "--format", "-f", help="Output format: lui (InterfaceSchema JSON), baml (BAML types)"),
    domain: str = typer.Option("imported", "--domain", "-d", help="Domain name for the imported schema"),
    schema_id: Optional[str] = typer.Option(None, "--id", help="Schema ID (auto-generated if not provided)"),
):
    """Import a JSON Schema or OpenAPI/YAML file into LUI format.

    Supports:
    - JSON Schema (draft-07 and later)
    - OpenAPI 3.x specifications (YAML or JSON)
    - Custom YAML schema definitions

    Examples:
        # Import JSON Schema and output LUI schema
        lui-sim import api/schema.json -o lui_schema.json

        # Import OpenAPI spec and generate BAML types
        lui-sim import api/openapi.yaml -f baml -o types.baml

        # Import and view without saving
        lui-sim import schema.json
    """
    source = Path(source_path)

    if not source.exists():
        console.print(f"[red]Error: File not found: {source_path}[/red]")
        raise typer.Exit(1)

    try:
        # Determine file type and import
        suffix = source.suffix.lower()

        if suffix in (".yaml", ".yml"):
            console.print(f"[dim]Importing YAML schema from {source_path}...[/dim]")
            lui_schema = import_yaml_schema(source, schema_id=schema_id, domain_name=domain)
        else:
            console.print(f"[dim]Importing JSON Schema from {source_path}...[/dim]")
            lui_schema = import_json_schema(source, schema_id=schema_id, domain_name=domain)

        # Generate output based on format
        if format.lower() == "baml":
            output_content = generate_baml_types(lui_schema)
            file_ext = ".baml"
        else:
            # Default to LUI/JSON format
            output_content = json.dumps(_schema_to_dict(lui_schema), indent=2)
            file_ext = ".json"

        # Output results
        if output:
            output_path = Path(output)
            with open(output_path, "w") as f:
                f.write(output_content)
            console.print(f"[green]✓ Schema imported successfully to: {output_path}[/green]")
        else:
            # Print to stdout
            console.print(Panel(output_content, title=f"Imported Schema ({format.upper()})"))

        # Show summary
        console.print(f"\n[bold]Import Summary:[/bold]")
        console.print(f"  Schema ID: [cyan]{lui_schema.schema_id}[/cyan]")
        console.print(f"  Name: [green]{lui_schema.name}[/green]")
        console.print(f"  Components: [yellow]{len(lui_schema.components)}[/yellow]")
        if lui_schema.components:
            for comp in lui_schema.components[:5]:  # Show first 5
                console.print(f"    - {comp.component_id} ({comp.component_type.value})")
            if len(lui_schema.components) > 5:
                console.print(f"    ... and {len(lui_schema.components) - 5} more")

    except ImportError as e:
        console.print(f"[red]Error: {e}[/red]")
        console.print("[dim]Hint: Install PyYAML for YAML support: pip install pyyaml[/dim]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error importing schema: {e}[/red]")
        raise typer.Exit(1)


def _schema_to_dict(schema) -> dict:
    """Convert InterfaceSchema to a dictionary for JSON output."""
    # Use Pydantic's model_dump if available
    if hasattr(schema, "model_dump"):
        return schema.model_dump(mode="json")
    elif hasattr(schema, "dict"):
        return schema.dict()
    else:
        # Manual conversion fallback
        return {
            "schema_id": schema.schema_id,
            "name": schema.name,
            "description": schema.description,
            "version": schema.version,
            "domain": {
                "domain_name": schema.domain.domain_name,
                "description": schema.domain.description,
            } if schema.domain else None,
            "components": [
                {
                    "component_id": c.component_id,
                    "component_type": c.component_type.value,
                    "intent": c.intent,
                }
                for c in schema.components
            ],
        }


@app.command()
def validate(schema_path: str = typer.Argument(..., help="Path to the LUI schema JSON file")):
    """Validate a LUI schema file."""
    try:
        schema_data = load_schema(schema_path)
        schema = load_schema_from_dict(schema_data)

        # Basic validation
        issues = []

        if not schema.name:
            issues.append("Schema name is empty")

        if not schema.components:
            issues.append("Schema has no components")

        for comp in schema.components:
            if not comp.invocation.primary_phrase:
                issues.append(f"Component '{comp.component_id}' has no primary invocation phrase")
            if not comp.feedback.success_template:
                issues.append(f"Component '{comp.component_id}' has no success template")

        if issues:
            console.print("[yellow]Validation warnings:[/yellow]")
            for issue in issues:
                console.print(f"  [yellow]⚠[/yellow] {issue}")
        else:
            console.print("[green]✓ Schema is valid[/green]")

    except Exception as e:
        console.print(f"[red]✗ Validation failed: {e}[/red]")
        raise typer.Exit(1)


def main():
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
