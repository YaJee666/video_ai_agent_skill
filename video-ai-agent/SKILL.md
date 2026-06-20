---
name: video-ai-agent
description: Call the Video AI Agent OpenAPI from Codex, Claude Code, or other coding agents for online video understanding tasks. Use when the user provides a Bilibili, YouTube, Douyin, TikTok, or directly accessible media URL and asks to summarize, clean transcript content, extract insights, answer questions, compare video content, or continue a Video AI Agent-backed chat through an API key.
---

# Video AI Agent

Use this skill to send online video analysis, summarization, transcript insight extraction, comparison, and Q&A requests to the Video AI Agent platform through its OpenAPI endpoint.

This skill is a lightweight client wrapper. It does not download or transcribe video locally. Put the user's complete intent and all video URLs in `messageContent`; the client also auto-extracts structured `source_url` / `video_id` fields so the backend can route the right video pipeline.

## Configuration

The bundled script loads Video AI Agent configuration automatically. Put the API key in the installed skill `.env` file for persistent local use, then agents can call the backend directly with only `--message`.

Minimum key scope:

- `jobs:write` and `jobs:read` for the default long-running jobs mode
- `chat:write` only when using `--mode sync`

Default endpoint:

```text
https://www.talkaibot.com/openapi/v1/chat/completions
```

Supported authentication headers on the backend:

- `X-API-Key: vag_sk_live_xxx`
- `Authorization: Bearer vag_sk_live_xxx`

Prefer `X-API-Key`.

## Supported Stable Sources

Use this skill for:

- Bilibili / B站 video URLs and BV IDs
- YouTube URLs, including `youtube.com/watch`, `youtu.be`, and Shorts
- Douyin / 抖音 video URLs
- TikTok video URLs
- directly accessible video, audio, or media URLs when the backend can read them

If the backend reports an unsupported or inaccessible URL, return that error instead of attempting local scraping.

## Quick Start

Use the bundled client script:

```bash
python scripts/video_ai_agent_chat.py --message "Summarize this video in Chinese: https://www.bilibili.com/video/BV..."
```

The script automatically reads `.env` from the installed skill directory and from the current working directory hierarchy:

```text
VIDEO_AI_AGENT_API_KEY
VIDEO_AI_AGENT_ENDPOINT
VIDEO_AI_AGENT_MODE
VIDEO_AI_AGENT_TIMEOUT_MS
VIDEO_AI_AGENT_PROJECT_ID
VIDEO_AI_AGENT_SESSION_ID
```

Configuration precedence is `CLI arguments > shell environment > .env > defaults`. Only pass `--api-key` for a one-off override:

```bash
python scripts/video_ai_agent_chat.py \
  --api-key "vag_sk_live_xxx" \
  --message "For https://www.youtube.com/watch?v=..., list the main points and practical takeaways."
```

To verify configuration without sending a request, use:

```bash
python scripts/video_ai_agent_chat.py --debug-config
```

## Workflow

1. Confirm the user wants a video task or a Video AI Agent-backed chat task.
2. Call `scripts/video_ai_agent_chat.py` directly with the complete instruction and all video URLs in `--message`; the default `jobs` mode is for long video work.
3. Do not preflight or print API key state; the script loads `.env` automatically and reports a clear configuration error if the key is missing.
4. Preserve conversation continuity when useful with `--session-id`.
5. Include `--project-id` only when the user wants the request associated with a known Video AI Agent project in the API key workspace.
6. Return the backend response text and mention request/session IDs when useful for debugging.

## Request Shape

By default, the script creates a job with `POST /openapi/v1/jobs` and polls it until completion. Use `--mode sync` only for short chat-completion requests.

Jobs mode wraps the user intent as:

```json
{
  "requestId": "req_agent_skill_...",
  "projectId": "optional project id",
  "workflowPreset": "video.qa.basic",
  "jobType": "video_ai_agent_skill",
  "input": {
    "messageContent": "full user intent and video URLs",
    "sessionId": "optional session id"
  },
  "metadata": {
    "request_source": "agent_skill_jobs",
    "skill_id": "video-ai-agent"
  }
}
```

Sync mode sends JSON compatible with `POST /openapi/v1/chat/completions`:

```json
{
  "requestId": "req_agent_skill_...",
  "projectId": "optional project id",
  "sessionId": "optional session id",
  "title": "optional title",
  "messageContent": "full user intent and video URLs",
  "metadata": {
    "request_source": "agent_skill",
    "skill_id": "video-ai-agent"
  }
}
```

## Good Prompts

Summarization:

```text
Summarize this video in Chinese, extract the key claims, and list the practical takeaways: <video url>
```

Video Q&A:

```text
For this video, explain the speaker's argument about model evaluation and identify any assumptions: <video url>
```

Comparison:

```text
Compare these two videos and identify where their recommendations conflict: <url 1> <url 2>
```

Transcript cleanup:

```text
Clean and restructure the content of this video into a readable outline with timestamps when available: <video url>
```

## Troubleshooting

If the backend returns `401` or `403`, check that the API key is active and has `chat:write`.

If the tool times out, retry with a larger timeout:

```bash
python scripts/video_ai_agent_chat.py --timeout-ms 900000 --message "..."
```

If a platform link is private, deleted, region-restricted, login-gated, or otherwise unsupported, report the backend error rather than attempting local scraping.

For setup details, read `references/setup.md`.
