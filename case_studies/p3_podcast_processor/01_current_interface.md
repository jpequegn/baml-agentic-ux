# P3 Podcast Processor - Current Interface Documentation

## Application Overview

**P3 (Parakeet Podcast Processor)** is an automated podcast processing pipeline that:
- Downloads podcast episodes from RSS feeds
- Transcribes audio using Whisper/Parakeet MLX
- Generates AI-powered summaries and digests
- Creates blog posts with iterative grading
- Supports interactive querying and analysis

## Current CLI Interface

### Core Pipeline Commands

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `p3 init` | Initialize P3 system | - |
| `p3 fetch` | Download episodes from RSS | `--max-episodes`, `--podcast` |
| `p3 transcribe` | Transcribe audio files | `--model`, `--episode-id` |
| `p3 digest` | Generate AI summaries | `--provider`, `--model`, `--episode-id` |
| `p3 export` | Export daily digests | `--date`, `--format`, `--output`, `--s3-only` |

### Content Generation

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `p3 write` | Generate blog posts | `--topic` (required), `--date`, `--target-grade` |

### Querying & Analysis

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `p3 query` | Ask questions about episode | `--episode-id`, `--question` |
| `p3 analyze` | Analyze topic across episodes | `--topic`, `--days`, `--max-episodes` |
| `p3 trends` | Identify trending topics | `--days` |
| `p3 chat` | Interactive episode chat | `--episode-id` |
| `p3 search_quotes` | Search for quotes | `--keyword`, `--max-results` |

### Status & Management

| Command | Purpose | Key Options |
|---------|---------|-------------|
| `p3 status` | Show processing status | - |
| `p3 list_episodes` | List episodes | `--status`, `--podcast`, `--limit`, `--recent` |
| `p3 episode_info` | Show episode details | `--episode-id` |
| `p3 cleanup` | Clean up old files | `--dry-run` |
| `p3 export_sync` | Export for Podlet sync | `--limit`, `--output-dir` |

## User Flows

### Flow 1: Daily Podcast Processing
```
p3 fetch --max-episodes 5
  -> p3 transcribe
    -> p3 digest
      -> p3 export --format markdown
```

### Flow 2: Blog Post Creation
```
p3 status (check what's available)
  -> p3 write --topic "AI in Venture Capital"
    -> Review generated blog post
```

### Flow 3: Research & Discovery
```
p3 trends --days 14
  -> p3 analyze --topic "machine learning"
    -> p3 query --episode-id 42 --question "What specific ML models were discussed?"
```

### Flow 4: Episode Discovery
```
p3 list_episodes --recent --limit 10
  -> p3 episode_info --episode-id 42
    -> p3 chat --episode-id 42
```

## Pain Points with Current CLI

1. **Remembering episode IDs**: Users must look up IDs before querying
2. **Multi-step workflows**: Pipeline requires multiple sequential commands
3. **Configuration complexity**: Many options across commands
4. **Discovery friction**: Hard to know what's available without running status commands
5. **No natural language**: Commands are structured and require exact syntax

## Opportunities for LUI

1. **Natural language queries**: "What did they say about AI in the last week?"
2. **Contextual awareness**: Remember current episode context
3. **Workflow automation**: "Process today's podcasts and write a blog"
4. **Conversational discovery**: "What podcasts are available?"
5. **Flexible entity references**: "the latest episode" vs `--episode-id 42`
