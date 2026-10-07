from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.service_request_status_service import (
    ServiceRequestStatusService,
)


def create_active_resident(database_path):
    repository = ResidentRepository(database_path)

    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="123 Test Street",
        contact_number="09123456789",
        email="juan@example.com",
        status="Active",
    )

    return repository.save(resident)


def create_request(database_path, resident_id, **overrides):
    repository = ServiceRequestRepository(database_path)

    values = {
        "resident_id": resident_id,
        "service_type": "Health Assistance",
        "description": "Medical support",
        "date_requested": date(2026, 10, 2),
        "status": "Pending",
    }

    values.update(overrides)

    request = ServiceRequest(**values)

    return repository.save(request)


def create_status_service(database_path):
    repository = ServiceRequestRepository(database_path)

    return ServiceRequestStatusService(repository)


def test_pending_to_in_progress_succeeds_and_persists(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(database_path, resident.id)
    service = create_status_service(database_path)

    result = service.update_status(request.id, "In Progress")

    assert result.status == "success"
    assert result.service_request.status == "In Progress"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "In Progress"


def test_pending_to_cancelled_succeeds(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(database_path, resident.id)
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Cancelled")

    assert result.status == "success"
    assert result.service_request.status == "Cancelled"


def test_in_progress_to_completed_succeeds(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(
        database_path,
        resident.id,
        status="In Progress",
    )
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Completed")

    assert result.status == "success"
    assert result.service_request.status == "Completed"


def test_in_progress_to_cancelled_succeeds(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(
        database_path,
        resident.id,
        status="In Progress",
    )
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Cancelled")

    assert result.status == "success"
    assert result.service_request.status == "Cancelled"


def test_pending_to_completed_is_rejected_and_remains_pending(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(database_path, resident.id)
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Completed")

    assert result.status == "invalid_transition"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "Pending"


def test_in_progress_to_pending_is_rejected_and_remains_in_progress(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(
        database_path,
        resident.id,
        status="In Progress",
    )
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Pending")

    assert result.status == "invalid_transition"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "In Progress"


def test_completed_request_is_terminal(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(
        database_path,
        resident.id,
        status="Completed",
    )
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Cancelled")

    assert result.status == "invalid_transition"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "Completed"


def test_cancelled_request_is_terminal(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(
        database_path,
        resident.id,
        status="Cancelled",
    )
    service = create_status_service(database_path)

    result = service.update_status(request.id, "In Progress")

    assert result.status == "invalid_transition"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "Cancelled"


def test_unsupported_status_is_rejected(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(database_path, resident.id)
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Approved")

    assert result.status == "unsupported_status"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "Pending"


def test_nonexistent_request_returns_not_found(tmp_path):
    database_path = tmp_path / "csms.db"
    service = create_status_service(database_path)

    result = service.update_status(999, "In Progress")

    assert result.status == "not_found"
    assert result.service_request is None

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(999)

    assert found is None


def test_status_update_preserves_non_status_fields(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(
        database_path,
        resident.id,
        service_type="Food Assistance",
        description="Monthly food support",
        date_requested=date(2026, 9, 30),
    )
    service = create_status_service(database_path)

    result = service.update_status(request.id, "In Progress")

    assert result.status == "success"

    updated = result.service_request

    assert updated.id == request.id
    assert updated.resident_id == resident.id
    assert updated.service_type == "Food Assistance"
    assert updated.description == "Monthly food support"
    assert updated.date_requested == date(2026, 9, 30)
    assert updated.status == "In Progress"


def test_invalid_transition_does_not_modify_persistence(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(database_path, resident.id)
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Completed")

    assert result.status == "invalid_transition"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "Pending"


def test_same_status_is_rejected(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(database_path, resident.id)
    service = create_status_service(database_path)

    result = service.update_status(request.id, "Pending")

    assert result.status == "invalid_transition"

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(request.id)

    assert found.status == "Pending"


def test_valid_status_transition_persists_across_repository_instances(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    request = create_request(database_path, resident.id)
    service = create_status_service(database_path)

    result = service.update_status(request.id, "In Progress")

    assert result.status == "success"

    second_repository = ServiceRequestRepository(database_path)
    found = second_repository.find_by_id(request.id)

    assert found is not None
    assert found.status == "In Progress"