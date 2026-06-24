# Video AI Agent Skill Setup

## Create an API key

1. Sign in to the Video AI Agent web app.
2. Open the API key or console page for the target workspace.
3. Create an API key.
4. Include the `jobs:write` and `jobs:read` scopes for default jobs mode. Add `chat:write` only if you plan to use `--mode sync`.
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

Preferred: create a `.env` file in the installed skill directory so every new agent session can call the backend without any preflight configuration checks.

```powershell
Copy-Item "$env:USERPROFILE\.codex\skills\video-ai-agent\.env.example" "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
notepad "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
```

`.env` example:

```text
VIDEO_AI_AGENT_API_KEY=vag_sk_live_xxx
VIDEO_AI_AGENT_ENDPOINT=https://www.talkaibot.com/openapi/v1/chat/completions
VIDEO_AI_AGENT_MODE=jobs
VIDEO_AI_AGENT_TIMEOUT_MS=600000
VIDEO_AI_AGENT_PROJECT_ID=proj_xxx
VIDEO_AI_AGENT_SESSION_ID=
```

The client script loads `.env` from the installed skill directory and from the current working directory hierarchy. Precedence is: CLI args > shell environment > `.env` > defaults.
When a supported video URL is present in `--message`, the client auto-adds structured `source_url`, `video_id`, and `context` fields for the backend runtime.

To refresh the skill, run the installer from a repository checkout. The installed skill folder does not include `scripts/install_skill.py`:

```powershell
python .\scripts\install_skill.py --target auto --update
```

To inspect resolved configuration without sending a request:

```powershell
python .\scripts\video_ai_agent_chat.py --debug-config
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

Local audio upload and segment transcription:

```powershell
python .\scripts\video_ai_agent_chat.py `
  --audio-file "C:\media\lesson.m4a" `
  --message "转写这个音频 2:20 到 2:40 的内容"
```

Local audio transcript-based writing:

```powershell
python .\scripts\video_ai_agent_chat.py `
  --audio-file "C:\media\interview.mp3" `
  --write-from-audio
```

## Notes

- Do not commit API keys to a repository.
- Prefer the installed skill `.env` file for persistent local API key configuration.
- Agents should call the script directly for video tasks; let the script report missing or invalid configuration.
- Keep the full user request and video URLs in `messageContent`.
- Use `sessionId` only when the user wants continuity across requests.
- Use `projectId` only when the key's workspace owns that project.
- Keep `VIDEO_AI_AGENT_MODE=jobs` for long video parsing, summarization, transcript cleanup, and Q&A.
- Local audio uploads automatically switch the request to sync mode after `POST /openapi/v1/files`.
- Use `--resource-id <id>` to reuse a previously uploaded audio resource without uploading it again.
- Use `--mode sync` only for short chat-completion requests.
- Increase `VIDEO_AI_AGENT_TIMEOUT_MS` if the job polling window is too short.
