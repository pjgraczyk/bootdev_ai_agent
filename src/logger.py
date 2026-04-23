from pydantic import BaseModel
import sqlite3
from datetime import datetime
from sqlite3 import OperationalError
from textwrap import dedent
from typing import Protocol

from langchain_core.messages import AIMessage


class MetadataDict(BaseModel):
    input_tokens: int
    output_tokens: int
    model_name: str


class Logger(Protocol):
    def log_interaction(
        self,
        user_prompt: str,
        response: AIMessage,
        tokens: MetadataDict,
    ) -> None: ...

    def close(self) -> None: ...


class SqliteLogger:
    def __init__(self, db_path: str = "data/agent_logs.db") -> None:
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.table_name = "agent_metadata_archive"
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
            self.connection.commit()
        except OperationalError:
            raise Exception("The table creation has failed, please try again...")

    def log_interaction(
        self, user_prompt: str, response: AIMessage, metadata: MetadataDict
    ) -> None:

        sql_stmt = f"""
            INSERT INTO {self.table_name} (
                timestamp, user_prompt, response,
                input_tokens, output_tokens, model_name
            )
                VALUES(?, ?, ?, ?, ?, ?)
        """
        # Extract token information from tokens dict or response object
        input_tokens, output_tokens, model_name = (
            metadata.model_name,
            metadata.output_tokens,
            metadata.model_name,
        )
        response_content = str(response.content)

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
