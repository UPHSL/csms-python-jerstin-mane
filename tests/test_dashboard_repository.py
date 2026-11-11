from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository


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


def test_count_all_residents_includes_inactive_residents(tmp_path):
    database_path = tmp_path / "csms.db"
    repository = ResidentRepository(database_path)

    create_resident(repository)
    create_resident(repository)
    create_resident(repository, status="Inactive")

    assert repository.count_all() == 3


def test_get_resident_status_counts_returns_correct_counts(tmp_path):
    database_path = tmp_path / "csms.db"
    repository = ResidentRepository(database_path)

    create_resident(repository)
    create_resident(repository)
    create_resident(repository, status="Inactive")

    assert repository.get_status_counts() == {
        "Active": 2,
        "Inactive": 1,
    }


def test_get_resident_status_counts_returns_zero_when_empty(tmp_path):
    database_path = tmp_path / "csms.db"
    repository = ResidentRepository(database_path)

    assert repository.get_status_counts() == {
        "Active": 0,
        "Inactive": 0,
    }


def test_count_all_service_requests_returns_correct_total(tmp_path):
    database_path = tmp_path / "csms.db"
    resident_repository = ResidentRepository(database_path)
    service_repository = ServiceRequestRepository(database_path)

    resident = create_resident(resident_repository)

    create_service_request(service_repository, resident.id)
    create_service_request(
        service_repository,
        resident.id,
        service_type="Medical Assistance",
    )
    create_service_request(
        service_repository,
        resident.id,
        status="Completed",
    )

    assert service_repository.count_all() == 3


def test_get_service_request_status_counts_returns_correct_counts(tmp_path):
    database_path = tmp_path / "csms.db"
    resident_repository = ResidentRepository(database_path)
    service_repository = ServiceRequestRepository(database_path)

    resident = create_resident(resident_repository)

    statuses = [
        "Pending",
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    ]

    for status in statuses:
        create_service_request(
            service_repository,
            resident.id,
            status=status,
        )

    assert service_repository.get_status_counts() == {
        "Pending": 2,
        "In Progress": 1,
        "Completed": 1,
        "Cancelled": 1,
    }


def test_get_service_request_status_counts_returns_zero_when_empty(
    tmp_path,
):
    database_path = tmp_path / "csms.db"
    repository = ServiceRequestRepository(database_path)

    assert repository.get_status_counts() == {
        "Pending": 0,
        "In Progress": 0,
        "Completed": 0,
        "Cancelled": 0,
    }


def test_find_recent_returns_at_most_five_requests_in_correct_order(
    tmp_path,
):
    database_path = tmp_path / "csms.db"
    resident_repository = ResidentRepository(database_path)
    service_repository = ServiceRequestRepository(database_path)

    resident = create_resident(resident_repository)

    requests = [
        create_service_request(
            service_repository,
            resident.id,
            date_requested=date(2026, 11, 1),
        ),
        create_service_request(
            service_repository,
            resident.id,
            date_requested=date(2026, 11, 3),
        ),
        create_service_request(
            service_repository,
            resident.id,
            date_requested=date(2026, 11, 2),
        ),
        create_service_request(
            service_repository,
            resident.id,
            date_requested=date(2026, 11, 3),
        ),
        create_service_request(
            service_repository,
            resident.id,
            date_requested=date(2026, 11, 4),
        ),
        create_service_request(
            service_repository,
            resident.id,
            date_requested=date(2026, 11, 3),
        ),
    ]

    results = service_repository.find_recent(limit=10)

    assert len(results) == 5
    assert [item.id for item in results] == [
        requests[4].id,
        requests[5].id,
        requests[3].id,
        requests[1].id,
        requests[2].id,
    ]

    assert all(isinstance(item, ServiceRequest) for item in results)
    assert all(isinstance(item.date_requested, date) for item in results)


def test_find_recent_returns_empty_list_when_no_requests_exist(tmp_path):
    database_path = tmp_path / "csms.db"
    repository = ServiceRequestRepository(database_path)

    assert repository.find_recent() == []
