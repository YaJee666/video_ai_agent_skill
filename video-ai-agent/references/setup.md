# Video AI Agent Skill Setup

## Create an API key

1. Sign in to the Video AI Agent web app.
2. Open the API key or console page for the target workspace.
3. Create an API key.
4. Include the `chat:write` scope.
5. Copy the `vag_sk_...` key when it is shown. It is only displayed once.

New users receive a USD 10 free credit for initial testing. Actual usage and remaining balance are shown in the Video AI Agent console.

## Install in Codex

Copy the `video-ai-agent` folder into a Codex skills directory, for example:

```text
%USERPROFILE%\.codex\skills\video-ai-agent
```

Then start a new Codex session so the skill metadata is discovered.

## Install in Claude Code

Copy the `video-ai-agent` folder into a Claude Code skill location supported by your local setup, then start a new Claude Code session.

The skill is intentionally plain: it contains `SKILL.md`, `references/`, `scripts/`, and `agents/`, so platforms that support folder-based skills can load the same package.

## Configure

Set the API key in the shell that runs the agent:

```powershell
$env:VIDEO_AI_AGENT_API_KEY = "vag_sk_live_xxx"
```

Optional settings:

```powershell
$env:VIDEO_AI_AGENT_ENDPOINT = "http://www.talkaibot.com/openapi/v1/chat/completions"
$env:VIDEO_AI_AGENT_TIMEOUT_MS = "600000"
$env:VIDEO_AI_AGENT_PROJECT_ID = "proj_xxx"
$env:VIDEO_AI_AGENT_SESSION_ID = "session_xxx"
```

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
- Keep the full user request and video URLs in `messageContent`.
- Use `sessionId` only when the user wants continuity across requests.
- Use `projectId` only when the key's workspace owns that project.
- Increase `VIDEO_AI_AGENT_TIMEOUT_MS` for long videos.
