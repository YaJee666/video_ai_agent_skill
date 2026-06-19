#!/usr/bin/env python3
"""Install the Video AI Agent folder-based skill into common agent skill roots."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from pathlib import Path


SKILL_NAME = "video-ai-agent"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def skill_source() -> Path:
    source = repo_root() / SKILL_NAME
    if not (source / "SKILL.md").is_file():
        raise SystemExit(f"Skill source not found: {source}")
    return source


def home() -> Path:
    return Path.home()


def known_roots() -> dict[str, Path]:
    roots = {
        "codex": home() / ".codex" / "skills",
        "claude": home() / ".claude" / "skills",
        "agents": home() / ".agents" / "skills",
    }
    openclaw_home = os.environ.get("OPENCLAW_HOME", "").strip()
    if openclaw_home:
        roots["openclaw"] = Path(openclaw_home).expanduser() / ".openclaw" / "skills"
    else:
        roots["openclaw"] = home() / ".openclaw" / "skills"
    return roots


def selected_roots(target: str) -> list[tuple[str, Path]]:
    roots = known_roots()
    if target == "all":
        return [(name, roots[name]) for name in ("codex", "claude", "agents", "openclaw")]
    if target == "auto":
        existing = [(name, path) for name, path in roots.items() if path.is_dir()]
        if existing:
            return existing
        return [("codex", roots["codex"])]
    if target not in roots:
        raise SystemExit(f"Unsupported target: {target}")
    return [(target, roots[target])]


def remove_existing(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def copy_skill(source: Path, destination: Path, *, dry_run: bool) -> None:
    if dry_run:
        action = "replace" if destination.exists() else "create"
        print(f"[dry-run] Would {action}: {destination}")
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        remove_existing(destination)
    shutil.copytree(source, destination)
    print(f"Installed: {destination}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Video AI Agent skill into agent skill directories.")
    parser.add_argument(
        "--target",
        choices=["auto", "codex", "claude", "agents", "openclaw", "all"],
        default="auto",
        help="Install target. Default: auto.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview install actions without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = skill_source()
    targets = selected_roots(args.target)

    print("Video AI Agent Skill Installer")
    print("=" * 36)
    print(f"Source: {source}")
    for name, root in targets:
        destination = root / SKILL_NAME
        copy_skill(source, destination, dry_run=args.dry_run)

    if not args.dry_run:
        print()
        print("Next steps:")
        print("1. Set VIDEO_AI_AGENT_API_KEY in the shell that runs your agent.")
        print("2. Start a new Codex / Claude Code session so the skill is discovered.")
        print('3. Try: Use $video-ai-agent to summarize this video URL.')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
