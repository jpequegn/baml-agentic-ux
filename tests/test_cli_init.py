"""Tests for init command."""

import pytest
from src.cli.init_command import parse_args, InitArgs


class TestParseArgs:
    """Test argument parsing."""

    def test_parses_template_flag(self):
        """Test parsing --template flag."""
        args = parse_args(["--template", "crud", "--name", "test"])
        assert args.template == "crud"

    def test_parses_short_template_flag(self):
        """Test parsing -t flag."""
        args = parse_args(["-t", "crud", "-n", "test"])
        assert args.template == "crud"

    def test_parses_name_flag(self):
        """Test parsing --name flag."""
        args = parse_args(["--template", "crud", "--name", "my-app"])
        assert args.name == "my-app"

    def test_parses_output_flag(self):
        """Test parsing --output flag."""
        args = parse_args(["-t", "crud", "-n", "test", "-o", "/tmp/out"])
        assert args.output == "/tmp/out"

    def test_list_flag(self):
        """Test parsing --list flag."""
        args = parse_args(["--list"])
        assert args.list_templates is True

    def test_force_flag(self):
        """Test parsing --force flag."""
        args = parse_args(["-t", "crud", "-n", "test", "--force"])
        assert args.force is True
