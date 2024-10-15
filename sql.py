from __future__ import annotations

import sqlite3

import click
import tabulate

DEFAULT_DIR = r"instance/database.sqlite"

conn = sqlite3.connect(DEFAULT_DIR)


@click.command()
@click.option("--query", "-q", help="SQL query to execute", required=True, type=str)
def main(query: str):
    if query is None:
        raise ValueError("No query provided.")

    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()

    print("Executed query successfully.")
    table = cursor.fetchall()
    print(tabulate.tabulate(table, headers=[desc[0] for desc in cursor.description], tablefmt="grid"))


if __name__ == "__main__":
    main()
