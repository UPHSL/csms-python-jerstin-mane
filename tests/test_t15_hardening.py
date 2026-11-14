from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository


def configure_repositories(client, tmp_path):
    database_path = tmp_path / "t15-test.db"
    client.application.config["DATABASE_PATH"] = database_path

    return (
        ResidentRepository(database_path),
        ServiceRequestRepository(database_path),
    )


def create_resident(repository, **overrides):
    values = {
        "first_name": "Juan",
        "last_name": "Dela Cruz",
        "address": "Binan, Laguna",
        "contact_number": "09123456789",
        "email": "juan@example.com",
        "status": "Active",
    }
    values.update(overrides)
    return repository.save(Resident(**values))


def create_request(repository, resident_id, **overrides):
    values = {
        "resident_id": resident_id,
        "service_type": "Health Assistance",
        "description": "Medical support",
        "date_requested": date(2026, 11, 10),
        "status": "Pending",
    }
    values.update(overrides)
    return repository.save(ServiceRequest(**values))


def test_malformed_resident_id_submission_is_rejected_without_saving(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    response = client.post(
        "/service-requests/new",
        data={
            "resident_id": "not-a-number",
            "service_type": "Health Assistance",
            "description": "Medical support",
            "date_requested": "2026-11-10",
        },
    )

    assert response.status_code == 200
    assert requests.find_all() == []
    assert residents.find_by_id(resident.id) is not None


def test_rejected_terminal_request_mutation_preserves_record(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)
    saved = create_request(
        requests,
        resident.id,
        status="Completed",
    )

    response = client.post(
        f"/service-requests/{saved.id}/process"
    )

    unchanged = requests.find_by_id(saved.id)

    assert response.status_code == 302
    assert unchanged is not None
    assert unchanged.status == "Completed"
    assert unchanged.resident_id == saved.resident_id
    assert unchanged.service_type == saved.service_type
    assert unchanged.description == saved.description
    assert unchanged.date_requested == saved.date_requested


def test_repeated_request_detail_gets_preserve_all_persisted_fields(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)
    saved = create_request(requests, resident.id)

    before = requests.find_by_id(saved.id)

    for _ in range(3):
        response = client.get(f"/service-requests/{saved.id}")
        assert response.status_code == 200

    after = requests.find_by_id(saved.id)

    assert before is not None
    assert after is not None
    assert (
        after.id,
        after.resident_id,
        after.service_type,
        after.description,
        after.date_requested,
        after.status,
    ) == (
        before.id,
        before.resident_id,
        before.service_type,
        before.description,
        before.date_requested,
        before.status,
    )


def test_resident_registration_request_submission_and_dashboard_work_together(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)

    registration_response = client.post(
        "/residents/register",
        data={
            "first_name": "Maria",
            "last_name": "Santos",
            "address": "Binan, Laguna",
            "contact_number": "09987654321",
            "email": "maria@example.com",
        },
    )

    assert registration_response.status_code == 302

    registered = residents.find_all()
    assert len(registered) == 1

    submission_response = client.post(
        "/service-requests/new",
        data={
            "resident_id": str(registered[0].id),
            "service_type": "Food Assistance",
            "description": "Monthly food support",
            "date_requested": "2026-11-10",
        },
    )

    assert submission_response.status_code == 302

    saved_requests = requests.find_all()
    assert len(saved_requests) == 1
    assert saved_requests[0].resident_id == registered[0].id

    dashboard_response = client.get("/dashboard")

    assert dashboard_response.status_code == 200
    assert b"Food Assistance" in dashboard_response.data


def test_sql_injection_like_search_input_does_not_return_unrelated_requests(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(
        requests,
        resident.id,
        service_type="Health Assistance",
    )
    create_request(
        requests,
        resident.id,
        service_type="Food Assistance",
    )

    response = client.get(
        "/service-requests?q=%27%20OR%201%3D1%20--"
    )

    assert response.status_code == 200
    assert b"Health Assistance" not in response.data
    assert b"Food Assistance" not in response.data
