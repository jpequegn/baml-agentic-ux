"""
Tests for Contract-Net Protocol Implementation

Issue #59 - Phase 3: Agent-to-Agent Interface Negotiation (Task 3.7)
"""

import pytest
from datetime import datetime, timedelta

from src.agent_negotiation.contract_net import (
    # Enums
    TaskPriority,
    TaskConstraintType,
    CFPUrgency,
    EvaluationType,
    CommitmentLevel,
    ConditionType,
    RefusalReason,
    EvaluationRiskLevel,
    NotificationType,
    ExecutionStatus,
    IssueSeverity,
    ContractNetStatus,
    # Types
    TaskConstraint,
    TaskMetadata,
    SchemaDefinition,
    TaskSpecification,
    SelectionCriteria,
    CFPContext,
    AgentIdentity,
    CallForProposals,
    CostEstimate,
    ProposalCondition,
    ExecutionStep,
    ExecutionPlan,
    AgentCapability,
    ContractProposal,
    BidRefusal,
    CriteriaScore,
    EvaluatedProposal,
    EvaluationSummary,
    BidEvaluation,
    SLATerms,
    AwardedTerms,
    AgentNotification,
    ContractAward,
    ExecutionCommitment,
    ContractConfirmation,
    ExecutionIssue,
    TaskProgressReport,
    QualityMetrics,
    TaskExecutionResult,
    ContractNetSession,
    BidDecision,
    # Protocol class
    ContractNetProtocol,
)


# ============================================
# Test Fixtures
# ============================================


@pytest.fixture
def manager_agent():
    """Create a manager agent identity."""
    return AgentIdentity(
        agent_id="urn:agent:acme:task-manager:1.0.0",
        name="Task Manager",
        version="1.0.0",
        description="Manages task allocation",
        provider="acme",
    )


@pytest.fixture
def contractor_agent():
    """Create a contractor agent identity."""
    return AgentIdentity(
        agent_id="urn:agent:acme:worker:1.0.0",
        name="Worker Agent",
        version="1.0.0",
        description="Performs data processing tasks",
        provider="acme",
    )


@pytest.fixture
def contractor_agent_2():
    """Create a second contractor agent identity."""
    return AgentIdentity(
        agent_id="urn:agent:acme:worker:2.0.0",
        name="Worker Agent 2",
        version="2.0.0",
        description="Performs data processing tasks with improved quality",
        provider="acme",
    )


@pytest.fixture
def input_schema():
    """Create an input schema."""
    return SchemaDefinition(
        schema_type="object",
        description="Input data for processing",
        properties={"data": {"type": "array"}},
        required=["data"],
    )


@pytest.fixture
def output_schema():
    """Create an output schema."""
    return SchemaDefinition(
        schema_type="object",
        description="Processed output",
        properties={"result": {"type": "object"}},
    )


@pytest.fixture
def task_specification(input_schema, output_schema):
    """Create a task specification."""
    return TaskSpecification(
        task_id="task-001",
        task_type="data_processing",
        description="Process customer data and generate report",
        required_capabilities=["data-transform", "report-gen"],
        input_schema=input_schema,
        expected_output_schema=output_schema,
        constraints=[
            TaskConstraint(
                constraint_id="max-latency",
                constraint_type=TaskConstraintType.MAX_LATENCY,
                description="Maximum processing time",
                value="5000",
                required=True,
            )
        ],
        priority=TaskPriority.HIGH,
    )


@pytest.fixture
def selection_criteria():
    """Create selection criteria."""
    return [
        SelectionCriteria(
            criteria_id="cost",
            name="Cost",
            description="Total cost of execution",
            weight=0.3,
            evaluation_type=EvaluationType.MINIMIZE,
            max_acceptable="1.0",
        ),
        SelectionCriteria(
            criteria_id="latency",
            name="Latency",
            description="Execution time",
            weight=0.3,
            evaluation_type=EvaluationType.MINIMIZE,
            max_acceptable="5000",
        ),
        SelectionCriteria(
            criteria_id="quality",
            name="Quality",
            description="Quality of output",
            weight=0.4,
            evaluation_type=EvaluationType.MAXIMIZE,
            min_acceptable="0.7",
        ),
    ]


@pytest.fixture
def capabilities():
    """Create agent capabilities."""
    return [
        AgentCapability(
            capability_id="data-transform",
            name="Data Transformation",
            description="Transform data between formats",
            capability_type="transform",
        ),
        AgentCapability(
            capability_id="report-gen",
            name="Report Generation",
            description="Generate reports from data",
            capability_type="action",
        ),
    ]


@pytest.fixture
def protocol():
    """Create a ContractNetProtocol instance."""
    return ContractNetProtocol()


# ============================================
# Enum Tests
# ============================================


class TestEnums:
    """Test enum values and behavior."""

    def test_task_priority_values(self):
        """Test TaskPriority enum values."""
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.NORMAL.value == "normal"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.CRITICAL.value == "critical"

    def test_task_constraint_type_values(self):
        """Test TaskConstraintType enum values."""
        assert TaskConstraintType.MAX_LATENCY.value == "max_latency"
        assert TaskConstraintType.MIN_QUALITY.value == "min_quality"
        assert TaskConstraintType.MAX_COST.value == "max_cost"

    def test_cfp_urgency_values(self):
        """Test CFPUrgency enum values."""
        assert CFPUrgency.RELAXED.value == "relaxed"
        assert CFPUrgency.NORMAL.value == "normal"
        assert CFPUrgency.URGENT.value == "urgent"
        assert CFPUrgency.IMMEDIATE.value == "immediate"

    def test_evaluation_type_values(self):
        """Test EvaluationType enum values."""
        assert EvaluationType.MINIMIZE.value == "minimize"
        assert EvaluationType.MAXIMIZE.value == "maximize"
        assert EvaluationType.TARGET.value == "target"

    def test_commitment_level_values(self):
        """Test CommitmentLevel enum values."""
        assert CommitmentLevel.TENTATIVE.value == "tentative"
        assert CommitmentLevel.CONDITIONAL.value == "conditional"
        assert CommitmentLevel.FIRM.value == "firm"
        assert CommitmentLevel.GUARANTEED.value == "guaranteed"

    def test_refusal_reason_values(self):
        """Test RefusalReason enum values."""
        assert RefusalReason.LACK_CAPABILITY.value == "lack_capability"
        assert RefusalReason.CAPACITY_EXCEEDED.value == "capacity_exceeded"

    def test_contract_net_status_values(self):
        """Test ContractNetStatus enum values."""
        assert ContractNetStatus.CFP_ISSUED.value == "cfp_issued"
        assert ContractNetStatus.COLLECTING_PROPOSALS.value == "collecting_proposals"
        assert ContractNetStatus.COMPLETED.value == "completed"


# ============================================
# Issue CFP Tests
# ============================================


class TestIssueCFP:
    """Test CFP issuance."""

    def test_issue_cfp_basic(
        self, protocol, manager_agent, task_specification, selection_criteria
    ):
        """Test basic CFP issuance."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        assert session.session_id.startswith("cns-")
        assert session.cfp.cfp_id.startswith("cfp-")
        assert session.cfp.issuer == manager_agent
        assert session.cfp.task_specification == task_specification
        assert session.status == ContractNetStatus.CFP_ISSUED
        assert len(session.proposals) == 0
        assert len(session.refusals) == 0

    def test_issue_cfp_with_target_agents(
        self, protocol, manager_agent, task_specification, selection_criteria
    ):
        """Test CFP with specific target agents."""
        target_agents = ["agent-1", "agent-2"]

        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
            target_agents=target_agents,
        )

        assert session.cfp.target_agents == target_agents

    def test_issue_cfp_with_proposal_limits(
        self, protocol, manager_agent, task_specification, selection_criteria
    ):
        """Test CFP with min/max proposal limits."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
            min_proposals=2,
            max_proposals=5,
        )

        assert session.cfp.min_proposals == 2
        assert session.cfp.max_proposals == 5

    def test_issue_cfp_with_context(
        self, protocol, manager_agent, task_specification, selection_criteria
    ):
        """Test CFP with context."""
        context = CFPContext(
            purpose="Urgent data processing",
            urgency=CFPUrgency.URGENT,
            budget_hint=100.0,
            notes="Quality is paramount",
        )

        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
            context=context,
        )

        assert session.cfp.cfp_context == context
        assert session.cfp.cfp_context.urgency == CFPUrgency.URGENT


# ============================================
# Submit Proposal Tests
# ============================================


class TestSubmitProposal:
    """Test proposal submission."""

    def test_submit_proposal_basic(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test basic proposal submission."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.5),
            estimated_latency_ms=2000,
            quality_score=0.9,
        )

        assert proposal.proposal_id.startswith("prop-")
        assert proposal.cfp_id == session.cfp.cfp_id
        assert proposal.proposer == contractor_agent
        assert len(proposal.offered_capabilities) == 2
        assert proposal.cost.per_invocation == 0.5
        assert proposal.estimated_latency_ms == 2000
        assert proposal.quality_score == 0.9

    def test_submit_proposal_with_execution_plan(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test proposal with execution plan."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        execution_plan = ExecutionPlan(
            steps=[
                ExecutionStep(
                    step_number=1,
                    description="Load data",
                    capability_id="data-transform",
                    estimated_duration_ms=500,
                ),
                ExecutionStep(
                    step_number=2,
                    description="Transform data",
                    capability_id="data-transform",
                    estimated_duration_ms=1000,
                    dependencies=[1],
                ),
                ExecutionStep(
                    step_number=3,
                    description="Generate report",
                    capability_id="report-gen",
                    estimated_duration_ms=500,
                    dependencies=[2],
                ),
            ],
            total_estimated_duration_ms=2000,
            parallelizable=False,
            checkpoints=["data_loaded", "data_transformed", "report_complete"],
        )

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            execution_plan=execution_plan,
        )

        assert proposal.execution_plan is not None
        assert len(proposal.execution_plan.steps) == 3
        assert proposal.execution_plan.total_estimated_duration_ms == 2000

    def test_submit_proposal_with_conditions(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test proposal with conditions."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        conditions = [
            ProposalCondition(
                condition_id="cond-1",
                condition_type=ConditionType.RESOURCE_AVAILABILITY,
                description="GPU must be available",
                value="gpu_available",
                negotiable=False,
            ),
        ]

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            commitment_level=CommitmentLevel.CONDITIONAL,
            conditions=conditions,
        )

        assert proposal.commitment_level == CommitmentLevel.CONDITIONAL
        assert len(proposal.conditions) == 1

    def test_submit_proposal_after_deadline_fails(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test that proposal submission after deadline fails."""
        # Create CFP with 0 second deadline (already passed)
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=0,
        )

        # Wait a moment to ensure deadline passes
        import time
        time.sleep(0.1)

        with pytest.raises(ValueError, match="deadline has passed"):
            protocol.submit_proposal(
                session_id=session.session_id,
                proposer=contractor_agent,
                offered_capabilities=capabilities,
                validity_seconds=3600,
            )

    def test_submit_proposal_max_reached_fails(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        contractor_agent_2,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test that exceeding max proposals fails."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
            max_proposals=1,
        )

        # First proposal succeeds
        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        # Second proposal fails
        with pytest.raises(ValueError, match="Maximum number of proposals"):
            protocol.submit_proposal(
                session_id=session.session_id,
                proposer=contractor_agent_2,
                offered_capabilities=capabilities,
                validity_seconds=3600,
            )


# ============================================
# Submit Refusal Tests
# ============================================


class TestSubmitRefusal:
    """Test bid refusal submission."""

    def test_submit_refusal_basic(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
    ):
        """Test basic refusal submission."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        refusal = protocol.submit_refusal(
            session_id=session.session_id,
            refusing_agent=contractor_agent,
            reason=RefusalReason.CAPACITY_EXCEEDED,
            explanation="Currently processing other high-priority tasks",
        )

        assert refusal.refusal_id.startswith("ref-")
        assert refusal.cfp_id == session.cfp.cfp_id
        assert refusal.reason == RefusalReason.CAPACITY_EXCEEDED
        assert len(session.refusals) == 1

    def test_submit_refusal_with_alternative(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
    ):
        """Test refusal with alternative suggestion."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        refusal = protocol.submit_refusal(
            session_id=session.session_id,
            refusing_agent=contractor_agent,
            reason=RefusalReason.LACK_CAPABILITY,
            explanation="Missing required capability",
            alternative_suggestion="Consider agent-xyz for this task",
            available_after="2024-01-15T10:00:00Z",
        )

        assert refusal.alternative_suggestion is not None
        assert refusal.available_after is not None


# ============================================
# Bid Evaluation Tests
# ============================================


class TestBidEvaluation:
    """Test bid evaluation."""

    def test_evaluate_bids_basic(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        contractor_agent_2,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test basic bid evaluation."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        # Submit proposals
        protocol.start_collecting_proposals(session.session_id)

        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.5),
            estimated_latency_ms=2000,
            quality_score=0.85,
        )

        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent_2,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.3),
            estimated_latency_ms=3000,
            quality_score=0.9,
        )

        # Evaluate
        evaluation = protocol.evaluate_bids(session.session_id)

        assert evaluation.evaluation_id.startswith("eval-")
        assert len(evaluation.evaluated_proposals) == 2
        assert evaluation.recommended_winner is not None
        assert evaluation.evaluation_summary.total_proposals == 2
        assert evaluation.evaluation_summary.qualified_proposals >= 0

    def test_evaluate_bids_ranking(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        contractor_agent_2,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test that proposals are correctly ranked."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        # Submit a clearly better proposal
        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.1),
            estimated_latency_ms=1000,
            quality_score=0.95,
        )

        # Submit a worse proposal
        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent_2,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.9),
            estimated_latency_ms=4500,
            quality_score=0.5,
        )

        evaluation = protocol.evaluate_bids(session.session_id)

        # Find proposals by proposer
        first_eval = next(
            ep for ep in evaluation.evaluated_proposals
            if ep.proposer_id == contractor_agent.agent_id
        )
        second_eval = next(
            ep for ep in evaluation.evaluated_proposals
            if ep.proposer_id == contractor_agent_2.agent_id
        )

        # Better proposal should have higher score and rank 1
        assert first_eval.overall_score > second_eval.overall_score
        assert first_eval.rank < second_eval.rank

    def test_evaluate_bids_disqualification(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test proposal disqualification."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        # Submit tentative proposal (should be disqualified)
        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            commitment_level=CommitmentLevel.TENTATIVE,
        )

        evaluation = protocol.evaluate_bids(session.session_id)

        assert evaluation.evaluated_proposals[0].disqualified is True
        assert "tentative" in evaluation.evaluated_proposals[0].disqualification_reason.lower()

    def test_evaluate_bids_min_proposals_not_met(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test evaluation fails when min proposals not met."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
            min_proposals=3,
        )

        protocol.start_collecting_proposals(session.session_id)

        # Only submit 1 proposal
        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        with pytest.raises(ValueError, match="Minimum proposals"):
            protocol.evaluate_bids(session.session_id)


# ============================================
# Contract Award Tests
# ============================================


class TestContractAward:
    """Test contract award."""

    def test_award_contract_basic(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test basic contract award."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.5),
        )

        protocol.evaluate_bids(session.session_id)

        award = protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal.proposal_id,
            contract_duration_hours=24,
        )

        assert award.award_id.startswith("award-")
        assert award.winning_proposal_id == proposal.proposal_id
        assert award.awarded_to == contractor_agent
        assert session.status == ContractNetStatus.AWAITING_CONFIRMATION

    def test_award_contract_with_sla(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test contract award with SLA terms."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        protocol.evaluate_bids(session.session_id)

        sla_terms = SLATerms(
            max_latency_ms=5000,
            availability_target=0.99,
            quality_threshold=0.8,
            penalty_clause="10% refund per SLA breach",
        )

        award = protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal.proposal_id,
            sla_terms=sla_terms,
        )

        assert award.contract_terms.agreed_sla is not None
        assert award.contract_terms.agreed_sla.max_latency_ms == 5000

    def test_award_contract_rejection_notifications(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        contractor_agent_2,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test rejection notifications to non-winners."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        proposal1 = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            quality_score=0.9,
        )

        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent_2,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            quality_score=0.7,
        )

        protocol.evaluate_bids(session.session_id)

        award = protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal1.proposal_id,
        )

        assert len(award.rejection_notifications) == 1
        assert award.rejection_notifications[0].agent_id == contractor_agent_2.agent_id
        assert award.rejection_notifications[0].notification_type == NotificationType.AWARD_DECLINED


# ============================================
# Contract Confirmation Tests
# ============================================


class TestContractConfirmation:
    """Test contract confirmation."""

    def test_confirm_award_accept(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test accepting a contract award."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        protocol.evaluate_bids(session.session_id)
        protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal.proposal_id,
        )

        confirmation = protocol.confirm_award(
            session_id=session.session_id,
            confirmed=True,
            confirming_agent=contractor_agent,
            start_time=datetime.utcnow().isoformat() + "Z",
            estimated_completion=(
                datetime.utcnow() + timedelta(hours=1)
            ).isoformat() + "Z",
            contact_endpoint="https://worker.example.com/api",
        )

        assert confirmation.confirmed is True
        assert confirmation.execution_commitment is not None
        assert session.status == ContractNetStatus.CONTRACT_ACTIVE

    def test_confirm_award_reject(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test rejecting a contract award."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        protocol.evaluate_bids(session.session_id)
        protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal.proposal_id,
        )

        confirmation = protocol.confirm_award(
            session_id=session.session_id,
            confirmed=False,
            confirming_agent=contractor_agent,
            rejection_reason="Resource constraints changed",
        )

        assert confirmation.confirmed is False
        assert confirmation.rejection_reason is not None
        assert session.status == ContractNetStatus.FAILED


# ============================================
# Task Execution Tests
# ============================================


class TestTaskExecution:
    """Test task execution flow."""

    def _setup_active_contract(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Helper to set up an active contract."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        protocol.evaluate_bids(session.session_id)
        protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal.proposal_id,
        )

        protocol.confirm_award(
            session_id=session.session_id,
            confirmed=True,
            confirming_agent=contractor_agent,
            start_time=datetime.utcnow().isoformat() + "Z",
            estimated_completion=(
                datetime.utcnow() + timedelta(hours=1)
            ).isoformat() + "Z",
        )

        return session

    def test_report_progress(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test progress reporting."""
        session = self._setup_active_contract(
            protocol,
            manager_agent,
            contractor_agent,
            task_specification,
            selection_criteria,
            capabilities,
        )

        report = protocol.report_progress(
            session_id=session.session_id,
            progress_percentage=50.0,
            current_step=2,
            status=ExecutionStatus.IN_PROGRESS,
        )

        assert report.report_id.startswith("prog-")
        assert report.progress_percentage == 50.0
        assert report.current_step == 2
        assert len(session.progress_reports) == 1

    def test_report_progress_with_issues(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test progress reporting with issues."""
        session = self._setup_active_contract(
            protocol,
            manager_agent,
            contractor_agent,
            task_specification,
            selection_criteria,
            capabilities,
        )

        issues = [
            ExecutionIssue(
                issue_id="issue-1",
                severity=IssueSeverity.WARNING,
                description="Minor data format issue",
                impact="May cause slight delay",
                resolution="Auto-corrected",
            ),
        ]

        report = protocol.report_progress(
            session_id=session.session_id,
            progress_percentage=30.0,
            current_step=1,
            status=ExecutionStatus.IN_PROGRESS,
            issues=issues,
            estimated_remaining_ms=3000,
        )

        assert len(report.issues) == 1
        assert report.estimated_remaining_ms == 3000

    def test_complete_task_success(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test successful task completion."""
        session = self._setup_active_contract(
            protocol,
            manager_agent,
            contractor_agent,
            task_specification,
            selection_criteria,
            capabilities,
        )

        result = protocol.complete_task(
            session_id=session.session_id,
            status=ExecutionStatus.COMPLETED,
            output='{"result": "processed data"}',
            actual_latency_ms=1500,
            summary="Task completed successfully",
            quality_metrics=QualityMetrics(
                accuracy=0.95,
                completeness=1.0,
                consistency=0.98,
            ),
        )

        assert result.result_id.startswith("res-")
        assert result.status == ExecutionStatus.COMPLETED
        assert session.status == ContractNetStatus.COMPLETED

    def test_complete_task_failure(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test task failure."""
        session = self._setup_active_contract(
            protocol,
            manager_agent,
            contractor_agent,
            task_specification,
            selection_criteria,
            capabilities,
        )

        result = protocol.complete_task(
            session_id=session.session_id,
            status=ExecutionStatus.FAILED,
            summary="Task failed due to data corruption",
        )

        assert result.status == ExecutionStatus.FAILED
        assert session.status == ContractNetStatus.FAILED


# ============================================
# State Transition Tests
# ============================================


class TestStateTransitions:
    """Test state transition validation."""

    def test_valid_transitions(
        self,
        protocol,
        manager_agent,
        task_specification,
        selection_criteria,
    ):
        """Test valid state transitions."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        assert session.status == ContractNetStatus.CFP_ISSUED

        # Transition to collecting
        protocol.start_collecting_proposals(session.session_id)
        assert session.status == ContractNetStatus.COLLECTING_PROPOSALS

    def test_invalid_transition_fails(
        self,
        protocol,
        manager_agent,
        task_specification,
        selection_criteria,
    ):
        """Test that invalid transitions fail."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        # Cannot go directly to COMPLETED
        with pytest.raises(ValueError, match="Cannot transition"):
            protocol._transition_status(
                session.session_id, ContractNetStatus.COMPLETED
            )

    def test_cancel_session(
        self,
        protocol,
        manager_agent,
        task_specification,
        selection_criteria,
    ):
        """Test session cancellation."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.cancel_session(session.session_id)
        assert session.status == ContractNetStatus.CANCELLED

    def test_cannot_cancel_completed_session(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test that completed sessions cannot be cancelled."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        protocol.evaluate_bids(session.session_id)
        protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal.proposal_id,
        )

        protocol.confirm_award(
            session_id=session.session_id,
            confirmed=True,
            confirming_agent=contractor_agent,
            start_time=datetime.utcnow().isoformat() + "Z",
            estimated_completion=(
                datetime.utcnow() + timedelta(hours=1)
            ).isoformat() + "Z",
        )

        protocol.complete_task(
            session_id=session.session_id,
            status=ExecutionStatus.COMPLETED,
            summary="Done",
        )

        with pytest.raises(ValueError, match="terminal state"):
            protocol.cancel_session(session.session_id)


# ============================================
# Bid Decision Tests
# ============================================


class TestBidDecision:
    """Test bid decision logic."""

    def test_decide_to_bid_sufficient_capabilities(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test bid decision with sufficient capabilities."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        decision = protocol.decide_to_bid(
            cfp=session.cfp,
            agent_identity=contractor_agent,
            available_capabilities=capabilities,
            current_workload=0.3,
        )

        assert decision.should_bid is True
        assert decision.capability_coverage == 1.0
        assert decision.confidence > 0.5

    def test_decide_to_bid_insufficient_capabilities(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
    ):
        """Test bid decision with insufficient capabilities."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        # Provide no matching capabilities
        no_caps: list = []

        decision = protocol.decide_to_bid(
            cfp=session.cfp,
            agent_identity=contractor_agent,
            available_capabilities=no_caps,
            current_workload=0.3,
        )

        assert decision.should_bid is False
        assert decision.capability_coverage == 0.0
        assert decision.refusal_reason == RefusalReason.LACK_CAPABILITY

    def test_decide_to_bid_high_workload(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test bid decision with high workload."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        decision = protocol.decide_to_bid(
            cfp=session.cfp,
            agent_identity=contractor_agent,
            available_capabilities=capabilities,
            current_workload=0.95,
        )

        assert decision.should_bid is False
        assert decision.refusal_reason == RefusalReason.CAPACITY_EXCEEDED


# ============================================
# Integration Tests
# ============================================


class TestIntegration:
    """Integration tests for complete flows."""

    def test_complete_contract_net_flow(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        contractor_agent_2,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test complete Contract-Net flow from CFP to completion."""
        # 1. Issue CFP
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )
        assert session.status == ContractNetStatus.CFP_ISSUED

        # 2. Start collecting proposals
        protocol.start_collecting_proposals(session.session_id)
        assert session.status == ContractNetStatus.COLLECTING_PROPOSALS

        # 3. Submit proposals
        proposal1 = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.5),
            quality_score=0.9,
        )

        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent_2,
            offered_capabilities=capabilities,
            validity_seconds=3600,
            cost=CostEstimate(currency="USD", per_invocation=0.8),
            quality_score=0.7,
        )

        assert len(session.proposals) == 2

        # 4. Evaluate bids
        evaluation = protocol.evaluate_bids(session.session_id)
        assert session.status == ContractNetStatus.EVALUATING_BIDS
        assert evaluation.recommended_winner is not None

        # 5. Award contract
        award = protocol.award_contract(
            session_id=session.session_id,
            winning_proposal_id=proposal1.proposal_id,
        )
        assert session.status == ContractNetStatus.AWAITING_CONFIRMATION
        assert award.awarded_to == contractor_agent

        # 6. Confirm award
        protocol.confirm_award(
            session_id=session.session_id,
            confirmed=True,
            confirming_agent=contractor_agent,
            start_time=datetime.utcnow().isoformat() + "Z",
            estimated_completion=(
                datetime.utcnow() + timedelta(hours=1)
            ).isoformat() + "Z",
        )
        assert session.status == ContractNetStatus.CONTRACT_ACTIVE

        # 7. Report progress
        protocol.report_progress(
            session_id=session.session_id,
            progress_percentage=50.0,
            current_step=2,
        )
        assert len(session.progress_reports) == 1

        # 8. Complete task
        result = protocol.complete_task(
            session_id=session.session_id,
            status=ExecutionStatus.COMPLETED,
            output='{"processed": true}',
            actual_latency_ms=1500,
            summary="Successfully completed",
        )
        assert session.status == ContractNetStatus.COMPLETED
        assert result.status == ExecutionStatus.COMPLETED

    def test_flow_with_refusals(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        contractor_agent_2,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test flow where some agents refuse to bid."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        # One agent refuses
        protocol.submit_refusal(
            session_id=session.session_id,
            refusing_agent=contractor_agent,
            reason=RefusalReason.CAPACITY_EXCEEDED,
            explanation="Too busy",
        )

        # Another submits proposal
        proposal = protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent_2,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        assert len(session.refusals) == 1
        assert len(session.proposals) == 1

        # Evaluation includes refusal count
        evaluation = protocol.evaluate_bids(session.session_id)
        assert evaluation.evaluation_summary.refusals_received == 1


# ============================================
# Edge Cases Tests
# ============================================


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_session_not_found(self, protocol):
        """Test handling of non-existent session."""
        with pytest.raises(ValueError, match="not found"):
            protocol.get_session("non-existent-session")

    def test_proposal_not_found_for_award(
        self,
        protocol,
        manager_agent,
        contractor_agent,
        task_specification,
        selection_criteria,
        capabilities,
    ):
        """Test handling of non-existent proposal for award."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        protocol.start_collecting_proposals(session.session_id)

        protocol.submit_proposal(
            session_id=session.session_id,
            proposer=contractor_agent,
            offered_capabilities=capabilities,
            validity_seconds=3600,
        )

        protocol.evaluate_bids(session.session_id)

        with pytest.raises(ValueError, match="not found"):
            protocol.award_contract(
                session_id=session.session_id,
                winning_proposal_id="non-existent-proposal",
            )

    def test_progress_report_on_non_active_session(
        self,
        protocol,
        manager_agent,
        task_specification,
        selection_criteria,
    ):
        """Test progress reporting on non-active session."""
        session = protocol.issue_cfp(
            issuer=manager_agent,
            task_specification=task_specification,
            selection_criteria=selection_criteria,
            deadline_seconds=3600,
        )

        with pytest.raises(ValueError, match="not active"):
            protocol.report_progress(
                session_id=session.session_id,
                progress_percentage=50.0,
                current_step=1,
            )
