from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_update_service import ResidentUpdateService
from csms.services.resident_validator import ResidentValidator


def create_service(tmp_path):
    repository = ResidentRepository(tmp_path / "test.db")
    validator = ResidentValidator()
    return repository, ResidentUpdateService(validator, repository)


def create_resident(
    repository,
    first_name="Juan",
    last_name="Dela Cruz",
    address="Santa Rosa, Laguna",
    contact_number="09171234567",
    email="juan@example.com",
    status="Active",
):
    resident = Resident(
        first_name=first_name,
        last_name=last_name,
        address=address,
        contact_number=contact_number,
        email=email,
        status=status,
    )
    return repository.save(resident)


def test_valid_update_succeeds(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    result = service.update_resident(
        resident.id,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    assert result.status == "success"
    assert result.resident is not None
    assert result.resident.first_name == "Maria"
    assert result.resident.last_name == "Santos"


def test_update_preserves_id(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    result = service.update_resident(
        resident.id,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    assert result.resident is not None
    assert result.resident.id == resident.id


def test_update_persists_all_permitted_fields(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    service.update_resident(
        resident.id,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    updated = repository.find_by_id(resident.id)

    assert updated is not None
    assert updated.first_name == "Maria"
    assert updated.last_name == "Santos"
    assert updated.address == "Biñan, Laguna"
    assert updated.contact_number == "09987654321"
    assert updated.email == "maria@example.com"


def test_update_preserves_status(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(
        repository,
        status="Inactive",
    )

    result = service.update_resident(
        resident.id,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    assert result.resident is not None
    assert result.resident.status == "Inactive"

    updated = repository.find_by_id(resident.id)

    assert updated is not None
    assert updated.status == "Inactive"


def test_invalid_update_fails(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    result = service.update_resident(
        resident.id,
        "",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    assert result.status == "validation_failed"
    assert "first_name" in result.errors


def test_invalid_update_does_not_modify_persisted_information(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    result = service.update_resident(
        resident.id,
        "",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    assert result.status == "validation_failed"

    unchanged = repository.find_by_id(resident.id)

    assert unchanged is not None
    assert unchanged.first_name == "Juan"
    assert unchanged.last_name == "Dela Cruz"
    assert unchanged.address == "Santa Rosa, Laguna"
    assert unchanged.contact_number == "09171234567"
    assert unchanged.email == "juan@example.com"


def test_nonexistent_resident_is_handled_safely(tmp_path):
    repository, service = create_service(tmp_path)

    result = service.update_resident(
        9999,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    assert result.status == "not_found"
    assert result.resident is None


def test_nonexistent_update_does_not_create_resident(tmp_path):
    repository, service = create_service(tmp_path)

    result = service.update_resident(
        9999,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    assert result.status == "not_found"
    assert repository.find_by_id(9999) is None
    assert repository.find_all() == []


def test_updated_resident_is_visible_through_querying(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    service.update_resident(
        resident.id,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09987654321",
        "maria@example.com",
    )

    results = repository.search_by_name("Maria")

    assert len(results) == 1
    assert results[0].id == resident.id
    assert results[0].first_name == "Maria"
    assert results[0].last_name == "Santos"


def test_update_preserves_leading_zero_contact_id_and_status(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(
        repository,
        status="Inactive",
    )

    result = service.update_resident(
        resident.id,
        "Maria",
        "Santos",
        "Biñan, Laguna",
        "09123456789",
        "maria@example.com",
    )

    assert result.resident is not None
    assert result.resident.id == resident.id
    assert result.resident.status == "Inactive"
    assert result.resident.contact_number == "09123456789"

    updated = repository.find_by_id(resident.id)

    assert updated is not None
    assert updated.id == resident.id
    assert updated.status == "Inactive"
    assert updated.contact_number == "09123456789"