from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository


def configure_repository(client, tmp_path):
    database_path = tmp_path / "test.db"
    client.application.config["DATABASE_PATH"] = database_path
    return ResidentRepository(database_path)


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


def test_resident_list_page_loads(client, tmp_path):
    configure_repository(client, tmp_path)

    response = client.get("/residents")

    assert response.status_code == 200
    assert b"Resident Management" in response.data
    assert b"Registered Residents" in response.data


def test_persisted_residents_are_displayed(client, tmp_path):
    repository = configure_repository(client, tmp_path)
    create_resident(repository)

    response = client.get("/residents")

    assert response.status_code == 200
    assert b"Juan" in response.data
    assert b"Dela Cruz" in response.data
    assert b"Santa Rosa, Laguna" in response.data
    assert b"09171234567" in response.data
    assert b"juan@example.com" in response.data


def test_partial_case_insensitive_search_works(client, tmp_path):
    repository = configure_repository(client, tmp_path)
    create_resident(repository, first_name="Jerstin", last_name="Mane")
    create_resident(repository, first_name="Maria", last_name="Santos")

    response = client.get("/residents?q=jER")

    assert response.status_code == 200
    assert b"Jerstin" in response.data
    assert b"Mane" in response.data
    assert b"Maria" not in response.data


def test_blank_search_displays_all_residents(client, tmp_path):
    repository = configure_repository(client, tmp_path)
    create_resident(repository, first_name="Juan")
    create_resident(
        repository,
        first_name="Maria",
        last_name="Santos",
        contact_number="09987654321",
        email="maria@example.com",
    )

    response = client.get("/residents?q=")

    assert response.status_code == 200
    assert b"Juan" in response.data
    assert b"Maria" in response.data


def test_registration_form_is_accessible(client, tmp_path):
    configure_repository(client, tmp_path)

    response = client.get("/residents/register")

    assert response.status_code == 200
    assert b'name="first_name"' in response.data
    assert b'name="last_name"' in response.data
    assert b'name="address"' in response.data
    assert b'name="contact_number"' in response.data
    assert b'name="email"' in response.data
    assert b'name="id"' not in response.data
    assert b'name="status"' not in response.data


def test_valid_registration_persists_active_resident(client, tmp_path):
    repository = configure_repository(client, tmp_path)

    response = client.post(
        "/residents/register",
        data={
            "first_name": "Maria",
            "last_name": "Santos",
            "address": "Biñan, Laguna",
            "contact_number": "09987654321",
            "email": "maria@example.com",
        },
    )

    assert response.status_code == 302

    residents = repository.find_all()

    assert len(residents) == 1
    assert residents[0].id is not None
    assert residents[0].id > 0
    assert residents[0].first_name == "Maria"
    assert residents[0].status == "Active"


def test_invalid_registration_shows_errors_without_saving(
    client,
    tmp_path,
):
    repository = configure_repository(client, tmp_path)

    response = client.post(
        "/residents/register",
        data={
            "first_name": "",
            "last_name": "Santos",
            "address": "Biñan, Laguna",
            "contact_number": "12345",
            "email": "invalid-email",
        },
    )

    assert response.status_code == 200
    assert b"First name is required." in response.data
    assert b"valid 11-digit Philippine mobile number" in response.data
    assert b"valid email address" in response.data
    assert repository.find_all() == []


def test_edit_form_displays_resident_values_without_editable_id_or_status(
    client,
    tmp_path,
):
    repository = configure_repository(client, tmp_path)
    resident = create_resident(repository, status="Inactive")

    response = client.get(f"/residents/{resident.id}/edit")

    assert response.status_code == 200
    assert b"Resident ID:" in response.data
    assert str(resident.id).encode() in response.data
    assert b"Inactive" in response.data
    assert b'value="Juan"' in response.data
    assert b'value="Dela Cruz"' in response.data
    assert b'value="09171234567"' in response.data
    assert b'value="juan@example.com"' in response.data
    assert b'name="id"' not in response.data
    assert b'name="status"' not in response.data


def test_valid_update_persists_changes_and_preserves_id_and_status(
    client,
    tmp_path,
):
    repository = configure_repository(client, tmp_path)
    resident = create_resident(repository, status="Inactive")

    response = client.post(
        f"/residents/{resident.id}/edit",
        data={
            "first_name": "Maria",
            "last_name": "Santos",
            "address": "Biñan, Laguna",
            "contact_number": "09987654321",
            "email": "maria@example.com",
        },
    )

    assert response.status_code == 302

    updated = repository.find_by_id(resident.id)

    assert updated is not None
    assert updated.id == resident.id
    assert updated.first_name == "Maria"
    assert updated.last_name == "Santos"
    assert updated.address == "Biñan, Laguna"
    assert updated.contact_number == "09987654321"
    assert updated.email == "maria@example.com"
    assert updated.status == "Inactive"


def test_invalid_update_shows_errors_without_modifying_resident(
    client,
    tmp_path,
):
    repository = configure_repository(client, tmp_path)
    resident = create_resident(repository)

    response = client.post(
        f"/residents/{resident.id}/edit",
        data={
            "first_name": "",
            "last_name": "Santos",
            "address": "Biñan, Laguna",
            "contact_number": "09987654321",
            "email": "maria@example.com",
        },
    )

    assert response.status_code == 200
    assert b"First name is required." in response.data

    unchanged = repository.find_by_id(resident.id)

    assert unchanged is not None
    assert unchanged.first_name == "Juan"
    assert unchanged.last_name == "Dela Cruz"
    assert unchanged.address == "Santa Rosa, Laguna"
    assert unchanged.contact_number == "09171234567"
    assert unchanged.email == "juan@example.com"


def test_missing_resident_edit_returns_not_found(client, tmp_path):
    configure_repository(client, tmp_path)

    response = client.get("/residents/9999/edit")

    assert response.status_code == 404


def test_active_resident_can_be_deactivated_through_interface(
    client,
    tmp_path,
):
    repository = configure_repository(client, tmp_path)
    resident = create_resident(repository)

    response = client.post(
        f"/residents/{resident.id}/deactivate"
    )

    assert response.status_code == 302

    deactivated = repository.find_by_id(resident.id)

    assert deactivated is not None
    assert deactivated.id == resident.id
    assert deactivated.status == "Inactive"


def test_inactive_resident_remains_visible_and_searchable(
    client,
    tmp_path,
):
    repository = configure_repository(client, tmp_path)
    resident = create_resident(repository, status="Inactive")

    response = client.get("/residents?q=Juan")

    assert response.status_code == 200
    assert b"Juan" in response.data
    assert b"Dela Cruz" in response.data
    assert b"Inactive" in response.data
    assert repository.find_by_id(resident.id) is not None


def test_get_pages_do_not_deactivate_residents(client, tmp_path):
    repository = configure_repository(client, tmp_path)
    resident = create_resident(repository)

    client.get("/residents")
    client.get("/residents/register")
    client.get(f"/residents/{resident.id}/edit")

    response = client.get(
        f"/residents/{resident.id}/deactivate"
    )

    assert response.status_code == 405

    unchanged = repository.find_by_id(resident.id)

    assert unchanged is not None
    assert unchanged.status == "Active"
