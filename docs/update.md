# Video AI Agent Skill — Update Guide

## For Humans

Copy this to your AI agent:

```text
帮我更新 Video AI Agent Skill：https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

Or in English:

```text
Update Video AI Agent Skill: https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

The update keeps your installed `.env` file, so your API key does not need to be re-entered.

---

## For AI Agents

### Goal

Update the local Video AI Agent Skill checkout and resync the `video-ai-agent` skill folder into Codex, Claude Code, OpenClaw, or generic agent skill directories.

This project is a folder-based skill, not a system package. Updating means:

1. Pull the latest repository code.
2. Re-copy the `video-ai-agent` skill folder into installed skill roots.
3. Preserve each installed skill's `.env` file.
4. Verify the client script still runs.

### Boundaries

- Do not delete or rewrite `.env`.
- Do not ask the user to paste their API key again unless `.env` is missing.
- Do not install system packages.
- Do not modify unrelated projects.
- Do not force-push, reset, or discard local changes in the checkout.
- If `git pull --ff-only` fails because the user has local edits, stop and report the conflict.

### Step 1: Find or create the checkout

Preferred checkout:

```text
~/.video-ai-agent-skill/repo
```

If it exists:

```bash
cd ~/.video-ai-agent-skill/repo
```

Windows PowerShell:

```powershell
Set-Location "$env:USERPROFILE\.video-ai-agent-skill\repo"
```

If it does not exist, clone it:

```bash
git clone https://github.com/YaJee666/video_ai_agent_skill.git ~/.video-ai-agent-skill/repo
cd ~/.video-ai-agent-skill/repo
```

Windows PowerShell:

```powershell
git clone https://github.com/YaJee666/video_ai_agent_skill.git "$env:USERPROFILE\.video-ai-agent-skill\repo"
Set-Location "$env:USERPROFILE\.video-ai-agent-skill\repo"
```

### Step 2: Preview the update

```bash
python scripts/install_skill.py --target auto --update --dry-run
```

This shows the `git pull --ff-only` step and which installed skill directories would be replaced. Existing `.env` files are preserved.

### Step 3: Update and resync skills

```bash
python scripts/install_skill.py --target auto --update
```

Use `--target all` if the user wants every known skill root updated:

```bash
python scripts/install_skill.py --target all --update
```

The script:

- runs `git pull --ff-only` from the repository root
- copies the latest `video-ai-agent` folder into target skill roots
- restores each target's `.env` after copying

### Step 4: Verify

Codex:

```bash
python ~/.codex/skills/video-ai-agent/scripts/video_ai_agent_chat.py --help
```

Claude Code:

```bash
python ~/.claude/skills/video-ai-agent/scripts/video_ai_agent_chat.py --help
```

If `.env` exists and contains `VIDEO_AI_AGENT_API_KEY`, run a smoke test:

```bash
python ~/.codex/skills/video-ai-agent/scripts/video_ai_agent_chat.py \
  --message "请用一句话说明你能做什么"
```

### Step 5: Report to the user

Tell the user:

1. Whether the checkout updated cleanly.
2. Which skill directories were resynced.
3. Whether `.env` was preserved.
4. Whether the `--help` or smoke test passed.
5. That they should start a new Codex / Claude Code session if the running session does not pick up the new skill metadata.

## Quick Reference

| Command | What it does |
| --- | --- |
| `python scripts/install_skill.py --target auto --update` | Pull latest code and update detected skill installs |
| `python scripts/install_skill.py --target all --update` | Pull latest code and update all known skill roots |
| `python scripts/install_skill.py --target auto --update --dry-run` | Preview update actions |
