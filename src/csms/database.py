import sqlite3
from pathlib import Path


DEFAULT_DATABASE_PATH = Path("instance") / "csms.db"


def initialize_database(database_path=DEFAULT_DATABASE_PATH):
    database_path = Path(database_path)

    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS residents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            address TEXT NOT NULL,
            contact_number TEXT NOT NULL,
            email TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    connection.commit()
    connection.close()
    