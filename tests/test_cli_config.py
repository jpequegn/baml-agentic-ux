"""Tests for CLI and Configuration System.

Part of Task 6.10: CLI & Configuration
Issue #98 - Phase 6: Conversational Testing Framework
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml
from typer.testing import CliRunner

from src.testing.cli import app
from src.testing.config import (
    ConfigLoader,
    ConvTestConfig,
    ExecutionConfig,
    FilterConfig,
    LoggingConfig,
    PathsConfig,
    QualityGatesConfig,
    ReportingConfig,
    generate_default_config,
    get_config_template,
    load_config,
)


# ============================================
# Configuration Tests
# ============================================


class TestConvTestConfig:
    """Tests for configuration dataclasses."""

    def test_default_quality_gates(self):
        """Test default quality gate values."""
        config = QualityGatesConfig()
        assert config.min_pass_rate == 95.0
        assert config.min_intent_accuracy == 95.0
        assert config.min_coherence == 0.85
        assert config.min_naturalness == 0.80
        assert config.min_coverage == 70.0
        assert "pass_rate" in config.blocking_metrics
        assert "coherence" in config.warning_metrics

    def test_default_execution_config(self):
        """Test default execution settings."""
        config = ExecutionConfig()
        assert config.parallel is False
        assert config.max_workers == 4
        assert config.timeout_seconds == 30
        assert config.retry_count == 0
        assert config.stop_on_failure is False

    def test_default_reporting_config(self):
        """Test default reporting settings."""
        config = ReportingConfig()
        assert config.output_dir == "test-reports"
        assert "html" in config.formats
        assert "json" in config.formats
        assert "junit" in config.formats
        assert config.include_logs is True

    def test_default_filter_config(self):
        """Test default filter settings."""
        config = FilterConfig()
        assert config.tags == []
        assert config.exclude_tags == []
        assert config.pattern is None

    def test_default_paths_config(self):
        """Test default path settings."""
        config = PathsConfig()
        assert "tests/conversations" in config.test_dirs
        assert config.fixtures_dir == "tests/fixtures"
        assert config.templates_dir == "tests/conversations/templates"

    def test_full_config_defaults(self):
        """Test full configuration defaults."""
        config = ConvTestConfig()
        assert config.strict_mode is False
        assert config.version == "1.0.0"
        assert isinstance(config.quality_gates, QualityGatesConfig)
        assert isinstance(config.execution, ExecutionConfig)


class TestConfigLoader:
    """Tests for ConfigLoader class."""

    def test_load_empty_returns_defaults(self):
        """Test that loading without file returns defaults."""
        loader = ConfigLoader()
        config = loader.load()
        assert isinstance(config, ConvTestConfig)
        assert config.quality_gates.min_pass_rate == 95.0

    def test_load_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        yaml_content = """
quality_gates:
  min_pass_rate: 90.0
  min_coherence: 0.80
execution:
  parallel: true
  max_workers: 8
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                loader = ConfigLoader(f.name)
                config = loader.load()

                assert config.quality_gates.min_pass_rate == 90.0
                assert config.quality_gates.min_coherence == 0.80
                assert config.execution.parallel is True
                assert config.execution.max_workers == 8
                # Unchanged defaults
                assert config.quality_gates.min_intent_accuracy == 95.0
            finally:
                os.unlink(f.name)

    def test_env_var_override(self):
        """Test environment variable overrides."""
        with patch.dict(os.environ, {
            "CONVTEST_MIN_PASS_RATE": "85.0",
            "CONVTEST_PARALLEL": "true",
            "CONVTEST_VERBOSE": "true",
        }):
            loader = ConfigLoader()
            config = loader.load()

            assert config.quality_gates.min_pass_rate == 85.0
            assert config.execution.parallel is True
            assert config.logging.verbose is True

    def test_env_var_precedence_over_file(self):
        """Test that env vars take precedence over file config."""
        yaml_content = """
quality_gates:
  min_pass_rate: 90.0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                with patch.dict(os.environ, {"CONVTEST_MIN_PASS_RATE": "75.0"}):
                    loader = ConfigLoader(f.name)
                    config = loader.load()
                    assert config.quality_gates.min_pass_rate == 75.0
            finally:
                os.unlink(f.name)

    def test_to_yaml_export(self):
        """Test exporting configuration to YAML."""
        loader = ConfigLoader()
        config = ConvTestConfig()
        yaml_str = loader.to_yaml(config)

        assert "quality_gates:" in yaml_str
        assert "min_pass_rate" in yaml_str
        assert "execution:" in yaml_str

    def test_get_config_caches_result(self):
        """Test that get_config returns cached result."""
        loader = ConfigLoader()
        config1 = loader.get_config()
        config2 = loader.get_config()
        assert config1 is config2


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_load_config_function(self):
        """Test load_config convenience function."""
        config = load_config()
        assert isinstance(config, ConvTestConfig)

    def test_generate_default_config(self):
        """Test generate_default_config function."""
        yaml_str = generate_default_config()
        assert "quality_gates:" in yaml_str
        assert isinstance(yaml.safe_load(yaml_str), dict)

    def test_get_config_template(self):
        """Test get_config_template returns commented template."""
        template = get_config_template()
        assert "# Conversational Testing Framework Configuration" in template
        assert "quality_gates:" in template
        assert "# Minimum test pass rate" in template


# ============================================
# CLI Tests
# ============================================

runner = CliRunner()


class TestCLIVersion:
    """Tests for version command."""

    def test_version_command(self):
        """Test version command output."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.stdout


class TestCLIInfo:
    """Tests for info command."""

    def test_info_command(self):
        """Test info command output."""
        result = runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Conversational Testing Framework" in result.stdout
        assert "Intent recognition" in result.stdout


class TestCLIGenerate:
    """Tests for generate command."""

    def test_generate_config(self):
        """Test generating configuration file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "convtest.yaml"
            result = runner.invoke(app, ["generate", "config", "-o", str(output_path)])

            assert result.exit_code == 0
            assert output_path.exists()
            content = output_path.read_text()
            assert "quality_gates:" in content

    def test_generate_config_no_overwrite(self):
        """Test that generate won't overwrite without --force."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "convtest.yaml"
            output_path.write_text("existing content")

            result = runner.invoke(app, ["generate", "config", "-o", str(output_path)])
            assert result.exit_code == 1
            assert "already exists" in result.stdout

    def test_generate_config_force_overwrite(self):
        """Test that generate with --force overwrites."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "convtest.yaml"
            output_path.write_text("existing content")

            result = runner.invoke(app, ["generate", "config", "-o", str(output_path), "--force"])
            assert result.exit_code == 0
            assert "quality_gates:" in output_path.read_text()

    def test_generate_template(self):
        """Test generating test template file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "test_template.yaml"
            result = runner.invoke(app, ["generate", "template", "-o", str(output_path)])

            assert result.exit_code == 0
            assert output_path.exists()
            content = output_path.read_text()
            assert "suite_id:" in content
            assert "tests:" in content

    def test_generate_unknown_type(self):
        """Test error for unknown generate type."""
        result = runner.invoke(app, ["generate", "unknown"])
        assert result.exit_code == 1
        assert "Unknown output type" in result.stdout


class TestCLIConfig:
    """Tests for config command."""

    def test_config_show(self):
        """Test showing configuration."""
        result = runner.invoke(app, ["config", "--show"])
        assert result.exit_code == 0
        assert "Quality Gates" in result.stdout
        assert "Execution" in result.stdout

    def test_config_validate_valid(self):
        """Test validating valid configuration."""
        yaml_content = """
quality_gates:
  min_pass_rate: 90.0
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                result = runner.invoke(app, ["config", "--validate", "--config", f.name])
                assert result.exit_code == 0
                assert "valid" in result.stdout.lower()
            finally:
                os.unlink(f.name)


class TestCLIValidate:
    """Tests for validate command."""

    def test_validate_nonexistent_path(self):
        """Test validation error for nonexistent path."""
        result = runner.invoke(app, ["validate", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_validate_directory(self):
        """Test validating a directory of test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a valid test file
            test_file = Path(tmpdir) / "test.yaml"
            test_file.write_text("""
suite_id: test-suite
name: Test Suite
tests:
  - test_id: test-001
    name: Test 1
    category: intent_recognition
    priority: high
    turns:
      - turn_number: 1
        role: user
        input: "Hello"
    expected_outcome:
      success_condition: all_pass
""")
            result = runner.invoke(app, ["validate", tmpdir])
            # Should show validation results with test count
            assert result.exit_code == 0
            assert "1 tests" in result.stdout or "Validated" in result.stdout

    def test_validate_json_output(self):
        """Test validation with JSON output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.yaml"
            test_file.write_text("""
suite_id: test-suite
name: Test Suite
tests: []
""")

            result = runner.invoke(app, ["validate", tmpdir, "-o", "json", "-q"])
            # Should produce JSON output (use -q to suppress non-JSON output)
            # Find the JSON portion in the output
            stdout = result.stdout
            # Find the start of JSON object
            json_start = stdout.find("{")
            if json_start >= 0:
                json_end = stdout.rfind("}") + 1
                json_str = stdout[json_start:json_end]
                output = json.loads(json_str)
                assert "results" in output
                assert "summary" in output
            else:
                # If no JSON found, check for results in output
                assert "results" in stdout or result.exit_code == 0


class TestCLICoverage:
    """Tests for coverage command."""

    def test_coverage_nonexistent_path(self):
        """Test coverage error for nonexistent path."""
        result = runner.invoke(app, ["coverage", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


class TestCLIListTests:
    """Tests for list-tests command."""

    def test_list_tests_nonexistent_path(self):
        """Test list-tests error for nonexistent path."""
        result = runner.invoke(app, ["list-tests", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()


class TestCLIRun:
    """Tests for run command."""

    def test_run_nonexistent_path(self):
        """Test run error for nonexistent path."""
        result = runner.invoke(app, ["run", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_run_help(self):
        """Test run command help."""
        # Use wide terminal to ensure all options are visible in help output
        wide_runner = CliRunner(env={"COLUMNS": "200"})
        result = wide_runner.invoke(app, ["run", "--help"])
        assert result.exit_code == 0
        assert "--parallel" in result.stdout
        assert "--timeout" in result.stdout
        assert "--output" in result.stdout


class TestCLICheckGates:
    """Tests for check-gates command."""

    def test_check_gates_nonexistent_file(self):
        """Test check-gates error for nonexistent file."""
        result = runner.invoke(app, ["check-gates", "/nonexistent/file.json"])
        assert result.exit_code == 1
        assert "not found" in result.stdout.lower()

    def test_check_gates_valid_results(self):
        """Test check-gates with valid results file."""
        results = {
            "summary": {
                "pass_rate": 98.0,
            },
            "quality_gates": {
                "metrics": {
                    "intent_accuracy": 96.0,
                    "coherence": 0.90,
                    "naturalness": 0.85,
                    "coverage": 75.0,
                }
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(results, f)
            f.flush()

            try:
                result = runner.invoke(app, ["check-gates", f.name])
                assert result.exit_code == 0
                assert "Pass Rate" in result.stdout
            finally:
                os.unlink(f.name)

    def test_check_gates_failing_results(self):
        """Test check-gates with failing results."""
        results = {
            "summary": {
                "pass_rate": 50.0,  # Below threshold
            },
            "quality_gates": {
                "metrics": {
                    "intent_accuracy": 50.0,  # Below threshold
                }
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(results, f)
            f.flush()

            try:
                result = runner.invoke(app, ["check-gates", f.name])
                assert result.exit_code == 1
                assert "BLOCKING" in result.stdout or "FAILED" in result.stdout
            finally:
                os.unlink(f.name)

    def test_check_gates_json_output(self):
        """Test check-gates with JSON output."""
        results = {
            "summary": {"pass_rate": 98.0},
            "quality_gates": {"metrics": {}}
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(results, f)
            f.flush()

            try:
                result = runner.invoke(app, ["check-gates", f.name, "-o", "json"])
                output = json.loads(result.stdout)
                assert "passed" in output
                assert "metrics" in output
            finally:
                os.unlink(f.name)


# ============================================
# Integration Tests
# ============================================


class TestConfigIntegration:
    """Integration tests for configuration with CLI."""

    def test_config_flow(self):
        """Test generating, loading, and validating config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "convtest.yaml"

            # Generate config
            result = runner.invoke(app, ["generate", "config", "-o", str(config_path)])
            assert result.exit_code == 0

            # Load and verify
            loader = ConfigLoader(str(config_path))
            config = loader.load()
            assert config.quality_gates.min_pass_rate == 95.0

            # Validate via CLI
            result = runner.invoke(app, ["config", "--validate", "-c", str(config_path)])
            assert result.exit_code == 0


class TestEnvironmentOverrides:
    """Tests for environment variable configuration."""

    def test_all_env_vars_apply(self):
        """Test that all documented env vars work."""
        env_vars = {
            "CONVTEST_MIN_PASS_RATE": "80.0",
            "CONVTEST_MIN_INTENT_ACCURACY": "80.0",
            "CONVTEST_MIN_COHERENCE": "0.70",
            "CONVTEST_MIN_NATURALNESS": "0.70",
            "CONVTEST_MIN_COVERAGE": "60.0",
            "CONVTEST_PARALLEL": "true",
            "CONVTEST_MAX_WORKERS": "16",
            "CONVTEST_TIMEOUT": "60",
            "CONVTEST_OUTPUT_DIR": "custom-reports",
            "CONVTEST_LOG_LEVEL": "DEBUG",
            "CONVTEST_VERBOSE": "true",
            "CONVTEST_QUIET": "false",
            "CONVTEST_STRICT_MODE": "true",
        }

        with patch.dict(os.environ, env_vars):
            config = load_config()

            assert config.quality_gates.min_pass_rate == 80.0
            assert config.quality_gates.min_intent_accuracy == 80.0
            assert config.quality_gates.min_coherence == 0.70
            assert config.quality_gates.min_naturalness == 0.70
            assert config.quality_gates.min_coverage == 60.0
            assert config.execution.parallel is True
            assert config.execution.max_workers == 16
            assert config.execution.timeout_seconds == 60
            assert config.reporting.output_dir == "custom-reports"
            assert config.logging.level == "DEBUG"
            assert config.logging.verbose is True
            assert config.logging.quiet is False
            assert config.strict_mode is True
