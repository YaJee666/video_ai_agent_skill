#!/usr/bin/env python3
"""Small dependency-free client for Video AI Agent OpenAPI chat."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import uuid
import urllib.error
import urllib.request
from typing import Any


DEFAULT_ENDPOINT = "http://www.talkaibot.com/openapi/v1/chat/completions"
DEFAULT_TIMEOUT_MS = 600000
SKILL_ID = "video-ai-agent"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Call Video AI Agent OpenAPI chat completions.")
    parser.add_argument("--api-key", default=env("VIDEO_AI_AGENT_API_KEY"), help="Video AI Agent API key.")
    parser.add_argument(
        "--endpoint",
        default=env("VIDEO_AI_AGENT_ENDPOINT", DEFAULT_ENDPOINT),
        help=f"OpenAPI endpoint. Default: {DEFAULT_ENDPOINT}",
    )
    parser.add_argument(
        "--timeout-ms",
        type=int,
        default=int(env("VIDEO_AI_AGENT_TIMEOUT_MS", str(DEFAULT_TIMEOUT_MS)) or DEFAULT_TIMEOUT_MS),
        help=f"Request timeout in milliseconds. Default: {DEFAULT_TIMEOUT_MS}",
    )
    parser.add_argument("--project-id", default=env("VIDEO_AI_AGENT_PROJECT_ID"), help="Optional project id.")
    parser.add_argument("--session-id", default=env("VIDEO_AI_AGENT_SESSION_ID"), help="Optional session id.")
    parser.add_argument("--thread-id", default="", help="Optional thread id.")
    parser.add_argument("--request-id", default="", help="Optional request id.")
    parser.add_argument("--title", default="", help="Optional chat title.")
    parser.add_argument("--metadata", default="", help="Optional JSON object merged into request metadata.")
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
        message = raw[:1000] if raw else exc.reason
        raise SystemExit(f"Video AI Agent HTTP {exc.code}: {message}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Video AI Agent request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise SystemExit(f"Video AI Agent request timed out after {timeout_ms}ms") from exc

    try:
        data = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Video AI Agent returned non-JSON content: {raw[:1000]}") from exc
    if not isinstance(data, dict):
        raise SystemExit("Video AI Agent returned an unexpected JSON value")
    return data


def render_text(data: dict[str, Any]) -> str:
    response = str(data.get("response") or "").strip()
    error = str(data.get("errorMessage") or data.get("message") or "").strip()
    lines = [response or error or json.dumps(data, ensure_ascii=False)]

    debug = compact(
        {
            "request_id": data.get("requestId") or data.get("request_id"),
            "session_id": data.get("sessionId") or data.get("session_id"),
            "thread_id": data.get("threadId") or data.get("thread_id"),
            "status_code": data.get("statusCode") or data.get("status_code"),
            "error_code": data.get("errorCode") or data.get("error_code"),
            "error_type": data.get("errorType") or data.get("error_type"),
        }
    )
    if debug:
        lines.extend(["", "[video_ai_agent]", json.dumps(debug, ensure_ascii=False)])
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    payload = build_payload(args)
    data = post_json(args.endpoint.strip(), args.api_key.strip(), payload, args.timeout_ms)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(render_text(data))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
