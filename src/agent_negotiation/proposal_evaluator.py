"""
Proposal Evaluation & Counter-Offer Generation

Evaluates negotiation proposals against policy and generates counter-offers.
Issue #58 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.6)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any, Callable
import uuid

# Import shared enums from negotiation_state to avoid duplication
from .negotiation_state import NegotiationAction, RiskLevel


# ============================================
# Enums
# ============================================


class CapabilityLevel(Enum):
    """Level of capability being offered."""
    FULL = "full"
    STANDARD = "standard"
    LIMITED = "limited"
    TRIAL = "trial"
    MINIMAL = "minimal"


class NegotiationStrategyType(Enum):
    """Negotiation strategy type."""
    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    PRINCIPLED = "principled"
    ACCOMMODATING = "accommodating"
    AVOIDING = "avoiding"


class CapabilityGapType(Enum):
    """Type of capability gap."""
    MISSING = "missing"
    INSUFFICIENT_LEVEL = "insufficient_level"
    PARAMETER_MISMATCH = "parameter_mismatch"
    RESTRICTION_CONFLICT = "restriction_conflict"


class TermGapType(Enum):
    """Type of term gap."""
    BELOW_MINIMUM = "below_minimum"
    ABOVE_MAXIMUM = "above_maximum"
    INCOMPATIBLE = "incompatible"
    MISSING = "missing"


class ChangeType(Enum):
    """Type of proposal change."""
    CONCESSION = "concession"
    REQUEST = "request"
    CLARIFICATION = "clarification"
    ADDITION = "addition"
    REMOVAL = "removal"
    MODIFICATION = "modification"


# NegotiationAction and RiskLevel are imported from negotiation_state


# ============================================
# Capability Types
# ============================================


@dataclass
class RequestedParameter:
    """A parameter being requested."""
    name: str
    value: str
    negotiable: bool = True
    min_acceptable: Optional[str] = None
    max_acceptable: Optional[str] = None


@dataclass
class CapabilityRequest:
    """A capability being requested in a proposal."""
    capability_id: str
    capability_name: str
    required: bool
    priority: int = 5
    parameters: Optional[List[RequestedParameter]] = None
    usage_context: Optional[str] = None


@dataclass
class OfferedParameter:
    """A parameter being offered."""
    name: str
    value: str
    fixed: bool = False
    alternatives: Optional[List[str]] = None


@dataclass
class CapabilityOffer:
    """A capability being offered in a proposal."""
    capability_id: str
    capability_name: str
    level: CapabilityLevel
    parameters: Optional[List[OfferedParameter]] = None
    restrictions: Optional[List[str]] = None
    estimated_cost: Optional[float] = None


# ============================================
# Evaluation Policy
# ============================================


@dataclass
class MinimumTerms:
    """Minimum acceptable terms."""
    min_duration_hours: Optional[int] = None
    max_rate_limit: Optional[int] = None
    min_priority_level: Optional[int] = None
    required_capabilities: List[str] = field(default_factory=list)
    forbidden_terms: Optional[List[str]] = None
    min_sla_availability: Optional[float] = None


@dataclass
class ScoringWeights:
    """Weights for proposal scoring."""
    term_attractiveness: float = 0.4
    offered_value: float = 0.3
    request_burden: float = 0.3

    def __post_init__(self):
        """Validate weights sum to 1.0."""
        total = self.term_attractiveness + self.offered_value + self.request_burden
        if abs(total - 1.0) > 0.01:
            # Normalize weights
            self.term_attractiveness /= total
            self.offered_value /= total
            self.request_burden /= total


@dataclass
class CapabilityPriority:
    """Priority for a specific capability."""
    capability_id: str
    importance: float
    acceptable_levels: List[CapabilityLevel]


@dataclass
class RiskFactorWeights:
    """Weights for different risk factors."""
    security: float = 0.3
    compliance: float = 0.2
    performance: float = 0.2
    reliability: float = 0.2
    cost: float = 0.1


@dataclass
class RiskTolerance:
    """Risk tolerance settings."""
    max_risk_level: RiskLevel
    require_mitigation_above: RiskLevel
    risk_factor_weights: Optional[RiskFactorWeights] = None


@dataclass
class EvaluationPolicy:
    """Policy for evaluating proposals."""
    min_acceptable_terms: MinimumTerms
    negotiation_strategy: NegotiationStrategyType
    max_counter_offers: int = 3
    auto_accept_threshold: float = 0.85
    auto_reject_threshold: float = 0.3
    scoring_weights: ScoringWeights = field(default_factory=ScoringWeights)
    capability_priorities: Optional[List[CapabilityPriority]] = None
    risk_tolerance: Optional[RiskTolerance] = None


# ============================================
# Gap Analysis
# ============================================


@dataclass
class CapabilityGap:
    """Gap in a specific capability."""
    capability_id: str
    capability_name: str
    gap_type: CapabilityGapType
    severity: float
    requested_level: Optional[str] = None
    offered_level: Optional[str] = None
    suggestion: Optional[str] = None


@dataclass
class TermGap:
    """Gap in terms."""
    term_name: str
    gap_type: TermGapType
    severity: float
    negotiable: bool = True
    requested_value: Optional[str] = None
    offered_value: Optional[str] = None


@dataclass
class ConstraintViolation:
    """A constraint that was violated."""
    constraint_id: str
    constraint_description: str
    violation_description: str
    severity: float
    waivable: bool = False


@dataclass
class GapAnalysis:
    """Analysis of gaps between proposal and requirements."""
    has_gaps: bool
    capability_gaps: List[CapabilityGap]
    term_gaps: List[TermGap]
    constraint_violations: List[ConstraintViolation]
    overall_gap_score: float
    bridgeable: bool
    bridge_difficulty: float

    @classmethod
    def no_gaps(cls) -> "GapAnalysis":
        """Create a gap analysis with no gaps."""
        return cls(
            has_gaps=False,
            capability_gaps=[],
            term_gaps=[],
            constraint_violations=[],
            overall_gap_score=0.0,
            bridgeable=True,
            bridge_difficulty=0.0,
        )


# ============================================
# Proposal Scoring
# ============================================


@dataclass
class TermScore:
    """Score for proposal terms."""
    score: float
    duration_score: float = 1.0
    rate_limit_score: float = 1.0
    priority_score: float = 1.0
    sla_score: float = 1.0
    billing_score: float = 1.0


@dataclass
class ValueScore:
    """Score for offered value."""
    score: float
    capability_coverage: float = 1.0
    capability_quality: float = 1.0
    parameter_match: float = 1.0


@dataclass
class BurdenScore:
    """Score for request burden."""
    score: float
    fulfillment_difficulty: float = 0.0
    resource_cost: float = 0.0
    opportunity_cost: float = 0.0


@dataclass
class RiskScore:
    """Risk score assessment."""
    score: float
    security_risk: float = 0.0
    compliance_risk: float = 0.0
    operational_risk: float = 0.0
    reputational_risk: float = 0.0


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown."""
    strengths: List[str]
    weaknesses: List[str]
    opportunities: List[str]
    threats: List[str]


@dataclass
class ProposalScore:
    """Detailed scoring of a proposal."""
    overall_score: float
    term_score: TermScore
    value_score: ValueScore
    burden_score: BurdenScore
    risk_score: RiskScore
    breakdown: ScoreBreakdown


# ============================================
# Evaluation Result
# ============================================


@dataclass
class EvaluationDecision:
    """Evaluation decision."""
    action: NegotiationAction
    auto_decided: bool = False
    threshold_triggered: Optional[str] = None
    requires_human_review: bool = False


@dataclass
class EvaluationRationale:
    """Rationale for the evaluation decision."""
    summary: str
    key_factors: List[str]
    concerns: Optional[List[str]] = None
    positive_aspects: Optional[List[str]] = None
    trade_offs: Optional[List[str]] = None


@dataclass
class ProposalChange:
    """A change made to a proposal."""
    field: str
    original_value: str
    new_value: str
    change_type: ChangeType
    justification: str


@dataclass
class CounterProposalResult:
    """Result of counter-proposal generation."""
    changes_made: List[ProposalChange]
    concessions_offered: List[str]
    concessions_requested: List[str]
    expected_acceptance: float
    rationale: str


@dataclass
class ProposalEvaluationResult:
    """Complete result of proposal evaluation."""
    decision: EvaluationDecision
    score: ProposalScore
    gap_analysis: GapAnalysis
    counter_proposal_result: Optional[CounterProposalResult]
    rationale: EvaluationRationale
    recommendations: List[str]
    confidence: float


# ============================================
# Proposal Evaluator
# ============================================


class ProposalEvaluator:
    """
    Evaluates negotiation proposals against policy and generates counter-offers.

    Scoring Formula:
    - Term Attractiveness (40%): Duration, auto-renew, conditions
    - Offered Value (30%): Value of capabilities offered
    - Request Burden (30%): Cost of fulfilling requests
    """

    # Default scoring thresholds
    DEFAULT_AUTO_ACCEPT = 0.85
    DEFAULT_AUTO_REJECT = 0.3

    # Level rankings for comparison
    LEVEL_RANKINGS: Dict[CapabilityLevel, int] = {
        CapabilityLevel.FULL: 5,
        CapabilityLevel.STANDARD: 4,
        CapabilityLevel.LIMITED: 3,
        CapabilityLevel.TRIAL: 2,
        CapabilityLevel.MINIMAL: 1,
    }

    def __init__(self, policy: EvaluationPolicy):
        """
        Initialize evaluator with policy.

        Args:
            policy: Evaluation policy to use
        """
        self.policy = policy
        self._counter_offer_count = 0

    @property
    def can_counter(self) -> bool:
        """Check if we can still make counter-offers."""
        return self._counter_offer_count < self.policy.max_counter_offers

    def evaluate(
        self,
        requested_capabilities: List[CapabilityRequest],
        offered_capabilities: List[CapabilityOffer],
        terms: Dict[str, Any],
    ) -> ProposalEvaluationResult:
        """
        Evaluate a proposal against policy.

        Args:
            requested_capabilities: Capabilities being requested from us
            offered_capabilities: Capabilities being offered to us
            terms: Proposed terms (duration_hours, rate_limit, priority_level, etc.)

        Returns:
            ProposalEvaluationResult with decision and analysis
        """
        # Calculate scores
        term_score = self._score_terms(terms)
        value_score = self._score_value(offered_capabilities)
        burden_score = self._score_burden(requested_capabilities)
        risk_score = self._assess_risk(offered_capabilities, requested_capabilities)

        # Calculate weighted overall score
        weights = self.policy.scoring_weights
        overall_score = (
            term_score.score * weights.term_attractiveness
            + value_score.score * weights.offered_value
            + (1.0 - burden_score.score) * weights.request_burden  # Invert burden
        )

        # Adjust for risk
        risk_penalty = risk_score.score * 0.2  # Up to 20% penalty for risk
        overall_score = max(0.0, overall_score - risk_penalty)

        # Perform gap analysis
        gap_analysis = self._analyze_gaps(
            offered_capabilities, requested_capabilities, terms
        )

        # Build score breakdown
        breakdown = self._build_breakdown(
            term_score, value_score, burden_score, risk_score, gap_analysis
        )

        proposal_score = ProposalScore(
            overall_score=overall_score,
            term_score=term_score,
            value_score=value_score,
            burden_score=burden_score,
            risk_score=risk_score,
            breakdown=breakdown,
        )

        # Make decision
        decision = self._make_decision(overall_score, gap_analysis)

        # Generate counter-proposal result if countering
        counter_result = None
        if decision.action == NegotiationAction.COUNTER and self.can_counter:
            counter_result = self._generate_counter_proposal_result(
                gap_analysis, offered_capabilities, requested_capabilities, terms
            )
            self._counter_offer_count += 1

        # Build rationale
        rationale = self._build_rationale(decision, proposal_score, gap_analysis)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            decision, proposal_score, gap_analysis
        )

        return ProposalEvaluationResult(
            decision=decision,
            score=proposal_score,
            gap_analysis=gap_analysis,
            counter_proposal_result=counter_result,
            rationale=rationale,
            recommendations=recommendations,
            confidence=self._calculate_confidence(proposal_score, gap_analysis),
        )

    def _score_terms(self, terms: Dict[str, Any]) -> TermScore:
        """Score the proposed terms."""
        min_terms = self.policy.min_acceptable_terms
        scores = {
            "duration": 1.0,
            "rate_limit": 1.0,
            "priority": 1.0,
            "sla": 1.0,
            "billing": 1.0,
        }

        # Duration scoring
        duration = terms.get("duration_hours")
        if duration is not None:
            if min_terms.min_duration_hours:
                if duration >= min_terms.min_duration_hours:
                    # Score based on how much above minimum
                    scores["duration"] = min(
                        1.0, 0.7 + (duration / min_terms.min_duration_hours) * 0.3
                    )
                else:
                    # Below minimum
                    scores["duration"] = max(
                        0.0, duration / min_terms.min_duration_hours
                    )
            else:
                # No minimum, any duration is acceptable
                scores["duration"] = 1.0 if duration > 0 else 0.5

        # Rate limit scoring (lower is worse)
        rate_limit = terms.get("rate_limit_per_minute")
        if rate_limit is not None:
            if min_terms.max_rate_limit:
                if rate_limit <= min_terms.max_rate_limit:
                    # Within acceptable range
                    scores["rate_limit"] = 1.0
                else:
                    # Exceeds our limit (bad for us)
                    scores["rate_limit"] = max(
                        0.0, min_terms.max_rate_limit / rate_limit
                    )
            else:
                # Score based on reasonable defaults
                scores["rate_limit"] = min(1.0, rate_limit / 100.0)

        # Priority scoring
        priority = terms.get("priority_level")
        if priority is not None:
            if min_terms.min_priority_level:
                if priority >= min_terms.min_priority_level:
                    scores["priority"] = 1.0
                else:
                    scores["priority"] = priority / min_terms.min_priority_level
            else:
                scores["priority"] = priority / 10.0  # Assuming 1-10 scale

        # SLA scoring
        sla = terms.get("sla_availability")
        if sla is not None:
            if min_terms.min_sla_availability:
                if sla >= min_terms.min_sla_availability:
                    scores["sla"] = 1.0
                else:
                    scores["sla"] = sla / min_terms.min_sla_availability
            else:
                scores["sla"] = sla  # Direct percentage

        # Billing model scoring
        billing = terms.get("billing_model")
        if billing:
            billing_scores = {
                "free": 1.0,
                "per_call": 0.7,
                "subscription": 0.5,
                "premium": 0.3,
            }
            scores["billing"] = billing_scores.get(billing.lower(), 0.5)

        # Calculate overall term score
        overall = sum(scores.values()) / len(scores)

        return TermScore(
            score=overall,
            duration_score=scores["duration"],
            rate_limit_score=scores["rate_limit"],
            priority_score=scores["priority"],
            sla_score=scores["sla"],
            billing_score=scores["billing"],
        )

    def _score_value(self, offered: List[CapabilityOffer]) -> ValueScore:
        """Score the value of offered capabilities."""
        if not offered:
            return ValueScore(score=0.0, capability_coverage=0.0)

        # Get required capabilities from policy
        required = self.policy.min_acceptable_terms.required_capabilities
        priorities = {
            p.capability_id: p for p in (self.policy.capability_priorities or [])
        }

        # Calculate coverage
        offered_ids = {o.capability_id for o in offered}
        if required:
            covered = len(offered_ids.intersection(required))
            coverage = covered / len(required)
        else:
            coverage = 1.0  # No specific requirements

        # Calculate quality based on levels
        quality_scores = []
        for offer in offered:
            level_rank = self.LEVEL_RANKINGS.get(offer.level, 3)
            base_quality = level_rank / 5.0

            # Adjust based on priority
            if offer.capability_id in priorities:
                priority = priorities[offer.capability_id]
                # Check if level is acceptable
                if offer.level in priority.acceptable_levels:
                    base_quality *= (1 + priority.importance * 0.5)
                else:
                    base_quality *= 0.5  # Penalty for unacceptable level

            quality_scores.append(base_quality)

        quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.5

        # Parameter match (simplified - assume good match if parameters exist)
        param_match = 0.8 if any(o.parameters for o in offered) else 0.6

        overall = (coverage * 0.4 + quality * 0.4 + param_match * 0.2)

        return ValueScore(
            score=overall,
            capability_coverage=coverage,
            capability_quality=quality,
            parameter_match=param_match,
        )

    def _score_burden(self, requested: List[CapabilityRequest]) -> BurdenScore:
        """Score the burden of fulfilling requests."""
        if not requested:
            return BurdenScore(score=0.0)

        # Calculate fulfillment difficulty
        difficulties = []
        for req in requested:
            base_difficulty = 0.3 if req.required else 0.1
            # Higher priority = more burden
            priority_factor = req.priority / 10.0
            difficulties.append(base_difficulty + priority_factor * 0.3)

        difficulty = sum(difficulties) / len(difficulties)

        # Resource cost based on number of requests
        resource_cost = min(1.0, len(requested) * 0.1)

        # Opportunity cost based on commitment
        opportunity_cost = 0.2  # Default moderate opportunity cost

        overall = (difficulty * 0.4 + resource_cost * 0.3 + opportunity_cost * 0.3)

        return BurdenScore(
            score=overall,
            fulfillment_difficulty=difficulty,
            resource_cost=resource_cost,
            opportunity_cost=opportunity_cost,
        )

    def _assess_risk(
        self,
        offered: List[CapabilityOffer],
        requested: List[CapabilityRequest],
    ) -> RiskScore:
        """Assess risks associated with the proposal."""
        if not self.policy.risk_tolerance:
            return RiskScore(score=0.0)

        risks = {
            "security": 0.0,
            "compliance": 0.0,
            "operational": 0.0,
            "reputational": 0.0,
        }

        # Security risk from limited/trial offers
        for offer in offered:
            if offer.level in (CapabilityLevel.TRIAL, CapabilityLevel.MINIMAL):
                risks["security"] += 0.1
            if offer.restrictions:
                risks["operational"] += 0.05 * len(offer.restrictions)

        # Compliance risk from required capabilities
        for req in requested:
            if req.required:
                risks["compliance"] += 0.05

        # Cap individual risks
        risks = {k: min(1.0, v) for k, v in risks.items()}

        # Apply weights if available
        weights = self.policy.risk_tolerance.risk_factor_weights
        if weights:
            weighted_risks = (
                risks["security"] * weights.security
                + risks["compliance"] * weights.compliance
                + risks["operational"] * weights.performance
                + risks["reputational"] * weights.reliability
            )
            # Normalize by total weights
            total_weight = (
                weights.security + weights.compliance + weights.performance + weights.reliability
            )
            overall = weighted_risks / total_weight if total_weight > 0 else 0.0
        else:
            overall = sum(risks.values()) / len(risks)

        return RiskScore(
            score=overall,
            security_risk=risks["security"],
            compliance_risk=risks["compliance"],
            operational_risk=risks["operational"],
            reputational_risk=risks["reputational"],
        )

    def _analyze_gaps(
        self,
        offered: List[CapabilityOffer],
        requested: List[CapabilityRequest],
        terms: Dict[str, Any],
    ) -> GapAnalysis:
        """Analyze gaps between proposal and requirements."""
        capability_gaps = []
        term_gaps = []
        constraint_violations = []

        # Check for missing required capabilities
        required = set(self.policy.min_acceptable_terms.required_capabilities)
        offered_ids = {o.capability_id for o in offered}
        missing = required - offered_ids

        for cap_id in missing:
            capability_gaps.append(
                CapabilityGap(
                    capability_id=cap_id,
                    capability_name=cap_id,  # Would need lookup for real name
                    gap_type=CapabilityGapType.MISSING,
                    severity=0.8,
                    suggestion=f"Request capability {cap_id} to be included",
                )
            )

        # Check capability levels
        priorities = {
            p.capability_id: p for p in (self.policy.capability_priorities or [])
        }
        for offer in offered:
            if offer.capability_id in priorities:
                priority = priorities[offer.capability_id]
                if offer.level not in priority.acceptable_levels:
                    capability_gaps.append(
                        CapabilityGap(
                            capability_id=offer.capability_id,
                            capability_name=offer.capability_name,
                            gap_type=CapabilityGapType.INSUFFICIENT_LEVEL,
                            severity=0.6,
                            requested_level=str(priority.acceptable_levels[0].value),
                            offered_level=offer.level.value,
                            suggestion=f"Request higher capability level",
                        )
                    )

        # Check term gaps
        min_terms = self.policy.min_acceptable_terms

        if min_terms.min_duration_hours:
            duration = terms.get("duration_hours", 0)
            if duration < min_terms.min_duration_hours:
                term_gaps.append(
                    TermGap(
                        term_name="duration_hours",
                        gap_type=TermGapType.BELOW_MINIMUM,
                        severity=0.5,
                        requested_value=str(min_terms.min_duration_hours),
                        offered_value=str(duration),
                    )
                )

        if min_terms.max_rate_limit:
            rate = terms.get("rate_limit_per_minute", float("inf"))
            if rate > min_terms.max_rate_limit:
                term_gaps.append(
                    TermGap(
                        term_name="rate_limit_per_minute",
                        gap_type=TermGapType.ABOVE_MAXIMUM,
                        severity=0.4,
                        requested_value=str(min_terms.max_rate_limit),
                        offered_value=str(rate),
                    )
                )

        if min_terms.min_priority_level:
            priority = terms.get("priority_level", 0)
            if priority < min_terms.min_priority_level:
                term_gaps.append(
                    TermGap(
                        term_name="priority_level",
                        gap_type=TermGapType.BELOW_MINIMUM,
                        severity=0.3,
                        requested_value=str(min_terms.min_priority_level),
                        offered_value=str(priority),
                    )
                )

        # Check forbidden terms
        if min_terms.forbidden_terms:
            billing = terms.get("billing_model", "")
            if billing.lower() in [t.lower() for t in min_terms.forbidden_terms]:
                constraint_violations.append(
                    ConstraintViolation(
                        constraint_id="forbidden_billing",
                        constraint_description=f"Billing model '{billing}' is forbidden",
                        violation_description=f"Proposal includes forbidden billing model: {billing}",
                        severity=0.9,
                        waivable=False,
                    )
                )

        # Calculate overall gap score
        has_gaps = bool(capability_gaps or term_gaps or constraint_violations)

        if has_gaps:
            gap_severities = (
                [g.severity for g in capability_gaps]
                + [g.severity for g in term_gaps]
                + [v.severity for v in constraint_violations]
            )
            overall_gap = sum(gap_severities) / len(gap_severities)
        else:
            overall_gap = 0.0

        # Determine if gaps are bridgeable
        has_non_waivable = any(not v.waivable for v in constraint_violations)
        bridgeable = not has_non_waivable and overall_gap < 0.8

        # Calculate bridge difficulty
        bridge_difficulty = overall_gap * (1.5 if not bridgeable else 1.0)
        bridge_difficulty = min(1.0, bridge_difficulty)

        return GapAnalysis(
            has_gaps=has_gaps,
            capability_gaps=capability_gaps,
            term_gaps=term_gaps,
            constraint_violations=constraint_violations,
            overall_gap_score=overall_gap,
            bridgeable=bridgeable,
            bridge_difficulty=bridge_difficulty,
        )

    def _build_breakdown(
        self,
        term_score: TermScore,
        value_score: ValueScore,
        burden_score: BurdenScore,
        risk_score: RiskScore,
        gap_analysis: GapAnalysis,
    ) -> ScoreBreakdown:
        """Build SWOT-style score breakdown."""
        strengths = []
        weaknesses = []
        opportunities = []
        threats = []

        # Identify strengths
        if term_score.score > 0.7:
            strengths.append("Favorable terms offered")
        if value_score.capability_coverage > 0.8:
            strengths.append("Good capability coverage")
        if burden_score.score < 0.3:
            strengths.append("Low burden of requests")

        # Identify weaknesses
        if term_score.score < 0.5:
            weaknesses.append("Unfavorable terms")
        if value_score.capability_quality < 0.5:
            weaknesses.append("Low quality capability levels")
        if gap_analysis.has_gaps:
            weaknesses.append(f"{len(gap_analysis.capability_gaps)} capability gaps")

        # Identify opportunities
        if gap_analysis.bridgeable and gap_analysis.has_gaps:
            opportunities.append("Gaps can be addressed through negotiation")
        if burden_score.score < 0.5:
            opportunities.append("Room to request additional value")

        # Identify threats
        if risk_score.score > 0.5:
            threats.append("Elevated risk levels")
        if gap_analysis.constraint_violations:
            threats.append("Constraint violations present")

        # Ensure at least one item in each category
        if not strengths:
            strengths.append("Opportunity to establish relationship")
        if not weaknesses:
            weaknesses.append("No significant weaknesses identified")
        if not opportunities:
            opportunities.append("Room for future expansion")
        if not threats:
            threats.append("Standard negotiation risks")

        return ScoreBreakdown(
            strengths=strengths,
            weaknesses=weaknesses,
            opportunities=opportunities,
            threats=threats,
        )

    def _make_decision(
        self,
        overall_score: float,
        gap_analysis: GapAnalysis,
    ) -> EvaluationDecision:
        """Make evaluation decision based on score and gaps."""
        # Check auto-accept threshold
        if overall_score >= self.policy.auto_accept_threshold and not gap_analysis.constraint_violations:
            return EvaluationDecision(
                action=NegotiationAction.ACCEPT,
                auto_decided=True,
                threshold_triggered="auto_accept",
            )

        # Check auto-reject threshold
        if overall_score <= self.policy.auto_reject_threshold or not gap_analysis.bridgeable:
            return EvaluationDecision(
                action=NegotiationAction.REJECT,
                auto_decided=True,
                threshold_triggered="auto_reject" if overall_score <= self.policy.auto_reject_threshold else "unbridgeable_gaps",
            )

        # Check if we can still counter
        if not self.can_counter:
            # Must make final decision
            if overall_score >= 0.5:
                return EvaluationDecision(
                    action=NegotiationAction.ACCEPT,
                    requires_human_review=True,
                )
            else:
                return EvaluationDecision(
                    action=NegotiationAction.REJECT,
                    requires_human_review=True,
                )

        # Default to counter-offer
        return EvaluationDecision(
            action=NegotiationAction.COUNTER,
            requires_human_review=overall_score < 0.5,
        )

    def _generate_counter_proposal_result(
        self,
        gap_analysis: GapAnalysis,
        offered: List[CapabilityOffer],
        requested: List[CapabilityRequest],
        terms: Dict[str, Any],
    ) -> CounterProposalResult:
        """Generate counter-proposal suggestions."""
        changes = []
        concessions_offered = []
        concessions_requested = []

        # Address capability gaps
        for gap in gap_analysis.capability_gaps:
            if gap.gap_type == CapabilityGapType.MISSING:
                changes.append(
                    ProposalChange(
                        field=f"capability:{gap.capability_id}",
                        original_value="not_offered",
                        new_value="requested",
                        change_type=ChangeType.REQUEST,
                        justification=gap.suggestion or f"Capability {gap.capability_id} is required",
                    )
                )
                concessions_requested.append(f"Include {gap.capability_name}")

            elif gap.gap_type == CapabilityGapType.INSUFFICIENT_LEVEL:
                changes.append(
                    ProposalChange(
                        field=f"capability_level:{gap.capability_id}",
                        original_value=gap.offered_level or "unknown",
                        new_value=gap.requested_level or "standard",
                        change_type=ChangeType.REQUEST,
                        justification=f"Higher capability level needed for {gap.capability_name}",
                    )
                )
                concessions_requested.append(f"Upgrade {gap.capability_name} to {gap.requested_level}")

        # Address term gaps
        for gap in gap_analysis.term_gaps:
            if gap.negotiable:
                changes.append(
                    ProposalChange(
                        field=gap.term_name,
                        original_value=gap.offered_value or "0",
                        new_value=gap.requested_value or "negotiable",
                        change_type=ChangeType.REQUEST,
                        justification=f"Term {gap.term_name} needs adjustment",
                    )
                )
                concessions_requested.append(f"Adjust {gap.term_name} to {gap.requested_value}")

        # Offer concessions based on strategy
        strategy = self.policy.negotiation_strategy
        if strategy in (NegotiationStrategyType.COOPERATIVE, NegotiationStrategyType.ACCOMMODATING):
            # Offer to reduce burden
            if requested and len(requested) > 1:
                concessions_offered.append("Willing to accept fewer required capabilities")
                changes.append(
                    ProposalChange(
                        field="request_flexibility",
                        original_value="strict",
                        new_value="flexible",
                        change_type=ChangeType.CONCESSION,
                        justification="Demonstrating flexibility to reach agreement",
                    )
                )

        # Calculate expected acceptance
        expected_acceptance = 0.5
        if len(changes) <= 2:
            expected_acceptance += 0.2
        if concessions_offered:
            expected_acceptance += 0.1
        expected_acceptance = min(0.9, expected_acceptance)

        rationale = self._build_counter_rationale(changes, strategy)

        return CounterProposalResult(
            changes_made=changes,
            concessions_offered=concessions_offered,
            concessions_requested=concessions_requested,
            expected_acceptance=expected_acceptance,
            rationale=rationale,
        )

    def _build_counter_rationale(
        self,
        changes: List[ProposalChange],
        strategy: NegotiationStrategyType,
    ) -> str:
        """Build rationale for counter-proposal."""
        strategy_approaches = {
            NegotiationStrategyType.COOPERATIVE: "seeking mutual benefit",
            NegotiationStrategyType.COMPETITIVE: "maximizing value",
            NegotiationStrategyType.PRINCIPLED: "applying fair standards",
            NegotiationStrategyType.ACCOMMODATING: "prioritizing relationship",
            NegotiationStrategyType.AVOIDING: "minimizing conflict",
        }

        approach = strategy_approaches.get(strategy, "standard negotiation")
        num_changes = len(changes)

        return (
            f"Counter-proposal generated with {num_changes} modification(s), "
            f"{approach}. Focus on addressing critical gaps while "
            f"maintaining reasonable expectations for the other party."
        )

    def _build_rationale(
        self,
        decision: EvaluationDecision,
        score: ProposalScore,
        gap_analysis: GapAnalysis,
    ) -> EvaluationRationale:
        """Build detailed rationale for decision."""
        action_summaries = {
            NegotiationAction.ACCEPT: "Proposal meets or exceeds requirements",
            NegotiationAction.REJECT: "Proposal does not meet minimum requirements",
            NegotiationAction.COUNTER: "Proposal has potential but requires modifications",
        }

        summary = action_summaries.get(
            decision.action,
            f"Decision: {decision.action.value}",
        )

        key_factors = []
        concerns = []
        positive_aspects = []

        # Overall score factor
        key_factors.append(f"Overall score: {score.overall_score:.2f}")

        # Term analysis
        if score.term_score.score > 0.7:
            positive_aspects.append("Favorable terms offered")
        elif score.term_score.score < 0.5:
            concerns.append("Terms below expectations")
            key_factors.append(f"Term score: {score.term_score.score:.2f}")

        # Value analysis
        if score.value_score.capability_coverage > 0.8:
            positive_aspects.append("Good capability coverage")
        else:
            concerns.append(f"Only {score.value_score.capability_coverage:.0%} capability coverage")

        # Gap analysis
        if gap_analysis.has_gaps:
            key_factors.append(f"{len(gap_analysis.capability_gaps)} capability gaps identified")
            if not gap_analysis.bridgeable:
                concerns.append("Gaps are not bridgeable")
        else:
            positive_aspects.append("No significant gaps identified")

        # Risk analysis
        if score.risk_score.score > 0.5:
            concerns.append(f"Elevated risk level: {score.risk_score.score:.2f}")

        # Auto-decision factors
        if decision.auto_decided:
            key_factors.append(f"Auto-{decision.action.value}: {decision.threshold_triggered}")

        return EvaluationRationale(
            summary=summary,
            key_factors=key_factors,
            concerns=concerns if concerns else None,
            positive_aspects=positive_aspects if positive_aspects else None,
        )

    def _generate_recommendations(
        self,
        decision: EvaluationDecision,
        score: ProposalScore,
        gap_analysis: GapAnalysis,
    ) -> List[str]:
        """Generate recommendations for next steps."""
        recommendations = []

        if decision.action == NegotiationAction.ACCEPT:
            recommendations.append("Proceed with acceptance")
            recommendations.append("Document agreed terms for reference")
            if decision.requires_human_review:
                recommendations.append("Consider human review before finalizing")

        elif decision.action == NegotiationAction.REJECT:
            recommendations.append("Communicate rejection with clear reasoning")
            if gap_analysis.bridgeable:
                recommendations.append("Consider if alternative proposal structure could work")

        elif decision.action == NegotiationAction.COUNTER:
            recommendations.append("Submit counter-proposal addressing key gaps")
            if gap_analysis.capability_gaps:
                recommendations.append(
                    f"Focus on resolving {len(gap_analysis.capability_gaps)} capability gaps"
                )
            if gap_analysis.term_gaps:
                recommendations.append(
                    f"Negotiate {len(gap_analysis.term_gaps)} term adjustments"
                )

        # General recommendations
        if score.risk_score.score > 0.3:
            recommendations.append("Consider risk mitigation measures")

        return recommendations

    def _calculate_confidence(
        self,
        score: ProposalScore,
        gap_analysis: GapAnalysis,
    ) -> float:
        """Calculate confidence in the evaluation."""
        # Base confidence
        confidence = 0.7

        # Higher confidence if score is very high or very low (clear decision)
        if score.overall_score > 0.8 or score.overall_score < 0.3:
            confidence += 0.15

        # Lower confidence if there are many gaps
        if len(gap_analysis.capability_gaps) > 3:
            confidence -= 0.1

        # Higher confidence if no constraint violations
        if not gap_analysis.constraint_violations:
            confidence += 0.1

        return max(0.3, min(1.0, confidence))

    def reset_counter_count(self) -> None:
        """Reset the counter-offer count."""
        self._counter_offer_count = 0
