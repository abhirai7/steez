from __future__ import annotations

import getpass
import sqlite3

from src.utils import Password

connection = sqlite3.connect("database.sqlite", check_same_thread=False)

cursor = connection.cursor()

print("Creating the schema...", end="")

with open("schema.sql") as f:
    schema = f.read()

cursor.executescript(schema)

print("Schema created successfully.")

print("Creating the admin user...")

password = getpass.getpass("Enter the password for the admin user: ")
confirm_password = getpass.getpass("Confirm the password: ")

if password != confirm_password:
    print("Passwords do not match. Exiting... Retry the setup.")
    exit(1)

password = Password(password)

query = r"""INSERT INTO `USERS` (`EMAIL`, `NAME`, `PASSWORD`, `ROLE`, `ADDRESS`, `PHONE`) VALUES (?, ?, ?, ?, ?, ?)"""

cursor.execute(query, ("", "STEEZ ADMIN", password.hex, "ADMIN", "", ""))

connection.commit()
