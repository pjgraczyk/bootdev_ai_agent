from sqlite3 import OperationalError
from textwrap import dedent
from typing import Protocol
from datetime import datetime
from langchain_core.messages import AIMessage
import sqlite3


class Logger(Protocol):
    """Protocol that all loggers must follow."""

    def log_interaction(self, user_prompt: str, response: AIMessage, tokens: dict) -> None:
        """Log a user-AI interaction."""
        ...

    def close(self) -> None:
        """Clean up resources."""
        ...


class SqliteLogger:
    """Logs interactions to a SQLite database as a context manager."""

    def __init__(self, db_path: str = "data/agent_logs.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        self.table_name = 'agent_metadata_archive'
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
            raise Exception('The table creation has failed, please try again...')

        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.connection and exc_type is None:
                self.connection.commit()
            elif self.connection:
                print(f'There was an exception: {exc_type=} {exc_val=} {exc_tb=}')
                self.connection.rollback()
            
        finally:
            self.close()
                        
    def log_interaction(self, user_prompt: str, response: AIMessage) -> None:
        sql_stmt = f"""
            INSERT INTO {self.table_name} (timestamp, user_prompt, response, input_tokens, output_tokens, model_name)
                VALUES(?, ?, ?, ?, ?, ?)
        """
        input_tokens = response.usage_metadata.get('input_tokens') if response.usage_metadata else None
        output_tokens = response.usage_metadata.get('output_tokens') if response.usage_metadata else None
        model_name = response.response_metadata.get("model_name") or response.response_metadata.get("model")
        if self.cursor and self.connection:
            self.cursor.execute(dedent(sql_stmt), (datetime.now(), user_prompt, response.content, input_tokens, output_tokens, model_name))
            self.connection.commit()

    def close(self) -> None:
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
