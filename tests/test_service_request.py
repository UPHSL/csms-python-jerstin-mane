from datetime import date

from csms.models.service_request import ServiceRequest


def test_service_request_can_be_created_with_required_information():
    service_request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Request for employment requirement",
        date_requested=date(2026, 10, 2),
    )

    assert isinstance(service_request, ServiceRequest)


def test_service_request_information_can_be_accessed():
    requested_date = date(2026, 10, 2)

    service_request = ServiceRequest(
        resident_id=25,
        service_type="Certificate Request",
        description="Request for employment requirement",
        date_requested=requested_date,
    )

    assert service_request.resident_id == 25
    assert service_request.service_type == "Certificate Request"
    assert service_request.description == "Request for employment requirement"
    assert service_request.date_requested == requested_date


def test_service_request_preserves_resident_id():
    service_request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Employment requirement",
        date_requested=date(2026, 10, 2),
    )

    assert service_request.resident_id == 25


def test_service_request_defaults_to_none_id_before_persistence():
    service_request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Employment requirement",
        date_requested=date(2026, 10, 2),
    )

    assert service_request.id is None


def test_service_request_defaults_to_pending_status():
    service_request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Employment requirement",
        date_requested=date(2026, 10, 2),
    )

    assert service_request.status == "Pending"


def test_service_request_objects_preserve_independent_information():
    first_request = ServiceRequest(
        resident_id=25,
        service_type="Barangay Clearance",
        description="Employment requirement",
        date_requested=date(2026, 10, 2),
    )

    second_request = ServiceRequest(
        resident_id=30,
        service_type="Community Assistance",
        description="Medical assistance",
        date_requested=date(2026, 10, 3),
    )

    assert first_request.resident_id == 25
    assert first_request.service_type == "Barangay Clearance"
    assert first_request.description == "Employment requirement"
    assert first_request.date_requested == date(2026, 10, 2)

    assert second_request.resident_id == 30
    assert second_request.service_type == "Community Assistance"
    assert second_request.description == "Medical assistance"
    assert second_request.date_requested == date(2026, 10, 3)
