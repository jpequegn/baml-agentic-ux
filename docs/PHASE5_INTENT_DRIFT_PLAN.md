# Phase 5: Intent Drift Detection - Implementation Plan

## Executive Summary

This plan implements intent drift detection for Language User Interfaces (LUI) - the ability to detect when user intent drifts beyond the capabilities of available LUI components and respond gracefully. Based on comprehensive research into semantic similarity measures, out-of-distribution detection, graceful degradation patterns, and conversational context tracking.

**Total Estimated Effort**: 42-52 hours
**Primary Goal**: Detect drift with >85% accuracy, zero hallucinated capabilities
**Key Innovation**: Multi-tier drift classification with graceful redirect responses

---

## Research Summary

### Semantic Drift Detection Methods

| Method | Use Case | Latency | Accuracy |
|--------|----------|---------|----------|
| **Cosine Similarity** | Fast initial screening | <5ms | ~75% |
| **BERTScore** | Semantic similarity | 20-50ms | ~85% |
| **Mahalanobis Distance** | OOD detection | 10-20ms | ~80% |
| **Energy-Based OOD** | High-confidence rejection | 15-30ms | ~88% |

### Drift Type Taxonomy

| Drift Type | Definition | Detection Signal |
|------------|------------|------------------|
| **SCOPE_EXPANSION** | Related but unsupported feature | Similarity 0.4-0.6, confidence 0.3-0.7 |
| **DOMAIN_SHIFT** | Completely different topic | Similarity <0.3, confidence <0.3 |
| **ABSTRACTION_CLIMB** | Too philosophical/meta | Abstract concepts detected |
| **PERSONALIZATION** | User-specific data needed | PII request patterns |
| **TEMPORAL_DRIFT** | Past/future beyond knowledge | Temporal expressions detected |

### Confidence Thresholds (Industry Standard)

| Confidence | Action | Response Pattern |
|------------|--------|------------------|
| **>0.85** | Direct execution | Standard response |
| **0.70-0.85** | Execute with hedge | "Based on my understanding..." |
| **0.50-0.70** | Clarification | "Did you mean X or Y?" |
| **0.30-0.50** | Redirect options | "I can help with A, B, or C" |
| **<0.30** | Graceful rejection | "That's outside my capabilities..." |

### Graceful Degradation Best Practices

| Strategy | Pattern | User Impact |
|----------|---------|-------------|
| **Fall-Forward** | Offer closest alternatives | +15% CSAT |
| **3-Strike Rule** | Progressive fallback | -40% frustration |
| **Context Continuity** | Preserve conversation state | +28% FCR |
| **Honest Limitation** | Transparent capability bounds | +20% trust |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Intent Drift Detection Layer                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐    │
│  │  Semantic    │  │    Drift     │  │      Response          │    │
│  │  Analyzer    │  │  Classifier  │  │      Generator         │    │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬─────────────┘    │
│         │                 │                      │                  │
│         └─────────────────┼──────────────────────┘                  │
│                           │                                         │
│                    ┌──────▼───────┐                                 │
│                    │   Drift      │                                 │
│                    │   Router     │                                 │
│                    └──────┬───────┘                                 │
│                           │                                         │
├───────────────────────────┼─────────────────────────────────────────┤
│                           │                                         │
│  ┌────────────────────────▼────────────────────────────────────┐   │
│  │              Existing LUI Framework                          │   │
│  │  (InterfaceSchema, ExtractIntent, GenerateResponse)         │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## BAML Type Definitions

### Core Drift Analysis Types

```baml
// Intent drift detection and analysis
class DriftAnalysis {
  original_intent string? @description("Last successfully matched intent")
  current_input string
  drift_score float @description("0.0 = on topic, 1.0 = completely off")
  drift_type DriftType
  confidence float @description("Confidence in drift classification")
  last_supported_intent string?
  semantic_distance float @description("Distance from nearest supported intent")
  suggested_redirects RedirectSuggestion[]
  graceful_response string
}

enum DriftType {
  NONE                // Within capability
  SCOPE_EXPANSION     // Related but unsupported feature
  DOMAIN_SHIFT        // Different domain entirely
  ABSTRACTION_CLIMB   // Too abstract/philosophical
  PERSONALIZATION     // Requires user-specific data we don't have
  TEMPORAL_DRIFT      // Past/future beyond system knowledge
  AMBIGUOUS           // Could be multiple intents, needs clarification
}

class RedirectSuggestion {
  component_id string
  component_intent string
  relevance_score float @description("0.0-1.0 relevance to original request")
  redirect_phrase string @description("Natural language redirect")
}
```

### Semantic Analysis Types

```baml
class SemanticAnalysis {
  input_embedding float[] @description("Vector embedding of input")
  nearest_intents NearestIntent[]
  domain_similarity float @description("Similarity to domain corpus")
  abstraction_level AbstractionLevel
  temporal_references TemporalReference[]
  pii_detected bool
  entities_found Entity[]
}

class NearestIntent {
  component_id string
  intent string
  similarity float @description("Cosine similarity 0.0-1.0")
  confidence float @description("Classification confidence")
}

enum AbstractionLevel {
  CONCRETE      // Specific, actionable requests
  MODERATE      // Some abstraction
  ABSTRACT      // Philosophical, meta-level
  META          // Questions about the system itself
}

class TemporalReference {
  expression string
  temporal_type TemporalType
  relative_to_now string @description("past, present, future")
  within_knowledge bool @description("Is this within system knowledge?")
}

enum TemporalType {
  SPECIFIC_DATE
  RELATIVE_TIME
  DURATION
  FREQUENCY
  HYPOTHETICAL_FUTURE
  HISTORICAL_PAST
}

class Entity {
  text string
  entity_type string
  is_pii bool
  is_supported bool @description("Entity type handled by system")
}
```

### Confidence Scoring Types

```baml
class ConfidenceAssessment {
  intent_confidence float @description("NLU intent classification confidence")
  entity_confidence float @description("Entity extraction confidence")
  context_coherence float @description("Coherence with conversation history")
  overall_confidence float @description("Weighted combination")
  confidence_tier ConfidenceTier
  recommended_action RecommendedAction
}

enum ConfidenceTier {
  HIGH            // >0.85 - Direct execution
  MEDIUM_HIGH     // 0.70-0.85 - Execute with hedge
  MEDIUM          // 0.50-0.70 - Clarification needed
  LOW             // 0.30-0.50 - Offer alternatives
  VERY_LOW        // <0.30 - Graceful rejection
}

enum RecommendedAction {
  EXECUTE                 // Proceed with matched intent
  EXECUTE_WITH_HEDGE      // Proceed but express uncertainty
  CLARIFY                 // Ask for clarification
  OFFER_ALTERNATIVES      // Show related capabilities
  GRACEFUL_REJECT         // Acknowledge limitation
  ESCALATE                // Hand off to human
}
```

### Graceful Response Types

```baml
class GracefulResponse {
  drift_type DriftType
  acknowledgment string @description("Acknowledge the user's request")
  limitation_explanation string? @description("Why we can't help")
  alternatives Redirect[]
  follow_up_question string? @description("If clarification needed")
  escalation_offer string? @description("Offer human handoff if appropriate")
}

class Redirect {
  capability string @description("What we CAN do")
  relevance string @description("How it relates to request")
  action_phrase string @description("'Would you like me to...'")
}

class DriftResponseTemplate {
  drift_type DriftType
  template_pattern string @description("Response template with placeholders")
  tone ResponseTone
  include_alternatives bool
  include_escalation bool
}

enum ResponseTone {
  HELPFUL           // Focus on what we can do
  APOLOGETIC        // Express regret (use sparingly)
  INFORMATIVE       // Explain the limitation
  REDIRECTIVE       // Guide to alternatives
}
```

### Conversation Context Types

```baml
class ConversationContext {
  turns ConversationTurn[]
  current_topic string?
  topic_history string[]
  coherence_scores float[] @description("Per-turn coherence")
  drift_accumulation float @description("Cumulative drift over turns")
  last_successful_intent string?
}

class ConversationTurn {
  turn_id int
  user_input string
  matched_intent string?
  confidence float
  drift_detected bool
  drift_type DriftType?
  response string
  timestamp string
}

class CoherenceAnalysis {
  turn_pair_coherence float[] @description("Adjacent turn coherence")
  overall_coherence float
  topic_shifts int @description("Number of topic changes")
  drift_trend DriftTrend
}

enum DriftTrend {
  STABLE            // Staying on topic
  GRADUAL_DRIFT     // Slowly drifting
  SUDDEN_DRIFT      // Abrupt topic change
  RETURNING         // Coming back to supported topic
}
```

---

## BAML Functions

### Primary Drift Detection

```baml
function DetectIntentDrift(
  conversation_history: ConversationTurn[],
  current_input: string,
  available_components: LUIComponent[]
) -> DriftAnalysis {
  client GPT4o
  prompt #"
    Analyze whether the user's input drifts beyond the capabilities of
    the available LUI components.

    Conversation History:
    {{ conversation_history }}

    Current User Input:
    {{ current_input }}

    Available Capabilities:
    {% for component in available_components %}
    - {{ component.intent }}: {{ component.invocation.primary_phrase }}
      Alternates: {{ component.invocation.alternate_phrases }}
    {% endfor %}

    Analyze for drift:

    1. **Semantic Distance**
       - Calculate similarity to each available intent
       - Identify the nearest supported intent
       - Determine if input is within capability boundary

    2. **Drift Type Classification**
       - NONE: Input matches or is very close to a supported intent
       - SCOPE_EXPANSION: Related to domain but requesting unsupported feature
       - DOMAIN_SHIFT: Completely different domain (e.g., weather on task manager)
       - ABSTRACTION_CLIMB: Philosophical or meta-level (e.g., "Why am I lazy?")
       - PERSONALIZATION: Requires user data we don't have
       - TEMPORAL_DRIFT: Questions about future/past beyond knowledge
       - AMBIGUOUS: Could match multiple intents, needs clarification

    3. **Drift Score** (0.0-1.0)
       - 0.0-0.2: On topic, clear intent match
       - 0.2-0.4: Minor deviation, can be handled
       - 0.4-0.6: Moderate drift, may need clarification
       - 0.6-0.8: Significant drift, redirect recommended
       - 0.8-1.0: Complete drift, graceful rejection needed

    4. **Redirect Suggestions**
       - Find the 2-3 most relevant capabilities
       - Craft natural redirect phrases

    5. **Graceful Response**
       - Acknowledge the user's request
       - Explain limitation (if appropriate)
       - Offer alternatives or escalation

    {{ ctx.output_format }}
  "#
}

function AnalyzeSemanticSimilarity(
  input: string,
  available_intents: string[],
  domain_corpus: string[]
) -> SemanticAnalysis {
  client GPT4o
  prompt #"
    Perform semantic analysis of the user input against available intents.

    User Input: {{ input }}

    Available Intents:
    {% for intent in available_intents %}
    - {{ intent }}
    {% endfor %}

    Domain Context:
    {{ domain_corpus }}

    Analyze:
    1. Find nearest intents by semantic similarity (0.0-1.0 scale)
    2. Determine overall domain similarity
    3. Identify abstraction level (concrete → meta)
    4. Extract temporal references
    5. Detect PII requests
    6. List entities found and their support status

    {{ ctx.output_format }}
  "#
}
```

### Confidence Assessment

```baml
function AssessConfidence(
  intent_result: IntentExtraction,
  semantic_analysis: SemanticAnalysis,
  conversation_context: ConversationContext
) -> ConfidenceAssessment {
  client GPT4o
  prompt #"
    Assess overall confidence in understanding the user's intent.

    Intent Extraction Result:
    {{ intent_result }}

    Semantic Analysis:
    {{ semantic_analysis }}

    Conversation Context:
    {{ conversation_context }}

    Calculate:
    1. **Intent Confidence**: How confident is the intent classification?
    2. **Entity Confidence**: How well were entities extracted?
    3. **Context Coherence**: Does this fit the conversation flow?
    4. **Overall Confidence**: Weighted combination

    Determine confidence tier:
    - HIGH (>0.85): Direct execution
    - MEDIUM_HIGH (0.70-0.85): Execute with hedge
    - MEDIUM (0.50-0.70): Clarification needed
    - LOW (0.30-0.50): Offer alternatives
    - VERY_LOW (<0.30): Graceful rejection

    Recommend action based on confidence tier.

    {{ ctx.output_format }}
  "#
}
```

### Graceful Response Generation

```baml
function GenerateGracefulResponse(
  drift_analysis: DriftAnalysis,
  conversation_context: ConversationContext,
  available_components: LUIComponent[]
) -> GracefulResponse {
  client GPT4o
  prompt #"
    Generate a graceful response for detected intent drift.

    Drift Analysis:
    {{ drift_analysis }}

    Conversation Context:
    {{ conversation_context }}

    Available Capabilities:
    {% for component in available_components %}
    - {{ component.intent }}: {{ component.invocation.primary_phrase }}
    {% endfor %}

    Generate response following these principles:

    1. **Acknowledge First**
       - Validate the user's request
       - Don't dismiss or ignore what they asked

    2. **Explain Limitation** (if appropriate)
       - Be honest about capability bounds
       - Don't over-apologize (paradoxically reduces satisfaction)

    3. **Offer Alternatives**
       - Suggest 2-3 relevant capabilities
       - Frame as "I CAN help you with..."
       - Make alternatives actionable

    4. **Escalation Option** (if appropriate)
       - Offer human handoff for complex needs
       - Provide clear path forward

    Response templates by drift type:

    SCOPE_EXPANSION:
    "I can help with [core capability], but [requested feature] isn't
    available yet. Would you like me to [related action] instead?"

    DOMAIN_SHIFT:
    "I'm designed to help with [domain]. For [their topic], you might
    want to try [suggestion]. Meanwhile, I can help you with [options]."

    ABSTRACTION_CLIMB:
    "That's a thoughtful question! I'm better at practical tasks like
    [examples]. Would any of these help with what you're thinking about?"

    PERSONALIZATION:
    "I don't have access to [personal data type]. I can help you
    [general alternative] if that would be useful."

    TEMPORAL_DRIFT:
    "My knowledge is current as of [date]. For [future/historical info],
    I recommend [resource]. I can help with [current capability]."

    {{ ctx.output_format }}
  "#
}
```

### Multi-Turn Coherence Analysis

```baml
function AnalyzeConversationCoherence(
  conversation_history: ConversationTurn[]
) -> CoherenceAnalysis {
  client GPT4o
  prompt #"
    Analyze the coherence and drift patterns across this conversation.

    Conversation History:
    {% for turn in conversation_history %}
    Turn {{ turn.turn_id }}:
    - User: {{ turn.user_input }}
    - Intent: {{ turn.matched_intent }}
    - Confidence: {{ turn.confidence }}
    - Drift: {{ turn.drift_detected }}
    {% endfor %}

    Analyze:
    1. **Turn-Pair Coherence**: Score semantic coherence between adjacent turns
    2. **Overall Coherence**: Average coherence across conversation
    3. **Topic Shifts**: Count significant topic changes
    4. **Drift Trend**: Is drift stable, gradual, sudden, or returning?

    A high-quality task-oriented conversation should:
    - Maintain topic coherence (>0.7 average)
    - Have few topic shifts (<3 per conversation)
    - Show returning pattern if drift occurs

    {{ ctx.output_format }}
  "#
}
```

---

## Python Implementation

### Semantic Analyzer

```python
# src/drift_detection/semantic_analyzer.py

import numpy as np
from dataclasses import dataclass
from typing import Optional
from enum import Enum

class DriftType(Enum):
    NONE = "none"
    SCOPE_EXPANSION = "scope_expansion"
    DOMAIN_SHIFT = "domain_shift"
    ABSTRACTION_CLIMB = "abstraction_climb"
    PERSONALIZATION = "personalization"
    TEMPORAL_DRIFT = "temporal_drift"
    AMBIGUOUS = "ambiguous"

@dataclass
class NearestIntent:
    component_id: str
    intent: str
    similarity: float
    confidence: float

@dataclass
class SemanticAnalysisResult:
    nearest_intents: list[NearestIntent]
    domain_similarity: float
    abstraction_level: str
    max_similarity: float

    @property
    def is_in_scope(self) -> bool:
        """Check if input is within capability scope."""
        return self.max_similarity >= 0.7


class SemanticAnalyzer:
    """
    Analyzes semantic similarity between user input and available intents.
    """

    # Thresholds for drift detection
    THRESHOLDS = {
        'in_scope': 0.7,           # Above this = clear match
        'scope_expansion': 0.4,    # 0.4-0.7 = related but may not match
        'domain_shift': 0.3,       # Below this = different domain
    }

    # Abstract concept indicators
    ABSTRACT_INDICATORS = [
        'why', 'meaning', 'purpose', 'philosophy', 'consciousness',
        'feel', 'think', 'believe', 'always', 'never', 'life',
        'existence', 'reality', 'truth', 'ethics', 'morality'
    ]

    # Meta-conversation indicators
    META_INDICATORS = [
        'you', 'your', 'ai', 'bot', 'system', 'programmed',
        'trained', 'designed', 'capability', 'limitation'
    ]

    def __init__(self, embedding_model=None):
        self.embedding_model = embedding_model

    def analyze(
        self,
        user_input: str,
        available_intents: list[dict],
        domain_keywords: list[str]
    ) -> SemanticAnalysisResult:
        """
        Analyze semantic similarity of input to available intents.
        """
        # Calculate similarity to each intent
        nearest = []
        for intent_data in available_intents:
            sim = self._calculate_similarity(
                user_input,
                intent_data['primary_phrase'],
                intent_data.get('alternate_phrases', [])
            )
            nearest.append(NearestIntent(
                component_id=intent_data['component_id'],
                intent=intent_data['intent'],
                similarity=sim,
                confidence=self._similarity_to_confidence(sim)
            ))

        # Sort by similarity
        nearest.sort(key=lambda x: x.similarity, reverse=True)

        # Calculate domain similarity
        domain_sim = self._calculate_domain_similarity(
            user_input, domain_keywords
        )

        # Determine abstraction level
        abstraction = self._detect_abstraction_level(user_input)

        max_sim = nearest[0].similarity if nearest else 0.0

        return SemanticAnalysisResult(
            nearest_intents=nearest[:5],  # Top 5
            domain_similarity=domain_sim,
            abstraction_level=abstraction,
            max_similarity=max_sim
        )

    def _calculate_similarity(
        self,
        input_text: str,
        primary_phrase: str,
        alternate_phrases: list[str]
    ) -> float:
        """
        Calculate semantic similarity (simplified version).
        In production, use sentence transformers or similar.
        """
        all_phrases = [primary_phrase] + alternate_phrases

        # Simplified: word overlap ratio
        input_words = set(input_text.lower().split())

        max_sim = 0.0
        for phrase in all_phrases:
            phrase_words = set(phrase.lower().split())
            if not phrase_words:
                continue

            # Jaccard similarity
            intersection = len(input_words & phrase_words)
            union = len(input_words | phrase_words)
            sim = intersection / union if union > 0 else 0.0
            max_sim = max(max_sim, sim)

        return max_sim

    def _calculate_domain_similarity(
        self,
        input_text: str,
        domain_keywords: list[str]
    ) -> float:
        """Calculate similarity to domain keywords."""
        input_words = set(input_text.lower().split())
        domain_words = set(kw.lower() for kw in domain_keywords)

        if not domain_words:
            return 0.5

        overlap = len(input_words & domain_words)
        return min(1.0, overlap / 3)  # Normalize

    def _detect_abstraction_level(self, input_text: str) -> str:
        """Detect the abstraction level of the input."""
        lower_input = input_text.lower()

        abstract_count = sum(
            1 for word in self.ABSTRACT_INDICATORS
            if word in lower_input
        )
        meta_count = sum(
            1 for word in self.META_INDICATORS
            if word in lower_input
        )

        if meta_count >= 2:
            return "META"
        elif abstract_count >= 2:
            return "ABSTRACT"
        elif abstract_count >= 1:
            return "MODERATE"
        else:
            return "CONCRETE"

    def _similarity_to_confidence(self, similarity: float) -> float:
        """Convert similarity score to confidence."""
        # Non-linear mapping
        if similarity >= 0.8:
            return 0.9 + (similarity - 0.8) * 0.5
        elif similarity >= 0.6:
            return 0.7 + (similarity - 0.6) * 1.0
        elif similarity >= 0.4:
            return 0.5 + (similarity - 0.4) * 1.0
        else:
            return similarity * 1.25
```

### Drift Classifier

```python
# src/drift_detection/drift_classifier.py

from dataclasses import dataclass
from typing import Optional
import re

@dataclass
class DriftClassification:
    drift_type: DriftType
    drift_score: float
    confidence: float
    explanation: str

@dataclass
class RedirectSuggestion:
    component_id: str
    intent: str
    relevance: float
    phrase: str


class DriftClassifier:
    """
    Classifies intent drift based on semantic analysis and heuristics.
    """

    # PII request patterns
    PII_PATTERNS = [
        r'\b(my|mine)\b.*(account|balance|password|history|data)',
        r'\b(personal|private)\b.*\b(information|details)\b',
        r'(what|show|tell).*(about me|my profile)',
    ]

    # Temporal patterns
    TEMPORAL_FUTURE = [
        r'\b(will|going to|next|future|tomorrow|upcoming)\b',
        r'\b(predict|forecast|expect)\b',
    ]

    TEMPORAL_PAST = [
        r'\b(was|were|last|previous|ago|history|back in)\b',
        r'\b(remember|recall|past)\b',
    ]

    def classify(
        self,
        user_input: str,
        semantic_result: SemanticAnalysisResult,
        conversation_context: Optional[dict] = None
    ) -> DriftClassification:
        """
        Classify the type and severity of intent drift.
        """
        max_sim = semantic_result.max_similarity
        domain_sim = semantic_result.domain_similarity
        abstraction = semantic_result.abstraction_level

        # Check for specific drift types
        if self._is_pii_request(user_input):
            return DriftClassification(
                drift_type=DriftType.PERSONALIZATION,
                drift_score=0.7,
                confidence=0.85,
                explanation="Request requires personal data not available"
            )

        if self._is_temporal_drift(user_input):
            return DriftClassification(
                drift_type=DriftType.TEMPORAL_DRIFT,
                drift_score=0.6,
                confidence=0.8,
                explanation="Request involves temporal information beyond knowledge"
            )

        if abstraction in ["ABSTRACT", "META"]:
            return DriftClassification(
                drift_type=DriftType.ABSTRACTION_CLIMB,
                drift_score=0.8 if abstraction == "META" else 0.65,
                confidence=0.75,
                explanation=f"Request is {abstraction.lower()}-level, not actionable"
            )

        # Classification based on similarity scores
        if max_sim >= 0.7:
            return DriftClassification(
                drift_type=DriftType.NONE,
                drift_score=0.1,
                confidence=0.9,
                explanation="Clear intent match found"
            )

        if max_sim >= 0.4:
            # Check if it's scope expansion vs ambiguous
            if len([n for n in semantic_result.nearest_intents if n.similarity > 0.4]) > 1:
                return DriftClassification(
                    drift_type=DriftType.AMBIGUOUS,
                    drift_score=0.4,
                    confidence=0.7,
                    explanation="Multiple intents match partially"
                )
            return DriftClassification(
                drift_type=DriftType.SCOPE_EXPANSION,
                drift_score=0.5,
                confidence=0.75,
                explanation="Related to domain but not directly supported"
            )

        if domain_sim >= 0.3:
            return DriftClassification(
                drift_type=DriftType.SCOPE_EXPANSION,
                drift_score=0.6,
                confidence=0.7,
                explanation="Within domain but beyond specific capabilities"
            )

        return DriftClassification(
            drift_type=DriftType.DOMAIN_SHIFT,
            drift_score=0.9,
            confidence=0.85,
            explanation="Request is outside the system's domain"
        )

    def _is_pii_request(self, text: str) -> bool:
        """Check if request involves personal information."""
        lower_text = text.lower()
        return any(
            re.search(pattern, lower_text)
            for pattern in self.PII_PATTERNS
        )

    def _is_temporal_drift(self, text: str) -> bool:
        """Check for temporal drift indicators."""
        lower_text = text.lower()

        # Check for future predictions
        for pattern in self.TEMPORAL_FUTURE:
            if re.search(pattern, lower_text):
                # Additional check for prediction requests
                if any(word in lower_text for word in ['predict', 'will be', 'forecast']):
                    return True

        # Check for historical queries
        for pattern in self.TEMPORAL_PAST:
            if re.search(pattern, lower_text):
                # Check if it's a data request about the past
                if any(word in lower_text for word in ['what was', 'how was', 'back in']):
                    return True

        return False

    def suggest_redirects(
        self,
        semantic_result: SemanticAnalysisResult,
        max_suggestions: int = 3
    ) -> list[RedirectSuggestion]:
        """Generate redirect suggestions based on nearest intents."""
        suggestions = []

        for intent in semantic_result.nearest_intents[:max_suggestions]:
            if intent.similarity >= 0.2:  # Minimum relevance threshold
                suggestions.append(RedirectSuggestion(
                    component_id=intent.component_id,
                    intent=intent.intent,
                    relevance=intent.similarity,
                    phrase=self._generate_redirect_phrase(intent)
                ))

        return suggestions

    def _generate_redirect_phrase(self, intent: NearestIntent) -> str:
        """Generate a natural redirect phrase."""
        return f"Would you like me to help you {intent.intent.lower()} instead?"
```

### Graceful Response Generator

```python
# src/drift_detection/response_generator.py

from dataclasses import dataclass
from typing import Optional

@dataclass
class GracefulResponse:
    acknowledgment: str
    limitation: Optional[str]
    alternatives: list[str]
    follow_up: Optional[str]
    full_response: str


class GracefulResponseGenerator:
    """
    Generates graceful responses for drift scenarios.
    """

    # Response templates by drift type
    TEMPLATES = {
        DriftType.SCOPE_EXPANSION: {
            'acknowledgment': "I understand you're looking for {request_summary}.",
            'limitation': "That specific feature isn't available yet.",
            'alternatives_intro': "However, I can help you with:",
            'follow_up': "Would any of these be helpful?",
        },
        DriftType.DOMAIN_SHIFT: {
            'acknowledgment': "That's an interesting question about {topic}.",
            'limitation': "I'm designed to help with task management, so that's outside my area.",
            'alternatives_intro': "Here's what I can help with:",
            'follow_up': "Is there a task-related way I can assist?",
        },
        DriftType.ABSTRACTION_CLIMB: {
            'acknowledgment': "That's a thoughtful question!",
            'limitation': "I'm better at practical, actionable tasks than philosophical discussions.",
            'alternatives_intro': "I could help you with concrete things like:",
            'follow_up': "Would any of these help with what you're thinking about?",
        },
        DriftType.PERSONALIZATION: {
            'acknowledgment': "I'd like to help with that.",
            'limitation': "I don't have access to your personal {data_type} information.",
            'alternatives_intro': "What I can do is:",
            'follow_up': "Would you like to try one of these options?",
        },
        DriftType.TEMPORAL_DRIFT: {
            'acknowledgment': "Good question about {time_reference}.",
            'limitation': "My knowledge has limitations on {temporal_scope}.",
            'alternatives_intro': "I can help with current information like:",
            'follow_up': "Would current information be useful?",
        },
        DriftType.AMBIGUOUS: {
            'acknowledgment': "I want to make sure I help with the right thing.",
            'limitation': None,
            'alternatives_intro': "Did you mean:",
            'follow_up': "Please let me know which one you'd like.",
        },
    }

    def generate(
        self,
        drift_classification: DriftClassification,
        redirect_suggestions: list[RedirectSuggestion],
        user_input: str
    ) -> GracefulResponse:
        """Generate a graceful response for the drift scenario."""
        template = self.TEMPLATES.get(
            drift_classification.drift_type,
            self.TEMPLATES[DriftType.DOMAIN_SHIFT]
        )

        # Build acknowledgment
        acknowledgment = template['acknowledgment'].format(
            request_summary=self._summarize_request(user_input),
            topic=self._extract_topic(user_input),
            data_type=self._extract_data_type(user_input),
            time_reference=self._extract_time_reference(user_input),
        )

        # Build limitation (if applicable)
        limitation = None
        if template['limitation']:
            limitation = template['limitation'].format(
                temporal_scope=self._get_temporal_scope(user_input)
            )

        # Build alternatives list
        alternatives = []
        for redirect in redirect_suggestions[:3]:
            alternatives.append(f"• {redirect.phrase}")

        # Build follow-up
        follow_up = template['follow_up'] if redirect_suggestions else None

        # Compose full response
        parts = [acknowledgment]
        if limitation:
            parts.append(limitation)
        if alternatives:
            parts.append(template['alternatives_intro'])
            parts.extend(alternatives)
        if follow_up:
            parts.append(follow_up)

        full_response = " ".join(parts)

        return GracefulResponse(
            acknowledgment=acknowledgment,
            limitation=limitation,
            alternatives=[r.phrase for r in redirect_suggestions],
            follow_up=follow_up,
            full_response=full_response
        )

    def _summarize_request(self, user_input: str) -> str:
        """Extract a brief summary of the user's request."""
        # Simplified: use first 5 words
        words = user_input.split()[:5]
        return " ".join(words) + "..." if len(words) == 5 else user_input

    def _extract_topic(self, user_input: str) -> str:
        """Extract the main topic from the input."""
        # Simplified extraction
        return user_input.split()[0] if user_input else "that topic"

    def _extract_data_type(self, user_input: str) -> str:
        """Extract what type of personal data is being requested."""
        keywords = ['account', 'balance', 'history', 'password', 'profile', 'data']
        lower_input = user_input.lower()
        for keyword in keywords:
            if keyword in lower_input:
                return keyword
        return "personal"

    def _extract_time_reference(self, user_input: str) -> str:
        """Extract temporal reference from input."""
        if 'tomorrow' in user_input.lower():
            return "tomorrow"
        if 'future' in user_input.lower():
            return "the future"
        if 'yesterday' in user_input.lower():
            return "yesterday"
        if 'last' in user_input.lower():
            return "the past"
        return "that time period"

    def _get_temporal_scope(self, user_input: str) -> str:
        """Determine the temporal scope being asked about."""
        lower = user_input.lower()
        if any(word in lower for word in ['predict', 'will', 'future']):
            return "future predictions"
        if any(word in lower for word in ['was', 'were', 'history', 'past']):
            return "historical information"
        return "that time period"
```

### Conversation Coherence Tracker

```python
# src/drift_detection/coherence_tracker.py

from dataclasses import dataclass, field
from typing import Optional
from collections import deque

@dataclass
class ConversationTurn:
    turn_id: int
    user_input: str
    matched_intent: Optional[str]
    confidence: float
    drift_detected: bool
    drift_type: Optional[DriftType]
    response: str

@dataclass
class CoherenceMetrics:
    turn_coherence: list[float]
    overall_coherence: float
    topic_shifts: int
    drift_trend: str
    cumulative_drift: float


class ConversationCoherenceTracker:
    """
    Tracks conversation coherence and drift accumulation over turns.
    """

    # Drift trend thresholds
    STABLE_THRESHOLD = 0.2       # Drift score staying below this = stable
    GRADUAL_THRESHOLD = 0.1     # Per-turn increase indicating gradual drift
    SUDDEN_THRESHOLD = 0.3      # Single-turn spike indicating sudden drift

    def __init__(self, window_size: int = 5):
        self.window_size = window_size
        self.turns: deque[ConversationTurn] = deque(maxlen=10)
        self.drift_scores: deque[float] = deque(maxlen=window_size)
        self.last_supported_intent: Optional[str] = None

    def add_turn(self, turn: ConversationTurn):
        """Add a conversation turn and update tracking."""
        self.turns.append(turn)

        if turn.matched_intent and turn.confidence > 0.7:
            self.last_supported_intent = turn.matched_intent

    def add_drift_score(self, score: float):
        """Add a drift score for the current turn."""
        self.drift_scores.append(score)

    def get_coherence_metrics(self) -> CoherenceMetrics:
        """Calculate coherence metrics for the conversation."""
        if len(self.turns) < 2:
            return CoherenceMetrics(
                turn_coherence=[1.0],
                overall_coherence=1.0,
                topic_shifts=0,
                drift_trend="STABLE",
                cumulative_drift=0.0
            )

        # Calculate turn-by-turn coherence
        turn_coherence = []
        topic_shifts = 0

        for i in range(1, len(self.turns)):
            prev_turn = self.turns[i-1]
            curr_turn = self.turns[i]

            # Simple coherence: both matched same intent = 1.0
            if prev_turn.matched_intent and curr_turn.matched_intent:
                if prev_turn.matched_intent == curr_turn.matched_intent:
                    coherence = 1.0
                else:
                    coherence = 0.6
                    topic_shifts += 1
            elif curr_turn.drift_detected:
                coherence = 0.3
                topic_shifts += 1
            else:
                coherence = 0.7

            turn_coherence.append(coherence)

        overall = sum(turn_coherence) / len(turn_coherence) if turn_coherence else 1.0

        # Calculate drift trend
        drift_trend = self._calculate_drift_trend()
        cumulative_drift = sum(self.drift_scores) / len(self.drift_scores) if self.drift_scores else 0.0

        return CoherenceMetrics(
            turn_coherence=turn_coherence,
            overall_coherence=overall,
            topic_shifts=topic_shifts,
            drift_trend=drift_trend,
            cumulative_drift=cumulative_drift
        )

    def _calculate_drift_trend(self) -> str:
        """Determine the drift trend over recent turns."""
        if len(self.drift_scores) < 2:
            return "STABLE"

        scores = list(self.drift_scores)

        # Check for sudden drift (large single-turn spike)
        for i in range(1, len(scores)):
            if scores[i] - scores[i-1] > self.SUDDEN_THRESHOLD:
                return "SUDDEN_DRIFT"

        # Check for gradual drift (consistent increases)
        increasing_count = sum(
            1 for i in range(1, len(scores))
            if scores[i] > scores[i-1]
        )
        if increasing_count >= len(scores) * 0.6:
            if max(scores) > 0.5:
                return "GRADUAL_DRIFT"

        # Check for returning (decreasing after increase)
        if len(scores) >= 3:
            peak_idx = scores.index(max(scores))
            if peak_idx < len(scores) - 1:
                if scores[-1] < max(scores) * 0.6:
                    return "RETURNING"

        # Default to stable
        if max(scores) < self.STABLE_THRESHOLD:
            return "STABLE"

        return "GRADUAL_DRIFT"

    def should_reset_context(self) -> bool:
        """Determine if context should be reset due to drift."""
        metrics = self.get_coherence_metrics()
        return (
            metrics.cumulative_drift > 0.7 or
            metrics.topic_shifts >= 3 or
            metrics.drift_trend == "SUDDEN_DRIFT"
        )

    def get_last_supported_intent(self) -> Optional[str]:
        """Get the last successfully matched intent."""
        return self.last_supported_intent
```

---

## Task Summary

| Task | Description | Effort | Dependencies |
|------|-------------|--------|--------------|
| 5.1 | Drift Analysis Types | 3-4h | None |
| 5.2 | Semantic Analyzer | 4-5h | 5.1 |
| 5.3 | Drift Classifier | 4-5h | 5.2 |
| 5.4 | Confidence Assessor | 3-4h | 5.2 |
| 5.5 | Graceful Response Generator | 4-5h | 5.3 |
| 5.6 | Conversation Coherence Tracker | 4-5h | 5.1 |
| 5.7 | Redirect Suggestion Engine | 3-4h | 5.3 |
| 5.8 | Intent Pipeline Integration | 5-6h | All |
| 5.9 | Response Template Library | 3-4h | 5.5 |
| 5.10 | Drift Analytics & Logging | 4-5h | 5.8 |
| 5.11 | Testing & Documentation | 5-6h | All |

**Total Estimated Effort**: 42-52 hours

---

## Success Criteria

- [ ] Drift detection accuracy >85% on test set
- [ ] Zero hallucinated capabilities (never claims unsupported features)
- [ ] Graceful responses rated natural by user testing
- [ ] Redirect suggestions relevant in >80% of cases
- [ ] Response latency <200ms for drift detection
- [ ] All 5 drift types correctly classified
- [ ] Multi-turn coherence tracking functional
- [ ] ≥80% test coverage

---

## Testing Strategy

### Unit Tests

```python
# tests/test_drift_detection/

def test_scope_expansion_detection():
    """Related but unsupported requests detected."""

def test_domain_shift_detection():
    """Completely off-topic requests detected."""

def test_abstraction_climb_detection():
    """Philosophical questions detected."""

def test_personalization_detection():
    """Personal data requests detected."""

def test_temporal_drift_detection():
    """Future/past requests detected."""

def test_confidence_thresholds():
    """Confidence tiers trigger correct actions."""

def test_graceful_response_templates():
    """Response templates produce natural language."""

def test_redirect_relevance():
    """Suggested redirects are semantically relevant."""

def test_multi_turn_coherence():
    """Coherence tracking across conversation."""

def test_drift_accumulation():
    """Gradual drift correctly identified."""
```

### Integration Tests

```python
def test_full_drift_pipeline():
    """End-to-end drift detection and response."""

def test_intent_extraction_with_drift():
    """Drift detection integrated with intent extraction."""

def test_conversation_flow_with_drift():
    """Complete conversation with drift recovery."""
```

### Example Test Scenarios

| Input | Expected Drift Type | Expected Response Pattern |
|-------|---------------------|---------------------------|
| "Show my tasks" | NONE | Standard intent match |
| "Why am I always late?" | ABSTRACTION_CLIMB | Acknowledge + practical redirect |
| "What's the weather?" | DOMAIN_SHIFT | Out of scope + offer alternatives |
| "Show my account balance" | PERSONALIZATION | Data limitation + alternatives |
| "What will happen next year?" | TEMPORAL_DRIFT | Knowledge limit + current alternatives |

---

## References

- [Semantic Similarity with Sentence Transformers](https://www.sbert.net/)
- [Out-of-Distribution Detection Survey](https://arxiv.org/abs/2110.11334)
- [Confidence Calibration in Deep Learning](https://arxiv.org/abs/1706.04599)
- [Graceful Degradation in Conversational AI](https://dl.acm.org/doi/10.1145/3313831.3376175)
- [RASA Fallback and Human Handoff](https://rasa.com/docs/rasa/fallback-handoff/)
- [Dialogflow Intent Detection Best Practices](https://cloud.google.com/dialogflow/docs/concepts/intent)

---

*Generated as part of the baml-agentic-ux research project, December 2024*
