#!/usr/bin/env python3
"""Small dependency-free client for Video AI Agent OpenAPI."""

from __future__ import annotations

import argparse
import http.client
import json
import os
import socket
import ssl
import sys
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_ENDPOINT = "https://www.talkaibot.com/openapi/v1/chat/completions"
DEFAULT_MODE = "jobs"
DEFAULT_JOB_WORKFLOW_PRESET = "video.qa.basic"
DEFAULT_POLL_INTERVAL_MS = 3000
DEFAULT_TIMEOUT_MS = 600000
SKILL_ID = "video-ai-agent"
DOTENV_VALUES: dict[str, str] = {}
DOTENV_SOURCES: dict[str, str] = {}


def configure_utf8_output() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="replace")


def _decode_env_value(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped[0] == stripped[-1] and stripped[0] in {"'", '"'}:
        return stripped[1:-1]
    return stripped


def load_dotenv_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}
    values: dict[str, str] = {}
    for raw_line in lines:
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.lstrip("\ufeff").strip()
        if key.startswith("export "):
            key = key[len("export "):].strip()
        if not key:
            continue
        values[key] = _decode_env_value(value)
    return values


def discover_dotenv_paths(script_path: Path, cwd: Path) -> list[Path]:
    skill_root = script_path.parents[1]
    paths = [
        script_path.parents[2] / ".env",
        skill_root / ".env",
    ]

    cwd_chain = [cwd, *cwd.parents]
    for directory in reversed(cwd_chain):
        paths.append(directory / ".env")

    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for path in paths:
        resolved = path.expanduser().resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_paths.append(resolved)
    return unique_paths


def load_dotenv() -> None:
    global DOTENV_VALUES, DOTENV_SOURCES
    DOTENV_VALUES = {}
    DOTENV_SOURCES = {}
    script_path = Path(__file__).resolve()
    for candidate in discover_dotenv_paths(script_path, Path.cwd()):
        values = load_dotenv_file(candidate)
        DOTENV_VALUES.update(values)
        for key in values:
            DOTENV_SOURCES[key] = str(candidate)


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def resolve_config_value(cli_value: str | None, env_name: str, default: str = "") -> str:
    cli = str(cli_value or "").strip()
    if cli:
        return cli
    env_value = env(env_name)
    if env_value:
        return env_value
    dotenv_value = DOTENV_VALUES.get(env_name, "").strip()
    if dotenv_value:
        return dotenv_value
    return str(default).strip()


def resolve_config_source(cli_value: str | None, env_name: str, default: str = "") -> str:
    if str(cli_value or "").strip():
        return "cli"
    if env(env_name):
        return "environment"
    if DOTENV_VALUES.get(env_name, "").strip():
        source = DOTENV_SOURCES.get(env_name, ".env")
        return f".env ({source})"
    if str(default).strip():
        return "default"
    return "unset"


def resolve_timeout_ms(cli_value: int | None) -> int:
    raw_value = resolve_config_value(
        str(cli_value) if cli_value is not None else "",
        "VIDEO_AI_AGENT_TIMEOUT_MS",
        str(DEFAULT_TIMEOUT_MS),
    )
    try:
        return int(raw_value)
    except ValueError as exc:
        raise SystemExit(f"VIDEO_AI_AGENT_TIMEOUT_MS must be an integer: {raw_value}") from exc


def apply_config_precedence(args: argparse.Namespace) -> argparse.Namespace:
    args.config_sources = {
        "VIDEO_AI_AGENT_API_KEY": resolve_config_source(args.api_key, "VIDEO_AI_AGENT_API_KEY"),
        "VIDEO_AI_AGENT_ENDPOINT": resolve_config_source(args.endpoint, "VIDEO_AI_AGENT_ENDPOINT", DEFAULT_ENDPOINT),
        "VIDEO_AI_AGENT_MODE": resolve_config_source(args.mode, "VIDEO_AI_AGENT_MODE", DEFAULT_MODE),
        "VIDEO_AI_AGENT_TIMEOUT_MS": resolve_config_source(
            str(args.timeout_ms) if args.timeout_ms is not None else "",
            "VIDEO_AI_AGENT_TIMEOUT_MS",
            str(DEFAULT_TIMEOUT_MS),
        ),
        "VIDEO_AI_AGENT_PROJECT_ID": resolve_config_source(args.project_id, "VIDEO_AI_AGENT_PROJECT_ID"),
        "VIDEO_AI_AGENT_SESSION_ID": resolve_config_source(args.session_id, "VIDEO_AI_AGENT_SESSION_ID"),
    }
    args.api_key = resolve_config_value(args.api_key, "VIDEO_AI_AGENT_API_KEY")
    args.endpoint = resolve_config_value(args.endpoint, "VIDEO_AI_AGENT_ENDPOINT", DEFAULT_ENDPOINT)
    args.mode = resolve_config_value(args.mode, "VIDEO_AI_AGENT_MODE", DEFAULT_MODE).lower()
    if args.mode not in {"jobs", "sync"}:
        raise SystemExit("VIDEO_AI_AGENT_MODE must be jobs or sync")
    args.timeout_ms = resolve_timeout_ms(args.timeout_ms)
    args.project_id = resolve_config_value(args.project_id, "VIDEO_AI_AGENT_PROJECT_ID")
    args.session_id = resolve_config_value(args.session_id, "VIDEO_AI_AGENT_SESSION_ID")
    return args


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call Video AI Agent OpenAPI.")
    parser.add_argument("--api-key", default="", help="Video AI Agent API key.")
    parser.add_argument(
        "--endpoint",
        default="",
        help=f"OpenAPI endpoint. Default: {DEFAULT_ENDPOINT}",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=None,
        help=f"Request timeout in milliseconds. Default: {DEFAULT_TIMEOUT_MS}",
    )
    parser.add_argument(
        "--mode",
        choices=["jobs", "sync"],
        default="",
        help="Use jobs for long video tasks, or sync for short chat completions. Default: jobs.",
    )
    parser.add_argument(
        "--workflow-preset",
        default=DEFAULT_JOB_WORKFLOW_PRESET,
        help=f"Workflow preset for jobs mode. Default: {DEFAULT_JOB_WORKFLOW_PRESET}",
    )
    parser.add_argument(
        "--poll-interval-ms",
        type=int,
        default=DEFAULT_POLL_INTERVAL_MS,
        help=f"Jobs polling interval in milliseconds. Default: {DEFAULT_POLL_INTERVAL_MS}",
    )
    parser.add_argument("--project-id", default="", help="Optional project id.")
    parser.add_argument("--session-id", default="", help="Optional session id.")
    parser.add_argument("--thread-id", default="", help="Optional thread id.")
    parser.add_argument("--request-id", default="", help="Optional request id.")
    parser.add_argument("--title", default="", help="Optional chat title.")
    parser.add_argument("--metadata", default="", help="Optional JSON object merged into request metadata.")
    parser.add_argument(
        "--debug-config",
        action="store_true",
        help="Print resolved configuration sources with secrets masked, then exit.",
    )
    parser.add_argument(
        "--dry-run-config",
        action="store_true",
        help="Alias for --debug-config.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full JSON response.")
    parser.add_argument("--message", default="", help="User instruction. If omitted, stdin is used.")
    return parser.parse_args()


def normalize_metadata(raw: str) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--metadata must be valid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise SystemExit("--metadata must be a JSON object")
    return value


def compact(value: dict[str, Any]) -> dict[str, Any]:
    return {
        key: item
        for key, item in value.items()
        if item is not None and (not isinstance(item, str) or item.strip())
    }


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    message = args.message.strip() or sys.stdin.read().strip()
    if not message:
        raise SystemExit("message is required. Pass --message or pipe text on stdin.")

    request_id = args.request_id.strip() or f"req_agent_skill_{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}"
    metadata = normalize_metadata(args.metadata)
    metadata.update(
        {
            "request_source": "agent_skill",
            "skill_id": SKILL_ID,
            "client_request_id": request_id,
            "client_timestamp_ms": int(time.time() * 1000),
        }
    )

    return compact(
        {
            "requestId": request_id,
            "projectId": args.project_id.strip(),
            "sessionId": args.session_id.strip(),
            "threadId": args.thread_id.strip(),
            "title": args.title.strip(),
            "messageContent": message,
            "metadata": metadata,
        }
    )


def mask_secret(value: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        return "<missing>"
    if len(normalized) <= 10:
        return normalized[:2] + "***"
    return normalized[:7] + "..." + normalized[-4:]


def render_config_debug(args: argparse.Namespace) -> str:
    sources = getattr(args, "config_sources", {})
    values = {
        "VIDEO_AI_AGENT_API_KEY": (
            mask_secret(args.api_key),
            sources.get("VIDEO_AI_AGENT_API_KEY", "unknown"),
        ),
        "VIDEO_AI_AGENT_ENDPOINT": (
            args.endpoint or "<missing>",
            sources.get("VIDEO_AI_AGENT_ENDPOINT", "unknown"),
        ),
        "VIDEO_AI_AGENT_MODE": (
            args.mode or "<missing>",
            sources.get("VIDEO_AI_AGENT_MODE", "unknown"),
        ),
        "VIDEO_AI_AGENT_TIMEOUT_MS": (
            str(args.timeout_ms),
            sources.get("VIDEO_AI_AGENT_TIMEOUT_MS", "unknown"),
        ),
        "VIDEO_AI_AGENT_PROJECT_ID": (
            args.project_id or "<empty>",
            sources.get("VIDEO_AI_AGENT_PROJECT_ID", "unknown"),
        ),
        "VIDEO_AI_AGENT_SESSION_ID": (
            args.session_id or "<empty>",
            sources.get("VIDEO_AI_AGENT_SESSION_ID", "unknown"),
        ),
    }
    lines = ["Video AI Agent config:"]
    for name, (value, source) in values.items():
        lines.append(f"{name}={value} source={source}")
    return "\n".join(lines)


def request_debug(payload: dict[str, Any], endpoint: str, timeout_ms: int) -> str:
    request_id = str(payload.get("requestId") or "").strip()
    suffix = []
    if request_id:
        suffix.append(f"request_id={request_id}")
    if endpoint:
        suffix.append(f"endpoint={endpoint}")
    suffix.append(f"timeout_ms={timeout_ms}")
    return " ".join(suffix)


def derive_endpoint(endpoint: str, suffix: str) -> str:
    normalized = endpoint.rstrip("/")
    marker = "/openapi/v1/"
    if marker in normalized:
        base = normalized.split(marker, 1)[0] + marker.rstrip("/")
    else:
        base = normalized
    return base.rstrip("/") + "/" + suffix.lstrip("/")


def post_json(endpoint: str, api_key: str, payload: dict[str, Any], timeout_ms: int) -> dict[str, Any]:
    if not api_key:
        raise SystemExit("VIDEO_AI_AGENT_API_KEY is required, or pass --api-key.")
    if timeout_ms < 1000:
        raise SystemExit("--timeout-ms must be at least 1000.")

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Content-Type": "application/json",
            "X-API-Key": api_key,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_ms / 1000) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw[:1000] if raw else str(exc.reason or "Service Unavailable")
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent HTTP {exc.code}: {message}\n[video_ai_agent] {detail}") from exc
    except urllib.error.URLError as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent request failed: {exc.reason}\n[video_ai_agent] {detail}") from exc
    except http.client.RemoteDisconnected as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(
            "Video AI Agent request failed: remote server closed the connection without a response.\n"
            f"[video_ai_agent] {detail}"
        ) from exc
    except (ConnectionResetError, ssl.SSLError, socket.timeout, OSError) as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent transport failed: {exc}\n[video_ai_agent] {detail}") from exc
    except TimeoutError as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent request timed out after {timeout_ms}ms\n[video_ai_agent] {detail}") from exc

    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Video AI Agent returned non-JSON content: {raw[:1000]}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Video AI Agent returned an unexpected JSON value")
    return data


def get_json(endpoint: str, api_key: str, payload: dict[str, Any], timeout_ms: int) -> dict[str, Any]:
    if not api_key:
        raise SystemExit("VIDEO_AI_AGENT_API_KEY is required, or pass --api-key.")
    request = urllib.request.Request(
        endpoint,
        headers={"X-API-Key": api_key},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_ms / 1000) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        message = raw[:1000] if raw else str(exc.reason or "Service Unavailable")
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent HTTP {exc.code}: {message}\n[video_ai_agent] {detail}") from exc
    except urllib.error.URLError as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent request failed: {exc.reason}\n[video_ai_agent] {detail}") from exc
    except http.client.RemoteDisconnected as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(
            "Video AI Agent request failed: remote server closed the connection without a response.\n"
            f"[video_ai_agent] {detail}"
        ) from exc
    except (ConnectionResetError, ssl.SSLError, socket.timeout, OSError) as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent transport failed: {exc}\n[video_ai_agent] {detail}") from exc
    except TimeoutError as exc:
        detail = request_debug(payload, endpoint, timeout_ms)
        raise SystemExit(f"Video AI Agent request timed out after {timeout_ms}ms\n[video_ai_agent] {detail}") from exc

    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Video AI Agent returned non-JSON content: {raw[:1000]}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Video AI Agent returned an unexpected JSON value")
    return data


def build_job_payload(args: argparse.Namespace, chat_payload: dict[str, Any]) -> dict[str, Any]:
    metadata = dict(chat_payload.get("metadata") or {})
    metadata["request_source"] = "agent_skill_jobs"
    return compact(
        {
            "requestId": chat_payload.get("requestId"),
            "projectId": chat_payload.get("projectId"),
            "workflowPreset": args.workflow_preset.strip() or DEFAULT_JOB_WORKFLOW_PRESET,
            "jobType": "video_ai_agent_skill",
            "input": {
                "messageContent": chat_payload.get("messageContent", ""),
                "sessionId": chat_payload.get("sessionId", ""),
                "threadId": chat_payload.get("threadId", ""),
                "title": chat_payload.get("title", ""),
                "metadata": metadata,
            },
            "runtimeContext": {
                "session_id": chat_payload.get("sessionId", ""),
                "thread_id": chat_payload.get("threadId", ""),
                "request_id": chat_payload.get("requestId", ""),
            },
            "metadata": metadata,
        }
    )


def is_terminal_job(status: str) -> bool:
    return status.strip().lower() in {"succeeded", "failed", "canceled"}


def run_job(endpoint: str, api_key: str, payload: dict[str, Any], timeout_ms: int, poll_interval_ms: int) -> dict[str, Any]:
    job_endpoint = derive_endpoint(endpoint, "jobs")
    job = post_json(job_endpoint, api_key, payload, timeout_ms)
    job_id = str(job.get("jobId") or job.get("job_id") or "").strip()
    if not job_id:
        raise SystemExit("Video AI Agent jobs response did not include jobId")

    started = time.monotonic()
    interval = max(poll_interval_ms, 250) / 1000
    status_endpoint = derive_endpoint(endpoint, f"jobs/{job_id}")
    current = job
    while not is_terminal_job(str(current.get("status") or "")):
        if (time.monotonic() - started) * 1000 >= timeout_ms:
            detail = request_debug(payload, status_endpoint, timeout_ms)
            raise SystemExit(f"Video AI Agent job timed out waiting for {job_id}\n[video_ai_agent] {detail}")
        time.sleep(interval)
        current = get_json(status_endpoint, api_key, payload, timeout_ms)
    return current


def render_text(data: dict[str, Any]) -> str:
    output_payload = data.get("output") if isinstance(data.get("output"), dict) else {}
    response = str(data.get("response") or output_payload.get("response") or "").strip()
    error_payload = data.get("error") if isinstance(data.get("error"), dict) else {}
    error = str(
        data.get("errorMessage")
        or data.get("message")
        or error_payload.get("message")
        or error_payload.get("error_message")
        or ""
    ).strip()
    lines = [response or error or json.dumps(data, ensure_ascii=False)]

    debug = compact(
        {
            "job_id": data.get("jobId") or data.get("job_id"),
            "request_id": data.get("requestId") or data.get("request_id"),
            "session_id": data.get("sessionId") or data.get("session_id"),
            "thread_id": data.get("threadId") or data.get("thread_id"),
            "status": data.get("status"),
            "status_code": data.get("statusCode") or data.get("status_code"),
            "error_code": data.get("errorCode") or data.get("error_code"),
            "error_type": data.get("errorType") or data.get("error_type"),
        }
    )
    if debug:
        lines.extend(["", "[video_ai_agent]", json.dumps(debug, ensure_ascii=False)])
    return "\n".join(lines)


def main() -> int:
    configure_utf8_output()
    load_dotenv()
    args = apply_config_precedence(parse_args())
    if args.debug_config or args.dry_run_config:
        print(render_config_debug(args))
        return 0
    payload = build_payload(args)
    if args.mode == "jobs":
        data = run_job(
            args.endpoint.strip(),
            args.api_key.strip(),
            build_job_payload(args, payload),
            args.timeout_ms,
            args.poll_interval_ms,
        )
    else:
        data = post_json(args.endpoint.strip(), args.api_key.strip(), payload, args.timeout_ms)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(render_text(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
