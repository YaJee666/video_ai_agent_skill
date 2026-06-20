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
        self.assertEqual(2222, resolved.timeout_ms)
        self.assertEqual("environment", resolved.config_sources["VIDEO_AI_AGENT_API_KEY"])
        self.assertEqual("cli", resolved.config_sources["VIDEO_AI_AGENT_ENDPOINT"])
        self.assertEqual("environment", resolved.config_sources["VIDEO_AI_AGENT_TIMEOUT_MS"])

    def test_debug_config_masks_api_key(self):
        args = argparse.Namespace(
            api_key="vag_sk_live_abcdefghijklmnopqrstuvwxyz",
            endpoint="https://www.talkaibot.com/openapi/v1/chat/completions",
            timeout_ms=600000,
            project_id="",
            session_id="",
            config_sources={
                "VIDEO_AI_AGENT_API_KEY": ".env (skill/.env)",
                "VIDEO_AI_AGENT_ENDPOINT": "default",
                "VIDEO_AI_AGENT_TIMEOUT_MS": "default",
                "VIDEO_AI_AGENT_PROJECT_ID": "unset",
                "VIDEO_AI_AGENT_SESSION_ID": "unset",
            },
        )

        rendered = self.client.render_config_debug(args)

        self.assertIn("VIDEO_AI_AGENT_API_KEY=vag_sk_...wxyz", rendered)
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz", rendered)

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


if __name__ == "__main__":
    unittest.main()
