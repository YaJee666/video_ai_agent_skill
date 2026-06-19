# Video AI Agent Skill

Give Codex, Claude Code, and other coding agents online video understanding in one step.

Video AI Agent Skill is a lightweight folder-based skill. It does not download, crack, or clean up video sites locally. Instead, it sends the full video understanding request to Video AI Agent OpenAPI, where the online service handles video parsing, subtitle/transcript extraction, cleanup, summarization, and Q&A.

## Highlights

- **Online video intelligence**: Send Bilibili, YouTube, Douyin, TikTok, and direct media URLs to Codex / Claude Code and get summaries, key claims, Q&A, and comparisons through one interface.
- **Zero local heavy dependencies**: No local GPU, Whisper, ffmpeg, yt-dlp, site scrapers, or cookie handling required.
- **Agent-friendly**: The skill ships with `SKILL.md`, a dependency-free Python client, and short docs that agents can understand directly.
- **More reliable online parsing**: Video downloading, transcription, and cleanup happen on the service side instead of fighting platform quirks locally.
- **Lower model cost**: No need to spend expensive GPT / Opus calls locally just to clean long subtitles.
- **USD 10 free credit**: New workspaces receive a free credit for initial testing.

## Supported Platforms

This README only lists stable support. Exact availability depends on what the online API returns.

| Platform | Supported Content | Example |
| --- | --- | --- |
| Bilibili / B站 | BV IDs, Bilibili video URLs, common short links | `https://www.bilibili.com/video/BV...` |
| YouTube | Normal videos, short links, Shorts | `https://www.youtube.com/watch?v=...` |
| Douyin / 抖音 | Douyin video URLs | `https://www.douyin.com/video/...` |
| TikTok | TikTok video URLs | `https://www.tiktok.com/@user/video/...` |
| Direct media URL | Directly accessible video, audio, or media files | `https://example.com/video.mp4` |

Possible failures include private videos, deleted videos, login walls, region restrictions, anti-bot blocks, and videos with no subtitles that the service cannot download or transcribe.

## Quick Start

### 1. One-line install

Copy this to your Codex, Claude Code, or another coding agent:

```text
Install Video AI Agent Skill: https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/install.md
```

For preview-only installation:

```text
Install Video AI Agent Skill (preview only): https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/install.md
Use the --dry-run flag during installation
```

For future updates:

```text
Update Video AI Agent Skill: https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

### 2. Get an API key

Create a Video AI Agent API key in the workspace console with the minimum scope:

```text
chat:write
```

The key is shown only once. Store it locally and do not commit it to Git.

New users receive **USD 10 free credit** for initial testing. Usage and remaining balance are shown in the console.

### 3. Install the skill

If you already cloned the repository, run:

```powershell
python .\scripts\install_skill.py --target auto
```

`--target auto` installs to existing common skill roots. If none are found, it defaults to Codex:

```text
%USERPROFILE%\.codex\skills\video-ai-agent
```

Other targets:

```powershell
python .\scripts\install_skill.py --target codex
python .\scripts\install_skill.py --target claude
python .\scripts\install_skill.py --target all
python .\scripts\install_skill.py --target auto --dry-run
```

### 4. Configure `.env`

Recommended: create a `.env` file inside the installed skill directory so you do not need to reconfigure every new shell.

Codex default location:

```powershell
Copy-Item "$env:USERPROFILE\.codex\skills\video-ai-agent\.env.example" "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
notepad "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
```

Example `.env`:

```text
VIDEO_AI_AGENT_API_KEY=vag_sk_live_xxx
VIDEO_AI_AGENT_ENDPOINT=http://www.talkaibot.com/openapi/v1/chat/completions
VIDEO_AI_AGENT_TIMEOUT_MS=600000
VIDEO_AI_AGENT_PROJECT_ID=
VIDEO_AI_AGENT_SESSION_ID=
```

The client loads `.env` from the current directory, the installed skill root, or the repository root. Priority is: `.env` file > shell environment > CLI arguments.

You can still set temporary environment variables:

```powershell
$env:VIDEO_AI_AGENT_API_KEY = "vag_sk_live_xxx"
```

### 5. Verify

From the repository root:

```powershell
python .\video-ai-agent\scripts\video_ai_agent_chat.py --message "Please summarize this video in Chinese: https://www.bilibili.com/video/BV..."
```

Or use the skill directly:

```text
Use $video-ai-agent to summarize this video in Chinese: https://www.youtube.com/watch?v=...
```

Start a new Codex / Claude Code session after installation so the agent sees the new skill metadata.

## Update Flow

Use the update guide:

```text
Update Video AI Agent Skill: https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

The update flow pulls the latest repository code, resyncs the skill folder, and preserves installed `.env` files, so the API key does not need to be re-entered.

## Why Online Parsing Helps

### No proxy needed

Your local agent does not need to directly fight video sites. The request goes to Video AI Agent OpenAPI, and the backend handles site access, downloads, subtitles, and transcription.

### No GPU needed

No local Whisper, VLM, or multimodal model is required. A Python standard-library client is enough.

### Faster network path

Video parsing often gets stuck on downloads, region restrictions, or slow transcription. The service-side pipeline avoids local download failures and repeated setup.

### No expensive local cleanup model

Many workflows download subtitles and then spend GPT / Opus calls cleaning them. This skill sends the job straight to Video AI Agent and gets cleaned summaries and Q&A back.

### Lighter agent workflow

The agent only needs to pass the full user intent and video URLs in `messageContent`. The backend chooses the right parsing path.

## FAQ

### How is this different from yt-dlp or local Whisper?

yt-dlp and Whisper are local toolchains that you must maintain yourself. Video AI Agent Skill is an OpenAPI client that pushes the work to the online service.

### How is this different from Agent-Reach?

Agent-Reach is an internet capability router and installer. Video AI Agent Skill focuses on video understanding and wraps it into one online service call.

### Do I need an API key?

Yes. The API uses workspace API key auth. The minimum scope is `chat:write`. The recommended place to store it is the installed skill `.env` file.

### Is there a free credit?

Yes. New workspaces get USD 10 free credit for testing. It is not unlimited free usage.

### Do I need a proxy?

Usually no. You only need network access to the Video AI Agent endpoint.

### Do I need a GPU?

No. Video transcription and understanding happen on the service side.

### Why do some videos fail?

Common causes include private videos, deleted videos, region restrictions, login walls, anti-bot blocks, and videos without usable subtitles/transcripts.

### Can I continue a conversation?

Yes. Use `VIDEO_AI_AGENT_SESSION_ID` or `--session-id`.

### How do I update the skill?

Copy the update one-liner to your agent or use the local update script. The update keeps the installed `.env` file.

### Can I put the API key directly on the command line?

You can, but it is not recommended. The `.env` file or a local secrets manager is better.

## License

MIT
