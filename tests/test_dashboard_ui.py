import re
from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository


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


def get_metric(response, label):
    page = response.get_data(as_text=True)

    pattern = (
        rf'<p class="summary-label">{re.escape(label)}</p>'
        rf'\s*<h3 class="summary-value">(\d+)</h3>'
    )

    match = re.search(pattern, page)

    assert match is not None, f"Dashboard metric not found: {label}"

    return int(match.group(1))


def test_dashboard_page_loads_successfully(client, tmp_path):
    configure_repositories(client, tmp_path)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert b"CSMS Dashboard" in response.data
    assert b"Resident Summary" in response.data
    assert b"Service Request Summary" in response.data
    assert b"Open Service Requests" in response.data
    assert b"Five Most Recent Service Requests" in response.data
    assert b"Resident Management" in response.data
    assert b"Service Requests" in response.data


def test_empty_dashboard_displays_zero_counts(client, tmp_path):
    configure_repositories(client, tmp_path)

    response = client.get("/dashboard")

    assert response.status_code == 200

    expected_metrics = [
        "Total Residents",
        "Active Residents",
        "Inactive Residents",
        "Total Service Requests",
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
        "Open Service Requests",
    ]

    for label in expected_metrics:
        assert get_metric(response, label) == 0

    assert b"No Service Requests available." in response.data


def test_dashboard_displays_correct_total_residents(client, tmp_path):
    residents, _ = configure_repositories(client, tmp_path)

    create_resident(residents)
    create_resident(residents)
    create_resident(residents, status="Inactive")

    response = client.get("/dashboard")

    assert get_metric(response, "Total Residents") == 3


def test_dashboard_displays_correct_resident_status_counts(client, tmp_path):
    residents, _ = configure_repositories(client, tmp_path)

    create_resident(residents)
    create_resident(residents)
    create_resident(residents, status="Inactive")

    response = client.get("/dashboard")

    assert get_metric(response, "Active Residents") == 2
    assert get_metric(response, "Inactive Residents") == 1

    assert get_metric(response, "Total Residents") == (
        get_metric(response, "Active Residents")
        + get_metric(response, "Inactive Residents")
    )


def test_dashboard_displays_correct_total_service_requests(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(requests, resident.id)
    create_request(requests, resident.id)
    create_request(requests, resident.id, status="Completed")

    response = client.get("/dashboard")

    assert get_metric(response, "Total Service Requests") == 3


def test_dashboard_displays_correct_service_request_status_counts(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    statuses = [
        "Pending",
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    ]

    for status in statuses:
        create_request(requests, resident.id, status=status)

    response = client.get("/dashboard")

    assert get_metric(response, "Pending") == 2
    assert get_metric(response, "In Progress") == 1
    assert get_metric(response, "Completed") == 1
    assert get_metric(response, "Cancelled") == 1


def test_dashboard_service_request_counts_reconcile(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    for status in [
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
        "Pending",
    ]:
        create_request(requests, resident.id, status=status)

    response = client.get("/dashboard")

    total = get_metric(response, "Total Service Requests")

    status_total = (
        get_metric(response, "Pending")
        + get_metric(response, "In Progress")
        + get_metric(response, "Completed")
        + get_metric(response, "Cancelled")
    )

    assert total == status_total


def test_dashboard_open_requests_only_counts_pending_and_in_progress(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    for status in [
        "Pending",
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    ]:
        create_request(requests, resident.id, status=status)

    response = client.get("/dashboard")

    expected_open = (
        get_metric(response, "Pending")
        + get_metric(response, "In Progress")
    )

    assert get_metric(response, "Open Service Requests") == expected_open
    assert get_metric(response, "Open Service Requests") == 3


def test_resident_deactivation_updates_dashboard_counts(
    client,
    tmp_path,
):
    residents, _ = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    before = client.get("/dashboard")

    assert get_metric(before, "Total Residents") == 1
    assert get_metric(before, "Active Residents") == 1
    assert get_metric(before, "Inactive Residents") == 0

    result = client.post(
        f"/residents/{resident.id}/deactivate",
    )

    assert result.status_code == 302

    after = client.get("/dashboard")

    assert get_metric(after, "Total Residents") == 1
    assert get_metric(after, "Active Residents") == 0
    assert get_metric(after, "Inactive Residents") == 1


def test_service_request_transition_updates_dashboard_counts(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    service_request = create_request(
        requests,
        resident.id,
        status="Pending",
    )

    before = client.get("/dashboard")

    assert get_metric(before, "Pending") == 1
    assert get_metric(before, "In Progress") == 0

    result = client.post(
        f"/service-requests/{service_request.id}/process",
    )

    assert result.status_code == 302

    after = client.get("/dashboard")

    assert get_metric(after, "Pending") == 0
    assert get_metric(after, "In Progress") == 1
    assert get_metric(after, "Total Service Requests") == 1
    assert get_metric(after, "Open Service Requests") == 1


def test_terminal_transition_updates_dashboard_open_count(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    service_request = create_request(
        requests,
        resident.id,
        status="In Progress",
    )

    before = client.get("/dashboard")

    assert get_metric(before, "Open Service Requests") == 1

    result = client.post(
        f"/service-requests/{service_request.id}/complete",
    )

    assert result.status_code == 302

    after = client.get("/dashboard")

    assert get_metric(after, "In Progress") == 0
    assert get_metric(after, "Completed") == 1
    assert get_metric(after, "Open Service Requests") == 0
    assert get_metric(after, "Total Service Requests") == 1


def test_dashboard_displays_no_more_than_five_recent_requests(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    for day in range(1, 8):
        create_request(
            requests,
            resident.id,
            date_requested=date(2026, 11, day),
        )

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert response.data.count(b'class="button button-small"') == 5


def test_dashboard_recent_requests_use_correct_ordering(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(
        requests,
        resident.id,
        service_type="Oldest Request",
        date_requested=date(2026, 11, 1),
    )

    create_request(
        requests,
        resident.id,
        service_type="Same Date First",
        date_requested=date(2026, 11, 3),
    )

    create_request(
        requests,
        resident.id,
        service_type="Same Date Second",
        date_requested=date(2026, 11, 3),
    )

    response = client.get("/dashboard")

    page = response.get_data(as_text=True)

    positions = [
        page.index("Same Date Second"),
        page.index("Same Date First"),
        page.index("Oldest Request"),
    ]

    assert positions == sorted(positions)


def test_completed_and_cancelled_requests_can_appear_in_recent_list(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_request(
        requests,
        resident.id,
        service_type="Completed Recent Request",
        status="Completed",
        date_requested=date(2026, 11, 10),
    )

    create_request(
        requests,
        resident.id,
        service_type="Cancelled Recent Request",
        status="Cancelled",
        date_requested=date(2026, 11, 9),
    )

    for day in range(1, 4):
        create_request(
            requests,
            resident.id,
            service_type=f"Older Request {day}",
            date_requested=date(2026, 11, day),
        )

    response = client.get("/dashboard")

    assert b"Completed Recent Request" in response.data
    assert b"Cancelled Recent Request" in response.data
    assert b"Completed" in response.data
    assert b"Cancelled" in response.data


def test_recent_request_view_link_uses_existing_details_page(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    service_request = create_request(requests, resident.id)

    response = client.get("/dashboard")

    assert response.status_code == 200
    assert (
        f'href="/service-requests/{service_request.id}"'.encode()
        in response.data
    )

    detail_response = client.get(
        f"/service-requests/{service_request.id}",
    )

    assert detail_response.status_code == 200
    assert b"Health Assistance" in detail_response.data


def test_dashboard_get_does_not_modify_persisted_data(
    client,
    tmp_path,
):
    residents, requests = configure_repositories(client, tmp_path)
    resident = create_resident(residents)

    create_resident(residents, status="Inactive")

    create_request(requests, resident.id)
    create_request(
        requests,
        resident.id,
        status="Completed",
    )

    residents_before = [
        (item.id, item.status)
        for item in residents.find_all()
    ]

    requests_before = [
        (item.id, item.status, item.date_requested)
        for item in requests.find_all()
    ]

    for _ in range(3):
        response = client.get("/dashboard")
        assert response.status_code == 200

    residents_after = [
        (item.id, item.status)
        for item in residents.find_all()
    ]

    requests_after = [
        (item.id, item.status, item.date_requested)
        for item in requests.find_all()
    ]

    assert residents_after == residents_before
    assert requests_after == requests_before
