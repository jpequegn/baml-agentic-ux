"""Init command for scaffolding LUI templates."""

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table

from src.templates import AVAILABLE_TEMPLATES, get_template_dir
from src.cli.scaffolder import scaffold_template

console = Console()


@dataclass
class InitArgs:
    """Parsed arguments for init command."""
    template: Optional[str] = None
    name: Optional[str] = None
    output: Optional[str] = None
    force: bool = False
    list_templates: bool = False


def parse_args(args: list[str] = None) -> InitArgs:
    """Parse command line arguments.

    Args:
        args: List of arguments (defaults to sys.argv[1:])

    Returns:
        Parsed InitArgs
    """
    parser = argparse.ArgumentParser(
        description="Scaffold a LUI template project",
        prog="baml-agentic-ux init",
    )

    parser.add_argument(
        "-t", "--template",
        help="Template name (crud, search, workflow, support)",
    )
    parser.add_argument(
        "-n", "--name",
        help="Project name",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output directory (defaults to ./<name>)",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Overwrite existing directory",
    )
    parser.add_argument(
        "--list",
        dest="list_templates",
        action="store_true",
        help="List available templates",
    )

    parsed = parser.parse_args(args)

    return InitArgs(
        template=parsed.template,
        name=parsed.name,
        output=parsed.output,
        force=parsed.force,
        list_templates=parsed.list_templates,
    )


def list_templates() -> None:
    """Display available templates."""
    table = Table(title="Available Templates")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")

    for name, desc in AVAILABLE_TEMPLATES.items():
        table.add_row(name, desc)

    console.print(table)


def run_interactive() -> InitArgs:
    """Run interactive mode to gather arguments.

    Returns:
        InitArgs populated from user input
    """
    import questionary

    console.print("\n[bold]Welcome to BAML Agentic UX![/bold] Let's scaffold a LUI project.\n")

    # Select template
    template_choices = [
        questionary.Choice(f"{name} - {desc}", value=name)
        for name, desc in AVAILABLE_TEMPLATES.items()
    ]

    template = questionary.select(
        "Select a template:",
        choices=template_choices,
    ).ask()

    if not template:
        sys.exit(1)

    # Get project name
    name = questionary.text(
        "Project name:",
        validate=lambda x: len(x) > 0 or "Name is required",
    ).ask()

    if not name:
        sys.exit(1)

    # Get output directory
    default_output = f"./{name}"
    output = questionary.text(
        "Output directory:",
        default=default_output,
    ).ask()

    if not output:
        output = default_output

    return InitArgs(
        template=template,
        name=name,
        output=output,
        force=False,
        list_templates=False,
    )


def run_scaffold(args: InitArgs) -> None:
    """Run the scaffolding process.

    Args:
        args: Parsed arguments
    """
    template_dir = get_template_dir(args.template)
    output_dir = Path(args.output or f"./{args.name}")

    if output_dir.exists() and not args.force:
        console.print(f"[red]Error:[/red] Directory {output_dir} already exists.")
        console.print("Use --force to overwrite.")
        sys.exit(1)

    console.print(f"\n[bold]Creating project...[/bold]")

    created_files = scaffold_template(
        template_dir=template_dir,
        project_name=args.name,
        output_dir=output_dir,
    )

    for f in created_files:
        console.print(f"  [green]+[/green] Created {f.name}")

    console.print(f"\n[bold green]Done![/bold green] Next steps:")
    console.print(f"  cd {output_dir}")
    console.print(f"  cat README.md        # Start here to learn the patterns")
    console.print(f"  python integration.py  # Run the example")


def main(args: list[str] = None) -> int:
    """Main entry point for init command.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success)
    """
    parsed = parse_args(args)

    if parsed.list_templates:
        list_templates()
        return 0

    # If template and name provided, run directly
    if parsed.template and parsed.name:
        run_scaffold(parsed)
        return 0

    # Otherwise, run interactive mode
    interactive_args = run_interactive()
    run_scaffold(interactive_args)
    return 0
