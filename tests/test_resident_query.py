from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_query_service import ResidentQueryService


def create_service(tmp_path):
    repository = ResidentRepository(tmp_path / "test.db")
    return ResidentQueryService(repository)


def create_resident(
    first_name,
    last_name,
    address="Test Address",
    contact_number="09123456789",
    email="test@example.com",
    status="Active",
):
    return Resident(
        first_name=first_name,
        last_name=last_name,
        address=address,
        contact_number=contact_number,
        email=email,
        status=status,
    )


def test_list_all_persisted_residents(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Juan", "Dela Cruz"))
    repository.save(create_resident("Maria", "Santos"))

    residents = service.list_residents()

    assert len(residents) == 2
    assert {resident.first_name for resident in residents} == {"Juan", "Maria"}


def test_list_empty_database_returns_empty_list(tmp_path):
    service = create_service(tmp_path)

    residents = service.list_residents()

    assert residents == []


def test_list_residents_uses_required_order(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Zara", "Santos"))
    repository.save(create_resident("Ana", "Dela Cruz"))
    repository.save(create_resident("Ben", "Dela Cruz"))
    repository.save(create_resident("Carla", "Santos"))

    residents = service.list_residents()

    assert [
        (resident.last_name, resident.first_name)
        for resident in residents
    ] == [
        ("Dela Cruz", "Ana"),
        ("Dela Cruz", "Ben"),
        ("Santos", "Carla"),
        ("Santos", "Zara"),
    ]


def test_search_first_name_partial_and_case_insensitive(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Jerstin", "Mane"))
    repository.save(create_resident("Jerald", "Santos"))
    repository.save(create_resident("Maria", "Cruz"))

    residents = service.search_residents("JER")

    assert {resident.first_name for resident in residents} == {
        "Jerstin",
        "Jerald",
    }


def test_search_last_name_partial_and_case_insensitive(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Juan", "Mane"))
    repository.save(create_resident("Maria", "Manera"))
    repository.save(create_resident("Pedro", "Santos"))

    residents = service.search_residents("MAN")

    assert {resident.last_name for resident in residents} == {
        "Mane",
        "Manera",
    }


def test_blank_search_returns_all_residents(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Juan", "Dela Cruz"))
    repository.save(create_resident("Maria", "Santos"))

    residents = service.search_residents("   ")

    assert len(residents) == 2


def test_search_with_no_match_returns_empty_list(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Juan", "Dela Cruz"))
    repository.save(create_resident("Maria", "Santos"))

    residents = service.search_residents("ZZZZ")

    assert residents == []


def test_search_preserves_resident_information(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    resident = repository.save(
        create_resident(
            "Juan",
            "Mane",
            address="Laguna",
            contact_number="09123456789",
            email="juan@example.com",
            status="Inactive",
        )
    )

    residents = service.search_residents("Juan")

    assert len(residents) == 1
    result = residents[0]

    assert result.id == resident.id
    assert result.first_name == "Juan"
    assert result.last_name == "Mane"
    assert result.address == "Laguna"
    assert result.contact_number == "09123456789"
    assert result.email == "juan@example.com"
    assert result.status == "Inactive"


def test_list_includes_active_and_inactive_residents(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Juan", "Mane", status="Active"))
    repository.save(create_resident("Maria", "Santos", status="Inactive"))

    residents = service.list_residents()

    assert {resident.status for resident in residents} == {
        "Active",
        "Inactive",
    }


def test_search_does_not_duplicate_resident_when_both_names_match(tmp_path):
    service = create_service(tmp_path)
    repository = service.repository

    repository.save(create_resident("Ana", "Ana"))

    residents = service.search_residents("Ana")

    assert len(residents) == 1