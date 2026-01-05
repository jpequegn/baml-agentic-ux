"""Configuration System for Conversational Testing Framework.

Provides YAML configuration file support with environment variable overrides.

Part of Task 6.10: CLI & Configuration
Issue #98 - Phase 6: Conversational Testing Framework
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml


# ============================================
# Configuration Dataclasses
# ============================================


@dataclass
class QualityGatesConfig:
    """Quality gate threshold configuration."""

    min_pass_rate: float = 95.0
    min_intent_accuracy: float = 95.0
    min_coherence: float = 0.85
    min_naturalness: float = 0.80
    min_coverage: float = 70.0
    blocking_metrics: list[str] = field(
        default_factory=lambda: ["pass_rate", "intent_accuracy"]
    )
    warning_metrics: list[str] = field(
        default_factory=lambda: ["coherence", "naturalness", "coverage"]
    )


@dataclass
class ExecutionConfig:
    """Test execution configuration."""

    parallel: bool = False
    max_workers: int = 4
    timeout_seconds: int = 30
    retry_count: int = 0
    retry_delay_seconds: float = 1.0
    stop_on_failure: bool = False
    random_seed: Optional[int] = None


@dataclass
class ReportingConfig:
    """Reporting configuration."""

    output_dir: str = "test-reports"
    formats: list[str] = field(default_factory=lambda: ["html", "json", "junit"])
    include_logs: bool = True
    include_metrics: bool = True
    timestamp_reports: bool = True
    generate_summary: bool = True


@dataclass
class FilterConfig:
    """Test filtering configuration."""

    tags: list[str] = field(default_factory=list)
    exclude_tags: list[str] = field(default_factory=list)
    categories: list[str] = field(default_factory=list)
    priorities: list[str] = field(default_factory=list)
    pattern: Optional[str] = None
    exclude_pattern: Optional[str] = None


@dataclass
class PathsConfig:
    """Path configuration."""

    test_dirs: list[str] = field(default_factory=lambda: ["tests/conversations"])
    fixtures_dir: str = "tests/fixtures"
    templates_dir: str = "tests/conversations/templates"
    output_dir: str = "test-reports"


@dataclass
class LoggingConfig:
    """Logging configuration."""

    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file: Optional[str] = None
    console: bool = True
    verbose: bool = False
    quiet: bool = False


@dataclass
class ConvTestConfig:
    """Main configuration for conversational testing framework."""

    quality_gates: QualityGatesConfig = field(default_factory=QualityGatesConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)
    reporting: ReportingConfig = field(default_factory=ReportingConfig)
    filters: FilterConfig = field(default_factory=FilterConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    strict_mode: bool = False
    version: str = "1.0.0"


# ============================================
# Environment Variable Mapping
# ============================================


ENV_VAR_MAPPING = {
    # Quality gates
    "CONVTEST_MIN_PASS_RATE": ("quality_gates", "min_pass_rate", float),
    "CONVTEST_MIN_INTENT_ACCURACY": ("quality_gates", "min_intent_accuracy", float),
    "CONVTEST_MIN_COHERENCE": ("quality_gates", "min_coherence", float),
    "CONVTEST_MIN_NATURALNESS": ("quality_gates", "min_naturalness", float),
    "CONVTEST_MIN_COVERAGE": ("quality_gates", "min_coverage", float),
    # Execution
    "CONVTEST_PARALLEL": ("execution", "parallel", lambda x: x.lower() == "true"),
    "CONVTEST_MAX_WORKERS": ("execution", "max_workers", int),
    "CONVTEST_TIMEOUT": ("execution", "timeout_seconds", int),
    "CONVTEST_RETRY_COUNT": ("execution", "retry_count", int),
    "CONVTEST_STOP_ON_FAILURE": (
        "execution",
        "stop_on_failure",
        lambda x: x.lower() == "true",
    ),
    # Reporting
    "CONVTEST_OUTPUT_DIR": ("reporting", "output_dir", str),
    "CONVTEST_REPORT_FORMATS": (
        "reporting",
        "formats",
        lambda x: x.split(","),
    ),
    # Logging
    "CONVTEST_LOG_LEVEL": ("logging", "level", str),
    "CONVTEST_VERBOSE": ("logging", "verbose", lambda x: x.lower() == "true"),
    "CONVTEST_QUIET": ("logging", "quiet", lambda x: x.lower() == "true"),
    # Global
    "CONVTEST_STRICT_MODE": ("strict_mode", None, lambda x: x.lower() == "true"),
}


# ============================================
# Configuration Loader
# ============================================


class ConfigLoader:
    """Loads and merges configuration from files and environment."""

    DEFAULT_CONFIG_FILES = [
        "convtest.yaml",
        "convtest.yml",
        ".convtest.yaml",
        ".convtest.yml",
        "pyproject.toml",  # [tool.convtest] section
    ]

    def __init__(self, config_file: Optional[str] = None):
        """Initialize config loader.

        Args:
            config_file: Optional explicit config file path.
        """
        self.config_file = config_file
        self._config: Optional[ConvTestConfig] = None

    def load(self) -> ConvTestConfig:
        """Load configuration with priority: env vars > explicit file > default files.

        Returns:
            Merged configuration.
        """
        # Start with defaults
        config = ConvTestConfig()

        # Load from file (if found)
        file_config = self._load_from_file()
        if file_config:
            config = self._merge_config(config, file_config)

        # Apply environment variable overrides
        config = self._apply_env_overrides(config)

        self._config = config
        return config

    def _find_config_file(self) -> Optional[Path]:
        """Find configuration file in current or parent directories.

        Returns:
            Path to config file or None.
        """
        if self.config_file:
            path = Path(self.config_file)
            if path.exists():
                return path
            return None

        # Search in current and parent directories
        current = Path.cwd()
        for _ in range(5):  # Max 5 levels up
            for filename in self.DEFAULT_CONFIG_FILES:
                config_path = current / filename
                if config_path.exists():
                    return config_path
            parent = current.parent
            if parent == current:
                break
            current = parent

        return None

    def _load_from_file(self) -> Optional[dict[str, Any]]:
        """Load configuration from file.

        Returns:
            Configuration dictionary or None.
        """
        config_path = self._find_config_file()
        if not config_path:
            return None

        if config_path.suffix == ".toml":
            return self._load_from_toml(config_path)
        else:
            return self._load_from_yaml(config_path)

    def _load_from_yaml(self, path: Path) -> dict[str, Any]:
        """Load configuration from YAML file.

        Args:
            path: Path to YAML file.

        Returns:
            Configuration dictionary.
        """
        with path.open() as f:
            data = yaml.safe_load(f) or {}
        return data

    def _load_from_toml(self, path: Path) -> dict[str, Any]:
        """Load configuration from TOML file (pyproject.toml).

        Args:
            path: Path to TOML file.

        Returns:
            Configuration dictionary from [tool.convtest] section.
        """
        try:
            import tomllib
        except ImportError:
            # Python < 3.11
            try:
                import tomli as tomllib  # type: ignore
            except ImportError:
                return {}

        with path.open("rb") as f:
            data = tomllib.load(f)

        return data.get("tool", {}).get("convtest", {})

    def _merge_config(
        self, base: ConvTestConfig, overrides: dict[str, Any]
    ) -> ConvTestConfig:
        """Merge configuration dictionary into config object.

        Args:
            base: Base configuration.
            overrides: Dictionary of overrides.

        Returns:
            Merged configuration.
        """
        # Quality gates
        if "quality_gates" in overrides:
            qg = overrides["quality_gates"]
            base.quality_gates.min_pass_rate = qg.get(
                "min_pass_rate", base.quality_gates.min_pass_rate
            )
            base.quality_gates.min_intent_accuracy = qg.get(
                "min_intent_accuracy", base.quality_gates.min_intent_accuracy
            )
            base.quality_gates.min_coherence = qg.get(
                "min_coherence", base.quality_gates.min_coherence
            )
            base.quality_gates.min_naturalness = qg.get(
                "min_naturalness", base.quality_gates.min_naturalness
            )
            base.quality_gates.min_coverage = qg.get(
                "min_coverage", base.quality_gates.min_coverage
            )
            if "blocking_metrics" in qg:
                base.quality_gates.blocking_metrics = qg["blocking_metrics"]
            if "warning_metrics" in qg:
                base.quality_gates.warning_metrics = qg["warning_metrics"]

        # Execution
        if "execution" in overrides:
            ex = overrides["execution"]
            base.execution.parallel = ex.get("parallel", base.execution.parallel)
            base.execution.max_workers = ex.get(
                "max_workers", base.execution.max_workers
            )
            base.execution.timeout_seconds = ex.get(
                "timeout_seconds", base.execution.timeout_seconds
            )
            base.execution.retry_count = ex.get(
                "retry_count", base.execution.retry_count
            )
            base.execution.retry_delay_seconds = ex.get(
                "retry_delay_seconds", base.execution.retry_delay_seconds
            )
            base.execution.stop_on_failure = ex.get(
                "stop_on_failure", base.execution.stop_on_failure
            )
            base.execution.random_seed = ex.get(
                "random_seed", base.execution.random_seed
            )

        # Reporting
        if "reporting" in overrides:
            rp = overrides["reporting"]
            base.reporting.output_dir = rp.get("output_dir", base.reporting.output_dir)
            if "formats" in rp:
                base.reporting.formats = rp["formats"]
            base.reporting.include_logs = rp.get(
                "include_logs", base.reporting.include_logs
            )
            base.reporting.include_metrics = rp.get(
                "include_metrics", base.reporting.include_metrics
            )
            base.reporting.timestamp_reports = rp.get(
                "timestamp_reports", base.reporting.timestamp_reports
            )
            base.reporting.generate_summary = rp.get(
                "generate_summary", base.reporting.generate_summary
            )

        # Filters
        if "filters" in overrides:
            fl = overrides["filters"]
            if "tags" in fl:
                base.filters.tags = fl["tags"]
            if "exclude_tags" in fl:
                base.filters.exclude_tags = fl["exclude_tags"]
            if "categories" in fl:
                base.filters.categories = fl["categories"]
            if "priorities" in fl:
                base.filters.priorities = fl["priorities"]
            base.filters.pattern = fl.get("pattern", base.filters.pattern)
            base.filters.exclude_pattern = fl.get(
                "exclude_pattern", base.filters.exclude_pattern
            )

        # Paths
        if "paths" in overrides:
            pt = overrides["paths"]
            if "test_dirs" in pt:
                base.paths.test_dirs = pt["test_dirs"]
            base.paths.fixtures_dir = pt.get("fixtures_dir", base.paths.fixtures_dir)
            base.paths.templates_dir = pt.get(
                "templates_dir", base.paths.templates_dir
            )
            base.paths.output_dir = pt.get("output_dir", base.paths.output_dir)

        # Logging
        if "logging" in overrides:
            lg = overrides["logging"]
            base.logging.level = lg.get("level", base.logging.level)
            base.logging.format = lg.get("format", base.logging.format)
            base.logging.file = lg.get("file", base.logging.file)
            base.logging.console = lg.get("console", base.logging.console)
            base.logging.verbose = lg.get("verbose", base.logging.verbose)
            base.logging.quiet = lg.get("quiet", base.logging.quiet)

        # Global
        base.strict_mode = overrides.get("strict_mode", base.strict_mode)
        base.version = overrides.get("version", base.version)

        return base

    def _apply_env_overrides(self, config: ConvTestConfig) -> ConvTestConfig:
        """Apply environment variable overrides to configuration.

        Args:
            config: Base configuration.

        Returns:
            Configuration with environment overrides applied.
        """
        for env_var, (section, attr, converter) in ENV_VAR_MAPPING.items():
            value = os.environ.get(env_var)
            if value is None:
                continue

            try:
                converted_value = converter(value)

                if attr is None:
                    # Top-level attribute
                    setattr(config, section, converted_value)
                else:
                    # Nested attribute
                    section_obj = getattr(config, section)
                    setattr(section_obj, attr, converted_value)
            except (ValueError, TypeError):
                # Skip invalid environment variable values
                pass

        return config

    def get_config(self) -> ConvTestConfig:
        """Get loaded configuration, loading if necessary.

        Returns:
            Configuration object.
        """
        if self._config is None:
            return self.load()
        return self._config

    def to_yaml(self, config: Optional[ConvTestConfig] = None) -> str:
        """Export configuration to YAML string.

        Args:
            config: Configuration to export, or current config if None.

        Returns:
            YAML string representation.
        """
        cfg = config or self.get_config()
        return yaml.dump(self._config_to_dict(cfg), default_flow_style=False)

    def _config_to_dict(self, config: ConvTestConfig) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Args:
            config: Configuration object.

        Returns:
            Dictionary representation.
        """
        return {
            "version": config.version,
            "strict_mode": config.strict_mode,
            "quality_gates": {
                "min_pass_rate": config.quality_gates.min_pass_rate,
                "min_intent_accuracy": config.quality_gates.min_intent_accuracy,
                "min_coherence": config.quality_gates.min_coherence,
                "min_naturalness": config.quality_gates.min_naturalness,
                "min_coverage": config.quality_gates.min_coverage,
                "blocking_metrics": config.quality_gates.blocking_metrics,
                "warning_metrics": config.quality_gates.warning_metrics,
            },
            "execution": {
                "parallel": config.execution.parallel,
                "max_workers": config.execution.max_workers,
                "timeout_seconds": config.execution.timeout_seconds,
                "retry_count": config.execution.retry_count,
                "retry_delay_seconds": config.execution.retry_delay_seconds,
                "stop_on_failure": config.execution.stop_on_failure,
                "random_seed": config.execution.random_seed,
            },
            "reporting": {
                "output_dir": config.reporting.output_dir,
                "formats": config.reporting.formats,
                "include_logs": config.reporting.include_logs,
                "include_metrics": config.reporting.include_metrics,
                "timestamp_reports": config.reporting.timestamp_reports,
                "generate_summary": config.reporting.generate_summary,
            },
            "filters": {
                "tags": config.filters.tags,
                "exclude_tags": config.filters.exclude_tags,
                "categories": config.filters.categories,
                "priorities": config.filters.priorities,
                "pattern": config.filters.pattern,
                "exclude_pattern": config.filters.exclude_pattern,
            },
            "paths": {
                "test_dirs": config.paths.test_dirs,
                "fixtures_dir": config.paths.fixtures_dir,
                "templates_dir": config.paths.templates_dir,
                "output_dir": config.paths.output_dir,
            },
            "logging": {
                "level": config.logging.level,
                "format": config.logging.format,
                "file": config.logging.file,
                "console": config.logging.console,
                "verbose": config.logging.verbose,
                "quiet": config.logging.quiet,
            },
        }


# ============================================
# Convenience Functions
# ============================================


def load_config(config_file: Optional[str] = None) -> ConvTestConfig:
    """Load configuration from file and environment.

    Args:
        config_file: Optional explicit config file path.

    Returns:
        Loaded configuration.
    """
    loader = ConfigLoader(config_file)
    return loader.load()


def generate_default_config() -> str:
    """Generate default configuration as YAML string.

    Returns:
        Default configuration YAML.
    """
    loader = ConfigLoader()
    config = ConvTestConfig()
    return loader.to_yaml(config)


def get_config_template() -> str:
    """Get configuration template with comments.

    Returns:
        Commented YAML configuration template.
    """
    return '''# Conversational Testing Framework Configuration
# https://github.com/your-repo/baml-agentic-ux

# Schema version
version: "1.0.0"

# Enable strict validation mode
strict_mode: false

# Quality gate thresholds
quality_gates:
  # Minimum test pass rate (blocking)
  min_pass_rate: 95.0
  # Minimum intent accuracy (blocking)
  min_intent_accuracy: 95.0
  # Minimum coherence score (warning)
  min_coherence: 0.85
  # Minimum naturalness score (warning)
  min_naturalness: 0.80
  # Minimum coverage percentage (warning)
  min_coverage: 70.0
  # Metrics that block merging if below threshold
  blocking_metrics:
    - pass_rate
    - intent_accuracy
  # Metrics that generate warnings if below threshold
  warning_metrics:
    - coherence
    - naturalness
    - coverage

# Test execution settings
execution:
  # Enable parallel test execution
  parallel: false
  # Maximum parallel workers
  max_workers: 4
  # Default timeout per test in seconds
  timeout_seconds: 30
  # Number of retries for failed tests
  retry_count: 0
  # Delay between retries in seconds
  retry_delay_seconds: 1.0
  # Stop suite execution on first failure
  stop_on_failure: false
  # Random seed for reproducible test ordering
  random_seed: null

# Report generation settings
reporting:
  # Output directory for reports
  output_dir: "test-reports"
  # Report formats to generate
  formats:
    - html
    - json
    - junit
  # Include execution logs in reports
  include_logs: true
  # Include quality metrics in reports
  include_metrics: true
  # Add timestamp to report filenames
  timestamp_reports: true
  # Generate summary report
  generate_summary: true

# Test filtering settings
filters:
  # Only run tests with these tags
  tags: []
  # Exclude tests with these tags
  exclude_tags: []
  # Only run tests in these categories
  categories: []
  # Only run tests with these priorities
  priorities: []
  # Pattern to match test names/IDs
  pattern: null
  # Pattern to exclude test names/IDs
  exclude_pattern: null

# Path configuration
paths:
  # Directories containing test files
  test_dirs:
    - "tests/conversations"
  # Directory for test fixtures
  fixtures_dir: "tests/fixtures"
  # Directory for test templates
  templates_dir: "tests/conversations/templates"
  # Output directory for generated files
  output_dir: "test-reports"

# Logging settings
logging:
  # Log level: DEBUG, INFO, WARNING, ERROR
  level: "INFO"
  # Log message format
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  # Log file path (null for no file logging)
  file: null
  # Enable console logging
  console: true
  # Enable verbose output
  verbose: false
  # Enable quiet mode (errors only)
  quiet: false

# Environment variable overrides
# The following environment variables can override config values:
#
# CONVTEST_MIN_PASS_RATE       - quality_gates.min_pass_rate
# CONVTEST_MIN_INTENT_ACCURACY - quality_gates.min_intent_accuracy
# CONVTEST_MIN_COHERENCE       - quality_gates.min_coherence
# CONVTEST_MIN_NATURALNESS     - quality_gates.min_naturalness
# CONVTEST_MIN_COVERAGE        - quality_gates.min_coverage
# CONVTEST_PARALLEL            - execution.parallel (true/false)
# CONVTEST_MAX_WORKERS         - execution.max_workers
# CONVTEST_TIMEOUT             - execution.timeout_seconds
# CONVTEST_OUTPUT_DIR          - reporting.output_dir
# CONVTEST_REPORT_FORMATS      - reporting.formats (comma-separated)
# CONVTEST_LOG_LEVEL           - logging.level
# CONVTEST_VERBOSE             - logging.verbose (true/false)
# CONVTEST_QUIET               - logging.quiet (true/false)
# CONVTEST_STRICT_MODE         - strict_mode (true/false)
'''
