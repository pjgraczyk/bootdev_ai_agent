import unittest
import tempfile
from pathlib import Path
from ai_agent import AIAgent
from config import Config
from unittest.mock import Mock


class TestAgentFunctionCalls(unittest.TestCase):
    def setUp(self):
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

    def tearDown(self):
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_agent_initialization(self):
        agent = AIAgent(self.mock_config)
        self.assertIsNotNone(agent)
        self.assertIsNotNone(agent.message_history)

    def test_add_prompt(self):
        agent = AIAgent(self.mock_config)
        user_message = agent.add_prompt("Hello, how are you?")
        self.assertEqual(user_message.content, "Hello, how are you?")

    def test_get_message_history(self):
        agent = AIAgent(self.mock_config)
        agent.add_prompt("First message")
        agent.add_prompt("Second message")

        messages = agent.get_message_history()
        self.assertEqual(len(messages), 3)

    def test_get_user_messages(self):
        """Test filtering user messages"""
        agent = AIAgent(self.mock_config)
        agent.add_prompt("User message 1")
        agent.add_prompt("User message 2")

        user_messages = agent.get_user_messages()
        self.assertEqual(len(user_messages), 2)
        self.assertEqual(user_messages[0].content, "User message 1")
        self.assertEqual(user_messages[1].content, "User message 2")


if __name__ == "__main__":
    unittest.main()
