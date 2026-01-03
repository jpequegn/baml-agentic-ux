# LUI Accessibility Implementation Checklist

Use this checklist to ensure your Language User Interface meets accessibility requirements. Check off items as you implement them.

## Quick Start Checklist

### Essential (Level A)

- [ ] All responses use plain language (Grade 12 or lower)
- [ ] Keyboard navigation works for all interactions
- [ ] Errors are clearly identified with remediation guidance
- [ ] Timeouts are at least 20 seconds
- [ ] No content flashes more than 3 times per second
- [ ] Screen reader compatibility (JAWS, NVDA, VoiceOver)

### Recommended (Level AA)

- [ ] Plain language at Grade 8 or lower
- [ ] Voice input supported
- [ ] Timeouts extendable to 30+ seconds
- [ ] Error prevention for important actions
- [ ] ARIA live regions for all dynamic content
- [ ] Consistent interaction patterns

### Advanced (Level AAA)

- [ ] Plain language at Grade 6 or lower
- [ ] All input methods supported (switch, eye tracking)
- [ ] Unlimited timeout extensions
- [ ] Full error prevention with undo
- [ ] Sign language support available

---

## Detailed Checklist by Category

## 1. Readability

### Level A
- [ ] Average reading grade level ≤ 12
- [ ] Average sentence length ≤ 30 words
- [ ] Complex words ≤ 20% of content
- [ ] Technical terms defined on first use
- [ ] Acronyms expanded on first use

### Level AA
- [ ] Average reading grade level ≤ 8
- [ ] Average sentence length ≤ 20 words
- [ ] Complex words ≤ 15% of content
- [ ] Jargon minimized or avoided
- [ ] Passive voice minimized

### Level AAA
- [ ] Average reading grade level ≤ 6
- [ ] Average sentence length ≤ 15 words
- [ ] Complex words ≤ 10% of content
- [ ] No jargon without simple alternatives
- [ ] Active voice used consistently

### Verification

```python
from src.accessibility import ReadabilityAnalyzer, JargonDetector

analyzer = ReadabilityAnalyzer()
metrics = analyzer.analyze(response_text)

# Check grade level
assert metrics.flesch_kincaid_grade <= 8  # Level AA

# Check jargon
detector = JargonDetector()
terms = detector.detect(response_text)
assert len(terms) == 0  # No jargon
```

---

## 2. Response Content

### Level A
- [ ] All responses have text format available
- [ ] Error messages identify the problem
- [ ] Error messages provide remediation steps
- [ ] Success confirmations are clear
- [ ] Status updates are informative

### Level AA
- [ ] Error messages suggest corrections
- [ ] Important actions have confirmation
- [ ] Progress is communicated for long operations
- [ ] Responses are concise and focused
- [ ] Multiple response formats available

### Level AAA
- [ ] Responses can be customized by user
- [ ] Summaries available for long content
- [ ] Content complexity adjustable
- [ ] Full transcripts available
- [ ] Responses work without context

### Verification

```python
from src.accessibility import LUIAccessibilityChecker, ComplianceLevel

checker = LUIAccessibilityChecker()

# Check response accessibility
result = checker.check_response(response, ComplianceLevel.LEVEL_AA)
assert result.passes
assert len(result.violations) == 0
```

---

## 3. Input Methods

### Level A
- [ ] All functions accessible via keyboard
- [ ] Tab order is logical
- [ ] Focus is visible
- [ ] No keyboard traps
- [ ] Standard keyboard shortcuts work

### Level AA
- [ ] Voice input supported
- [ ] Touch input supported
- [ ] Complex gestures have alternatives
- [ ] Input method can be changed anytime
- [ ] Input errors can be easily corrected

### Level AAA
- [ ] Switch access supported
- [ ] Eye tracking supported
- [ ] Pointer speed/precision adjustable
- [ ] Custom input methods configurable
- [ ] All inputs have alternatives

### Verification

```python
from src.accessibility import (
    InteractionTimingValidator,
    InputMethodConfig,
    ComplianceLevel,
)

validator = InteractionTimingValidator()

config = InputMethodConfig(
    keyboard_accessible=True,
    voice_input=True,
    touch_input=True,
    switch_access=True,
)

result = validator.validate_input_methods(config, ComplianceLevel.LEVEL_AA)
assert result.passes
```

---

## 4. Timing

### Level A
- [ ] Initial timeout ≥ 20 seconds
- [ ] User can extend time (if time limit exists)
- [ ] Warning before timeout
- [ ] Essential timeouts are clearly communicated
- [ ] No auto-submit on timeout

### Level AA
- [ ] Initial timeout ≥ 30 seconds
- [ ] Timeout can be extended to at least 10x
- [ ] Warning at least 10 seconds before timeout
- [ ] Auto-updating content can be paused
- [ ] No time-based interactions without alternatives

### Level AAA
- [ ] Initial timeout ≥ 60 seconds
- [ ] Unlimited timeout extensions
- [ ] No timing required for any interaction
- [ ] User can stop all time-based changes
- [ ] Re-authentication preserves data

### Verification

```python
from src.accessibility import (
    InteractionTimingValidator,
    TimeoutConfig,
    ComplianceLevel,
)

validator = InteractionTimingValidator()

config = TimeoutConfig(
    initial_timeout_seconds=30,
    warning_before_seconds=10,
    extension_allowed=True,
    extension_seconds=30,
    max_extensions=-1,  # Unlimited
)

result = validator.validate_timeout(config, ComplianceLevel.LEVEL_AA)
assert result.passes
```

---

## 5. Seizure Safety

### All Levels (Critical)
- [ ] No content flashes more than 3 times per second
- [ ] No red flashes
- [ ] Flashing area < 25% of viewport
- [ ] Animations can be paused
- [ ] Animations can be disabled
- [ ] Reduced motion preference respected
- [ ] No auto-playing animations

### Verification

```python
from src.accessibility import SeizureSafetyChecker, AnimationConfig

checker = SeizureSafetyChecker()

# Check content
result = checker.check_content({
    "has_animations": True,
    "has_flashing": False,
})
assert result.passes

# Check animation config
config = AnimationConfig(
    has_animation=True,
    flash_frequency_hz=0,
    can_pause=True,
    can_disable=True,
    reduced_motion_supported=True,
)
result = checker.check_animation(config)
assert result.passes
```

---

## 6. Screen Reader Compatibility

### Level A
- [ ] All content accessible to JAWS
- [ ] All content accessible to NVDA
- [ ] All content accessible to VoiceOver
- [ ] Dynamic content uses aria-live
- [ ] Roles correctly specified
- [ ] Labels provided for all controls

### Level AA
- [ ] TalkBack (Android) supported
- [ ] Narrator (Windows) supported
- [ ] Content order matches visual order
- [ ] Headings properly structured
- [ ] Focus management correct

### Level AAA
- [ ] Orca (Linux) supported
- [ ] Custom screen reader hints
- [ ] Verbose mode available
- [ ] Audio descriptions available
- [ ] Full ARIA semantics used

### Verification

```python
from src.accessibility import ARIALiveRegionGenerator, ARIAPoliteness

generator = ARIALiveRegionGenerator()

# All dynamic content should use live regions
html = generator.generate_live_region(
    response,
    politeness=ARIAPoliteness.POLITE,
)
assert "aria-live" in html

# Errors should be assertive
error_html = generator.generate_error_region(error_message)
assert "assertive" in error_html or "alert" in error_html
```

---

## 7. Error Handling

### Level A
- [ ] Errors clearly identified
- [ ] Error location specified
- [ ] Error described in text
- [ ] Not reliant on color alone
- [ ] User can recover from errors

### Level AA
- [ ] Correction suggestions provided
- [ ] Important actions reversible
- [ ] Data validated before submission
- [ ] Confirmation for important actions
- [ ] Clear path to fix errors

### Level AAA
- [ ] Undo available for all actions
- [ ] Auto-save enabled
- [ ] Recovery options for all failures
- [ ] Confirmation for all changes
- [ ] Preview before submission

### Verification

```python
from src.accessibility import ErrorHandlingConfig, InteractionTimingValidator

validator = InteractionTimingValidator()

config = ErrorHandlingConfig(
    error_prevention=True,
    error_identification=True,
    error_suggestions=True,
    undo_available=True,
)

# Validate via timing validator
# (error handling is part of interaction validation)
```

---

## 8. Visual Accessibility

### Level A
- [ ] Information not conveyed by color alone
- [ ] Text alternatives for images
- [ ] Sufficient color contrast (4.5:1)
- [ ] Content resizable to 200%
- [ ] No loss of content when zoomed

### Level AA
- [ ] Enhanced contrast (7:1) for important text
- [ ] Non-text contrast (3:1)
- [ ] Text spacing adjustable
- [ ] Reflow at 320px width
- [ ] Status messages accessible

### Level AAA
- [ ] Maximum contrast
- [ ] Background images optional
- [ ] All content visible at 400%
- [ ] Line height adjustable
- [ ] Fonts customizable

---

## 9. Hearing Accessibility

### Level A
- [ ] Audio has text alternatives
- [ ] Critical audio information in text
- [ ] Visual alerts for audio cues
- [ ] No audio-only interactions

### Level AA
- [ ] Captions for all audio
- [ ] Audio descriptions available
- [ ] Transcripts available
- [ ] Audio can be adjusted separately

### Level AAA
- [ ] Sign language interpretation
- [ ] Extended audio description
- [ ] Real-time captions
- [ ] All audio has full transcript

---

## 10. Motor Accessibility

### Level A
- [ ] All functions keyboard accessible
- [ ] No keyboard traps
- [ ] Target size minimum 44x44 CSS pixels
- [ ] No complex gestures required
- [ ] Sufficient spacing between targets

### Level AA
- [ ] Target size 44x44 CSS pixels
- [ ] Pointer cancellation available
- [ ] Motion actuation has alternatives
- [ ] Drag alternatives available

### Level AAA
- [ ] Target size 48x48 CSS pixels
- [ ] No motion-based input required
- [ ] All gestures have alternatives
- [ ] Full switch access support

---

## 11. Cognitive Accessibility

### Level A
- [ ] Plain language used
- [ ] Consistent layout
- [ ] Clear error messages
- [ ] Instructions provided
- [ ] No unexpected changes

### Level AA
- [ ] Reading level appropriate
- [ ] Consistent navigation
- [ ] Predictable behavior
- [ ] Distractions minimized
- [ ] Help available

### Level AAA
- [ ] Simplified mode available
- [ ] Glossary of terms
- [ ] Step-by-step guidance
- [ ] Memory aids provided
- [ ] Context always clear

---

## 12. Disability Coverage

### Verification

```python
from src.accessibility import CombinedDisabilityEvaluator, DisabilityType

evaluator = CombinedDisabilityEvaluator()
results = evaluator.evaluate(schema)

# Check all disability types
required_score = 0.7  # 70% for Level AA

for dtype in DisabilityType:
    score = results[dtype].accommodation_score
    print(f"{dtype.value}: {score:.0%}")
    assert score >= required_score, f"{dtype.value} below threshold"
```

---

## Pre-Release Checklist

### Testing

- [ ] Automated accessibility tests pass
- [ ] Manual screen reader testing completed
- [ ] Keyboard-only navigation tested
- [ ] Color blindness simulation tested
- [ ] Low vision simulation tested
- [ ] Cognitive load assessed

### Documentation

- [ ] Accessibility features documented
- [ ] Known limitations documented
- [ ] Workarounds documented
- [ ] Contact for accessibility issues provided

### Report

```python
from src.accessibility import (
    AccessibilityReportGenerator,
    ComplianceLevel,
)

generator = AccessibilityReportGenerator()
report = generator.generate_report(schema, ComplianceLevel.LEVEL_AA)

# Generate reports
md_report = generator.export_markdown(report)
json_report = generator.export_json(report)

# Save reports
with open("accessibility_report.md", "w") as f:
    f.write(md_report)
```

---

## Coverage Summary

After completing the checklist, verify coverage:

```python
from src.accessibility import (
    SchemaAccessibilityChecker,
    CombinedDisabilityEvaluator,
    AccessibilityReportGenerator,
    ComplianceLevel,
)

def verify_full_coverage(schema: dict, level: ComplianceLevel) -> dict:
    """Verify full accessibility coverage."""

    # Schema validation
    schema_checker = SchemaAccessibilityChecker()
    schema_result = schema_checker.check_schema(schema, level)

    # Disability coverage
    disability_evaluator = CombinedDisabilityEvaluator()
    disability_results = disability_evaluator.evaluate(schema)

    # Generate report
    report_generator = AccessibilityReportGenerator()
    report = report_generator.generate_report(schema, level)

    return {
        "schema_score": schema_result.overall_score,
        "schema_passes": schema_result.passes,
        "disability_scores": {
            dtype.value: result.accommodation_score
            for dtype, result in disability_results.items()
        },
        "overall_score": report.summary.overall_score,
        "violation_count": len(report.violations),
        "achieved_level": report.summary.achieved_level.value,
    }
```

---

## See Also

- [API.md](./API.md) - Complete API reference
- [GUIDE.md](./GUIDE.md) - Usage guide and examples
- [LUIAG.md](./LUIAG.md) - LUIAG compliance reference
