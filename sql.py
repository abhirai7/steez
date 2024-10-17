from __future__ import annotations

import click
import sqlalchemy
import tabulate

DEFAULT_DIR = r"instance/database.sqlite"

conn = sqlalchemy.create_engine(f"sqlite:///{DEFAULT_DIR}").connect()
conn.engine.echo = True


@click.command()
@click.option("--query", "-q", help="SQL query to execute", required=True, type=str)
def main(query: str):
    if query is None:
        raise ValueError("No query provided.")

    with conn as cursor:
        cursor = cursor.execute(sqlalchemy.text(query))
        headers = cursor.keys()
        if cursor.returns_rows:
            data = cursor.fetchall()
            click.echo(tabulate.tabulate(data, headers=headers, tablefmt="grid"))
        else:
            click.echo("Query executed successfully.")
            click.echo(f"Affected rows: {cursor.rowcount}")
            click.echo(f"Last row ID: {cursor.lastrowid}")


if __name__ == "__main__":
    main()
