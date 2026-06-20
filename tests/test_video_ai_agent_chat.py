import argparse
import http.client
import importlib.util
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "video-ai-agent"
    / "scripts"
    / "video_ai_agent_chat.py"
)


def load_client_module():
    spec = importlib.util.spec_from_file_location("video_ai_agent_chat", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class VideoAiAgentChatClientTest(unittest.TestCase):
    def setUp(self):
        self.client = load_client_module()

    def tearDown(self):
        self.client.DOTENV_VALUES = {}
        self.client.DOTENV_SOURCES = {}

    def test_default_endpoint_uses_https(self):
        self.assertEqual(
            "https://www.talkaibot.com/openapi/v1/chat/completions",
            self.client.DEFAULT_ENDPOINT,
        )

    def test_config_precedence_prefers_cli_then_environment_then_dotenv(self):
        self.client.DOTENV_VALUES = {
            "VIDEO_AI_AGENT_API_KEY": "vag_sk_from_dotenv",
            "VIDEO_AI_AGENT_ENDPOINT": "https://dotenv.example/openapi",
            "VIDEO_AI_AGENT_TIMEOUT_MS": "1111",
        }
        self.client.DOTENV_SOURCES = {
            "VIDEO_AI_AGENT_API_KEY": "skill/.env",
            "VIDEO_AI_AGENT_ENDPOINT": "skill/.env",
            "VIDEO_AI_AGENT_TIMEOUT_MS": "skill/.env",
        }
        args = argparse.Namespace(
            api_key="",
            endpoint="https://cli.example/openapi",
            mode="",
            timeout_ms=None,
            project_id="",
            session_id="",
        )

        with mock.patch.dict(
            self.client.os.environ,
            {
                "VIDEO_AI_AGENT_API_KEY": "vag_sk_from_env",
                "VIDEO_AI_AGENT_TIMEOUT_MS": "2222",
            },
            clear=False,
        ):
            resolved = self.client.apply_config_precedence(args)

        self.assertEqual("vag_sk_from_env", resolved.api_key)
        self.assertEqual("https://cli.example/openapi", resolved.endpoint)
        self.assertEqual("jobs", resolved.mode)
        self.assertEqual(2222, resolved.timeout_ms)
        self.assertEqual("environment", resolved.config_sources["VIDEO_AI_AGENT_API_KEY"])
        self.assertEqual("cli", resolved.config_sources["VIDEO_AI_AGENT_ENDPOINT"])
        self.assertEqual("default", resolved.config_sources["VIDEO_AI_AGENT_MODE"])
        self.assertEqual("environment", resolved.config_sources["VIDEO_AI_AGENT_TIMEOUT_MS"])

    def test_debug_config_masks_api_key(self):
        args = argparse.Namespace(
            api_key="vag_sk_live_abcdefghijklmnopqrstuvwxyz",
            endpoint="https://www.talkaibot.com/openapi/v1/chat/completions",
            mode="jobs",
            timeout_ms=600000,
            project_id="",
            session_id="",
            config_sources={
                "VIDEO_AI_AGENT_API_KEY": ".env (skill/.env)",
                "VIDEO_AI_AGENT_ENDPOINT": "default",
                "VIDEO_AI_AGENT_MODE": "default",
                "VIDEO_AI_AGENT_TIMEOUT_MS": "default",
                "VIDEO_AI_AGENT_PROJECT_ID": "unset",
                "VIDEO_AI_AGENT_SESSION_ID": "unset",
            },
        )

        rendered = self.client.render_config_debug(args)

        self.assertIn("VIDEO_AI_AGENT_API_KEY=vag_sk_...wxyz", rendered)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", rendered)

    def test_build_payload_extracts_youtube_video_source(self):
        args = argparse.Namespace(
            api_key="",
            endpoint="",
            mode="jobs",
            timeout_ms=None,
            project_id="",
            session_id="",
            request_id="req_test_42",
            title="",
            message="Please summarize this video: https://www.youtube.com/watch?v=N9iLEhievoM",
            metadata="",
        )

        payload = self.client.build_payload(args)

        self.assertEqual("https://www.youtube.com/watch?v=N9iLEhievoM", payload["source_url"])
        self.assertEqual("https://www.youtube.com/watch?v=N9iLEhievoM", payload["video_url"])
        self.assertEqual("N9iLEhievoM", payload["video_id"])
        self.assertEqual("youtube", payload["platform"])
        self.assertEqual("https://www.youtube.com/watch?v=N9iLEhievoM", payload["context"]["sourceUrl"])
        self.assertEqual("N9iLEhievoM", payload["context"]["videoId"])
        self.assertEqual("youtube", payload["metadata"]["platform"])
        self.assertEqual("N9iLEhievoM", payload["metadata"]["video_id"])

    def test_remote_disconnect_error_includes_request_context(self):
        payload = {"requestId": "req_test_1", "messageContent": "hello"}

        with mock.patch.object(
            self.client.urllib.request,
            "urlopen",
            side_effect=http.client.RemoteDisconnected("closed"),
        ):
            with self.assertRaises(SystemExit) as raised:
                self.client.post_json(
                    "https://www.talkaibot.com/openapi/v1/chat/completions",
                    "vag_sk_test",
                    payload,
                    1000,
                )

        message = str(raised.exception)
        self.assertIn("remote server closed the connection", message)
        self.assertIn("request_id=req_test_1", message)
        self.assertIn("timeout_ms=1000", message)

    def test_derive_endpoint_reuses_openapi_base(self):
        self.assertEqual(
            "https://www.talkaibot.com/openapi/v1/jobs",
            self.client.derive_endpoint(
                "https://www.talkaibot.com/openapi/v1/chat/completions",
                "jobs",
            ),
        )

    def test_build_job_payload_wraps_chat_request_for_runtime_jobs(self):
        args = argparse.Namespace(workflow_preset="video.qa.basic")
        chat_payload = {
            "requestId": "req-test",
            "projectId": "project-1",
            "sessionId": "session-1",
            "threadId": "thread-1",
            "title": "Video QA",
            "messageContent": "summarize this video",
            "metadata": {"client_request_id": "req-test", "request_source": "agent_skill"},
        }

        payload = self.client.build_job_payload(args, chat_payload)

        self.assertEqual("req-test", payload["requestId"])
        self.assertEqual("project-1", payload["projectId"])
        self.assertEqual("video.qa.basic", payload["workflowPreset"])
        self.assertEqual("summarize this video", payload["input"]["messageContent"])
        self.assertEqual("agent_skill_jobs", payload["metadata"]["request_source"])
        self.assertEqual("req-test", payload["runtimeContext"]["request_id"])

    def test_run_job_polls_until_terminal_status(self):
        payload = {"requestId": "req-test"}
        responses = [
            self._json_response({"jobId": "job-1", "status": "queued", "requestId": "req-test"}),
            self._json_response({"jobId": "job-1", "status": "running", "requestId": "req-test"}),
            self._json_response({
                "jobId": "job-1",
                "status": "succeeded",
                "requestId": "req-test",
                "output": {"response": "done"},
            }),
        ]

        with mock.patch.object(self.client.urllib.request, "urlopen", side_effect=responses):
            with mock.patch.object(self.client.time, "sleep", return_value=None):
                result = self.client.run_job(
                    "https://www.talkaibot.com/openapi/v1/chat/completions",
                    "vag_sk_test",
                    payload,
                    60000,
                    1,
                )

        self.assertEqual("succeeded", result["status"])
        self.assertEqual("done", result["output"]["response"])

    def _json_response(self, payload):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.__exit__.return_value = None
        response.read.return_value = self.client.json.dumps(payload).encode("utf-8")
        return response


if __name__ == "__main__":
    unittest.main()
