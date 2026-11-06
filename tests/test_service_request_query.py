from datetime import date

import pytest

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.request_service import ServiceRequestQueryService


def create_query_service(database_path):
    repository = ServiceRequestRepository(database_path)
    return ServiceRequestQueryService(repository)


def create_resident(database_path):
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


def save_request(repository, resident_id, **overrides):
    request = create_request(resident_id, **overrides)
    return repository.save(request)


def test_list_requests_returns_all_persisted_requests(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    first = save_request(repository, resident.id)
    second = save_request(
        repository,
        resident.id,
        service_type="Food Assistance",
    )

    results = service.list_requests()

    assert len(results) == 2
    assert {request.id for request in results} == {
        first.id,
        second.id,
    }


def test_list_requests_returns_empty_list_when_no_requests_exist(tmp_path):
    database_path = tmp_path / "csms.db"
    service = create_query_service(database_path)

    results = service.list_requests()

    assert results == []


def test_list_requests_uses_date_and_id_descending_order(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    older = save_request(
        repository,
        resident.id,
        date_requested=date(2026, 9, 30),
    )

    newer_first = save_request(
        repository,
        resident.id,
        date_requested=date(2026, 10, 2),
    )

    newer_second = save_request(
        repository,
        resident.id,
        date_requested=date(2026, 10, 2),
    )

    results = service.list_requests()

    assert [request.id for request in results] == [
        newer_second.id,
        newer_first.id,
        older.id,
    ]


def test_get_request_returns_existing_request_by_id(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    saved = save_request(repository, resident.id)

    result = service.get_request(saved.id)

    assert result is not None
    assert result.id == saved.id


def test_get_request_returns_none_for_missing_id_without_creating_record(
    tmp_path,
):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    save_request(repository, resident.id)

    result = service.get_request(999)

    assert result is None
    assert len(service.list_requests()) == 1


def test_search_matches_partial_service_type_case_insensitively(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    matching = save_request(
        repository,
        resident.id,
        service_type="Medical Assistance",
        description="Health consultation",
    )

    save_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="School supplies",
    )

    results = service.list_requests(search_term="MEDICAL")

    assert [request.id for request in results] == [matching.id]


def test_search_matches_partial_description_case_insensitively(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    matching = save_request(
        repository,
        resident.id,
        description="Monthly medicine support",
    )

    save_request(
        repository,
        resident.id,
        description="School supplies",
    )

    results = service.list_requests(search_term="MEDICINE")

    assert [request.id for request in results] == [matching.id]


def test_blank_search_returns_all_requests(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    save_request(repository, resident.id)
    save_request(
        repository,
        resident.id,
        service_type="Food Assistance",
    )

    results = service.list_requests(search_term="   ")

    assert len(results) == 2


def test_search_returns_empty_list_when_no_match_exists(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    save_request(repository, resident.id)

    results = service.list_requests(search_term="Transportation")

    assert results == []


def test_status_filter_returns_only_matching_requests(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    pending = save_request(
        repository,
        resident.id,
        status="Pending",
    )

    save_request(
        repository,
        resident.id,
        status="Completed",
    )

    results = service.list_requests(status="Pending")

    assert [request.id for request in results] == [pending.id]


def test_list_requests_without_status_filter_includes_all_statuses(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    statuses = [
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    ]

    for status in statuses:
        save_request(repository, resident.id, status=status)

    results = service.list_requests()

    assert {request.status for request in results} == set(statuses)


def test_combined_search_and_status_filters_are_applied_together(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    matching = save_request(
        repository,
        resident.id,
        service_type="Medical Assistance",
        description="Health consultation",
        status="Pending",
    )

    save_request(
        repository,
        resident.id,
        service_type="Medical Assistance",
        description="Health consultation",
        status="Completed",
    )

    save_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="Food support",
        status="Pending",
    )

    results = service.list_requests(
        search_term="medical",
        status="Pending",
    )

    assert [request.id for request in results] == [matching.id]


def test_request_matching_both_search_fields_is_not_duplicated(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    matching = save_request(
        repository,
        resident.id,
        service_type="Medical Assistance",
        description="Medical support needed",
    )

    results = service.list_requests(search_term="medical")

    assert len(results) == 1
    assert results[0].id == matching.id


def test_all_request_fields_are_preserved_when_retrieved(tmp_path):
    database_path = tmp_path / "csms.db"
    resident = create_resident(database_path)
    repository = ServiceRequestRepository(database_path)
    service = create_query_service(database_path)

    saved = save_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="Monthly food support",
        date_requested=date(2026, 9, 30),
        status="In Progress",
    )

    result = service.get_request(saved.id)

    assert result.id == saved.id
    assert result.resident_id == resident.id
    assert result.service_type == "Food Assistance"
    assert result.description == "Monthly food support"
    assert result.date_requested == date(2026, 9, 30)
    assert result.status == "In Progress"


def test_unsupported_status_is_rejected(tmp_path):
    database_path = tmp_path / "csms.db"
    service = create_query_service(database_path)

    with pytest.raises(ValueError):
        service.list_requests(status="Approved")
