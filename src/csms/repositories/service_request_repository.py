import sqlite3
from pathlib import Path

from csms.database import DEFAULT_DATABASE_PATH, initialize_database
from csms.models.service_request import ServiceRequest


class ServiceRequestRepository:
    def __init__(self, database_path=DEFAULT_DATABASE_PATH):
        self.database_path = Path(database_path)
        initialize_database(self.database_path)

    def save(self, service_request):
        connection = sqlite3.connect(self.database_path)

        cursor = connection.execute(
            """
            INSERT INTO service_requests (
                resident_id,
                service_type,
                description,
                date_requested,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                service_request.resident_id,
                service_request.service_type,
                service_request.description,
                service_request.date_requested.isoformat(),
                service_request.status,
            ),
        )

        connection.commit()

        service_request.id = cursor.lastrowid

        connection.close()

        return service_request

    def find_by_id(self, service_request_id):
        connection = sqlite3.connect(self.database_path)

        connection.row_factory = sqlite3.Row

        row = connection.execute(
            """
            SELECT
                id,
                resident_id,
                service_type,
                description,
                date_requested,
                status
            FROM service_requests
            WHERE id = ?
            """,
            (service_request_id,),
        ).fetchone()

        connection.close()

        if row is None:
            return None

        from datetime import date

        return ServiceRequest(
            id=row["id"],
            resident_id=row["resident_id"],
            service_type=row["service_type"],
            description=row["description"],
            date_requested=date.fromisoformat(row["date_requested"]),
            status=row["status"],
        )

    def find_all(self, search_term=None, status=None):
        connection = sqlite3.connect(self.database_path)

        connection.row_factory = sqlite3.Row

        conditions = []
        parameters = []

        if search_term:
            pattern = f"%{search_term}%"

            conditions.append(
                """
                (
                    LOWER(service_type) LIKE LOWER(?)
                    OR LOWER(description) LIKE LOWER(?)
                )
                """
            )

            parameters.extend([pattern, pattern])

        if status:
            conditions.append("status = ?")
            parameters.append(status)

        query = """
            SELECT
                id,
                resident_id,
                service_type,
                description,
                date_requested,
                status
            FROM service_requests
        """

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += """
            ORDER BY
                date_requested DESC,
                id DESC
        """

        rows = connection.execute(query, parameters).fetchall()

        connection.close()

        from datetime import date

        return [
            ServiceRequest(
                id=row["id"],
                resident_id=row["resident_id"],
                service_type=row["service_type"],
                description=row["description"],
                date_requested=date.fromisoformat(row["date_requested"]),
                status=row["status"],
            )
            for row in rows
        ]

    def update_status(self, service_request_id, status):
        connection = sqlite3.connect(self.database_path)

        connection.execute(
            """
            UPDATE service_requests
            SET status = ?
            WHERE id = ?
            """,
            (status, service_request_id),
        )

        connection.commit()
        connection.close()

        return self.find_by_id(service_request_id)

    def count_all(self) -> int:
        """Count all persisted Service Requests."""
        connection = sqlite3.connect(self.database_path)

        row = connection.execute(
            """
            SELECT COUNT(*)
            FROM service_requests
            """
        ).fetchone()

        connection.close()

        return row[0]

    def get_status_counts(self) -> dict[str, int]:
        """Count persisted Service Requests grouped by status."""
        connection = sqlite3.connect(self.database_path)

        rows = connection.execute(
            """
            SELECT
                status,
                COUNT(*)
            FROM service_requests
            GROUP BY status
            """
        ).fetchall()

        connection.close()

        counts = {
            "Pending": 0,
            "In Progress": 0,
            "Completed": 0,
            "Cancelled": 0,
        }

        for status, total in rows:
            if status in counts:
                counts[status] = total

        return counts

    def find_recent(self, limit: int = 5) -> list[ServiceRequest]:
        """Find the most recent Service Requests."""
        from datetime import date

        limit = max(0, min(int(limit), 5))

        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row

        rows = connection.execute(
            """
            SELECT
                id,
                resident_id,
                service_type,
                description,
                date_requested,
                status
            FROM service_requests
            ORDER BY
                date_requested DESC,
                id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

        connection.close()

        return [
            ServiceRequest(
                id=row["id"],
                resident_id=row["resident_id"],
                service_type=row["service_type"],
                description=row["description"],
                date_requested=date.fromisoformat(row["date_requested"]),
                status=row["status"],
            )
            for row in rows
        ]
