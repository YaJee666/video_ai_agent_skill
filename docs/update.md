# Video AI Agent Skill Update Guide

## For Humans

Copy this to your agent:

```text
Update Video AI Agent Skill: https://raw.githubusercontent.com/YaJee666/video_ai_agent_skill/main/docs/update.md
```

The update flow preserves the installed `.env` file, so your API key does not need to be entered again.

## What the updater does

`python scripts/install_skill.py --target auto --update` now works from:

- the repo checkout
- an installed Codex / Claude Code skill copy
- a cached source checkout under `~/.video-ai-agent-skill/repo`

If no source checkout exists yet, the script bootstraps one from:

```text
https://github.com/YaJee666/video_ai_agent_skill.git
```

You can override the source checkout with:

```powershell
python scripts/install_skill.py --source-repo "C:\path\to\video_ai_agent_skill" --target auto --update
```

## Recommended update flow

Preview:

```powershell
python scripts/install_skill.py --target auto --update --dry-run
```

Apply:

```powershell
python scripts/install_skill.py --target auto --update
```

Update every known skill root:

```powershell
python scripts/install_skill.py --target all --update
```

## Notes

- `.env` files are preserved during resync.
- Start a new Codex / Claude Code session after the update if the running session does not pick up the new skill metadata.
- Use `--source-repo` when you want to point at a specific local checkout or mirror.
