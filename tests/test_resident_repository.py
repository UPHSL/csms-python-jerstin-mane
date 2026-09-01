from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository


def make_valid_resident(**overrides):
    data = {
        "first_name": "Juan",
        "last_name": "Dela Cruz",
        "address": "Barangay Santo Tomas",
        "contact_number": "09171234567",
        "email": "juan@example.com",
        "status": "Active",
    }

    data.update(overrides)

    return Resident(**data)


def test_save_resident_succeeds(tmp_path):
    database_path = tmp_path / "test.db"
    repository = ResidentRepository(database_path)

    resident = make_valid_resident()

    saved_resident = repository.save(resident)

    assert saved_resident is resident
    assert saved_resident.id is not None


def test_saved_resident_receives_database_generated_id(tmp_path):
    database_path = tmp_path / "test.db"
    repository = ResidentRepository(database_path)

    resident = make_valid_resident()

    assert resident.id is None

    repository.save(resident)

    assert resident.id is not None
    assert isinstance(resident.id, int)


def test_find_by_id_returns_saved_resident(tmp_path):
    database_path = tmp_path / "test.db"
    repository = ResidentRepository(database_path)

    resident = make_valid_resident()
    repository.save(resident)

    found_resident = repository.find_by_id(resident.id)

    assert found_resident is not None
    assert found_resident.id == resident.id


def test_saved_resident_information_is_preserved(tmp_path):
    database_path = tmp_path / "test.db"
    repository = ResidentRepository(database_path)

    resident = make_valid_resident()
    repository.save(resident)

    found_resident = repository.find_by_id(resident.id)

    assert found_resident.first_name == "Juan"
    assert found_resident.last_name == "Dela Cruz"
    assert found_resident.address == "Barangay Santo Tomas"
    assert found_resident.contact_number == "09171234567"
    assert found_resident.email == "juan@example.com"
    assert found_resident.status == "Active"


def test_active_status_is_preserved(tmp_path):
    database_path = tmp_path / "test.db"
    repository = ResidentRepository(database_path)

    resident = make_valid_resident(status="Active")
    repository.save(resident)

    found_resident = repository.find_by_id(resident.id)

    assert found_resident.status == "Active"


def test_find_by_id_returns_none_for_missing_resident(tmp_path):
    database_path = tmp_path / "test.db"
    repository = ResidentRepository(database_path)

    found_resident = repository.find_by_id(999999)

    assert found_resident is None


def test_resident_persists_across_repository_instances(tmp_path):
    database_path = tmp_path / "test.db"

    first_repository = ResidentRepository(database_path)

    resident = make_valid_resident()
    first_repository.save(resident)

    second_repository = ResidentRepository(database_path)

    found_resident = second_repository.find_by_id(resident.id)

    assert found_resident is not None
    assert found_resident.id == resident.id
    assert found_resident.first_name == resident.first_name
    assert found_resident.contact_number == resident.contact_number


def test_inactive_resident_status_is_preserved(tmp_path):
    database_path = tmp_path / "test.db"
    repository = ResidentRepository(database_path)

    resident = make_valid_resident(status="Inactive")
    repository.save(resident)

    found_resident = repository.find_by_id(resident.id)

    assert found_resident is not None
    assert found_resident.status == "Inactive"