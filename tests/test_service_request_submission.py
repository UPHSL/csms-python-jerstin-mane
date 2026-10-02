import sqlite3
from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.service_request_submission_service import (
    ServiceRequestSubmissionService,
)
from csms.services.service_request_validator import ServiceRequestValidator


def create_submission_service(database_path):
    resident_repository = ResidentRepository(database_path)
    service_request_repository = ServiceRequestRepository(database_path)
    validator = ServiceRequestValidator()

    return ServiceRequestSubmissionService(
        service_request_repository,
        resident_repository,
        validator,
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


def create_inactive_resident(database_path):
    repository = ResidentRepository(database_path)

    resident = Resident(
        first_name="Maria",
        last_name="Santos",
        address="456 Test Street",
        contact_number="09987654321",
        email="maria@example.com",
        status="Inactive",
    )

    return repository.save(resident)


def create_request(resident_id, **overrides):
    values = {
        "resident_id": resident_id,
        "service_type": "Health Assistance",
        "description": "Medical support",
        "date_requested": date(2026, 10, 2),
        "status": "Pending",
    }

    values.update(overrides)

    return ServiceRequest(**values)


def test_valid_submission_succeeds_for_active_resident(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(resident.id)

    result = service.submit(request)

    assert result.status == "success"
    assert result.service_request is not None


def test_generated_id_is_created_after_persistence(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(resident.id)

    assert request.id is None

    result = service.submit(request)

    assert result.status == "success"
    assert result.service_request.id is not None


def test_persisted_request_can_be_retrieved_by_generated_id(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(resident.id)

    result = service.submit(request)

    repository = ServiceRequestRepository(database_path)
    found = repository.find_by_id(result.service_request.id)

    assert found is not None
    assert found.id == result.service_request.id


def test_all_request_information_is_preserved(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(
        resident.id,
        service_type="Food Assistance",
        description="Monthly food support",
        date_requested=date(2026, 9, 30),
    )

    result = service.submit(request)
    saved = result.service_request

    assert saved.resident_id == resident.id
    assert saved.service_type == "Food Assistance"
    assert saved.description == "Monthly food support"
    assert saved.date_requested == date(2026, 9, 30)
    assert saved.status == "Pending"


def test_submitted_request_status_is_pending(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(resident.id)

    result = service.submit(request)

    assert result.service_request.status == "Pending"


def test_blank_service_type_fails(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(resident.id, service_type="   ")

    result = service.submit(request)

    assert result.status == "validation_failed"
    assert result.service_request is None
    assert "Service type is required." in result.errors


def test_blank_description_fails(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(resident.id, description="   ")

    result = service.submit(request)

    assert result.status == "validation_failed"
    assert result.service_request is None
    assert "Description is required." in result.errors


def test_invalid_request_does_not_reach_persistence(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(
        resident.id,
        service_type="",
        description="",
    )

    result = service.submit(request)

    assert result.status == "validation_failed"

    connection = sqlite3.connect(database_path)
    count = connection.execute(
        "SELECT COUNT(*) FROM service_requests"
    ).fetchone()[0]
    connection.close()

    assert count == 0


def test_nonexistent_resident_prevents_submission(tmp_path):
    database_path = tmp_path / "csms.db"
    service = create_submission_service(database_path)

    request = create_request(999)

    result = service.submit(request)

    assert result.status == "resident_not_found"
    assert result.service_request is None

    connection = sqlite3.connect(database_path)
    count = connection.execute(
        "SELECT COUNT(*) FROM service_requests"
    ).fetchone()[0]
    connection.close()

    assert count == 0


def test_inactive_resident_is_rejected_without_persistence(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_inactive_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(resident.id)

    result = service.submit(request)

    assert result.status == "resident_inactive"
    assert result.service_request is None

    connection = sqlite3.connect(database_path)
    count = connection.execute(
        "SELECT COUNT(*) FROM service_requests"
    ).fetchone()[0]
    connection.close()

    assert count == 0


def test_non_pending_initial_status_is_rejected(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(
        resident.id,
        status="Completed",
    )

    result = service.submit(request)

    assert result.status == "validation_failed"
    assert result.service_request is None


def test_submission_persists_across_separate_repository_access(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)

    first_service = create_submission_service(database_path)
    request = create_request(resident.id)

    result = first_service.submit(request)

    second_repository = ServiceRequestRepository(database_path)
    found = second_repository.find_by_id(result.service_request.id)

    assert found is not None
    assert found.id == result.service_request.id
    assert found.resident_id == resident.id


def test_submission_does_not_modify_resident(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    original_status = resident.status
    original_first_name = resident.first_name
    original_last_name = resident.last_name
    original_address = resident.address
    original_contact_number = resident.contact_number
    original_email = resident.email

    request = create_request(resident.id)

    result = service.submit(request)

    assert result.status == "success"

    repository = ResidentRepository(database_path)
    found = repository.find_by_id(resident.id)

    assert found.status == original_status
    assert found.first_name == original_first_name
    assert found.last_name == original_last_name
    assert found.address == original_address
    assert found.contact_number == original_contact_number
    assert found.email == original_email


def test_invalid_date_is_rejected_without_persistence(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_active_resident(database_path)
    service = create_submission_service(database_path)

    request = create_request(
        resident.id,
        date_requested="2026-10-02",
    )

    result = service.submit(request)

    assert result.status == "validation_failed"
    assert result.service_request is None
    assert "Date requested must be a valid date." in result.errors

    connection = sqlite3.connect(database_path)
    count = connection.execute(
        "SELECT COUNT(*) FROM service_requests"
    ).fetchone()[0]
    connection.close()

    assert count == 0