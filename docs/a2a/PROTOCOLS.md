# A2A Protocol Specifications

## Overview

This document describes the protocols implemented in the agent-to-agent negotiation system, including message formats, state transitions, and interaction patterns.

## Supported Protocols

| Protocol | Version | Purpose |
|----------|---------|---------|
| A2A | 1.0 | Google Agent-to-Agent protocol |
| MCP | 1.0 | Model Context Protocol |
| OpenAPI | 3.0 | REST API specification |
| JSON-RPC | 2.0 | Generic RPC |
| gRPC | 1.0 | High-performance RPC |
| GraphQL | 1.0 | Query language |
| WebSocket | 1.0 | Bidirectional communication |

## Agent Card Protocol

### Discovery Endpoint

Agents expose their capabilities at a well-known endpoint:

```
GET /.well-known/agent.json
```

### Response Format

```json
{
  "identity": {
    "agent_id": "urn:agent:acme:translator:1.0.0",
    "name": "translator",
    "version": "1.0.0",
    "description": "Multi-language translation service",
    "provider": "acme"
  },
  "capabilities": [
    {
      "capability_id": "translate-text",
      "capability_type": "transform",
      "name": "translate_text",
      "description": "Translate text between languages",
      "input_schema": {
        "type": "object",
        "properties": {
          "text": {"type": "string"},
          "source_language": {"type": "string"},
          "target_language": {"type": "string"}
        },
        "required": ["text", "target_language"]
      },
      "output_schema": {
        "type": "object",
        "properties": {
          "translated_text": {"type": "string"},
          "detected_language": {"type": "string"}
        }
      }
    }
  ],
  "supported_protocols": [
    {"protocol": "a2a", "version": "1.0"},
    {"protocol": "mcp", "version": "1.0"}
  ],
  "endpoints": [
    {
      "endpoint_type": "primary",
      "url": "https://api.acme.com/agents/translator",
      "protocol": "a2a",
      "auth_method": "bearer_token"
    }
  ],
  "compliance_tags": ["gdpr", "soc2"]
}
```

## Capability Registry Protocol

### Registration

```
POST /registry/agents
Content-Type: application/json
Authorization: Bearer <token>

{
  "agent_card": { ... },
  "ttl_seconds": 3600,
  "metadata": {
    "environment": "production",
    "region": "us-west-2"
  }
}
```

**Response:**
```json
{
  "success": true,
  "registration_id": "reg-123",
  "expires_at": "2024-12-29T12:00:00Z",
  "indexed_capabilities": ["translate-text", "detect-language"]
}
```

### Discovery

```
POST /registry/discover
Content-Type: application/json

{
  "required_capabilities": ["transform"],
  "constraints": [
    {
      "field": "compliance_tags",
      "operator": "contains",
      "value": "gdpr"
    }
  ],
  "max_results": 10,
  "timeout_ms": 5000
}
```

**Response:**
```json
{
  "agents": [
    {
      "agent": { ... },
      "match_score": 0.95,
      "capability_coverage": 1.0,
      "compatibility_notes": []
    }
  ],
  "total_count": 3,
  "discovery_time_ms": 45,
  "source": "registry"
}
```

### Deregistration

```
DELETE /registry/agents/{agent_id}
Authorization: Bearer <token>
```

## Negotiation Protocol

### State Machine

```
States:
- INITIATED: Session created
- PROPOSAL_SENT: Initial proposal sent
- COUNTER_OFFERED: Counter-proposal received
- ACCEPTED: Agreement reached
- REJECTED: Negotiation failed
- EXPIRED: Session timed out
- CANCELLED: Session cancelled
- ADAPTED: Adapted to alternative

Valid Transitions:
INITIATED → PROPOSAL_SENT, CANCELLED
PROPOSAL_SENT → COUNTER_OFFERED, ACCEPTED, REJECTED, EXPIRED
COUNTER_OFFERED → COUNTER_OFFERED, ACCEPTED, REJECTED, EXPIRED
ACCEPTED → (terminal)
REJECTED → (terminal)
EXPIRED → (terminal)
CANCELLED → (terminal)
ADAPTED → (terminal)
```

### Initiate Negotiation

```
POST /negotiations
Content-Type: application/json
Authorization: Bearer <token>

{
  "initiator": {
    "agent_id": "urn:agent:client:app:1.0.0"
  },
  "target": {
    "agent_id": "urn:agent:acme:translator:1.0.0"
  },
  "proposal": {
    "requested_capabilities": [
      {
        "capability_type": "transform",
        "priority": "required",
        "constraints": [
          {"type": "rate_limit", "value": "1000/hour"}
        ]
      }
    ],
    "offered_capabilities": [],
    "terms": {
      "duration_seconds": 86400,
      "auto_renew": false
    },
    "validity_period_seconds": 3600
  }
}
```

**Response:**
```json
{
  "session_id": "neg-456",
  "status": "proposal_sent",
  "created_at": "2024-12-28T10:00:00Z",
  "expires_at": "2024-12-29T10:00:00Z",
  "history": [
    {
      "turn_number": 1,
      "actor": "urn:agent:client:app:1.0.0",
      "action": "propose",
      "timestamp": "2024-12-28T10:00:00Z"
    }
  ]
}
```

### Respond to Proposal

```
POST /negotiations/{session_id}/respond
Content-Type: application/json
Authorization: Bearer <token>

{
  "action": "counter",
  "counter_proposal": {
    "requested_capabilities": [...],
    "offered_capabilities": [...],
    "terms": {
      "duration_seconds": 43200,
      "auto_renew": true
    }
  },
  "rationale": "Reduced duration, added auto-renew"
}
```

### Finalize Agreement

```
POST /negotiations/{session_id}/finalize
Authorization: Bearer <token>
```

**Response:**
```json
{
  "agreement_id": "agr-789",
  "parties": [...],
  "capabilities_granted": [
    {
      "capability": {...},
      "grantee": "urn:agent:client:app:1.0.0",
      "grantor": "urn:agent:acme:translator:1.0.0",
      "access_token": "cap-token-xyz",
      "conditions": [...]
    }
  ],
  "terms": {...},
  "created_at": "2024-12-28T10:30:00Z",
  "expires_at": "2024-12-29T10:30:00Z"
}
```

## Capability Invocation Protocol

### Invoke Capability

```
POST /capabilities/{capability_id}/invoke
Content-Type: application/json
Authorization: Bearer <capability_token>

{
  "input": {
    "text": "Hello, world!",
    "target_language": "es"
  },
  "options": {
    "timeout_ms": 5000,
    "trace_id": "trace-123"
  }
}
```

**Response:**
```json
{
  "output": {
    "translated_text": "¡Hola, mundo!",
    "detected_language": "en"
  },
  "metadata": {
    "latency_ms": 120,
    "tokens_used": 15
  }
}
```

## Composition Protocol

### Plan Composition

```
POST /compositions/plan
Content-Type: application/json

{
  "goal": "Translate and summarize document",
  "required_capabilities": ["transform", "summarize"],
  "constraints": [
    {"type": "max_latency_ms", "value": "10000"}
  ]
}
```

**Response:**
```json
{
  "plan_id": "plan-001",
  "goal": "Translate and summarize document",
  "steps": [
    {
      "step_id": "step-1",
      "agent": {...},
      "capability": {...},
      "input_bindings": [
        {"parameter_name": "text", "source": "user_input", "source_reference": "document"}
      ],
      "output_name": "translated_doc"
    },
    {
      "step_id": "step-2",
      "agent": {...},
      "capability": {...},
      "input_bindings": [
        {"parameter_name": "text", "source": "previous_step", "source_reference": "step-1"}
      ],
      "output_name": "summary"
    }
  ],
  "data_flow": [
    {"from_step": "step-1", "to_step": "step-2", "data_path": "$.translated_doc"}
  ],
  "estimated_latency_ms": 2500
}
```

### Execute Composition

```
POST /compositions/{plan_id}/execute
Content-Type: application/json
Authorization: Bearer <token>

{
  "inputs": {
    "document": "Long document text..."
  },
  "config": {
    "parallel_execution": false,
    "global_timeout_ms": 30000
  }
}
```

**Response:**
```json
{
  "execution_id": "exec-001",
  "plan_id": "plan-001",
  "status": "completed",
  "started_at": "2024-12-28T10:00:00Z",
  "completed_at": "2024-12-28T10:00:02.5Z",
  "step_results": [
    {
      "step_id": "step-1",
      "status": "completed",
      "output": "...",
      "latency_ms": 1200
    },
    {
      "step_id": "step-2",
      "status": "completed",
      "output": "...",
      "latency_ms": 1300
    }
  ],
  "final_output": "Summary of the translated document..."
}
```

## Conflict Resolution Protocol

### Analyze Conflicts

```
POST /conflicts/analyze
Content-Type: application/json

{
  "proposal_a": {...},
  "proposal_b": {...}
}
```

**Response:**
```json
{
  "conflicts": [
    {
      "conflict_id": "conf-1",
      "conflict_type": "schema_mismatch",
      "description": "Input schema type mismatch: string vs object",
      "severity": "high"
    }
  ],
  "severity": "high",
  "resolvable": true,
  "resolution_paths": [
    {
      "path_id": "path-1",
      "strategy": "transform",
      "steps": [...],
      "estimated_success_probability": 0.9
    }
  ]
}
```

### Request Mediation

```
POST /conflicts/mediate
Content-Type: application/json

{
  "session_id": "neg-456",
  "conflict": {...},
  "party_a_position": {...},
  "party_b_position": {...},
  "mediation_style": "facilitative"
}
```

## Error Responses

All endpoints return errors in a consistent format:

```json
{
  "error": {
    "code": "CAPABILITY_NOT_FOUND",
    "message": "The requested capability does not exist",
    "details": {
      "capability_id": "unknown-cap"
    },
    "trace_id": "trace-123"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AGENT_NOT_FOUND` | 404 | Agent does not exist |
| `CAPABILITY_NOT_FOUND` | 404 | Capability does not exist |
| `SESSION_NOT_FOUND` | 404 | Negotiation session not found |
| `INVALID_TRANSITION` | 400 | Invalid state transition |
| `PROPOSAL_EXPIRED` | 410 | Proposal validity period expired |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Rate Limiting

Rate limits are communicated via headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1735384800
```

## Versioning

API versioning via Accept header:

```
Accept: application/vnd.a2a.v1+json
```

Or URL path:

```
/v1/registry/discover
```
