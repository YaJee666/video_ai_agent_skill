# Video AI Agent Skill Update Guide

## For Humans

Copy this to your agent:

```text
Update Video AI Agent Skill: https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

The update flow preserves the installed `.env` file, so your API key does not need to be entered again.

## Important

Run the update command from a cloned repository checkout, not from an installed skill directory such as `~/.codex/skills/video-ai-agent`.

The installed skill folder only contains the client script and docs. It does not contain `scripts/install_skill.py`.

If you do not already have a checkout, clone one first:

```powershell
git clone https://github.com/YaJee666/video_ai_agent_skill.git "$env:USERPROFILE\.video-ai-agent-skill\repo"
Set-Location "$env:USERPROFILE\.video-ai-agent-skill\repo"
```

## Recommended update flow

Preview the update:

```powershell
python .\scripts\install_skill.py --target auto --update --dry-run
```

Apply the update:

```powershell
python .\scripts\install_skill.py --target auto --update
```

Update every known skill root:

```powershell
python .\scripts\install_skill.py --target all --update
```

## Notes

- `.env` files are preserved during resync.
- `--target auto` updates any detected Codex / Claude Code / `.agents` / OpenClaw skill roots, or creates the Codex root when none exist.
- Start a new Codex / Claude Code session after the update if the running session does not pick up the new skill metadata.
