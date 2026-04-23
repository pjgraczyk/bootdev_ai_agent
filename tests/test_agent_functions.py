import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from ai_agent import AIAgent
from config import Config


class TestAgentFunctionCalls(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = Path(self.temp_dir) / "test_file.txt"
        self.test_file.write_text("test content")

        self.pkg_dir = Path(self.temp_dir) / "pkg"
        self.pkg_dir.mkdir()
        (self.pkg_dir / "subfile.txt").write_text("sub content")

        self.mock_config = Mock(spec=Config)
        self.mock_config.model = "test-model"
        self.mock_config.api_key = "test-key"
        self.mock_config.temperature = 0.7
        self.mock_config.retries = 3
        self.mock_config.verbose = False
        self.mock_config.system_prompt = "You are a helpful AI assistant"
        self.mock_config.tools = []

    def tearDown(self) -> None:
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_agent_initialization(self) -> None:
        agent = AIAgent(self.mock_config)
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.memory)
        self.assertIsNotNone(agent.agent)
        self.assertEqual(agent.thread_id, "default")

    def test_agent_has_console(self) -> None:
        agent = AIAgent(self.mock_config)
        self.assertIsNotNone(agent.console)

    def test_agent_config(self) -> None:
        agent = AIAgent(self.mock_config)
        self.assertEqual(agent.system_prompt, "You are a helpful AI assistant")
        self.assertFalse(agent.verbose)


if __name__ == "__main__":
    unittest.main()
