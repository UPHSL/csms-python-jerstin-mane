import sqlite3

from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_registration_service import (
    ResidentRegistrationService,
)
from csms.services.resident_validator import ResidentValidator


def create_service(database_path):
    repository = ResidentRepository(database_path)
    validator = ResidentValidator()

    return ResidentRegistrationService(
        validator=validator,
        repository=repository,
    )


def create_valid_resident():
    return Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Santa Rosa, Laguna",
        contact_number="09123456789",
        email="juan@example.com",
    )


def test_valid_registration_succeeds(tmp_path):
    service = create_service(tmp_path / "test.db")
    resident = create_valid_resident()

    result = service.register_resident(resident)

    assert result.success is True
    assert result.resident is not None
    assert result.errors == []


def test_registration_assigns_generated_id(tmp_path):
    service = create_service(tmp_path / "test.db")
    resident = create_valid_resident()

    result = service.register_resident(resident)

    assert result.resident is not None
    assert result.resident.id is not None
    assert result.resident.id > 0


def test_registered_resident_can_be_retrieved(tmp_path):
    database_path = tmp_path / "test.db"
    service = create_service(database_path)

    resident = create_valid_resident()
    result = service.register_resident(resident)

    repository = ResidentRepository(database_path)
    found = repository.find_by_id(result.resident.id)

    assert found is not None
    assert found.id == result.resident.id


def test_registration_preserves_resident_information(tmp_path):
    service = create_service(tmp_path / "test.db")
    resident = create_valid_resident()

    result = service.register_resident(resident)

    saved = result.resident

    assert saved is not None
    assert saved.first_name == resident.first_name
    assert saved.last_name == resident.last_name
    assert saved.address == resident.address
    assert saved.contact_number == resident.contact_number
    assert saved.email == resident.email


def test_registration_preserves_default_active_status(tmp_path):
    service = create_service(tmp_path / "test.db")
    resident = create_valid_resident()

    result = service.register_resident(resident)

    assert result.resident is not None
    assert result.resident.status == "Active"


def test_invalid_registration_fails(tmp_path):
    service = create_service(tmp_path / "test.db")

    resident = create_valid_resident()
    resident.first_name = ""

    result = service.register_resident(resident)

    assert result.success is False
    assert result.resident is None
    assert result.errors


def test_invalid_resident_is_not_persisted(tmp_path):
    database_path = tmp_path / "test.db"
    service = create_service(database_path)

    resident = create_valid_resident()
    resident.first_name = ""

    result = service.register_resident(resident)

    connection = sqlite3.connect(database_path)
    count = connection.execute(
        "SELECT COUNT(*) FROM residents"
    ).fetchone()[0]
    connection.close()

    assert result.success is False
    assert count == 0


def test_validation_failure_identifies_invalid_field(tmp_path):
    service = create_service(tmp_path / "test.db")

    resident = create_valid_resident()
    resident.first_name = ""

    result = service.register_resident(resident)

    assert "first_name" in result.errors