"""Accessibility analysis module for LUI applications.

This module provides tools for analyzing readability and accessibility
compliance of text content following WCAG and plain language guidelines.
"""

from .readability import (
    ReadabilityAnalyzer,
    ReadabilityMetrics,
    SentenceAnalyzer,
    SentenceAnalysis,
)

__all__ = [
    "ReadabilityAnalyzer",
    "ReadabilityMetrics",
    "SentenceAnalyzer",
    "SentenceAnalysis",
]
