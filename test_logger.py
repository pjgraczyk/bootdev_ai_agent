import sqlite3
import tempfile
import unittest
from pathlib import Path

from logger import SqliteLogger


class DummyResponse:
    def __init__(self):
        self.content = "Hello from AI"
        self.usage_metadata = {"input_tokens": 10, "output_tokens": 20, "total_tokens": 30}
        self.response_metadata = {"model_name": "mistral-tiny"}
        self.tool_calls = [{"id": "call_1", "name": "read_file", "args": {"path": "main.py"}, "status": "success"}]
        self.additional_kwargs = {"tool_calls": [{"id": "call_2", "name": "write_file", "args": {"path": "foo.txt"}}]}


class TestSqliteLogger(unittest.TestCase):
    def test_schema_and_interaction_logging(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "agent_logs.db"
            response = DummyResponse()

            with SqliteLogger(str(db_path)) as logger:
                logger.log_interaction(
                    "Test prompt",
                    response,  # type: ignore[arg-type]
                    extra_data={"metadata": {"session_id": "abc123", "source": "unittest"}},
                )

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            cur.execute("SELECT COUNT(*) FROM interactions")
            self.assertEqual(cur.fetchone()[0], 1)

            cur.execute("SELECT input_tokens, output_tokens, total_tokens FROM token_usage")
            self.assertEqual(cur.fetchone(), (10, 20, 30))

            cur.execute("SELECT tool_name FROM tool_events ORDER BY id")
            self.assertEqual([row[0] for row in cur.fetchall()], ["read_file", "write_file"])

            cur.execute("SELECT meta_key FROM interaction_metadata ORDER BY id")
            self.assertEqual([row[0] for row in cur.fetchall()], ["session_id", "source"])

            cur.execute("SELECT COUNT(*) FROM agent_metadata_archive")
            self.assertEqual(cur.fetchone()[0], 1)

            conn.close()


if __name__ == "__main__":
    unittest.main()
