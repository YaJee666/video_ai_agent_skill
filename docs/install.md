# Video AI Agent Skill — Installation Guide

## For Humans

Copy this to your AI agent:

```text
帮我安装 Video AI Agent Skill：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/install.md
```

Security-conscious? Ask the agent to preview the install first:

```text
帮我安装 Video AI Agent Skill（先预览，不要改文件）：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/install.md
安装时使用 --dry-run 参数
```

After installation, put your API key in the installed skill `.env` file:

```powershell
Copy-Item "$env:USERPROFILE\.codex\skills\video-ai-agent\.env.example" "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
notepad "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
```

New users receive a USD 10 free credit for initial testing. Usage and remaining balance are shown in the Video AI Agent console.

---

## For AI Agents

### Goal

Install the `video-ai-agent` folder-based skill so Codex, Claude Code, or another compatible coding agent can call Video AI Agent OpenAPI for online video summarization, transcript cleanup, comparison, and Q&A.

This installer does not install video downloaders, local ASR, GPU dependencies, or platform scrapers. The user's agent calls the online API; the backend handles video parsing, transcription, cleanup, and summarization.

### Boundaries

Stay within these limits:

- Do not install system packages.
- Do not ask for or store API keys in the repository.
- Store API keys in the installed skill `.env` file, not in the cloned repo, unless the user explicitly asks otherwise.
- Do not commit secrets.
- Do not modify projects in the user's current workspace except the dedicated install checkout under the user's home directory.
- Do not overwrite unrelated skill folders.
- If a destination skill folder already exists, replace only `video-ai-agent`.

### Directory Rules

Use dedicated directories:

| Purpose | Directory | Example |
| --- | --- | --- |
| Installer checkout | `~/.video-ai-agent-skill/repo` | cloned GitHub repo |
| Codex skill | `~/.codex/skills/video-ai-agent` | `SKILL.md`, `scripts/`, `references/` |
| Claude Code skill | `~/.claude/skills/video-ai-agent` | same folder |
| Generic agent skill | `~/.agents/skills/video-ai-agent` | same folder |

### Step 1: Get the repository

Prefer cloning into the dedicated install directory:

```bash
git clone https://github.com/YaJee666/video_ai_agent_skill.git ~/.video-ai-agent-skill/repo
```

If it already exists:

```bash
cd ~/.video-ai-agent-skill/repo
git pull --ff-only
```

Windows PowerShell:

```powershell
git clone https://github.com/YaJee666/video_ai_agent_skill.git "$env:USERPROFILE\.video-ai-agent-skill\repo"
```

If it already exists:

```powershell
Set-Location "$env:USERPROFILE\.video-ai-agent-skill\repo"
git pull --ff-only
```

### Step 2: Install the skill

From the repository root:

```bash
python scripts/install_skill.py --target auto
```

Windows PowerShell:

```powershell
python .\scripts\install_skill.py --target auto
```

`--target auto` installs into existing known skill roots. If none exist, it creates the Codex skill root by default:

```text
~/.codex/skills/video-ai-agent
```

Install to a specific agent:

```bash
python scripts/install_skill.py --target codex
python scripts/install_skill.py --target claude
python scripts/install_skill.py --target agents
python scripts/install_skill.py --target all
```

Preview without writing files:

```bash
python scripts/install_skill.py --target auto --dry-run
```

### Step 3: Configure the API key

Ask the user to create an API key in the Video AI Agent console with this minimum scope:

```text
chat:write
```

Then ask them to write it into the installed skill `.env` file.

PowerShell:

```powershell
Copy-Item "$env:USERPROFILE\.codex\skills\video-ai-agent\.env.example" "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
notepad "$env:USERPROFILE\.codex\skills\video-ai-agent\.env"
```

Bash:

```bash
cp ~/.codex/skills/video-ai-agent/.env.example ~/.codex/skills/video-ai-agent/.env
${EDITOR:-vi} ~/.codex/skills/video-ai-agent/.env
```

Optional settings:

```text
VIDEO_AI_AGENT_ENDPOINT=http://www.talkaibot.com/openapi/v1/chat/completions
VIDEO_AI_AGENT_TIMEOUT_MS=600000
VIDEO_AI_AGENT_PROJECT_ID=
VIDEO_AI_AGENT_SESSION_ID=
```

The client script loads `.env` from the current directory, the installed skill root, or the repository root. Precedence is: CLI args > shell environment > `.env`.

### Step 4: Verify

Run:

```bash
python ~/.codex/skills/video-ai-agent/scripts/video_ai_agent_chat.py --help
```

For Claude Code:

```bash
python ~/.claude/skills/video-ai-agent/scripts/video_ai_agent_chat.py --help
```

If `VIDEO_AI_AGENT_API_KEY` is configured in `.env`, run a smoke test:

```bash
python ~/.codex/skills/video-ai-agent/scripts/video_ai_agent_chat.py \
  --message "请用一句话说明你能做什么"
```

### Step 5: Tell the user how to use it

After installation, tell the user to start a new Codex / Claude Code session so the skill metadata is discovered.

Example prompt:

```text
Use $video-ai-agent to summarize this video in Chinese: https://www.youtube.com/watch?v=...
```

For future updates, give the user this one-liner:

```text
帮我更新 Video AI Agent Skill：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

## Quick Reference

| Command | What it does |
| --- | --- |
| `python scripts/install_skill.py --target auto` | Install into detected skill roots |
| `python scripts/install_skill.py --target codex` | Install into `~/.codex/skills/video-ai-agent` |
| `python scripts/install_skill.py --target claude` | Install into `~/.claude/skills/video-ai-agent` |
| `python scripts/install_skill.py --target all` | Install into Codex, Claude Code, and generic `.agents` roots |
| `python scripts/install_skill.py --target auto --dry-run` | Preview install actions |
| `python scripts/install_skill.py --target auto --update` | Pull latest code and resync installed skills |
