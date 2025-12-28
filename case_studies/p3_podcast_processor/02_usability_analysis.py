"""Run usability analysis on the P3 podcast processor LUI schema."""

import asyncio
import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from baml_client import b
from baml_client.types import (
    InterfaceSchema,
    UserPersona,
    TechnicalSkillLevel,
    DomainKnowledgeLevel,
    AccessibilityNeed,
    InteractionStyle,
    UsabilityGUISpec,
)
from lui_simulator.simulator import load_schema_from_dict


def load_p3_schema() -> InterfaceSchema:
    """Load the P3 LUI schema from JSON."""
    schema_path = Path(__file__).parent.parent.parent / "examples" / "p3_podcast_schema.json"
    with open(schema_path) as f:
        data = json.load(f)
    return load_schema_from_dict(data)


def create_user_personas() -> list[UserPersona]:
    """Create user personas for P3 analysis."""
    return [
        UserPersona(
            persona_name="Casual Podcast Listener",
            description="Someone who wants summaries without technical complexity",
            technical_skill=TechnicalSkillLevel.BASIC,
            domain_knowledge=DomainKnowledgeLevel.BEGINNER,
            accessibility_needs=[AccessibilityNeed.NONE],
            primary_goals=[
                "Get summaries of podcasts",
                "Search for interesting topics",
                "Save time by not listening to everything"
            ],
            pain_points=[
                "Too many commands to remember",
                "Episode IDs are confusing",
                "Don't know where to start"
            ],
            preferred_interaction_style=InteractionStyle.CONVERSATIONAL,
        ),
        UserPersona(
            persona_name="Content Creator",
            description="Blogger or writer using podcasts for content ideas",
            technical_skill=TechnicalSkillLevel.INTERMEDIATE,
            domain_knowledge=DomainKnowledgeLevel.INTERMEDIATE,
            accessibility_needs=[AccessibilityNeed.NONE],
            primary_goals=[
                "Generate blog posts quickly",
                "Find trending topics",
                "Extract quotes for articles"
            ],
            pain_points=[
                "Manual workflow is slow",
                "Need to run many commands",
                "Hard to track what's processed"
            ],
            preferred_interaction_style=InteractionStyle.EFFICIENT,
        ),
        UserPersona(
            persona_name="Power User Developer",
            description="Technical user who wants full control",
            technical_skill=TechnicalSkillLevel.EXPERT,
            domain_knowledge=DomainKnowledgeLevel.ADVANCED,
            accessibility_needs=[AccessibilityNeed.NONE],
            primary_goals=[
                "Automate workflows",
                "Customize processing",
                "Integrate with other tools"
            ],
            pain_points=[
                "Limited batch processing",
                "Can't script complex queries"
            ],
            preferred_interaction_style=InteractionStyle.COMMAND,
        ),
    ]


def create_gui_spec() -> UsabilityGUISpec:
    """Create a GUI specification for comparison (typical podcast app)."""
    return UsabilityGUISpec(
        name="Traditional Podcast Manager App",
        description="A typical desktop podcast application with visual interface",
        screen_count=6,
        main_features=[
            "Podcast subscription management",
            "Episode list with filters",
            "Audio player with playback controls",
            "Download queue visualization",
            "Search and discovery",
            "Notes and highlights"
        ],
        navigation_style="Sidebar navigation with main content area",
        interaction_patterns=[
            "Click to play/pause",
            "Drag to reorder queue",
            "Right-click context menus",
            "Keyboard shortcuts",
            "Search with autocomplete",
            "Visual progress indicators"
        ],
    )


async def run_full_analysis():
    """Run comprehensive usability analysis on P3 schema."""
    print("Loading P3 LUI Schema...")
    schema = load_p3_schema()

    print(f"Schema: {schema.name}")
    print(f"Components: {len(schema.components)}")
    print(f"Flows: {len(schema.flows) if schema.flows else 0}")
    print()

    # Get personas and GUI spec
    personas = create_user_personas()
    gui_spec = create_gui_spec()

    # Run main usability analysis
    print("=" * 60)
    print("RUNNING MAIN USABILITY ANALYSIS")
    print("=" * 60)

    try:
        analysis = await b.AnalyzeLUIUsability(
            schema=schema,
            target_users=personas,
            comparison_gui=gui_spec,
        )

        print(f"\nOverall Score: {analysis.overall_score}/100")
        print(f"Grade: {analysis.grade.value}")
        print(f"\nSummary: {analysis.summary}")

        print("\n" + "-" * 40)
        print("CATEGORY SCORES")
        print("-" * 40)
        for score in analysis.category_scores:
            print(f"  {score.category.value}: {score.score}/100 (weight: {score.weight})")
            print(f"    Notes: {score.notes[:100]}...")

        print("\n" + "-" * 40)
        print(f"ISSUES ({len(analysis.issues)})")
        print("-" * 40)
        for issue in analysis.issues:
            print(f"  [{issue.severity.value}] {issue.title}")
            print(f"    Category: {issue.category.value}")
            print(f"    Impact: {issue.impact[:80]}...")

        print("\n" + "-" * 40)
        print(f"RECOMMENDATIONS ({len(analysis.recommendations)})")
        print("-" * 40)
        for rec in analysis.recommendations:
            print(f"  [{rec.priority.value}] {rec.title}")
            print(f"    Effort: {rec.implementation_effort.value}")
            print(f"    Expected: {rec.expected_improvement[:80]}...")

        print("\n" + "-" * 40)
        print("STRENGTHS")
        print("-" * 40)
        for strength in analysis.strengths:
            print(f"  + {strength}")

        if analysis.comparison_to_gui:
            print("\n" + "-" * 40)
            print("GUI COMPARISON")
            print("-" * 40)
            print("\nLUI Advantages:")
            for adv in analysis.comparison_to_gui.advantages_lui:
                print(f"  + {adv}")
            print("\nGUI Advantages:")
            for adv in analysis.comparison_to_gui.advantages_gui:
                print(f"  + {adv}")
            print(f"\nNotes: {analysis.comparison_to_gui.conversion_notes}")

        return analysis

    except Exception as e:
        print(f"Analysis failed: {e}")
        raise


async def run_heuristic_evaluation():
    """Run heuristic evaluation on P3 schema."""
    print("\n" + "=" * 60)
    print("RUNNING HEURISTIC EVALUATION")
    print("=" * 60)

    schema = load_p3_schema()

    try:
        evaluations = await b.EvaluateHeuristics(schema=schema)

        for eval in evaluations:
            print(f"\n{eval.heuristic.value}: {eval.rating.value}")
            print(f"  Findings:")
            for finding in eval.findings[:3]:
                print(f"    - {finding}")
            if eval.violations:
                print(f"  Violations ({len(eval.violations)}):")
                for v in eval.violations[:2]:
                    print(f"    - [{v.severity.value}] {v.description[:60]}...")

        return evaluations

    except Exception as e:
        print(f"Heuristic evaluation failed: {e}")
        raise


async def run_persona_analysis():
    """Run persona-specific analysis."""
    print("\n" + "=" * 60)
    print("RUNNING PERSONA-SPECIFIC ANALYSIS")
    print("=" * 60)

    schema = load_p3_schema()
    personas = create_user_personas()

    results = []
    for persona in personas:
        print(f"\n--- {persona.persona_name} ---")
        try:
            analysis = await b.AnalyzeForPersona(
                schema=schema,
                persona=persona,
            )
            print(f"Score: {analysis.overall_score}/100 ({analysis.grade.value})")
            print(f"Summary: {analysis.summary[:150]}...")
            results.append((persona.persona_name, analysis))
        except Exception as e:
            print(f"Failed: {e}")

    return results


async def main():
    """Run all analyses and save results."""
    print("P3 Podcast Processor - LUI Usability Analysis")
    print("=" * 60)
    print()

    # Run analyses
    main_analysis = await run_full_analysis()
    heuristics = await run_heuristic_evaluation()
    persona_results = await run_persona_analysis()

    # Save results summary
    results_path = Path(__file__).parent / "analysis_results.md"
    with open(results_path, "w") as f:
        f.write("# P3 LUI Usability Analysis Results\n\n")
        f.write(f"## Overall Score: {main_analysis.overall_score}/100 ({main_analysis.grade.value})\n\n")
        f.write(f"### Summary\n{main_analysis.summary}\n\n")

        f.write("### Category Scores\n")
        for score in main_analysis.category_scores:
            f.write(f"- **{score.category.value}**: {score.score}/100\n")

        f.write("\n### Identified Issues\n")
        for issue in main_analysis.issues:
            f.write(f"- [{issue.severity.value}] **{issue.title}**: {issue.description[:100]}...\n")

        f.write("\n### Recommendations\n")
        for rec in main_analysis.recommendations:
            f.write(f"- [{rec.priority.value}] **{rec.title}**: {rec.suggested_change[:100]}...\n")

        f.write("\n### Strengths\n")
        for strength in main_analysis.strengths:
            f.write(f"- {strength}\n")

        f.write("\n### Persona Results\n")
        for name, analysis in persona_results:
            f.write(f"- **{name}**: {analysis.overall_score}/100 ({analysis.grade.value})\n")

    print(f"\nResults saved to: {results_path}")


if __name__ == "__main__":
    asyncio.run(main())
