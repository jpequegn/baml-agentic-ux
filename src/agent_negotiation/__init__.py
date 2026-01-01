"""
Agent Negotiation Module

Agent-to-Agent interface negotiation components for Phase 3.
"""

from .agent_card import (
    # Protocol types
    ProtocolType,
    SupportedProtocol,
    # Endpoint types
    EndpointType,
    AuthMethod,
    AuthConfig,
    CardEndpoint,
    RetryPolicy,
    # Compliance types
    ComplianceStandard,
    ComplianceTag,
    DataHandlingPolicy,
    # Agent Card
    AgentCard,
    AgentCardSummary,
    # Discovery types
    WellKnownAgentDescriptions,
    AgentCardRequest,
    AgentCardResponse,
    AgentCardError,
    # Protocol negotiation
    ProtocolNegotiationRequest,
    ProtocolNegotiationResult,
    # Validation
    CardValidationResult,
    CardValidationError,
    CardValidationWarning,
    # Utilities
    AgentCardBuilder,
    AgentCardValidator,
    AgentCardSerializer,
)

from .capability_registry import (
    # Constraint types
    ConstraintType,
    ConstraintOperator,
    DiscoveryConstraint,
    # Discovery types
    DiscoverySource,
    DiscoveryRequest,
    AgentMatch,
    DiscoveryResponse,
    # Registry operations
    RegistrationRequest,
    RegistrationError,
    RegistrationResponse,
    DeregistrationRequest,
    DeregistrationResponse,
    # Registry status
    RegistryStatus,
    CapabilityStats,
    CapabilityIndex,
    # Registry class
    CapabilityRegistry,
)

from .capability_matcher import (
    # Transformation types
    TransformationDirection,
    TransformationType,
    TransformationComplexity,
    SchemaTransformation,
    PropertyMatch,
    SchemaCompatibility,
    # Constraint satisfaction
    ConstraintSatisfaction,
    # Adaptation suggestions
    SuggestionType,
    SuggestionPriority,
    EffortLevel,
    AdaptationSuggestion,
    # Capability matching
    CapabilityDetailedMatch,
    CapabilityMatchResult,
    MatchOptions,
    BestMatch,
    CapabilityMatchResponse,
    # Matcher class
    CapabilityMatcher,
)

from .negotiation_state import (
    # Enums
    NegotiationStatus,
    NegotiationAction,
    NegotiationOutcome,
    UrgencyLevel,
    RiskLevel,
    StrategyApproach,
    ConstraintType,
    ConstraintOperator,
    TERMINAL_STATES,
    # Proposal types
    NegotiationParameter,
    SLARequirement,
    NegotiationTerms,
    ProposalConstraint,
    CapabilityNegotiationItem,
    NegotiationProposal,
    # Turn types
    TurnMetadata,
    NegotiationTurn,
    # Result types
    NegotiationResult,
    NegotiationContext,
    # Identity (local copy)
    AgentIdentity,
    # Transition types
    StateTransitionError,
    StateTransitionResult,
    # Risk types
    RiskFactor,
    RiskAssessment,
    # Strategy types
    NegotiationStrategy,
    # State change callback type
    StateChangeCallback,
    # Session class
    NegotiationSession,
    # State machine class
    NegotiationStateMachine,
)

from .proposal_evaluator import (
    # Enums (NegotiationAction and RiskLevel are imported from negotiation_state)
    CapabilityLevel,
    NegotiationStrategyType,
    CapabilityGapType,
    TermGapType,
    ChangeType,
    # Capability types
    RequestedParameter,
    CapabilityRequest,
    OfferedParameter,
    CapabilityOffer,
    # Policy types
    MinimumTerms,
    ScoringWeights,
    CapabilityPriority,
    RiskFactorWeights,
    RiskTolerance,
    EvaluationPolicy,
    # Gap analysis types
    CapabilityGap,
    TermGap,
    ConstraintViolation,
    GapAnalysis,
    # Scoring types
    TermScore,
    ValueScore,
    BurdenScore,
    RiskScore,
    ScoreBreakdown,
    ProposalScore,
    # Result types
    EvaluationDecision,
    EvaluationRationale,
    ProposalChange,
    CounterProposalResult,
    ProposalEvaluationResult,
    # Evaluator class
    ProposalEvaluator,
)

from .contract_net import (
    # Task enums
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
    # Task specification types
    TaskConstraint,
    TaskMetadata,
    SchemaDefinition,
    TaskSpecification,
    # CFP types
    SelectionCriteria,
    CFPContext,
    CallForProposals,
    # Proposal types
    CostEstimate,
    ProposalCondition,
    ExecutionStep,
    ExecutionPlan,
    AgentCapability,
    ContractProposal,
    # Refusal types
    BidRefusal,
    # Evaluation types
    CriteriaScore,
    EvaluatedProposal,
    EvaluationSummary,
    BidEvaluation,
    # Award types
    SLATerms,
    AwardedTerms,
    AgentNotification,
    ContractAward,
    # Confirmation types
    ExecutionCommitment,
    ContractConfirmation,
    # Execution types
    ExecutionIssue,
    TaskProgressReport,
    QualityMetrics,
    TaskExecutionResult,
    # Session types
    ContractNetSession,
    BidDecision,
    # Protocol class
    ContractNetProtocol,
)

from .conflict_detector import (
    # Conflict type enums
    ConflictType,
    ConflictSeverity,
    ConflictCategory,
    ResolutionStrategy,
    EffortLevel as ConflictEffortLevel,  # Alias to avoid conflict with capability_matcher.EffortLevel
    # Conflict description types
    ConflictContext,
    Conflict,
    # Resolution types
    ResolutionRisk,
    EffortEstimate,
    ResolutionStep,
    ResolutionPath,
    # Conflict analysis types
    ConflictSeverityCount,
    ConflictCategoryCount,
    ConflictTypeCount,
    ConflictSummary,
    ConflictAnalysis,
    # Detection request/response types
    ConstraintSpec,
    DetectionOptions,
    SchemaDefinition as ConflictSchemaDefinition,  # Alias to avoid conflict with contract_net.SchemaDefinition
    ConflictDetectionRequest,
    ConflictDetectionResponse,
    # Callback type
    ConflictCallback,
    # Detector class
    ConflictDetector,
)

from .schema_transformer import (
    # Transformation type enums
    FieldTransformType,
    DataLossRisk,
    TransformValidation,
    ConditionOperator as TransformConditionOperator,
    TransformComplexity,
    # Value mapping types
    MappingEntry,
    ValueMapping,
    FormatSpec,
    TransformCondition,
    # Field transformation
    FieldTransformation,
    # Schema types
    FieldSpec,
    SchemaSpec,
    # Validation types
    ValidationIssue,
    CoverageAnalysis,
    PlanValidation,
    PlanMetadata,
    # Transform plan
    SchemaTransformPlan,
    # Result types
    LostField,
    TruncatedField,
    PrecisionLossField,
    DataLossReport,
    FieldTransformResult,
    TransformResult,
    # Request/response types
    PlanGenerationOptions,
    ExecutionOptions,
    # Transformer class
    SchemaTransformer,
)

from .conflict_mediator import (
    # Mediation style enums
    MediationStyle,
    MediationResolutionStrategy,
    MediationOutcome,
    ConflictPriority,
    # Party position types
    TermSummary,
    NegotiationProposalSummary,
    PositionConstraint,
    TradeOffPair,
    FlexibilityAssessment,
    PartyPosition,
    # Mediation request types
    ConflictHistoryEntry,
    ConflictSummaryForMediation,
    MediationOptions,
    MediationContext,
    MediationRequest,
    # Mediation result types
    Concession,
    CompromiseTerm,
    CompromiseProposal,
    MediationMetrics,
    MediationResult,
    # Deadlock resolution types
    TurnSummary,
    DeadlockResolutionRequest,
    AlternativeStrategy,
    DeadlockResolution,
    # Escalation types
    EscalationRequest,
    EscalationResponse,
    # Common ground analysis types
    AgreedTerm,
    CloseTerm,
    NegotiableTerm,
    IncompatibleTerm,
    CommonGroundAnalysis,
    # Creative solution types
    CreativeSolution,
    # Callback types
    MediationCallback,
    EscalationCallback,
    # Mediator class
    ConflictMediator,
)

from .composition_planner import (
    # Input source enums
    InputSource,
    OptimizationGoal,
    PlanStatus,
    DependencyType,
    FailureSeverity,
    StepExecutionType,
    # Input binding types
    InputBinding,
    CompositionConstraint,
    # Composition step types
    StepRetryPolicy,
    StepCondition,
    CompositionStep,
    # Data flow types
    DataFlowEdge,
    StepDependency,
    # Failure mode types
    FailureMode,
    RiskAssessment as CompositionRiskAssessment,  # Alias to avoid conflict
    # Plan types
    PlanMetadata as CompositionPlanMetadata,  # Alias to avoid conflict
    CompositionPlan,
    # Available agent types
    AvailableCapability,
    AvailableAgent,
    # Planning request/response types
    PlanningPreferences,
    PlanningContext,
    PlanCompositionRequest,
    PlanCompositionResponse,
    # Optimization types
    OptimizationMetrics,
    PlanImprovement as CompositionPlanImprovement,  # Alias to avoid conflict
    OptimizePlanResponse,
    # Validation types
    ValidationError as CompositionValidationError,  # Alias to avoid conflict
    ValidationWarning as CompositionValidationWarning,  # Alias to avoid conflict
    PlanValidationResult,
    # Planner class
    CompositionPlanner,
)

__all__ = [
    # Protocol types
    "ProtocolType",
    "SupportedProtocol",
    # Endpoint types
    "EndpointType",
    "AuthMethod",
    "AuthConfig",
    "CardEndpoint",
    "RetryPolicy",
    # Compliance types
    "ComplianceStandard",
    "ComplianceTag",
    "DataHandlingPolicy",
    # Agent Card
    "AgentCard",
    "AgentCardSummary",
    # Discovery types (agent_card)
    "WellKnownAgentDescriptions",
    "AgentCardRequest",
    "AgentCardResponse",
    "AgentCardError",
    # Protocol negotiation
    "ProtocolNegotiationRequest",
    "ProtocolNegotiationResult",
    # Validation
    "CardValidationResult",
    "CardValidationError",
    "CardValidationWarning",
    # Utilities
    "AgentCardBuilder",
    "AgentCardValidator",
    "AgentCardSerializer",
    # Constraint types
    "ConstraintType",
    "ConstraintOperator",
    "DiscoveryConstraint",
    # Discovery types (capability_registry)
    "DiscoverySource",
    "DiscoveryRequest",
    "AgentMatch",
    "DiscoveryResponse",
    # Registry operations
    "RegistrationRequest",
    "RegistrationError",
    "RegistrationResponse",
    "DeregistrationRequest",
    "DeregistrationResponse",
    # Registry status
    "RegistryStatus",
    "CapabilityStats",
    "CapabilityIndex",
    # Registry class
    "CapabilityRegistry",
    # Transformation types
    "TransformationDirection",
    "TransformationType",
    "TransformationComplexity",
    "SchemaTransformation",
    "PropertyMatch",
    "SchemaCompatibility",
    # Constraint satisfaction
    "ConstraintSatisfaction",
    # Adaptation suggestions
    "SuggestionType",
    "SuggestionPriority",
    "EffortLevel",
    "AdaptationSuggestion",
    # Capability matching
    "CapabilityDetailedMatch",
    "CapabilityMatchResult",
    "MatchOptions",
    "BestMatch",
    "CapabilityMatchResponse",
    # Matcher class
    "CapabilityMatcher",
    # Negotiation status and action enums
    "NegotiationStatus",
    "NegotiationAction",
    "NegotiationOutcome",
    "UrgencyLevel",
    "RiskLevel",
    "StrategyApproach",
    "ConstraintType",
    "ConstraintOperator",
    "TERMINAL_STATES",
    # Proposal types
    "NegotiationParameter",
    "SLARequirement",
    "NegotiationTerms",
    "ProposalConstraint",
    "CapabilityNegotiationItem",
    "NegotiationProposal",
    # Turn types
    "TurnMetadata",
    "NegotiationTurn",
    # Result types
    "NegotiationResult",
    "NegotiationContext",
    "AgentIdentity",
    # Transition types
    "StateTransitionError",
    "StateTransitionResult",
    # Risk types
    "RiskFactor",
    "RiskAssessment",
    # Strategy types
    "NegotiationStrategy",
    # State change callback type
    "StateChangeCallback",
    # Session class
    "NegotiationSession",
    # State machine class
    "NegotiationStateMachine",
    # Proposal evaluation enums
    "CapabilityLevel",
    "NegotiationStrategyType",
    "CapabilityGapType",
    "TermGapType",
    "ChangeType",
    # Capability types
    "RequestedParameter",
    "CapabilityRequest",
    "OfferedParameter",
    "CapabilityOffer",
    # Policy types
    "MinimumTerms",
    "ScoringWeights",
    "CapabilityPriority",
    "RiskFactorWeights",
    "RiskTolerance",
    "EvaluationPolicy",
    # Gap analysis types
    "CapabilityGap",
    "TermGap",
    "ConstraintViolation",
    "GapAnalysis",
    # Scoring types
    "TermScore",
    "ValueScore",
    "BurdenScore",
    "RiskScore",
    "ScoreBreakdown",
    "ProposalScore",
    # Result types
    "EvaluationDecision",
    "EvaluationRationale",
    "ProposalChange",
    "CounterProposalResult",
    "ProposalEvaluationResult",
    # Evaluator class
    "ProposalEvaluator",
    # Contract-Net task enums
    "TaskPriority",
    "TaskConstraintType",
    "CFPUrgency",
    "EvaluationType",
    "CommitmentLevel",
    "ConditionType",
    "RefusalReason",
    "EvaluationRiskLevel",
    "NotificationType",
    "ExecutionStatus",
    "IssueSeverity",
    "ContractNetStatus",
    # Task specification types
    "TaskConstraint",
    "TaskMetadata",
    "SchemaDefinition",
    "TaskSpecification",
    # CFP types
    "SelectionCriteria",
    "CFPContext",
    "CallForProposals",
    # Contract proposal types
    "CostEstimate",
    "ProposalCondition",
    "ExecutionStep",
    "ExecutionPlan",
    "AgentCapability",
    "ContractProposal",
    # Refusal types
    "BidRefusal",
    # Evaluation types
    "CriteriaScore",
    "EvaluatedProposal",
    "EvaluationSummary",
    "BidEvaluation",
    # Award types
    "SLATerms",
    "AwardedTerms",
    "AgentNotification",
    "ContractAward",
    # Confirmation types
    "ExecutionCommitment",
    "ContractConfirmation",
    # Execution types
    "ExecutionIssue",
    "TaskProgressReport",
    "QualityMetrics",
    "TaskExecutionResult",
    # Session types
    "ContractNetSession",
    "BidDecision",
    # Protocol class
    "ContractNetProtocol",
    # Conflict detection enums
    "ConflictType",
    "ConflictSeverity",
    "ConflictCategory",
    "ResolutionStrategy",
    "ConflictEffortLevel",
    # Conflict description types
    "ConflictContext",
    "Conflict",
    # Resolution types
    "ResolutionRisk",
    "EffortEstimate",
    "ResolutionStep",
    "ResolutionPath",
    # Conflict analysis types
    "ConflictSeverityCount",
    "ConflictCategoryCount",
    "ConflictTypeCount",
    "ConflictSummary",
    "ConflictAnalysis",
    # Conflict detection request/response types
    "ConstraintSpec",
    "DetectionOptions",
    "ConflictSchemaDefinition",
    "ConflictDetectionRequest",
    "ConflictDetectionResponse",
    # Conflict callback type
    "ConflictCallback",
    # Conflict detector class
    "ConflictDetector",
    # Schema transformation enums
    "FieldTransformType",
    "DataLossRisk",
    "TransformValidation",
    "TransformConditionOperator",
    "TransformComplexity",
    # Value mapping types
    "MappingEntry",
    "ValueMapping",
    "FormatSpec",
    "TransformCondition",
    # Field transformation
    "FieldTransformation",
    # Schema types
    "FieldSpec",
    "SchemaSpec",
    # Validation types
    "ValidationIssue",
    "CoverageAnalysis",
    "PlanValidation",
    "PlanMetadata",
    # Transform plan
    "SchemaTransformPlan",
    # Transform result types
    "LostField",
    "TruncatedField",
    "PrecisionLossField",
    "DataLossReport",
    "FieldTransformResult",
    "TransformResult",
    # Transform request/response types
    "PlanGenerationOptions",
    "ExecutionOptions",
    # Transformer class
    "SchemaTransformer",
    # Mediation style enums
    "MediationStyle",
    "MediationResolutionStrategy",
    "MediationOutcome",
    "ConflictPriority",
    # Party position types
    "TermSummary",
    "NegotiationProposalSummary",
    "PositionConstraint",
    "TradeOffPair",
    "FlexibilityAssessment",
    "PartyPosition",
    # Mediation request types
    "ConflictHistoryEntry",
    "ConflictSummaryForMediation",
    "MediationOptions",
    "MediationContext",
    "MediationRequest",
    # Mediation result types
    "Concession",
    "CompromiseTerm",
    "CompromiseProposal",
    "MediationMetrics",
    "MediationResult",
    # Deadlock resolution types
    "TurnSummary",
    "DeadlockResolutionRequest",
    "AlternativeStrategy",
    "DeadlockResolution",
    # Escalation types
    "EscalationRequest",
    "EscalationResponse",
    # Common ground analysis types
    "AgreedTerm",
    "CloseTerm",
    "NegotiableTerm",
    "IncompatibleTerm",
    "CommonGroundAnalysis",
    # Creative solution types
    "CreativeSolution",
    # Callback types
    "MediationCallback",
    "EscalationCallback",
    # Mediator class
    "ConflictMediator",
    # Composition planning enums
    "InputSource",
    "OptimizationGoal",
    "PlanStatus",
    "DependencyType",
    "FailureSeverity",
    "StepExecutionType",
    # Input binding types
    "InputBinding",
    "CompositionConstraint",
    # Composition step types
    "StepRetryPolicy",
    "StepCondition",
    "CompositionStep",
    # Data flow types
    "DataFlowEdge",
    "StepDependency",
    # Failure mode types
    "FailureMode",
    "CompositionRiskAssessment",
    # Plan types
    "CompositionPlanMetadata",
    "CompositionPlan",
    # Available agent types
    "AvailableCapability",
    "AvailableAgent",
    # Planning request/response types
    "PlanningPreferences",
    "PlanningContext",
    "PlanCompositionRequest",
    "PlanCompositionResponse",
    # Optimization types
    "OptimizationMetrics",
    "CompositionPlanImprovement",
    "OptimizePlanResponse",
    # Validation types
    "CompositionValidationError",
    "CompositionValidationWarning",
    "PlanValidationResult",
    # Planner class
    "CompositionPlanner",
]
