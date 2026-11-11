from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.dashboard_service import DashboardService


def create_resident(repository, status="Active"):
    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="123 Test Street",
        contact_number="09123456789",
        email="juan@example.com",
        status=status,
    )

    return repository.save(resident)


def create_service_request(
    repository,
    resident_id,
    **overrides,
):
    values = {
        "resident_id": resident_id,
        "service_type": "Food Assistance",
        "description": "Monthly food support",
        "date_requested": date(2026, 11, 1),
        "status": "Pending",
    }

    values.update(overrides)

    service_request = ServiceRequest(**values)

    return repository.save(service_request)


def create_dashboard_service(database_path):
    resident_repository = ResidentRepository(database_path)
    service_request_repository = ServiceRequestRepository(database_path)

    return DashboardService(
        resident_repository,
        service_request_repository,
    )


def test_dashboard_returns_zero_counts_when_database_is_empty(tmp_path):
    database_path = tmp_path / "csms.db"
    service = create_dashboard_service(database_path)

    result = service.get_dashboard_summary()

    assert result == {
        "total_residents": 0,
        "active_residents": 0,
        "inactive_residents": 0,
        "total_service_requests": 0,
        "pending_requests": 0,
        "in_progress_requests": 0,
        "completed_requests": 0,
        "cancelled_requests": 0,
        "open_service_requests": 0,
        "recent_service_requests": [],
    }


def test_dashboard_returns_correct_resident_and_request_metrics(tmp_path):
    database_path = tmp_path / "csms.db"

    resident_repository = ResidentRepository(database_path)
    service_request_repository = ServiceRequestRepository(database_path)

    resident = create_resident(resident_repository)
    create_resident(resident_repository)
    create_resident(resident_repository, status="Inactive")

    statuses = [
        "Pending",
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    ]

    for status in statuses:
        create_service_request(
            service_request_repository,
            resident.id,
            status=status,
        )

    service = DashboardService(
        resident_repository,
        service_request_repository,
    )

    result = service.get_dashboard_summary()

    assert result["total_residents"] == 3
    assert result["active_residents"] == 2
    assert result["inactive_residents"] == 1

    assert result["total_service_requests"] == 5
    assert result["pending_requests"] == 2
    assert result["in_progress_requests"] == 1
    assert result["completed_requests"] == 1
    assert result["cancelled_requests"] == 1

    assert result["open_service_requests"] == 3

    assert result["total_residents"] == (
        result["active_residents"] + result["inactive_residents"]
    )

    assert result["total_service_requests"] == (
        result["pending_requests"]
        + result["in_progress_requests"]
        + result["completed_requests"]
        + result["cancelled_requests"]
    )


def test_dashboard_returns_five_most_recent_service_requests(tmp_path):
    database_path = tmp_path / "csms.db"

    resident_repository = ResidentRepository(database_path)
    service_request_repository = ServiceRequestRepository(database_path)

    resident = create_resident(resident_repository)

    for day in range(1, 7):
        create_service_request(
            service_request_repository,
            resident.id,
            date_requested=date(2026, 11, day),
        )

    service = DashboardService(
        resident_repository,
        service_request_repository,
    )

    result = service.get_dashboard_summary()
    recent_requests = result["recent_service_requests"]

    assert len(recent_requests) == 5

    assert [item.date_requested for item in recent_requests] == [
        date(2026, 11, 6),
        date(2026, 11, 5),
        date(2026, 11, 4),
        date(2026, 11, 3),
        date(2026, 11, 2),
    ]

    assert [item.id for item in recent_requests] == sorted(
        [item.id for item in recent_requests],
        reverse=True,
    )
