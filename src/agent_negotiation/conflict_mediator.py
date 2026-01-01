"""
Conflict Mediation System for Agent Negotiation.

Provides mediation capabilities for resolving conflicts between negotiating parties
and handling deadlocks in agent-to-agent interface negotiation.

Issue #62 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.10)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional
from datetime import datetime
import uuid


# ============================================
# Mediation Style Enums
# ============================================


class MediationStyle(Enum):
    """Style of mediation to apply."""
    FACILITATIVE = "facilitative"  # Help parties find their own solution through dialogue
    EVALUATIVE = "evaluative"  # Mediator suggests and evaluates potential solutions
    TRANSFORMATIVE = "transformative"  # Focus on changing relationship dynamics and understanding
    DIRECTIVE = "directive"  # Mediator provides binding decision when parties cannot agree


class MediationResolutionStrategy(Enum):
    """Strategy for resolving deadlocks."""
    TRANSFORM = "transform"  # Convert data format to achieve compatibility
    SUBSET = "subset"  # Use common subset of capabilities that both support
    MEDIATE = "mediate"  # Third-party mediation to find compromise
    ESCALATE = "escalate"  # Escalate to human decision maker
    ALTERNATIVE = "alternative"  # Substitute with different but equivalent capability
    NEGOTIATE_TERMS = "negotiate_terms"  # Adjust terms while keeping core requirements
    BRIDGE = "bridge"  # Create adapter or bridge layer between parties
    SPLIT_DIFFERENCE = "split_difference"  # Average numeric terms between positions
    PACKAGE_DEAL = "package_deal"  # Trade-offs between multiple issues
    TIME_SHARE = "time_share"  # Alternate access or usage periods


class MediationOutcome(Enum):
    """Outcome status of mediation."""
    RESOLVED = "resolved"  # All conflicts successfully resolved
    PARTIALLY_RESOLVED = "partially_resolved"  # Some conflicts resolved, others remain
    DEADLOCK = "deadlock"  # No resolution possible, escalation needed
    DEFERRED = "deferred"  # Resolution postponed for future discussion
    WITHDRAWN = "withdrawn"  # Party withdrew from mediation


class ConflictPriority(Enum):
    """Priority level for conflict resolution."""
    CRITICAL = "critical"  # Must resolve to proceed
    HIGH = "high"  # Should resolve soon
    MEDIUM = "medium"  # Can work around temporarily
    LOW = "low"  # Nice to resolve but not blocking


# ============================================
# Party Position Types
# ============================================


@dataclass
class TermSummary:
    """Summary of a negotiation term."""
    term_name: str
    term_value: str
    negotiable: bool
    min_acceptable: Optional[str] = None
    max_acceptable: Optional[str] = None


@dataclass
class NegotiationProposalSummary:
    """Summary of a negotiation proposal for mediation."""
    proposal_id: str
    terms: list[TermSummary]
    capabilities: list[str]
    valid_until: str  # ISO 8601 timestamp


@dataclass
class PositionConstraint:
    """Constraint on a party's position."""
    constraint_id: str
    field: str
    constraint_type: str  # min, max, equals, etc.
    value: str
    reason: str
    waivable: bool


@dataclass
class TradeOffPair:
    """A pair of terms that can be traded off against each other."""
    term_a: str
    term_b: str
    relationship: str  # inverse, proportional, etc.


@dataclass
class FlexibilityAssessment:
    """Assessment of flexibility in a position."""
    flexible_terms: list[str]
    trade_off_pairs: list[TradeOffPair]
    total_flexibility_score: float  # 0.0-1.0


@dataclass
class PartyPosition:
    """Position of a negotiating party."""
    party_id: str
    party_name: str
    proposal: NegotiationProposalSummary
    priorities: list[str]
    constraints: list[PositionConstraint]
    flexibility: FlexibilityAssessment


# ============================================
# Mediation Request/Response Types
# ============================================


@dataclass
class ConflictHistoryEntry:
    """Entry in conflict history."""
    timestamp: str
    strategy_tried: MediationResolutionStrategy
    outcome: str
    notes: Optional[str] = None


@dataclass
class ConflictSummaryForMediation:
    """Summary of conflict for mediation purposes."""
    conflict_id: str
    conflict_type: str
    severity: str
    description: str
    affected_terms: list[str]
    history: Optional[list[ConflictHistoryEntry]] = None


@dataclass
class MediationOptions:
    """Options for the mediation process."""
    max_iterations: int
    auto_escalate: bool
    escalation_threshold: int
    allow_partial_resolution: bool
    generate_alternatives: bool
    max_alternatives: int
    preserve_relationship: bool


@dataclass
class MediationContext:
    """Context for mediation."""
    urgency: ConflictPriority
    business_impact: Optional[str] = None
    previous_mediations: Optional[list[str]] = None
    relationship_history: Optional[str] = None
    external_constraints: Optional[list[str]] = None


@dataclass
class MediationRequest:
    """Request for mediation."""
    request_id: str
    session_id: str
    conflict: ConflictSummaryForMediation
    party_a: PartyPosition
    party_b: PartyPosition
    mediation_style: MediationStyle
    options: MediationOptions
    context: Optional[MediationContext] = None


# ============================================
# Mediation Result Types
# ============================================


@dataclass
class Concession:
    """A concession made by a party."""
    term_name: str
    original_value: str
    conceded_value: str
    impact: str
    compensation: Optional[str] = None


@dataclass
class CompromiseTerm:
    """A term in a compromise proposal."""
    term_name: str
    original_a: str
    original_b: str
    compromise_value: str
    rationale: str


@dataclass
class CompromiseProposal:
    """A proposed compromise."""
    proposal_id: str
    description: str
    terms: list[CompromiseTerm]
    concessions_a: list[Concession]
    concessions_b: list[Concession]
    gains_a: list[str]
    gains_b: list[str]
    fairness_score: float  # 0.0-1.0
    viability_score: float  # 0.0-1.0


@dataclass
class MediationMetrics:
    """Metrics about the mediation process."""
    iterations_used: int
    time_elapsed_ms: int
    proposals_generated: int
    proposals_rejected: int
    common_ground_found: float  # 0.0-1.0
    gap_closed: float  # 0.0-1.0


@dataclass
class MediationResult:
    """Result of mediation attempt."""
    result_id: str
    request_id: str
    outcome: MediationOutcome
    resolved: bool
    compromise_proposal: Optional[CompromiseProposal]
    accepted_by: list[str]
    rejected_by: list[str]
    remaining_conflicts: list[ConflictSummaryForMediation]
    mediator_notes: str
    recommendations: list[str]
    alternatives: Optional[list[CompromiseProposal]]
    metrics: MediationMetrics


# ============================================
# Deadlock Resolution Types
# ============================================


@dataclass
class TurnSummary:
    """Summary of a negotiation turn."""
    turn_number: int
    actor: str
    action: str
    key_changes: list[str]
    progress_made: bool


@dataclass
class DeadlockResolutionRequest:
    """Request to resolve a deadlock."""
    request_id: str
    session_id: str
    deadlock_turns: int
    turn_history: list[TurnSummary]
    party_positions: list[PartyPosition]
    previously_tried: list[MediationResolutionStrategy]


@dataclass
class AlternativeStrategy:
    """An alternative strategy option."""
    strategy: MediationResolutionStrategy
    description: str
    pros: list[str]
    cons: list[str]
    likelihood_of_success: float  # 0.0-1.0


@dataclass
class DeadlockResolution:
    """Result of deadlock resolution attempt."""
    resolution_id: str
    request_id: str
    resolution_possible: bool
    strategy: MediationResolutionStrategy
    proposal: Optional[CompromiseProposal]
    explanation: str
    escalation_needed: bool
    escalation_reason: Optional[str]
    alternative_strategies: list[AlternativeStrategy]
    confidence: float  # 0.0-1.0


# ============================================
# Escalation Types
# ============================================


@dataclass
class EscalationRequest:
    """Request for escalation."""
    request_id: str
    session_id: str
    reason: str
    conflict_summary: ConflictSummaryForMediation
    mediation_history: list[MediationResult]
    urgency: ConflictPriority
    recommended_action: str


@dataclass
class EscalationResponse:
    """Response to escalation request."""
    response_id: str
    request_id: str
    escalation_accepted: bool
    assigned_to: Optional[str] = None
    expected_resolution_time: Optional[str] = None
    interim_action: Optional[str] = None
    notes: Optional[str] = None


# ============================================
# Common Ground Analysis Types
# ============================================


@dataclass
class AgreedTerm:
    """A term where parties agree."""
    term_name: str
    agreed_value: str


@dataclass
class CloseTerm:
    """A term where positions are close."""
    term_name: str
    value_a: str
    value_b: str
    gap_assessment: str
    suggested_compromise: str


@dataclass
class NegotiableTerm:
    """A term that is negotiable."""
    term_name: str
    value_a: str
    value_b: str
    flexibility_a: str
    flexibility_b: str
    trade_off_potential: str


@dataclass
class IncompatibleTerm:
    """A term where positions are incompatible."""
    term_name: str
    value_a: str
    value_b: str
    reason: str
    possible_workarounds: list[str]


@dataclass
class CommonGroundAnalysis:
    """Analysis of common ground between parties."""
    agreed_terms: list[AgreedTerm]
    close_terms: list[CloseTerm]
    negotiable_terms: list[NegotiableTerm]
    incompatible_terms: list[IncompatibleTerm]
    overall_alignment: float  # 0.0-1.0
    recommended_focus: list[str]


# ============================================
# Creative Solution Types
# ============================================


@dataclass
class CreativeSolution:
    """A creative solution to a conflict."""
    solution_id: str
    title: str
    description: str
    how_it_works: str
    benefits_party_a: list[str]
    benefits_party_b: list[str]
    implementation_steps: list[str]
    risks: list[str]
    novelty_score: float  # 0.0-1.0
    feasibility_score: float  # 0.0-1.0


# ============================================
# Callback Types
# ============================================


MediationCallback = Callable[[MediationResult], None]
EscalationCallback = Callable[[EscalationRequest], EscalationResponse]


# ============================================
# ConflictMediator Class
# ============================================


class ConflictMediator:
    """
    Mediates conflicts between negotiating parties.

    Provides capabilities for:
    - Finding common ground between parties
    - Generating compromise proposals
    - Resolving deadlocks with various strategies
    - Escalating unresolvable conflicts
    """

    def __init__(
        self,
        default_style: MediationStyle = MediationStyle.FACILITATIVE,
        escalation_callback: Optional[EscalationCallback] = None,
    ):
        """
        Initialize the conflict mediator.

        Args:
            default_style: Default mediation style to use
            escalation_callback: Callback for handling escalations
        """
        self.default_style = default_style
        self.escalation_callback = escalation_callback
        self._mediation_history: dict[str, list[MediationResult]] = {}

    def mediate(
        self,
        request: MediationRequest,
        callback: Optional[MediationCallback] = None,
    ) -> MediationResult:
        """
        Mediate a conflict between two parties.

        Args:
            request: The mediation request
            callback: Optional callback for mediation result

        Returns:
            MediationResult with the outcome
        """
        start_time = datetime.now()

        # Find common ground
        common_ground = self.find_common_ground(request.party_a, request.party_b)

        # Generate compromise proposals based on mediation style
        compromise = self._generate_compromise(
            request, common_ground, request.mediation_style
        )

        # Generate alternatives if requested
        alternatives = None
        if request.options.generate_alternatives:
            alternatives = self._generate_alternatives(
                request, common_ground, request.options.max_alternatives
            )

        # Determine outcome
        outcome, resolved = self._determine_outcome(
            compromise, common_ground, request.options
        )

        elapsed_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Build result
        result = MediationResult(
            result_id=str(uuid.uuid4()),
            request_id=request.request_id,
            outcome=outcome,
            resolved=resolved,
            compromise_proposal=compromise,
            accepted_by=[],  # Would be populated by party responses
            rejected_by=[],
            remaining_conflicts=self._get_remaining_conflicts(
                request.conflict, resolved
            ),
            mediator_notes=self._generate_mediator_notes(
                request, common_ground, compromise
            ),
            recommendations=self._generate_recommendations(
                request, common_ground, outcome
            ),
            alternatives=alternatives,
            metrics=MediationMetrics(
                iterations_used=1,  # Base implementation
                time_elapsed_ms=elapsed_ms,
                proposals_generated=1 + (len(alternatives) if alternatives else 0),
                proposals_rejected=0,
                common_ground_found=common_ground.overall_alignment,
                gap_closed=self._calculate_gap_closed(common_ground),
            ),
        )

        # Store in history
        session_history = self._mediation_history.setdefault(request.session_id, [])
        session_history.append(result)

        if callback:
            callback(result)

        return result

    def find_common_ground(
        self,
        party_a: PartyPosition,
        party_b: PartyPosition,
    ) -> CommonGroundAnalysis:
        """
        Find common ground between two party positions.

        Args:
            party_a: First party's position
            party_b: Second party's position

        Returns:
            Analysis of common ground
        """
        agreed_terms: list[AgreedTerm] = []
        close_terms: list[CloseTerm] = []
        negotiable_terms: list[NegotiableTerm] = []
        incompatible_terms: list[IncompatibleTerm] = []

        # Build term maps for comparison
        terms_a = {t.term_name: t for t in party_a.proposal.terms}
        terms_b = {t.term_name: t for t in party_b.proposal.terms}

        all_terms = set(terms_a.keys()) | set(terms_b.keys())

        for term_name in all_terms:
            term_a = terms_a.get(term_name)
            term_b = terms_b.get(term_name)

            if term_a is None or term_b is None:
                # One party doesn't have this term
                incompatible_terms.append(IncompatibleTerm(
                    term_name=term_name,
                    value_a=term_a.term_value if term_a else "N/A",
                    value_b=term_b.term_value if term_b else "N/A",
                    reason="Term not present in both proposals",
                    possible_workarounds=["Add term to proposal", "Mark as optional"],
                ))
                continue

            # Check for agreement
            if term_a.term_value == term_b.term_value:
                agreed_terms.append(AgreedTerm(
                    term_name=term_name,
                    agreed_value=term_a.term_value,
                ))
                continue

            # Check if terms are negotiable
            if term_a.negotiable and term_b.negotiable:
                # Check if positions are close
                gap = self._assess_value_gap(term_a, term_b)

                if gap < 0.2:  # Close positions
                    close_terms.append(CloseTerm(
                        term_name=term_name,
                        value_a=term_a.term_value,
                        value_b=term_b.term_value,
                        gap_assessment=f"Small gap ({gap:.0%})",
                        suggested_compromise=self._suggest_compromise_value(term_a, term_b),
                    ))
                else:
                    negotiable_terms.append(NegotiableTerm(
                        term_name=term_name,
                        value_a=term_a.term_value,
                        value_b=term_b.term_value,
                        flexibility_a=self._assess_flexibility(term_a, party_a),
                        flexibility_b=self._assess_flexibility(term_b, party_b),
                        trade_off_potential=self._assess_trade_off_potential(
                            term_name, party_a, party_b
                        ),
                    ))
            else:
                # At least one party has hard constraint
                incompatible_terms.append(IncompatibleTerm(
                    term_name=term_name,
                    value_a=term_a.term_value,
                    value_b=term_b.term_value,
                    reason="At least one party has non-negotiable position",
                    possible_workarounds=self._find_workarounds(term_name, term_a, term_b),
                ))

        # Calculate overall alignment
        total_terms = len(all_terms)
        if total_terms == 0:
            alignment = 0.0
        else:
            agreed_weight = len(agreed_terms) * 1.0
            close_weight = len(close_terms) * 0.8
            negotiable_weight = len(negotiable_terms) * 0.5
            alignment = (agreed_weight + close_weight + negotiable_weight) / total_terms

        # Determine recommended focus
        recommended_focus = []
        if close_terms:
            recommended_focus.append(f"Close positions on: {', '.join(t.term_name for t in close_terms)}")
        if negotiable_terms:
            # Focus on high trade-off potential
            high_potential = [t for t in negotiable_terms if "High" in t.trade_off_potential]
            if high_potential:
                recommended_focus.append(f"Trade-off opportunities: {', '.join(t.term_name for t in high_potential)}")

        return CommonGroundAnalysis(
            agreed_terms=agreed_terms,
            close_terms=close_terms,
            negotiable_terms=negotiable_terms,
            incompatible_terms=incompatible_terms,
            overall_alignment=min(1.0, alignment),
            recommended_focus=recommended_focus,
        )

    def resolve_deadlock(
        self,
        request: DeadlockResolutionRequest,
    ) -> DeadlockResolution:
        """
        Attempt to resolve a negotiation deadlock.

        Args:
            request: The deadlock resolution request

        Returns:
            DeadlockResolution with recommended strategy
        """
        # Analyze the deadlock
        root_cause = self._analyze_deadlock_root_cause(request)

        # Determine best strategy based on what hasn't been tried
        untried_strategies = [
            s for s in MediationResolutionStrategy
            if s not in request.previously_tried
        ]

        if not untried_strategies:
            # All strategies tried, escalation needed
            return DeadlockResolution(
                resolution_id=str(uuid.uuid4()),
                request_id=request.request_id,
                resolution_possible=False,
                strategy=MediationResolutionStrategy.ESCALATE,
                proposal=None,
                explanation="All resolution strategies have been attempted without success",
                escalation_needed=True,
                escalation_reason="Exhausted all automated resolution strategies",
                alternative_strategies=[],
                confidence=0.9,
            )

        # Select best strategy
        best_strategy = self._select_best_strategy(
            request, untried_strategies, root_cause
        )

        # Generate proposal based on strategy
        proposal = self._generate_strategy_proposal(request, best_strategy)

        # Generate alternatives
        alternatives = self._generate_alternative_strategies(
            request, untried_strategies, best_strategy
        )

        return DeadlockResolution(
            resolution_id=str(uuid.uuid4()),
            request_id=request.request_id,
            resolution_possible=True,
            strategy=best_strategy,
            proposal=proposal,
            explanation=self._explain_strategy_selection(best_strategy, root_cause),
            escalation_needed=False,
            escalation_reason=None,
            alternative_strategies=alternatives,
            confidence=self._calculate_strategy_confidence(best_strategy, request),
        )

    def escalate(
        self,
        request: EscalationRequest,
    ) -> EscalationResponse:
        """
        Escalate an unresolvable conflict.

        Args:
            request: The escalation request

        Returns:
            EscalationResponse with escalation status
        """
        if self.escalation_callback:
            return self.escalation_callback(request)

        # Default escalation response
        return EscalationResponse(
            response_id=str(uuid.uuid4()),
            request_id=request.request_id,
            escalation_accepted=True,
            assigned_to="human_mediator",
            expected_resolution_time=None,
            interim_action="Continue with partial agreement if possible",
            notes="Automated escalation - awaiting human review",
        )

    def generate_creative_solutions(
        self,
        conflict: ConflictSummaryForMediation,
        constraints: list[str],
        preferences: list[str],
        max_solutions: int = 5,
    ) -> list[CreativeSolution]:
        """
        Generate creative solutions for a conflict.

        Args:
            conflict: The conflict to solve
            constraints: Constraints to respect
            preferences: Preferences to consider
            max_solutions: Maximum solutions to generate

        Returns:
            List of creative solutions
        """
        solutions: list[CreativeSolution] = []

        # Generate different types of creative solutions
        solution_generators = [
            self._generate_time_based_solution,
            self._generate_scope_based_solution,
            self._generate_resource_based_solution,
            self._generate_hybrid_solution,
            self._generate_incremental_solution,
        ]

        for i, generator in enumerate(solution_generators[:max_solutions]):
            solution = generator(conflict, constraints, preferences, i)
            if solution:
                solutions.append(solution)

        return solutions

    def get_mediation_history(
        self,
        session_id: str,
    ) -> list[MediationResult]:
        """Get mediation history for a session."""
        return self._mediation_history.get(session_id, [])

    # ============================================
    # Private Helper Methods
    # ============================================

    def _generate_compromise(
        self,
        request: MediationRequest,
        common_ground: CommonGroundAnalysis,
        style: MediationStyle,
    ) -> Optional[CompromiseProposal]:
        """Generate a compromise proposal based on common ground and mediation style."""
        if not common_ground.close_terms and not common_ground.negotiable_terms:
            return None

        terms: list[CompromiseTerm] = []
        concessions_a: list[Concession] = []
        concessions_b: list[Concession] = []
        gains_a: list[str] = []
        gains_b: list[str] = []

        # Include agreed terms
        for agreed in common_ground.agreed_terms:
            terms.append(CompromiseTerm(
                term_name=agreed.term_name,
                original_a=agreed.agreed_value,
                original_b=agreed.agreed_value,
                compromise_value=agreed.agreed_value,
                rationale="Both parties already agree",
            ))

        # Handle close terms
        for close in common_ground.close_terms:
            terms.append(CompromiseTerm(
                term_name=close.term_name,
                original_a=close.value_a,
                original_b=close.value_b,
                compromise_value=close.suggested_compromise,
                rationale=f"Positions are close - {close.gap_assessment}",
            ))

            # Track concessions
            if close.suggested_compromise != close.value_a:
                concessions_a.append(Concession(
                    term_name=close.term_name,
                    original_value=close.value_a,
                    conceded_value=close.suggested_compromise,
                    impact="Minor adjustment",
                ))
            if close.suggested_compromise != close.value_b:
                concessions_b.append(Concession(
                    term_name=close.term_name,
                    original_value=close.value_b,
                    conceded_value=close.suggested_compromise,
                    impact="Minor adjustment",
                ))

        # Handle negotiable terms based on style
        for negotiable in common_ground.negotiable_terms:
            compromise_value = self._negotiate_term(
                negotiable, style, request.party_a, request.party_b
            )

            terms.append(CompromiseTerm(
                term_name=negotiable.term_name,
                original_a=negotiable.value_a,
                original_b=negotiable.value_b,
                compromise_value=compromise_value,
                rationale=f"Negotiated using {style.value} approach",
            ))

            if compromise_value != negotiable.value_a:
                concessions_a.append(Concession(
                    term_name=negotiable.term_name,
                    original_value=negotiable.value_a,
                    conceded_value=compromise_value,
                    impact="Negotiated concession",
                    compensation=negotiable.trade_off_potential if "High" in negotiable.trade_off_potential else None,
                ))
            if compromise_value != negotiable.value_b:
                concessions_b.append(Concession(
                    term_name=negotiable.term_name,
                    original_value=negotiable.value_b,
                    conceded_value=compromise_value,
                    impact="Negotiated concession",
                ))

        # Calculate fairness score
        fairness = self._calculate_fairness(concessions_a, concessions_b)

        # Calculate viability
        viability = common_ground.overall_alignment

        # Determine gains
        if len(concessions_a) <= len(concessions_b):
            gains_a.append("Fewer concessions required")
        else:
            gains_b.append("Fewer concessions required")

        if terms:
            gains_a.append(f"Agreement on {len(terms)} terms")
            gains_b.append(f"Agreement on {len(terms)} terms")

        return CompromiseProposal(
            proposal_id=str(uuid.uuid4()),
            description=f"Compromise proposal using {style.value} mediation",
            terms=terms,
            concessions_a=concessions_a,
            concessions_b=concessions_b,
            gains_a=gains_a,
            gains_b=gains_b,
            fairness_score=fairness,
            viability_score=viability,
        )

    def _generate_alternatives(
        self,
        request: MediationRequest,
        common_ground: CommonGroundAnalysis,
        max_alternatives: int,
    ) -> list[CompromiseProposal]:
        """Generate alternative compromise proposals."""
        alternatives: list[CompromiseProposal] = []

        # Try different styles
        other_styles = [s for s in MediationStyle if s != request.mediation_style]

        for style in other_styles[:max_alternatives]:
            alt = self._generate_compromise(request, common_ground, style)
            if alt:
                alternatives.append(alt)

        return alternatives

    def _determine_outcome(
        self,
        compromise: Optional[CompromiseProposal],
        common_ground: CommonGroundAnalysis,
        options: MediationOptions,
    ) -> tuple[MediationOutcome, bool]:
        """Determine the mediation outcome."""
        if not compromise:
            return MediationOutcome.DEADLOCK, False

        if not common_ground.incompatible_terms:
            return MediationOutcome.RESOLVED, True

        if options.allow_partial_resolution and (
            common_ground.agreed_terms or common_ground.close_terms
        ):
            return MediationOutcome.PARTIALLY_RESOLVED, True

        return MediationOutcome.DEADLOCK, False

    def _get_remaining_conflicts(
        self,
        original: ConflictSummaryForMediation,
        resolved: bool,
    ) -> list[ConflictSummaryForMediation]:
        """Get remaining unresolved conflicts."""
        if resolved:
            return []
        return [original]

    def _generate_mediator_notes(
        self,
        request: MediationRequest,
        common_ground: CommonGroundAnalysis,
        compromise: Optional[CompromiseProposal],
    ) -> str:
        """Generate notes about the mediation process."""
        notes = []
        notes.append(f"Mediation style: {request.mediation_style.value}")
        notes.append(f"Overall alignment: {common_ground.overall_alignment:.0%}")
        notes.append(f"Agreed terms: {len(common_ground.agreed_terms)}")
        notes.append(f"Close terms: {len(common_ground.close_terms)}")
        notes.append(f"Negotiable terms: {len(common_ground.negotiable_terms)}")
        notes.append(f"Incompatible terms: {len(common_ground.incompatible_terms)}")

        if compromise:
            notes.append(f"Fairness score: {compromise.fairness_score:.0%}")
            notes.append(f"Viability score: {compromise.viability_score:.0%}")

        return "; ".join(notes)

    def _generate_recommendations(
        self,
        request: MediationRequest,
        common_ground: CommonGroundAnalysis,
        outcome: MediationOutcome,
    ) -> list[str]:
        """Generate recommendations for the parties."""
        recommendations = []

        if outcome == MediationOutcome.DEADLOCK:
            recommendations.append("Consider escalating to human mediator")
            recommendations.append("Review non-negotiable constraints for flexibility")

        if common_ground.incompatible_terms:
            recommendations.append(
                f"Focus on resolving incompatible terms: "
                f"{', '.join(t.term_name for t in common_ground.incompatible_terms)}"
            )

        if common_ground.recommended_focus:
            recommendations.extend(common_ground.recommended_focus)

        if request.options.preserve_relationship:
            recommendations.append("Maintain open communication channels")

        return recommendations

    def _calculate_gap_closed(self, common_ground: CommonGroundAnalysis) -> float:
        """Calculate the percentage of gap closed."""
        total = (
            len(common_ground.agreed_terms) +
            len(common_ground.close_terms) +
            len(common_ground.negotiable_terms) +
            len(common_ground.incompatible_terms)
        )
        if total == 0:
            return 0.0

        closed = len(common_ground.agreed_terms) + len(common_ground.close_terms) * 0.8
        return closed / total

    def _assess_value_gap(
        self,
        term_a: TermSummary,
        term_b: TermSummary,
    ) -> float:
        """Assess the gap between two term values (0.0 = same, 1.0 = very different)."""
        # Try numeric comparison
        try:
            val_a = float(term_a.term_value)
            val_b = float(term_b.term_value)
            max_val = max(abs(val_a), abs(val_b), 1)
            return abs(val_a - val_b) / max_val
        except ValueError:
            pass

        # String comparison - simple equality check
        if term_a.term_value == term_b.term_value:
            return 0.0

        # Check if one contains the other
        if term_a.term_value in term_b.term_value or term_b.term_value in term_a.term_value:
            return 0.3

        return 0.7

    def _suggest_compromise_value(
        self,
        term_a: TermSummary,
        term_b: TermSummary,
    ) -> str:
        """Suggest a compromise value between two terms."""
        # Try numeric averaging
        try:
            val_a = float(term_a.term_value)
            val_b = float(term_b.term_value)
            return str((val_a + val_b) / 2)
        except ValueError:
            pass

        # Use party A's value as default if ranges allow
        if term_a.min_acceptable and term_b.max_acceptable:
            try:
                min_a = float(term_a.min_acceptable)
                max_b = float(term_b.max_acceptable)
                if min_a <= max_b:
                    return str((min_a + max_b) / 2)
            except ValueError:
                pass

        # Default to party A's value
        return term_a.term_value

    def _assess_flexibility(
        self,
        term: TermSummary,
        party: PartyPosition,
    ) -> str:
        """Assess flexibility for a term."""
        if not term.negotiable:
            return "No flexibility - non-negotiable"

        if term.term_name in party.flexibility.flexible_terms:
            return "High flexibility"

        # Check if involved in trade-offs
        for pair in party.flexibility.trade_off_pairs:
            if term.term_name in (pair.term_a, pair.term_b):
                return f"Conditional flexibility - trade-off with {pair.term_b if term.term_name == pair.term_a else pair.term_a}"

        return "Limited flexibility"

    def _assess_trade_off_potential(
        self,
        term_name: str,
        party_a: PartyPosition,
        party_b: PartyPosition,
    ) -> str:
        """Assess trade-off potential for a term."""
        a_trade_offs = [
            p for p in party_a.flexibility.trade_off_pairs
            if term_name in (p.term_a, p.term_b)
        ]
        b_trade_offs = [
            p for p in party_b.flexibility.trade_off_pairs
            if term_name in (p.term_a, p.term_b)
        ]

        if a_trade_offs and b_trade_offs:
            return "High - both parties have trade-off options"
        if a_trade_offs or b_trade_offs:
            return "Medium - one party has trade-off options"
        return "Low - no clear trade-off options"

    def _find_workarounds(
        self,
        term_name: str,
        term_a: TermSummary,
        term_b: TermSummary,
    ) -> list[str]:
        """Find possible workarounds for incompatible terms."""
        workarounds = []

        if not term_a.negotiable and term_b.negotiable:
            workarounds.append(f"Party B could accept {term_a.term_value}")
        elif term_a.negotiable and not term_b.negotiable:
            workarounds.append(f"Party A could accept {term_b.term_value}")
        else:
            workarounds.append("Review constraints for flexibility")
            workarounds.append("Consider alternative approaches")

        return workarounds

    def _negotiate_term(
        self,
        negotiable: NegotiableTerm,
        style: MediationStyle,
        party_a: PartyPosition,
        party_b: PartyPosition,
    ) -> str:
        """Negotiate a value for a term based on mediation style."""
        if style == MediationStyle.FACILITATIVE:
            # Let parties find middle ground
            return self._split_difference(negotiable.value_a, negotiable.value_b)

        elif style == MediationStyle.EVALUATIVE:
            # Mediator suggests based on fairness
            return self._evaluate_fair_value(negotiable, party_a, party_b)

        elif style == MediationStyle.TRANSFORMATIVE:
            # Focus on underlying needs
            return self._transform_value(negotiable, party_a, party_b)

        elif style == MediationStyle.DIRECTIVE:
            # Mediator decides
            return self._directive_value(negotiable, party_a, party_b)

        return negotiable.value_a

    def _split_difference(self, value_a: str, value_b: str) -> str:
        """Split the difference between two values."""
        try:
            a = float(value_a)
            b = float(value_b)
            return str((a + b) / 2)
        except ValueError:
            return value_a

    def _evaluate_fair_value(
        self,
        negotiable: NegotiableTerm,
        party_a: PartyPosition,
        party_b: PartyPosition,
    ) -> str:
        """Evaluate a fair value based on party positions."""
        # Weight by flexibility
        flex_a = 1.0 if "High" in negotiable.flexibility_a else 0.5
        flex_b = 1.0 if "High" in negotiable.flexibility_b else 0.5

        try:
            a = float(negotiable.value_a)
            b = float(negotiable.value_b)
            # Weight toward less flexible party
            total_flex = flex_a + flex_b
            weight_a = flex_b / total_flex  # More weight to A if B is flexible
            weight_b = flex_a / total_flex
            return str(a * weight_a + b * weight_b)
        except ValueError:
            return negotiable.value_a if flex_a < flex_b else negotiable.value_b

    def _transform_value(
        self,
        negotiable: NegotiableTerm,
        party_a: PartyPosition,
        party_b: PartyPosition,
    ) -> str:
        """Transform the negotiation to address underlying needs."""
        # Look for creative solutions in trade-offs
        for pair in party_a.flexibility.trade_off_pairs:
            if negotiable.term_name in (pair.term_a, pair.term_b):
                # Consider the relationship
                return self._split_difference(negotiable.value_a, negotiable.value_b)

        return self._split_difference(negotiable.value_a, negotiable.value_b)

    def _directive_value(
        self,
        negotiable: NegotiableTerm,
        party_a: PartyPosition,
        party_b: PartyPosition,
    ) -> str:
        """Provide a directive decision on value."""
        # Check which value is more reasonable
        try:
            a = float(negotiable.value_a)
            b = float(negotiable.value_b)
            # Choose value closer to industry standard (assume midpoint)
            mid = (a + b) / 2
            return str(mid)
        except ValueError:
            # Default to first party
            return negotiable.value_a

    def _calculate_fairness(
        self,
        concessions_a: list[Concession],
        concessions_b: list[Concession],
    ) -> float:
        """Calculate fairness score based on concessions."""
        count_a = len(concessions_a)
        count_b = len(concessions_b)

        if count_a == 0 and count_b == 0:
            return 1.0

        total = count_a + count_b
        balance = 1.0 - abs(count_a - count_b) / total
        return balance

    def _analyze_deadlock_root_cause(
        self,
        request: DeadlockResolutionRequest,
    ) -> str:
        """Analyze the root cause of a deadlock."""
        if not request.turn_history:
            return "Insufficient data to determine root cause"

        # Check for patterns
        no_progress_count = sum(
            1 for t in request.turn_history if not t.progress_made
        )

        if no_progress_count == len(request.turn_history):
            return "Complete stagnation - parties unable to find any common ground"

        if no_progress_count > len(request.turn_history) * 0.8:
            return "Near-complete stagnation - minimal progress over multiple turns"

        return "Partial progress but unable to close remaining gaps"

    def _select_best_strategy(
        self,
        request: DeadlockResolutionRequest,
        untried: list[MediationResolutionStrategy],
        root_cause: str,
    ) -> MediationResolutionStrategy:
        """Select the best strategy for deadlock resolution."""
        # Prioritize based on root cause
        if "stagnation" in root_cause.lower():
            priorities = [
                MediationResolutionStrategy.BRIDGE,
                MediationResolutionStrategy.ALTERNATIVE,
                MediationResolutionStrategy.SPLIT_DIFFERENCE,
            ]
        else:
            priorities = [
                MediationResolutionStrategy.PACKAGE_DEAL,
                MediationResolutionStrategy.NEGOTIATE_TERMS,
                MediationResolutionStrategy.SUBSET,
            ]

        for priority in priorities:
            if priority in untried:
                return priority

        # Return first untried
        return untried[0] if untried else MediationResolutionStrategy.ESCALATE

    def _generate_strategy_proposal(
        self,
        request: DeadlockResolutionRequest,
        strategy: MediationResolutionStrategy,
    ) -> Optional[CompromiseProposal]:
        """Generate a proposal based on the selected strategy."""
        if len(request.party_positions) < 2:
            return None

        party_a = request.party_positions[0]
        party_b = request.party_positions[1]

        terms: list[CompromiseTerm] = []
        concessions_a: list[Concession] = []
        concessions_b: list[Concession] = []

        # Generate terms based on strategy
        terms_a = {t.term_name: t for t in party_a.proposal.terms}
        terms_b = {t.term_name: t for t in party_b.proposal.terms}

        if strategy == MediationResolutionStrategy.SPLIT_DIFFERENCE:
            for name in set(terms_a.keys()) & set(terms_b.keys()):
                compromise = self._split_difference(
                    terms_a[name].term_value,
                    terms_b[name].term_value,
                )
                terms.append(CompromiseTerm(
                    term_name=name,
                    original_a=terms_a[name].term_value,
                    original_b=terms_b[name].term_value,
                    compromise_value=compromise,
                    rationale="Split the difference",
                ))

        elif strategy == MediationResolutionStrategy.SUBSET:
            # Use common capabilities
            common_caps = set(party_a.proposal.capabilities) & set(party_b.proposal.capabilities)
            for name in set(terms_a.keys()) & set(terms_b.keys()):
                if terms_a[name].term_value == terms_b[name].term_value:
                    terms.append(CompromiseTerm(
                        term_name=name,
                        original_a=terms_a[name].term_value,
                        original_b=terms_b[name].term_value,
                        compromise_value=terms_a[name].term_value,
                        rationale="Common subset",
                    ))

        if not terms:
            return None

        return CompromiseProposal(
            proposal_id=str(uuid.uuid4()),
            description=f"Deadlock resolution using {strategy.value} strategy",
            terms=terms,
            concessions_a=concessions_a,
            concessions_b=concessions_b,
            gains_a=["Deadlock resolved"],
            gains_b=["Deadlock resolved"],
            fairness_score=0.8,
            viability_score=0.7,
        )

    def _generate_alternative_strategies(
        self,
        request: DeadlockResolutionRequest,
        untried: list[MediationResolutionStrategy],
        selected: MediationResolutionStrategy,
    ) -> list[AlternativeStrategy]:
        """Generate alternative strategy options."""
        alternatives = []

        strategy_info = {
            MediationResolutionStrategy.TRANSFORM: {
                "desc": "Convert data formats to achieve compatibility",
                "pros": ["Preserves both parties' core requirements", "Technical solution"],
                "cons": ["May require significant implementation effort", "Runtime overhead"],
                "success": 0.7,
            },
            MediationResolutionStrategy.SUBSET: {
                "desc": "Use only capabilities both parties support",
                "pros": ["Guaranteed compatibility", "Simple to implement"],
                "cons": ["Reduced functionality", "May not meet all requirements"],
                "success": 0.8,
            },
            MediationResolutionStrategy.BRIDGE: {
                "desc": "Create adapter layer between parties",
                "pros": ["Preserves full functionality", "Flexible"],
                "cons": ["Additional complexity", "Maintenance burden"],
                "success": 0.65,
            },
            MediationResolutionStrategy.PACKAGE_DEAL: {
                "desc": "Bundle multiple issues for trade-offs",
                "pros": ["Addresses multiple concerns", "Creative solutions"],
                "cons": ["Complex to negotiate", "May introduce new conflicts"],
                "success": 0.6,
            },
            MediationResolutionStrategy.TIME_SHARE: {
                "desc": "Alternate between parties' preferences",
                "pros": ["Fair distribution", "Both get what they want sometimes"],
                "cons": ["Complexity in scheduling", "May not suit all use cases"],
                "success": 0.5,
            },
        }

        for strategy in untried:
            if strategy == selected or strategy == MediationResolutionStrategy.ESCALATE:
                continue

            info = strategy_info.get(strategy, {
                "desc": f"Apply {strategy.value} approach",
                "pros": ["Alternative approach"],
                "cons": ["Untested in this context"],
                "success": 0.5,
            })

            alternatives.append(AlternativeStrategy(
                strategy=strategy,
                description=info["desc"],
                pros=info["pros"],
                cons=info["cons"],
                likelihood_of_success=info["success"],
            ))

        return alternatives[:3]  # Return top 3

    def _explain_strategy_selection(
        self,
        strategy: MediationResolutionStrategy,
        root_cause: str,
    ) -> str:
        """Explain why a strategy was selected."""
        explanations = {
            MediationResolutionStrategy.TRANSFORM:
                "Data transformation can resolve format incompatibilities",
            MediationResolutionStrategy.SUBSET:
                "Using common capabilities ensures compatibility",
            MediationResolutionStrategy.BRIDGE:
                "An adapter layer can mediate between different interfaces",
            MediationResolutionStrategy.SPLIT_DIFFERENCE:
                "Averaging positions creates a fair middle ground",
            MediationResolutionStrategy.PACKAGE_DEAL:
                "Bundling issues allows for creative trade-offs",
            MediationResolutionStrategy.NEGOTIATE_TERMS:
                "Adjusting terms while keeping core requirements",
            MediationResolutionStrategy.ALTERNATIVE:
                "Substituting equivalent capabilities can break deadlock",
            MediationResolutionStrategy.TIME_SHARE:
                "Alternating usage can satisfy both parties",
            MediationResolutionStrategy.ESCALATE:
                "Human intervention needed for this complex situation",
            MediationResolutionStrategy.MEDIATE:
                "Third-party mediation can provide neutral perspective",
        }

        base = explanations.get(
            strategy,
            f"Strategy {strategy.value} selected based on analysis"
        )
        return f"{base}. Root cause: {root_cause}"

    def _calculate_strategy_confidence(
        self,
        strategy: MediationResolutionStrategy,
        request: DeadlockResolutionRequest,
    ) -> float:
        """Calculate confidence in the strategy's success."""
        base_confidence = {
            MediationResolutionStrategy.SUBSET: 0.85,
            MediationResolutionStrategy.SPLIT_DIFFERENCE: 0.75,
            MediationResolutionStrategy.TRANSFORM: 0.7,
            MediationResolutionStrategy.BRIDGE: 0.65,
            MediationResolutionStrategy.NEGOTIATE_TERMS: 0.6,
            MediationResolutionStrategy.PACKAGE_DEAL: 0.55,
            MediationResolutionStrategy.ALTERNATIVE: 0.5,
            MediationResolutionStrategy.TIME_SHARE: 0.45,
            MediationResolutionStrategy.MEDIATE: 0.4,
            MediationResolutionStrategy.ESCALATE: 0.3,
        }.get(strategy, 0.5)

        # Adjust based on deadlock severity
        if request.deadlock_turns > 10:
            base_confidence *= 0.8
        elif request.deadlock_turns > 5:
            base_confidence *= 0.9

        # Adjust based on prior failures
        prior_failures = len(request.previously_tried)
        base_confidence *= (1 - prior_failures * 0.05)

        return max(0.1, min(1.0, base_confidence))

    def _generate_time_based_solution(
        self,
        conflict: ConflictSummaryForMediation,
        constraints: list[str],
        preferences: list[str],
        index: int,
    ) -> CreativeSolution:
        """Generate a time-based creative solution."""
        return CreativeSolution(
            solution_id=str(uuid.uuid4()),
            title="Phased Implementation",
            description="Implement requirements in phases over time",
            how_it_works="Start with common requirements, add party-specific features in later phases",
            benefits_party_a=["Gets core requirements immediately", "Can influence phase 2 priorities"],
            benefits_party_b=["Gets core requirements immediately", "Time to adapt to changes"],
            implementation_steps=[
                "Define phase 1 common requirements",
                "Implement phase 1",
                "Gather feedback",
                "Plan party-specific enhancements",
                "Implement subsequent phases",
            ],
            risks=["Timeline may extend", "Phase 2 requirements may change"],
            novelty_score=0.6,
            feasibility_score=0.8,
        )

    def _generate_scope_based_solution(
        self,
        conflict: ConflictSummaryForMediation,
        constraints: list[str],
        preferences: list[str],
        index: int,
    ) -> CreativeSolution:
        """Generate a scope-based creative solution."""
        return CreativeSolution(
            solution_id=str(uuid.uuid4()),
            title="Scope Segmentation",
            description="Divide scope so each party owns different segments",
            how_it_works="Party A handles segment X, Party B handles segment Y, with clear interfaces",
            benefits_party_a=["Full control over owned segment", "Clear responsibility boundaries"],
            benefits_party_b=["Full control over owned segment", "Reduced coordination overhead"],
            implementation_steps=[
                "Define segment boundaries",
                "Assign segments to parties",
                "Define interface contracts",
                "Implement independently",
                "Integrate at defined interfaces",
            ],
            risks=["Interface complexity", "Integration challenges"],
            novelty_score=0.5,
            feasibility_score=0.75,
        )

    def _generate_resource_based_solution(
        self,
        conflict: ConflictSummaryForMediation,
        constraints: list[str],
        preferences: list[str],
        index: int,
    ) -> CreativeSolution:
        """Generate a resource-based creative solution."""
        return CreativeSolution(
            solution_id=str(uuid.uuid4()),
            title="Resource Pooling",
            description="Pool resources to meet both parties' requirements",
            how_it_works="Combine resources from both parties to achieve more than either could alone",
            benefits_party_a=["Access to additional resources", "Shared cost burden"],
            benefits_party_b=["Access to additional resources", "Economies of scale"],
            implementation_steps=[
                "Inventory available resources",
                "Identify synergies",
                "Define resource sharing agreement",
                "Implement pooled solution",
                "Monitor and adjust allocation",
            ],
            risks=["Resource contention", "Dependency on partner"],
            novelty_score=0.55,
            feasibility_score=0.7,
        )

    def _generate_hybrid_solution(
        self,
        conflict: ConflictSummaryForMediation,
        constraints: list[str],
        preferences: list[str],
        index: int,
    ) -> CreativeSolution:
        """Generate a hybrid creative solution."""
        return CreativeSolution(
            solution_id=str(uuid.uuid4()),
            title="Hybrid Approach",
            description="Combine multiple approaches to address different aspects",
            how_it_works="Use different strategies for different parts of the conflict",
            benefits_party_a=["Customized approach", "Best-fit solutions for each aspect"],
            benefits_party_b=["Flexible resolution", "Addresses specific concerns"],
            implementation_steps=[
                "Decompose conflict into aspects",
                "Select best strategy per aspect",
                "Define integration approach",
                "Implement in coordinated manner",
                "Validate combined solution",
            ],
            risks=["Complexity", "Integration challenges"],
            novelty_score=0.7,
            feasibility_score=0.65,
        )

    def _generate_incremental_solution(
        self,
        conflict: ConflictSummaryForMediation,
        constraints: list[str],
        preferences: list[str],
        index: int,
    ) -> CreativeSolution:
        """Generate an incremental creative solution."""
        return CreativeSolution(
            solution_id=str(uuid.uuid4()),
            title="Incremental Resolution",
            description="Resolve conflict incrementally, building trust step by step",
            how_it_works="Start with smallest viable agreement, expand as trust builds",
            benefits_party_a=["Low initial commitment", "Can exit if not working"],
            benefits_party_b=["Low initial risk", "Builds confidence gradually"],
            implementation_steps=[
                "Identify minimum viable agreement",
                "Implement smallest scope",
                "Validate and build trust",
                "Expand scope incrementally",
                "Iterate until full resolution",
            ],
            risks=["Slow progress", "May stall at any stage"],
            novelty_score=0.5,
            feasibility_score=0.85,
        )
