from sqlite3 import OperationalError
from textwrap import dedent
from typing import Protocol
from datetime import datetime
from langchain_core.messages import AIMessage
import sqlite3


class Logger(Protocol):
    def log_interaction(
        self, user_prompt: str, response: AIMessage, tokens: dict
    ) -> None: ...

    def close(self) -> None: ...


class SqliteLogger:
    def __init__(self, db_path: str = "data/agent_logs.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None
        self.table_name = "agent_metadata_archive"

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        sql_stmt = f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                user_prompt TEXT,
                response TEXT,
                input_tokens INT,
                output_tokens INT,
                model_name VARCHAR(100)
            )
        """
        try:
            self.cursor.execute(dedent(sql_stmt))
        except OperationalError:
            raise Exception(
                "The table creation has failed, please try again..."
            )

        return self

    def __exit__(self, exc_type, *_):
        try:
            if self.connection and exc_type is None:
                self.connection.commit()
            elif self.connection:
                self.connection.rollback()

        finally:
            self.close()

    def log_interaction(self, user_prompt: str, response) -> None:
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)
            self.cursor = self.connection.cursor()

        sql_stmt = f"""
            INSERT INTO {self.table_name} (timestamp, user_prompt, response, input_tokens, output_tokens, model_name)
                VALUES(?, ?, ?, ?, ?, ?)
        """
        if isinstance(response, dict):
            input_tokens = response.get("input_tokens")
            output_tokens = response.get("output_tokens")
            model_name = response.get("model_name") or response.get("model")
            response_content = str(response.get("messages", ""))
        else:
            input_tokens = (
                response.usage_metadata.get("input_tokens")
                if response.usage_metadata
                else None
            )
            output_tokens = (
                response.usage_metadata.get("output_tokens")
                if response.usage_metadata
                else None
            )
            model_name = response.response_metadata.get(
                "model_name"
            ) or response.response_metadata.get("model")
            response_content = response.content

        if self.cursor and self.connection:
            self.cursor.execute(
                dedent(sql_stmt),
                (
                    datetime.now(),
                    user_prompt,
                    response_content,
                    input_tokens,
                    output_tokens,
                    model_name,
                ),
            )
            self.connection.commit()

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
