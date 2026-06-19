# Video AI Agent Skill Setup

## Create an API key

1. Sign in to the Video AI Agent web app.
2. Open the API key or console page for the target workspace.
3. Create an API key.
4. Include the `chat:write` scope.
5. Copy the `vag_sk_...` key when it is shown. It is only displayed once.

New users receive a USD 10 free credit for initial testing. Actual usage and remaining balance are shown in the Video AI Agent console.

## Install in Codex

Preferred installer from this repository root:

```powershell
python .\scripts\install_skill.py --target codex
```

Manual fallback: copy the `video-ai-agent` folder into a Codex skills directory, for example:

```text
%USERPROFILE%\.codex\skills\video-ai-agent
```

Then start a new Codex session so the skill metadata is discovered.

## Install in Claude Code

Preferred installer from this repository root:

```powershell
python .\scripts\install_skill.py --target claude
```

Manual fallback: copy the `video-ai-agent` folder into a Claude Code skill location supported by your local setup, then start a new Claude Code session.

The skill is intentionally plain: it contains `SKILL.md`, `references/`, `scripts/`, and `agents/`, so platforms that support folder-based skills can load the same package.

## Configure

Preferred: create a `.env` file in the installed skill directory so every new agent session can reuse the same configuration.

```powershell
Copy-Item "$env:USERPROFILE\.codex\skills\video-ai-agent\.env.example" "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
notepad "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
```

`.env` example:

```text
VIDEO_AI_AGENT_API_KEY=vag_sk_live_xxx
VIDEO_AI_AGENT_ENDPOINT=http://www.talkaibot.com/openapi/v1/chat/completions
VIDEO_AI_AGENT_TIMEOUT_MS=600000
VIDEO_AI_AGENT_PROJECT_ID=proj_xxx
VIDEO_AI_AGENT_SESSION_ID=
```

The client script loads `.env` from the current directory, the skill root, or the repository root. CLI arguments override shell environment variables, and shell environment variables override `.env`.

## Verify

From the skill directory:

```powershell
python .\scripts\video_ai_agent_chat.py --message "Hello, what can you do?"
```

Video smoke test:

```powershell
python .\scripts\video_ai_agent_chat.py --message "Please summarize this video in Chinese: https://www.bilibili.com/video/BV..."
```

## Notes

- Do not commit API keys to a repository.
- Prefer the installed skill `.env` file for persistent local API key configuration.
- Keep the full user request and video URLs in `messageContent`.
- Use `sessionId` only when the user wants continuity across requests.
- Use `projectId` only when the key's workspace owns that project.
- Increase `VIDEO_AI_AGENT_TIMEOUT_MS` for long videos.
