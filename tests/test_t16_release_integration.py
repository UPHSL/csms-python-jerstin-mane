
from datetime import date

from csms.models.resident import Resident
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from csms.services.dashboard_service import DashboardService
from csms.services.resident_registration_service import (
    ResidentRegistrationService,
)
from csms.services.resident_validator import ResidentValidator
from csms.services.service_request_submission_service import (
    ServiceRequestSubmissionService,
)
from csms.services.service_request_validator import (
    ServiceRequestValidator,
)


def test_resident_registration_request_submission_and_dashboard_integration(
    tmp_path,
):
    database_path = tmp_path / "csms_release_test.db"

    resident_repository = ResidentRepository(database_path)
    service_request_repository = ServiceRequestRepository(database_path)

    registration_service = ResidentRegistrationService(
        validator=ResidentValidator(),
        repository=resident_repository,
    )

    submission_service = ServiceRequestSubmissionService(
        service_request_repository=service_request_repository,
        resident_repository=resident_repository,
        validator=ServiceRequestValidator(),
    )

    dashboard_service = DashboardService(
        resident_repository=resident_repository,
        service_request_repository=service_request_repository,
    )

    resident = Resident(
        first_name="Juan",
        last_name="Dela Cruz",
        address="Santa Rosa, Laguna",
        contact_number="09123456789",
        email="juan@example.com",
    )

    registration_result = registration_service.register_resident(resident)

    assert registration_result.success is True
    assert registration_result.resident is not None
    assert registration_result.resident.id is not None

    registered_resident = registration_result.resident

    service_request = ServiceRequest(
        resident_id=registered_resident.id,
        service_type="Health Assistance",
        description="Medical support request",
        date_requested=date(2026, 11, 19),
    )

    submission_result = submission_service.submit(service_request)

    assert submission_result.status == "success"
    assert submission_result.service_request is not None

    saved_request = submission_result.service_request

    assert saved_request.id is not None
    assert saved_request.resident_id == registered_resident.id
    assert saved_request.status == "Pending"

    persisted_resident = ResidentRepository(database_path).find_by_id(
        registered_resident.id
    )

    persisted_request = ServiceRequestRepository(database_path).find_by_id(
        saved_request.id
    )

    assert persisted_resident is not None
    assert persisted_resident.first_name == "Juan"
    assert persisted_resident.status == "Active"

    assert persisted_request is not None
    assert persisted_request.resident_id == persisted_resident.id
    assert persisted_request.service_type == "Health Assistance"
    assert persisted_request.status == "Pending"

    dashboard_summary = dashboard_service.get_dashboard_summary()

    assert dashboard_summary["total_residents"] == 1
    assert dashboard_summary["active_residents"] == 1
    assert dashboard_summary["total_service_requests"] == 1
    assert dashboard_summary["pending_requests"] == 1
    assert dashboard_summary["open_service_requests"] == 1
