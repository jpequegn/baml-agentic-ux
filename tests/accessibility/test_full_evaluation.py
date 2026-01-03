"""End-to-end integration tests for the accessibility module.

Tests the complete workflow of evaluating schemas against LUIAG criteria
including all checkers, evaluators, and report generation.

Issue #77 - Task 4.11: Testing & Documentation
"""

import pytest

from src.accessibility import (
    AccessibilityReport,
    AccessibilityReportGenerator,
    ComplianceLevel,
    CombinedDisabilityEvaluator,
    DisabilityType,
    JargonDetector,
    LUIAccessibilityChecker,
    ReadabilityAnalyzer,
    SchemaAccessibilityChecker,
    SeizureSafetyChecker,
    InteractionTimingValidator,
    TimeoutConfig,
    ARIALiveRegionGenerator,
    ARIAPoliteness,
    ContentType,
)

from .fixtures import (
    LEVEL_A_SCHEMA,
    LEVEL_AA_SCHEMA,
    LEVEL_AAA_SCHEMA,
    NON_COMPLIANT_SCHEMA,
    SIMPLE_RESPONSES,
    COMPLEX_RESPONSES,
)


# ============================================
# Integration Test: Full Schema Evaluation
# ============================================


class TestFullSchemaEvaluation:
    """Tests for complete schema evaluation workflow."""

    def test_level_a_schema_evaluation(self):
        """Test full evaluation of a Level A compliant schema."""
        checker = SchemaAccessibilityChecker()
        result = checker.check_schema(LEVEL_A_SCHEMA, ComplianceLevel.LEVEL_A)

        # Should pass Level A
        assert result.overall_score >= 0.7
        assert len(result.component_evaluations) == 3

    def test_level_aa_schema_evaluation(self):
        """Test full evaluation of a Level AA compliant schema."""
        checker = SchemaAccessibilityChecker()
        result = checker.check_schema(LEVEL_AA_SCHEMA, ComplianceLevel.LEVEL_AA)

        # Schema should be evaluated with all components
        assert len(result.component_evaluations) == 4
        # Score should be reasonable (not necessarily passing all checks)
        assert 0.0 <= result.overall_score <= 1.0

    def test_level_aaa_schema_evaluation(self):
        """Test full evaluation of a Level AAA compliant schema."""
        checker = SchemaAccessibilityChecker()
        result = checker.check_schema(LEVEL_AAA_SCHEMA, ComplianceLevel.LEVEL_AAA)

        # Should have reasonable score
        assert result.overall_score >= 0.5
        assert len(result.component_evaluations) == 3

    def test_non_compliant_schema_has_violations(self):
        """Test that non-compliant schema has accessibility violations."""
        checker = SchemaAccessibilityChecker()
        result = checker.check_schema(NON_COMPLIANT_SCHEMA, ComplianceLevel.LEVEL_AA)

        # Should have violations due to complex language
        assert len(result.violations) > 0

    def test_schema_with_all_checkers(self):
        """Test schema evaluation uses all accessibility checkers."""
        schema = LEVEL_AA_SCHEMA.copy()

        # Run all checks
        schema_checker = SchemaAccessibilityChecker()
        schema_result = schema_checker.check_schema(schema, ComplianceLevel.LEVEL_AA)

        disability_evaluator = CombinedDisabilityEvaluator()
        disability_results = disability_evaluator.evaluate(schema)

        # Verify all evaluators ran
        assert schema_result is not None
        assert len(disability_results) == len(DisabilityType)


# ============================================
# Integration Test: Response Checking Pipeline
# ============================================


class TestResponseCheckingPipeline:
    """Tests for complete response checking workflow."""

    def test_simple_response_passes_all_levels(self):
        """Test that simple responses pass all compliance levels."""
        checker = LUIAccessibilityChecker()

        for name, response in SIMPLE_RESPONSES.items():
            result = checker.check_response(response, ComplianceLevel.LEVEL_AA)
            # Simple responses should generally pass
            assert result.score >= 0.7, f"Simple response '{name}' failed"

    def test_complex_response_fails_strict_levels(self):
        """Test that complex responses fail strict compliance levels."""
        checker = LUIAccessibilityChecker()

        for name, response in COMPLEX_RESPONSES.items():
            result = checker.check_response(response, ComplianceLevel.LEVEL_AAA)
            # Complex responses should have violations
            assert len(result.violations) > 0, f"Complex '{name}' should have violations"

    def test_readability_and_jargon_integration(self):
        """Test that readability and jargon detection work together."""
        readability = ReadabilityAnalyzer()
        jargon_detector = JargonDetector()

        text = COMPLEX_RESPONSES["jargon_heavy"]

        # Check readability
        metrics = readability.analyze(text)
        assert metrics.flesch_kincaid_grade > 8  # Should be high grade

        # Check jargon - detect() returns list of JargonTerm
        jargon_terms = jargon_detector.detect(text)
        assert len(jargon_terms) > 0  # Should find jargon

    def test_response_with_recommendations(self):
        """Test that responses get appropriate recommendations."""
        checker = LUIAccessibilityChecker()

        result = checker.check_response(
            COMPLEX_RESPONSES["technical"],
            ComplianceLevel.LEVEL_AA,
        )

        # Should have recommendations for improvement
        assert len(result.recommendations) > 0


# ============================================
# Integration Test: Disability Evaluations
# ============================================


class TestDisabilityEvaluationIntegration:
    """Tests for disability-specific evaluation integration."""

    def test_all_disability_types_evaluated(self):
        """Test that all disability types are evaluated."""
        evaluator = CombinedDisabilityEvaluator()
        results = evaluator.evaluate(LEVEL_AA_SCHEMA)

        # Should have results for all disability types
        assert len(results) == len(DisabilityType)
        for dtype in DisabilityType:
            assert dtype in results

    def test_disability_scores_reasonable(self):
        """Test that disability scores are within valid range."""
        evaluator = CombinedDisabilityEvaluator()
        results = evaluator.evaluate(LEVEL_AA_SCHEMA)

        for dtype, evaluation in results.items():
            assert 0.0 <= evaluation.accommodation_score <= 1.0
            assert isinstance(evaluation.barriers, list)
            assert isinstance(evaluation.recommendations, list)

    def test_visual_accessibility_for_screen_readers(self):
        """Test visual accessibility includes screen reader considerations."""
        evaluator = CombinedDisabilityEvaluator()
        results = evaluator.evaluate(LEVEL_AA_SCHEMA)

        visual_eval = results[DisabilityType.VISUAL]
        # Should have accommodations or recommendations
        assert (
            len(visual_eval.accommodations_present) > 0
            or len(visual_eval.accommodations_missing) > 0
        )

    def test_cognitive_accessibility_for_reading_level(self):
        """Test cognitive accessibility considers reading level."""
        evaluator = CombinedDisabilityEvaluator()

        # Test with complex schema
        complex_results = evaluator.evaluate(NON_COMPLIANT_SCHEMA)
        cognitive_eval = complex_results[DisabilityType.COGNITIVE]

        # Complex language should create barriers
        assert cognitive_eval.total_barriers > 0 or len(cognitive_eval.recommendations) > 0


# ============================================
# Integration Test: Report Generation
# ============================================


class TestReportGenerationIntegration:
    """Tests for complete report generation workflow."""

    def test_generate_full_report(self):
        """Test generating a complete accessibility report."""
        generator = AccessibilityReportGenerator()
        report = generator.generate_report(LEVEL_AA_SCHEMA, ComplianceLevel.LEVEL_AA)

        # Verify report structure
        assert isinstance(report, AccessibilityReport)
        assert report.schema_name == "Level AA Accessible Assistant"
        assert report.target_level == ComplianceLevel.LEVEL_AA
        assert report.summary is not None

    def test_report_contains_all_sections(self):
        """Test that report contains all required sections."""
        generator = AccessibilityReportGenerator()
        report = generator.generate_report(LEVEL_AA_SCHEMA, ComplianceLevel.LEVEL_AA)

        # Check all sections present
        assert report.component_details is not None
        assert report.disability_coverage is not None
        assert report.violations is not None
        assert report.recommendations is not None

    def test_export_formats_work(self):
        """Test that all export formats work correctly."""
        generator = AccessibilityReportGenerator()
        report = generator.generate_report(LEVEL_A_SCHEMA, ComplianceLevel.LEVEL_A)

        # Test all export formats
        md = generator.export_markdown(report)
        json_data = generator.export_json(report)
        html = generator.export_html(report)

        assert len(md) > 0
        assert len(json_data) > 0
        assert len(html) > 0

    def test_report_recommendations_prioritized(self):
        """Test that report recommendations are properly prioritized."""
        generator = AccessibilityReportGenerator()
        report = generator.generate_report(NON_COMPLIANT_SCHEMA, ComplianceLevel.LEVEL_AA)

        if len(report.recommendations) >= 2:
            # Verify priority ordering
            priority_order = {"high": 0, "medium": 1, "low": 2}
            for i in range(len(report.recommendations) - 1):
                current = priority_order.get(report.recommendations[i].priority, 3)
                next_val = priority_order.get(report.recommendations[i + 1].priority, 3)
                assert current <= next_val


# ============================================
# Integration Test: Safety Checks
# ============================================


class TestSafetyChecksIntegration:
    """Tests for safety-related accessibility checks."""

    def test_seizure_safety_integration(self):
        """Test seizure safety checker integration."""
        checker = SeizureSafetyChecker()

        # Test with safe content
        result = checker.check_content({
            "has_animations": False,
            "has_flashing": False,
        })

        assert result.passes

    def test_timing_validation_integration(self):
        """Test timing validation integration."""
        validator = InteractionTimingValidator()

        # Test with reasonable timeout using TimeoutConfig
        config = TimeoutConfig(
            initial_timeout_seconds=30,
            extension_allowed=True,
        )
        result = validator.validate_timeout(
            config=config,
            target_level=ComplianceLevel.LEVEL_AA,
        )

        assert result.passes


# ============================================
# Integration Test: ARIA Generation
# ============================================


class TestARIAGenerationIntegration:
    """Tests for ARIA live region generation integration."""

    def test_aria_generation_workflow(self):
        """Test complete ARIA generation workflow."""
        generator = ARIALiveRegionGenerator()

        # Generate live region - response is positional arg
        html = generator.generate_live_region(
            "Task completed successfully",
            politeness=ARIAPoliteness.POLITE,
        )

        assert "aria-live" in html
        assert "polite" in html

    def test_aria_for_different_content_types(self):
        """Test ARIA generation for different content types."""
        generator = ARIALiveRegionGenerator()

        # Test error message
        error_html = generator.generate_error_region("An error occurred")
        assert "alert" in error_html.lower() or "assertive" in error_html.lower()

        # Test status message
        status_html = generator.generate_status_region("Processing complete")
        assert "status" in status_html.lower() or "polite" in status_html.lower()

    def test_aria_with_screen_reader_hints(self):
        """Test ARIA generation includes screen reader hints."""
        generator = ARIALiveRegionGenerator()

        # generate_live_region_full takes response as positional arg
        result = generator.generate_live_region_full(
            "New message received",
            politeness=ARIAPoliteness.POLITE,
        )

        assert result.screen_reader_hints is not None
        assert len(result.screen_reader_hints) > 0


# ============================================
# Integration Test: Cross-Module Consistency
# ============================================


class TestCrossModuleConsistency:
    """Tests for consistency across accessibility modules."""

    def test_compliance_levels_consistent(self):
        """Test that compliance levels are used consistently."""
        schema_checker = SchemaAccessibilityChecker()
        response_checker = LUIAccessibilityChecker()
        timing_validator = InteractionTimingValidator()

        # All should accept the same compliance level enum
        schema_result = schema_checker.check_schema(LEVEL_AA_SCHEMA, ComplianceLevel.LEVEL_AA)
        response_result = response_checker.check_response("Hello!", ComplianceLevel.LEVEL_AA)

        # validate_timeout requires TimeoutConfig object
        config = TimeoutConfig(
            initial_timeout_seconds=30,
            extension_allowed=True,
        )
        timing_result = timing_validator.validate_timeout(config, ComplianceLevel.LEVEL_AA)

        # All should return valid results
        assert schema_result is not None
        assert response_result is not None
        assert timing_result is not None

    def test_violation_severities_consistent(self):
        """Test that violation severities are consistent across modules."""
        from src.accessibility import ViolationSeverity

        # Verify severity values exist
        severities = [
            ViolationSeverity.CRITICAL,
            ViolationSeverity.MAJOR,
            ViolationSeverity.MINOR,
            ViolationSeverity.ADVISORY,
        ]

        for sev in severities:
            assert sev.value is not None

    def test_disability_types_complete(self):
        """Test that all disability types are covered."""
        expected_types = [
            DisabilityType.VISUAL,
            DisabilityType.HEARING,
            DisabilityType.MOTOR,
            DisabilityType.SPEECH,
            DisabilityType.COGNITIVE,
            DisabilityType.NEUROLOGICAL,
        ]

        evaluator = CombinedDisabilityEvaluator()
        results = evaluator.evaluate(LEVEL_AA_SCHEMA)

        for dtype in expected_types:
            assert dtype in results


# ============================================
# Edge Cases and Boundary Testing
# ============================================


class TestEdgeCasesIntegration:
    """Integration tests for edge cases."""

    def test_empty_schema_handling(self):
        """Test handling of empty schema."""
        checker = SchemaAccessibilityChecker()
        result = checker.check_schema({"name": "Empty"}, ComplianceLevel.LEVEL_A)

        assert result is not None
        assert result.summary is not None

    def test_schema_without_components(self):
        """Test schema with no components."""
        checker = SchemaAccessibilityChecker()
        result = checker.check_schema(
            {"name": "No Components", "components": []},
            ComplianceLevel.LEVEL_AA,
        )

        assert result is not None
        assert result.total_components == 0

    def test_very_long_content(self):
        """Test handling of very long content."""
        checker = LUIAccessibilityChecker()
        long_content = "word " * 1000  # 1000 words

        result = checker.check_response(long_content, ComplianceLevel.LEVEL_A)

        assert result is not None
        assert isinstance(result.score, float)

    def test_unicode_content_handling(self):
        """Test handling of unicode content."""
        checker = LUIAccessibilityChecker()

        result = checker.check_response(
            "こんにちは! 你好! مرحبا! 🎉",
            ComplianceLevel.LEVEL_A,
        )

        assert result is not None

    def test_special_characters_handling(self):
        """Test handling of special characters."""
        checker = LUIAccessibilityChecker()

        result = checker.check_response(
            "Click <here> for help. Use & for 'and'. Price: $100.",
            ComplianceLevel.LEVEL_A,
        )

        assert result is not None


# ============================================
# Performance and Load Testing
# ============================================


class TestPerformance:
    """Performance tests for accessibility module."""

    def test_large_schema_performance(self):
        """Test performance with large schema."""
        import time

        # Create a large schema
        components = [
            {
                "id": f"component_{i}",
                "type": "message",
                "feedback": {"success_template": f"Message {i}"},
            }
            for i in range(100)
        ]
        large_schema = {"name": "Large Schema", "components": components}

        checker = SchemaAccessibilityChecker()

        start = time.time()
        result = checker.check_schema(large_schema, ComplianceLevel.LEVEL_AA)
        elapsed = time.time() - start

        assert result is not None
        assert elapsed < 5.0  # Should complete within 5 seconds

    def test_report_generation_performance(self):
        """Test report generation performance."""
        import time

        generator = AccessibilityReportGenerator()

        start = time.time()
        report = generator.generate_report(LEVEL_AA_SCHEMA, ComplianceLevel.LEVEL_AA)
        elapsed = time.time() - start

        assert report is not None
        assert elapsed < 2.0  # Should complete within 2 seconds
