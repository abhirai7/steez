from __future__ import annotations

import os
import sqlite3

import tabulate
from colorama import Fore, just_fix_windows_console

database_path = input("Database path, Hit `Enter` for temporary storage: ")
if not database_path.strip():
    database_path = ":memory:"

print(
    f"Connecting to database... Script will create one if it doesn't exist... {database_path}",
)

con = sqlite3.connect(database_path)
cur = con.cursor()

if os.name == "nt":
    just_fix_windows_console()


def parse_input(query: str) -> sqlite3.Cursor | str:
    try:
        cursor = cur.execute(query)
    except Exception as e:
        return f"Invalid input {e}"
    else:
        return cursor


def clear() -> None:
    if os.name == "nt":
        os.system("cls")
    elif os.name == "posix":
        os.system("clear")


clear()

result = parse_input("SELECT name, sql FROM sqlite_master WHERE type='table';")
if isinstance(result, str):
    print(result)

elif r := result.fetchall():
    headers = [description[0] for description in result.description]
    table = tabulate.tabulate(r, headers=headers, tablefmt="psql")
    print(table)
else:
    print("No tables found")

while True:
    query = input(f"{Fore.CYAN}SQL> {Fore.RESET}")
    if query.lower() in {"exit", "quit"}:
        break

    if query.lower() in {"cls", "clear"}:
        clear()
        continue

    if query.lower() in {"commit", "save"}:
        con.commit()
        continue

    result = parse_input(query)
    if isinstance(result, str):
        print(f"{Fore.RED}Error: {result}{Fore.RESET}")
        continue

    try:
        if r := result.fetchall():
            headers = [description[0] for description in result.description]
            table = tabulate.tabulate(r, headers=headers, tablefmt="psql")
            print(table)
    except Exception as e:
        print(f"{Fore.RED}Error: {e}{Fore.RESET}")
        continue

    if result.rowcount == -1:
        continue

    print(
        f"{Fore.WHITE}Query OK: {Fore.RED}{result.rowcount}{Fore.WHITE} rows affected{Fore.RESET}",
    )

    con.commit()

con.close()
