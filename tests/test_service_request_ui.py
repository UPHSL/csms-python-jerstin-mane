from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


def configure_repositories(client, tmp_path):
    database_path = tmp_path / "test.db"
    client.application.config["DATABASE_PATH"] = database_path

    return (
        ResidentRepository(database_path),
        ServiceRequestRepository(database_path),
    )


def create_resident(repository, status="Active"):
    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Santa Rosa, Laguna",
        contact_number="09123456789",
        email="juan@example.com",
        status=status,
    )

    return repository.save(resident)


def create_request(repository, resident_id, **overrides):
    values = {
        "resident_id": resident_id,
        "service_type": "Health Assistance",
        "description": "Medical support",
        "date_requested": date(2026, 11, 10),
        "status": "Pending",
    }

    values.update(overrides)

    service_request = ServiceRequest(**values)

    return repository.save(service_request)


def valid_submission_data(resident_id):
    return {
        "resident_id": str(resident_id),
        "service_type": "Food Assistance",
        "description": "Monthly food support",
        "date_requested": "2026-11-10",
    }


def test_service_request_list_page_loads(client, tmp_path):
    configure_repositories(client, tmp_path)

    response = client.get("/service-requests")

    assert response.status_code == 200
    assert b"Service Request Management" in response.data
    assert b"Submit Service Request" in response.data
    assert b"Search by Service Type or Description" in response.data
    assert b"Filter by Status" in response.data
    assert b"Resident Management" in response.data


def test_persisted_service_requests_are_displayed(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    saved = create_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="Monthly food support",
    )

    response = client.get("/service-requests")

    assert response.status_code == 200
    assert str(saved.id).encode() in response.data
    assert str(resident.id).encode() in response.data
    assert b"Food Assistance" in response.data
    assert b"Monthly food support" in response.data
    assert b"2026-11-10" in response.data
    assert b"Pending" in response.data


def test_service_request_ordering_is_preserved(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(
        repository,
        resident.id,
        description="Oldest request description",
        date_requested=date(2026, 10, 1),
    )

    create_request(
        repository,
        resident.id,
        description="Newer first request",
        date_requested=date(2026, 11, 10),
    )

    create_request(
        repository,
        resident.id,
        description="Newest second request",
        date_requested=date(2026, 11, 10),
    )

    response = client.get("/service-requests")

    assert response.status_code == 200

    newest_position = response.data.index(b"Newest second request")
    newer_position = response.data.index(b"Newer first request")
    oldest_position = response.data.index(b"Oldest request description")

    assert newest_position < newer_position < oldest_position


def test_partial_case_insensitive_search_works(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(
        repository,
        resident.id,
        service_type="Medical Assistance",
        description="Health consultation",
    )

    create_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="School supplies",
    )

    response = client.get("/service-requests?q=MEDICAL")

    assert response.status_code == 200
    assert b"Medical Assistance" in response.data
    assert b"Food Assistance" not in response.data
    assert b'value="MEDICAL"' in response.data


def test_status_filter_returns_only_matching_requests(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(
        repository,
        resident.id,
        service_type="Pending Assistance",
        status="Pending",
    )

    create_request(
        repository,
        resident.id,
        service_type="Completed Assistance",
        status="Completed",
    )

    response = client.get("/service-requests?status=Pending")

    assert response.status_code == 200
    assert b"Pending Assistance" in response.data
    assert b"Completed Assistance" not in response.data
    assert b'value="Pending"' in response.data
    assert b"selected" in response.data


def test_combined_search_and_status_filter_works(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(
        repository,
        resident.id,
        service_type="Medical Pending",
        description="Medical consultation",
        status="Pending",
    )

    create_request(
        repository,
        resident.id,
        service_type="Medical Completed",
        description="Medical consultation",
        status="Completed",
    )

    create_request(
        repository,
        resident.id,
        service_type="Food Pending",
        description="Food support",
        status="Pending",
    )

    response = client.get(
        "/service-requests?q=medical&status=Pending"
    )

    assert response.status_code == 200
    assert b"Medical Pending" in response.data
    assert b"Medical Completed" not in response.data
    assert b"Food Pending" not in response.data
    assert b'value="medical"' in response.data
    assert b'value="Pending"' in response.data
    assert b"selected" in response.data

def test_submission_form_is_accessible(client, tmp_path):
    configure_repositories(client, tmp_path)

    response = client.get("/service-requests/new")

    assert response.status_code == 200
    assert b'name="resident_id"' in response.data
    assert b'name="service_type"' in response.data
    assert b'name="description"' in response.data
    assert b'name="date_requested"' in response.data
    assert b'name="id"' not in response.data
    assert b'name="status"' not in response.data
    assert b"Initial Status:</strong> Pending" in response.data


def test_valid_submission_persists_a_pending_request(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    response = client.post(
        "/service-requests/new",
        data=valid_submission_data(resident.id),
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/service-requests")

    saved_requests = repository.find_all()

    assert len(saved_requests) == 1

    saved = saved_requests[0]

    assert saved.id is not None
    assert saved.id > 0
    assert saved.resident_id == resident.id
    assert saved.service_type == "Food Assistance"
    assert saved.description == "Monthly food support"
    assert saved.date_requested == date(2026, 11, 10)
    assert saved.status == "Pending"


def test_invalid_submission_shows_validation_feedback(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    data = valid_submission_data(resident.id)
    data["service_type"] = "   "

    response = client.post(
        "/service-requests/new",
        data=data,
    )

    assert response.status_code == 200
    assert b"Service type is required." in response.data
    assert repository.find_all() == []
    assert b'Monthly food support' in response.data


def test_missing_resident_submission_is_rejected(client, tmp_path):
    _, repository = configure_repositories(client, tmp_path)

    response = client.post(
        "/service-requests/new",
        data=valid_submission_data(9999),
    )

    assert response.status_code == 200
    assert b"Resident not found." in response.data
    assert repository.find_all() == []


def test_inactive_resident_submission_is_rejected(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents, status="Inactive")

    response = client.post(
        "/service-requests/new",
        data=valid_submission_data(resident.id),
    )

    assert response.status_code == 200
    assert (
        b"Inactive Residents cannot submit new Service Requests."
        in response.data
    )
    assert repository.find_all() == []


def test_existing_service_request_details_can_be_viewed(
    client,
    tmp_path,
):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    saved = create_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="Monthly food support for the resident.",
        status="In Progress",
    )

    response = client.get(f"/service-requests/{saved.id}")

    assert response.status_code == 200
    assert str(saved.id).encode() in response.data
    assert str(resident.id).encode() in response.data
    assert b"Food Assistance" in response.data
    assert b"Monthly food support for the resident." in response.data
    assert b"2026-11-10" in response.data
    assert b"In Progress" in response.data


def test_missing_service_request_view_and_action_return_not_found(
    client,
    tmp_path,
):
    configure_repositories(client, tmp_path)

    view_response = client.get("/service-requests/9999")
    action_response = client.post("/service-requests/9999/process")

    assert view_response.status_code == 404
    assert action_response.status_code == 404


def test_pending_request_can_start_processing(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    saved = create_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="Monthly food support",
    )

    response = client.post(
        f"/service-requests/{saved.id}/process"
    )

    assert response.status_code == 302

    updated = repository.find_by_id(saved.id)

    assert updated is not None
    assert updated.status == "In Progress"
    assert updated.id == saved.id
    assert updated.resident_id == resident.id
    assert updated.service_type == "Food Assistance"
    assert updated.description == "Monthly food support"
    assert updated.date_requested == date(2026, 11, 10)


def test_pending_request_can_be_cancelled(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)
    saved = create_request(repository, resident.id)

    response = client.post(
        f"/service-requests/{saved.id}/cancel"
    )

    assert response.status_code == 302

    updated = repository.find_by_id(saved.id)

    assert updated is not None
    assert updated.status == "Cancelled"
    assert updated.id == saved.id
    assert updated.resident_id == resident.id


def test_in_progress_request_can_be_completed(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    saved = create_request(
        repository,
        resident.id,
        status="In Progress",
    )

    response = client.post(
        f"/service-requests/{saved.id}/complete"
    )

    assert response.status_code == 302

    updated = repository.find_by_id(saved.id)

    assert updated is not None
    assert updated.status == "Completed"
    assert updated.id == saved.id


def test_in_progress_request_can_be_cancelled(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    saved = create_request(
        repository,
        resident.id,
        status="In Progress",
    )

    response = client.post(
        f"/service-requests/{saved.id}/cancel"
    )

    assert response.status_code == 302

    updated = repository.find_by_id(saved.id)

    assert updated is not None
    assert updated.status == "Cancelled"
    assert updated.id == saved.id


def test_invalid_direct_transition_is_rejected(client, tmp_path):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)
    saved = create_request(repository, resident.id)

    response = client.post(
        f"/service-requests/{saved.id}/complete",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid status transition" in response.data

    unchanged = repository.find_by_id(saved.id)

    assert unchanged is not None
    assert unchanged.status == "Pending"


def test_terminal_requests_remain_visible_searchable_and_viewable(
    client,
    tmp_path,
):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    completed = create_request(
        repository,
        resident.id,
        service_type="Food Assistance",
        description="Monthly food support",
        status="Completed",
    )

    cancelled = create_request(
        repository,
        resident.id,
        service_type="Medical Assistance",
        description="Medical consultation",
        status="Cancelled",
    )

    list_response = client.get("/service-requests")

    assert list_response.status_code == 200
    assert b"Completed" in list_response.data
    assert b"Cancelled" in list_response.data

    search_response = client.get(
        "/service-requests?q=medical&status=Cancelled"
    )

    assert search_response.status_code == 200
    assert b"Medical Assistance" in search_response.data
    assert b"Food Assistance" not in search_response.data

    completed_response = client.get(
        f"/service-requests/{completed.id}"
    )
    cancelled_response = client.get(
        f"/service-requests/{cancelled.id}"
    )

    assert completed_response.status_code == 200
    assert cancelled_response.status_code == 200

    for response in (completed_response, cancelled_response):
        assert b"No further workflow actions are available." in response.data
        assert b"Start Processing" not in response.data
        assert b"Complete Request" not in response.data
        assert b"Cancel Request" not in response.data


def test_get_requests_do_not_change_service_request_state(
    client,
    tmp_path,
):
    residents, repository = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    saved = create_request(repository, resident.id)

    client.get("/service-requests")
    client.get("/service-requests?q=health")
    client.get("/service-requests?status=Pending")
    client.get("/service-requests/new")
    client.get(f"/service-requests/{saved.id}")

    process_response = client.get(
        f"/service-requests/{saved.id}/process"
    )
    complete_response = client.get(
        f"/service-requests/{saved.id}/complete"
    )
    cancel_response = client.get(
        f"/service-requests/{saved.id}/cancel"
    )

    assert process_response.status_code == 405
    assert complete_response.status_code == 405
    assert cancel_response.status_code == 405

    unchanged = repository.find_by_id(saved.id)

    assert unchanged is not None
    assert unchanged.status == "Pending"
    assert len(repository.find_all()) == 1
