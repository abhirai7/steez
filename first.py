from __future__ import annotations

import sqlite3

from src.utils import Password

connection = sqlite3.connect("database.sqlite", check_same_thread=False)

cursor = connection.cursor()

with open("schema.sql") as f:
    schema = f.read()

cursor.executescript(schema)

password = Password("password")

query = r"""INSERT INTO `USERS` (`EMAIL`, `NAME`, `PASSWORD`, `ROLE`, `ADDRESS`, `PHONE`) VALUES (?, ?, ?, ?, ?, ?)"""

cursor.execute(query, ("", "STEEZ ADMIN", password.hex, "ADMIN", "", ""))

connection.commit()
