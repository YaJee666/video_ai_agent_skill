import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install_skill.py"


def load_installer_module():
    spec = importlib.util.spec_from_file_location("install_skill", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class InstallSkillTest(unittest.TestCase):
    def setUp(self):
        self.installer = load_installer_module()

    def make_source(self, root: Path) -> Path:
        source = root / "source-skill"
        (source / "scripts").mkdir(parents=True)
        (source / "SKILL.md").write_text("# skill\n", encoding="utf-8")
        (source / "scripts" / "client.py").write_text("print('ok')\n", encoding="utf-8")
        return source

    def test_find_seed_env_uses_first_existing_target_env(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            codex = root / "codex"
            agents = root / "agents"
            (codex / self.installer.SKILL_NAME).mkdir(parents=True)
            (codex / self.installer.SKILL_NAME / ".env").write_bytes(b"VIDEO_AI_AGENT_API_KEY=vag_sk_test\n")

            seed = self.installer.find_seed_env([("codex", codex), ("agents", agents)])

        self.assertEqual(b"VIDEO_AI_AGENT_API_KEY=vag_sk_test\n", seed)

    def test_copy_skill_seeds_env_when_destination_has_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_source(root)
            destination = root / "agents" / self.installer.SKILL_NAME

            self.installer.copy_skill(
                source,
                destination,
                dry_run=False,
                seed_env=b"VIDEO_AI_AGENT_API_KEY=vag_sk_seed\n",
            )

            self.assertEqual(
                b"VIDEO_AI_AGENT_API_KEY=vag_sk_seed\n",
                (destination / ".env").read_bytes(),
            )
            self.assertTrue((destination / "SKILL.md").is_file())

    def test_copy_skill_preserves_destination_env_over_seed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = self.make_source(root)
            destination = root / "agents" / self.installer.SKILL_NAME
            destination.mkdir(parents=True)
            (destination / ".env").write_bytes(b"VIDEO_AI_AGENT_API_KEY=vag_sk_existing\n")

            self.installer.copy_skill(
                source,
                destination,
                dry_run=False,
                seed_env=b"VIDEO_AI_AGENT_API_KEY=vag_sk_seed\n",
            )

            self.assertEqual(
                b"VIDEO_AI_AGENT_API_KEY=vag_sk_existing\n",
                (destination / ".env").read_bytes(),
            )


if __name__ == "__main__":
    unittest.main()
