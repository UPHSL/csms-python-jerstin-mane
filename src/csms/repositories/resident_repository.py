import sqlite3
from pathlib import Path

from csms.database import DEFAULT_DATABASE_PATH, initialize_database
from csms.models.resident import Resident


class ResidentRepository:
    def __init__(self, database_path=DEFAULT_DATABASE_PATH):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def save(self, resident):
        connection = sqlite3.connect(self.database_path)

        cursor = connection.execute(
            """
            INSERT INTO residents (
                first_name,
                last_name,
                address,
                contact_number,
                email,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                resident.first_name,
                resident.last_name,
                resident.address,
                resident.contact_number,
                resident.email,
                resident.status,
            ),
        )

        connection.commit()

        resident.id = cursor.lastrowid

        connection.close()

        return resident

    def find_by_id(self, resident_id):
        connection = sqlite3.connect(self.database_path)

        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT
                id,
                first_name,
                last_name,
                address,
                contact_number,
                email,
                status
            FROM residents
            WHERE id = ?
            """,
            (resident_id,),
        ).fetchone()

        connection.close()

        if row is None:
            return None

        return Resident(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            address=row["address"],
            contact_number=row["contact_number"],
            email=row["email"],
            status=row["status"],
        )

    def find_all(self):
        connection = sqlite3.connect(self.database_path)

        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                first_name,
                last_name,
                address,
                contact_number,
                email,
                status
            FROM residents
            ORDER BY
                LOWER(last_name) ASC,
                LOWER(first_name) ASC,
                id ASC
            """
        ).fetchall()

        connection.close()

        return [
            Resident(
                id=row["id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                address=row["address"],
                contact_number=row["contact_number"],
                email=row["email"],
                status=row["status"],
            )
            for row in rows
        ]

    def search_by_name(self, search_term):
        connection = sqlite3.connect(self.database_path)

        connection.row_factory = sqlite3.Row

        pattern = f"%{search_term}%"

        rows = connection.execute(
            """
            SELECT
                id,
                first_name,
                last_name,
                address,
                contact_number,
                email,
                status
            FROM residents
            WHERE
                LOWER(first_name) LIKE LOWER(?)
                OR LOWER(last_name) LIKE LOWER(?)
            ORDER BY
                LOWER(last_name) ASC,
                LOWER(first_name) ASC,
                id ASC
            """,
            (pattern, pattern),
        ).fetchall()

        connection.close()

        return [
            Resident(
                id=row["id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                address=row["address"],
                contact_number=row["contact_number"],
                email=row["email"],
                status=row["status"],
            )
            for row in rows
        ]