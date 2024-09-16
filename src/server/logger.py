import logging
import sqlite3


class SQLiteHandler(logging.Handler):
    def __init__(self, connection: sqlite3.Connection):
        super().__init__()
        self.connection = connection

    def emit(self, record: logging.LogRecord) -> None:
        cursor = self.connection.cursor()
        query = r"INSERT INTO LOGS (MESSAGE, LEVEL, NAME) VALUES (?, ?, ?)"
        cursor.execute(
            query,
            (record.getMessage(), record.levelname, record.name),
        )
        self.connection.commit()
