from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_deactivation_service import ResidentDeactivationService


def create_service(tmp_path):
    repository = ResidentRepository(tmp_path / "test.db")
    return repository, ResidentDeactivationService(repository)


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


def test_active_resident_can_be_deactivated(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    result = service.deactivate_resident(resident.id)

    assert result.status == "success"
    assert result.resident is not None
    assert result.resident.status == "Inactive"


def test_deactivation_persists_inactive_status(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    service.deactivate_resident(resident.id)

    deactivated = repository.find_by_id(resident.id)

    assert deactivated is not None
    assert deactivated.status == "Inactive"


def test_deactivation_preserves_id(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    result = service.deactivate_resident(resident.id)

    assert result.resident is not None
    assert result.resident.id == resident.id

    persisted = repository.find_by_id(resident.id)

    assert persisted is not None
    assert persisted.id == resident.id


def test_deactivation_preserves_personal_and_contact_information(
    tmp_path,
):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    service.deactivate_resident(resident.id)

    deactivated = repository.find_by_id(resident.id)

    assert deactivated is not None
    assert deactivated.first_name == "Juan"
    assert deactivated.last_name == "Dela Cruz"
    assert deactivated.address == "Santa Rosa, Laguna"
    assert deactivated.contact_number == "09171234567"
    assert deactivated.email == "juan@example.com"


def test_deactivated_resident_remains_persisted_and_retrievable(
    tmp_path,
):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    service.deactivate_resident(resident.id)

    retrieved = repository.find_by_id(resident.id)

    assert retrieved is not None
    assert retrieved.id == resident.id
    assert retrieved.status == "Inactive"


def test_deactivated_resident_remains_available_through_search_and_list(
    tmp_path,
):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    service.deactivate_resident(resident.id)

    search_results = repository.search_by_name("Juan")
    all_residents = repository.find_all()

    assert len(search_results) == 1
    assert search_results[0].id == resident.id
    assert search_results[0].status == "Inactive"

    assert len(all_residents) == 1
    assert all_residents[0].id == resident.id
    assert all_residents[0].status == "Inactive"


def test_already_inactive_resident_is_handled_safely(tmp_path):
    repository, service = create_service(tmp_path)
    resident = create_resident(
        repository,
        status="Inactive",
    )

    result = service.deactivate_resident(resident.id)

    assert result.status == "already_inactive"
    assert result.resident is not None
    assert result.resident.id == resident.id
    assert result.resident.status == "Inactive"


def test_nonexistent_resident_is_handled_safely(tmp_path):
    repository, service = create_service(tmp_path)

    result = service.deactivate_resident(9999)

    assert result.status == "not_found"
    assert result.resident is None


def test_nonexistent_deactivation_does_not_create_or_delete_resident(
    tmp_path,
):
    repository, service = create_service(tmp_path)
    resident = create_resident(repository)

    result = service.deactivate_resident(9999)

    assert result.status == "not_found"
    assert repository.find_by_id(9999) is None

    existing = repository.find_by_id(resident.id)

    assert existing is not None
    assert existing.id == resident.id
    assert existing.status == "Active"


def test_deactivating_one_resident_does_not_affect_another(tmp_path):
    repository, service = create_service(tmp_path)
    resident_one = create_resident(
        repository,
        first_name="Juan",
        last_name="Dela Cruz",
        contact_number="09171234567",
        email="juan@example.com",
    )
    resident_two = create_resident(
        repository,
        first_name="Maria",
        last_name="Santos",
        contact_number="09987654321",
        email="maria@example.com",
    )

    service.deactivate_resident(resident_one.id)

    first = repository.find_by_id(resident_one.id)
    second = repository.find_by_id(resident_two.id)

    assert first is not None
    assert second is not None

    assert first.status == "Inactive"
    assert second.status == "Active"
    assert second.first_name == "Maria"
    assert second.last_name == "Santos"
    assert second.contact_number == "09987654321"
    assert second.email == "maria@example.com"
