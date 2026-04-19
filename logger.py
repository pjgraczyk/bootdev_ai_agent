from datetime import datetime, timezone
from sqlite3 import OperationalError
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Protocol
import json
import logging
import os
import sqlite3

if TYPE_CHECKING:
    from langchain_core.messages import AIMessage
else:
    AIMessage = Any

LOGGER = logging.getLogger(__name__)
UNKNOWN_TOOL_NAME = "unknown_tool"
ERROR_MISSING_TOOL_NAME_STATUS = "error_missing_tool_name"


class Logger(Protocol):
    """Protocol that all loggers must follow."""

    def log_interaction(
        self,
        user_prompt: str,
        response: AIMessage,
        extra_data: dict[str, Any] | None = None,
    ) -> None:
        """Log a user-AI interaction."""
        ...

    def close(self) -> None:
        """Clean up resources."""
        ...


class SqliteLogger:
    """Logs interactions to a SQLite database as a context manager."""

    def __init__(self, db_path: str = "data/agent_logs.db"):
        self.db_path = db_path
        self.connection: sqlite3.Connection | None = None
        self.cursor: sqlite3.Cursor | None = None

    def __enter__(self):
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        sql_stmt = """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL,
                user_prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                model_name VARCHAR(100)
            );

            CREATE TABLE IF NOT EXISTS token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER NOT NULL,
                input_tokens INT,
                output_tokens INT,
                total_tokens INT,
                raw_usage_json TEXT,
                FOREIGN KEY (interaction_id) REFERENCES interactions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS tool_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER NOT NULL,
                tool_name TEXT NOT NULL,
                tool_call_id TEXT,
                tool_type TEXT,
                args_json TEXT,
                result_json TEXT,
                status TEXT,
                raw_event_json TEXT,
                FOREIGN KEY (interaction_id) REFERENCES interactions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS interaction_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                interaction_id INTEGER NOT NULL,
                meta_key TEXT NOT NULL,
                meta_value TEXT,
                FOREIGN KEY (interaction_id) REFERENCES interactions(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS agent_metadata_archive (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                user_prompt TEXT,
                response TEXT,
                input_tokens INT,
                output_tokens INT,
                model_name VARCHAR(100)
            );
        """
        try:
            self.cursor.executescript(dedent(sql_stmt))
        except OperationalError:
            raise Exception("The table creation has failed, please try again...")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.connection and exc_type is None:
                self.connection.commit()
            elif self.connection:
                print(f"There was an exception: {exc_type=} {exc_val=} {exc_tb=}")
                self.connection.rollback()
        finally:
            self.close()

    @staticmethod
    def _serialize(value: Any) -> str | None:
        if value is None:
            return None
        try:
            return json.dumps(value, default=str, ensure_ascii=False)
        except (TypeError, ValueError):
            LOGGER.warning(
                "Falling back to string serialization for unsupported value type=%s sample=%r",
                type(value).__name__,
                value,
            )
            return json.dumps(str(value), ensure_ascii=False)

    @staticmethod
    def _extract_tool_events(response: AIMessage) -> list[dict[str, Any]]:
        tool_events: list[dict[str, Any]] = []
        tool_calls = getattr(response, "tool_calls", None)
        if isinstance(tool_calls, list):
            for event in tool_calls:
                if isinstance(event, dict):
                    tool_events.append(event)

        additional_tool_calls = None
        if getattr(response, "additional_kwargs", None):
            additional_tool_calls = response.additional_kwargs.get("tool_calls")
        if isinstance(additional_tool_calls, list):
            for event in additional_tool_calls:
                if isinstance(event, dict):
                    tool_events.append(event)
        return tool_events

    def log_interaction(
        self,
        user_prompt: str,
        response: AIMessage,
        extra_data: dict[str, Any] | None = None,
    ) -> None:
        extra_data = extra_data or {}
        timestamp_value = extra_data.get("timestamp")
        if isinstance(timestamp_value, datetime):
            if timestamp_value.tzinfo is None:
                LOGGER.warning("Naive datetime provided for timestamp; assuming UTC.")
                timestamp = timestamp_value.replace(tzinfo=timezone.utc).isoformat()
            else:
                timestamp = timestamp_value.astimezone(timezone.utc).isoformat()
        elif timestamp_value is not None:
            timestamp = str(timestamp_value)
        else:
            timestamp = datetime.now(timezone.utc).isoformat()

        usage_metadata = response.usage_metadata or {}
        if response.usage_metadata is None:
            LOGGER.warning("Response usage_metadata is missing; token usage will be stored as NULL where applicable.")
        input_tokens = usage_metadata.get("input_tokens")
        output_tokens = usage_metadata.get("output_tokens")
        total_tokens = usage_metadata.get("total_tokens")
        model_name = response.response_metadata.get("model_name") or response.response_metadata.get("model")

        tool_events = self._extract_tool_events(response)
        extra_tool_events = extra_data.get("tool_events")
        if isinstance(extra_tool_events, list):
            for event in extra_tool_events:
                if isinstance(event, dict):
                    tool_events.append(event)

        metadata = extra_data.get("metadata")
        if not isinstance(metadata, dict):
            metadata = {}

        if self.cursor and self.connection:
            self.cursor.execute(
                """
                INSERT INTO interactions (timestamp, user_prompt, response, model_name)
                VALUES (?, ?, ?, ?)
                """,
                (timestamp, str(user_prompt), str(response.content), model_name),
            )
            interaction_id = self.cursor.lastrowid

            self.cursor.execute(
                """
                INSERT INTO token_usage (interaction_id, input_tokens, output_tokens, total_tokens, raw_usage_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    interaction_id,
                    input_tokens,
                    output_tokens,
                    total_tokens,
                    self._serialize(usage_metadata),
                ),
            )

            for event in tool_events:
                tool_name = event.get("name") or event.get("tool_name")
                status = event.get("status")
                if not tool_name:
                    tool_name = UNKNOWN_TOOL_NAME
                    status = status or ERROR_MISSING_TOOL_NAME_STATUS
                self.cursor.execute(
                    """
                    INSERT INTO tool_events (
                        interaction_id, tool_name, tool_call_id, tool_type, args_json, result_json, status, raw_event_json
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        interaction_id,
                        str(tool_name),
                        event.get("id") or event.get("tool_call_id"),
                        event.get("type"),
                        self._serialize(event.get("args")),
                        self._serialize(event.get("result")),
                        status,
                        self._serialize(event),
                    ),
                )

            for key, value in metadata.items():
                self.cursor.execute(
                    """
                    INSERT INTO interaction_metadata (interaction_id, meta_key, meta_value)
                    VALUES (?, ?, ?)
                    """,
                    (interaction_id, str(key), self._serialize(value)),
                )

            self.cursor.execute(
                """
                INSERT INTO agent_metadata_archive (
                    timestamp, user_prompt, response, input_tokens, output_tokens, model_name
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (timestamp, str(user_prompt), str(response.content), input_tokens, output_tokens, model_name),
            )
            self.connection.commit()

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
