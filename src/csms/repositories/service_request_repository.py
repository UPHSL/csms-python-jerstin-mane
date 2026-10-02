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