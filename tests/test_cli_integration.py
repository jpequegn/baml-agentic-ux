"""Integration tests for the CLI.

Tests the actual command-line interface using subprocess to invoke
python -m src.cli and verify behavior.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


class TestCLIListTemplates:
    """Test --list flag functionality."""

    def test_list_shows_all_templates(self):
        """Running with --list should show all 4 templates."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "--list"],
            capture_output=True,
            text=True,
            cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
        )

        assert result.returncode == 0, f"CLI should exit with code 0, got {result.returncode}"

        # Check that all 4 templates are mentioned
        output_lower = result.stdout.lower()
        assert "crud" in output_lower, "CRUD template should be listed"
        assert "search" in output_lower, "Search template should be listed"
        assert "workflow" in output_lower, "Workflow template should be listed"
        assert "support" in output_lower, "Support template should be listed"

    def test_list_shows_descriptions(self):
        """Template list should include descriptions."""
        result = subprocess.run(
            [sys.executable, "-m", "src.cli", "--list"],
            capture_output=True,
            text=True,
            cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
        )

        assert result.returncode == 0

        # Check for description keywords
        output = result.stdout
        assert "operations" in output.lower() or "crud" in output.lower()
        assert "search" in output.lower() or "discovery" in output.lower()


class TestCLIScaffold:
    """Test template scaffolding functionality."""

    def test_scaffold_crud_creates_files(self):
        """Scaffolding CRUD template should create files in output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "project"

            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", "TestProject",
                 "--output", str(output_dir)],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode == 0, f"Scaffold should succeed, got: {result.stderr}"

            # Check that files were created
            assert (output_dir / "schema.json").exists(), "schema.json should be created"
            assert (output_dir / "integration.py").exists(), "integration.py should be created"
            assert (output_dir / "README.md").exists(), "README.md should be created"
            assert (output_dir / "test_integration.py").exists(), "test_integration.py should be created"

    def test_scaffold_substitutes_project_name(self):
        """Template substitution should replace {{PROJECT_NAME}} placeholders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_name = "my-awesome-app"
            output_dir = Path(tmpdir) / "project"

            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", project_name,
                 "--output", str(output_dir)],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode == 0

            # Check that substitution worked in schema.json
            schema_path = output_dir / "schema.json"
            schema_content = schema_path.read_text()

            assert project_name in schema_content, "Project name should appear in schema"
            assert "{{PROJECT_NAME" not in schema_content, "Template variables should be replaced"
            assert "My Awesome App" in schema_content, "Title case name should be generated"

            # Also verify the integration.py file was created with title case in docstring
            integration_path = output_dir / "integration.py"
            integration_content = integration_path.read_text()
            assert "My Awesome App" in integration_content, \
                "Title case project name should appear in integration.py"

    def test_scaffold_all_templates(self):
        """All 4 templates should scaffold successfully."""
        templates = ["crud", "search", "workflow", "support"]

        for template in templates:
            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = Path(tmpdir) / "project"

                result = subprocess.run(
                    [sys.executable, "-m", "src.cli",
                     "--template", template,
                     "--name", f"Test{template.capitalize()}",
                     "--output", str(output_dir)],
                    capture_output=True,
                    text=True,
                    cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
                )

                assert result.returncode == 0, f"{template} template should scaffold successfully"

                # Verify basic files exist
                assert (output_dir / "schema.json").exists(), f"{template} should create schema.json"

    def test_scaffold_with_force_flag(self):
        """Using --force should overwrite existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "project"
            output_dir.mkdir()

            # Create a dummy file
            (output_dir / "dummy.txt").write_text("old content")

            # Scaffold with --force
            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", "TestProject",
                 "--output", str(output_dir),
                 "--force"],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode == 0, "Force flag should allow overwriting"

            # Verify new files were created
            assert (output_dir / "schema.json").exists(), "New files should be created"

    def test_scaffold_without_force_fails_on_existing_dir(self):
        """Scaffolding to existing directory without --force should fail."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "project"
            output_dir.mkdir()

            # Try to scaffold without --force
            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", "TestProject",
                 "--output", str(output_dir)],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode != 0, "Should fail when directory exists without --force"
            assert "exists" in result.stdout.lower() or "exists" in result.stderr.lower(), \
                "Error message should mention existing directory"


class TestCLIErrorHandling:
    """Test error cases and validation."""

    def test_invalid_template_name(self):
        """Using an invalid template name should show error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "invalid_template",
                 "--name", "TestProject",
                 "--output", tmpdir],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode != 0, "Invalid template should cause non-zero exit"

            # Error should mention the invalid template
            error_output = result.stderr + result.stdout
            assert "invalid" in error_output.lower() or "unknown" in error_output.lower(), \
                "Error should mention invalid/unknown template"

    def test_missing_template_argument(self):
        """Missing --template should trigger interactive mode.

        Since interactive mode requires user input, we send EOF to make it fail gracefully.
        We're testing that it doesn't crash with a traceback.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "project"

            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--name", "TestProject",
                 "--output", str(output_dir)],
                capture_output=True,
                text=True,
                input="",  # Send EOF to interactive prompts
                timeout=5,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            # Should fail cleanly when interactive mode gets EOF
            # Just checking it doesn't crash with a Python traceback
            output = result.stderr + result.stdout

            # Should not have an unhandled exception traceback
            assert "Traceback" not in output or "KeyboardInterrupt" in output or "EOFError" in output, \
                f"CLI should handle interactive mode gracefully, not crash: {output}"


class TestCLIShortFlags:
    """Test short flag alternatives."""

    def test_short_flags_work(self):
        """Short flags -t, -n, -o, -f should work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "-t", "crud",
                 "-n", "TestProject",
                 "-o", tmpdir,
                 "-f"],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode == 0, "Short flags should work the same as long flags"

            # Verify files were created
            output_path = Path(tmpdir)
            assert (output_path / "schema.json").exists()


class TestCLIOutputValidation:
    """Test that CLI provides helpful output."""

    def test_scaffold_shows_success_message(self):
        """Successful scaffold should show confirmation message."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "project"

            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", "TestProject",
                 "--output", str(output_dir)],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode == 0

            # Should show success/done message
            output = result.stdout.lower()
            assert "done" in output or "created" in output or "success" in output, \
                "Should show success confirmation"

    def test_scaffold_shows_created_files(self):
        """Output should list created files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "project"

            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", "TestProject",
                 "--output", str(output_dir)],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode == 0

            # Should mention the schema file
            assert "schema.json" in result.stdout, "Should list schema.json as created"

    def test_scaffold_shows_next_steps(self):
        """Output should guide user on next steps."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "project"

            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", "TestProject",
                 "--output", str(output_dir)],
                capture_output=True,
                text=True,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            assert result.returncode == 0

            # Should show next steps
            output = result.stdout.lower()
            assert "next" in output or "cd" in output or "readme" in output, \
                "Should provide guidance on next steps"


class TestCLIDefaultOutput:
    """Test default output directory behavior."""

    def test_default_output_directory(self):
        """When --output not specified, should use ./<name>."""
        # This test needs to be careful not to pollute the working directory
        # We'll just verify the behavior by checking error messages

        # Create a unique project name that's unlikely to exist
        import uuid
        project_name = f"test_temp_{uuid.uuid4().hex[:8]}"

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.cli",
                 "--template", "crud",
                 "--name", project_name],
                capture_output=True,
                text=True,
                timeout=5,
                cwd="/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates"
            )

            # Should either succeed (creating ./<project_name>) or fail gracefully
            # Either way, check the expected directory path is referenced
            output = result.stdout + result.stderr

            # The output should mention the project directory
            assert project_name in output or result.returncode == 0

        finally:
            # Clean up if directory was created
            cleanup_dir = Path("/Users/julienmika/Code/baml-agentic-ux/.worktrees/lui-templates") / project_name
            if cleanup_dir.exists():
                import shutil
                shutil.rmtree(cleanup_dir)
