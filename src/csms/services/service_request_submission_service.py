from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import ServiceRequestRepository
from csms.services.service_request_submission_result import (
    ServiceRequestSubmissionResult,
)
from csms.services.service_request_validator import ServiceRequestValidator


class ServiceRequestSubmissionService:
    def __init__(
        self,
        service_request_repository: ServiceRequestRepository,
        resident_repository: ResidentRepository,
        validator: ServiceRequestValidator,
    ) -> None:
        self.service_request_repository = service_request_repository
        self.resident_repository = resident_repository
        self.validator = validator

    def submit(self, service_request):
        validation_errors = self.validator.validate(service_request)

        if validation_errors:
            return ServiceRequestSubmissionResult.validation_failed(
                validation_errors
            )

        resident = self.resident_repository.find_by_id(
            service_request.resident_id
        )

        if resident is None:
            return ServiceRequestSubmissionResult.resident_not_found()

        if resident.status == "Inactive":
            return ServiceRequestSubmissionResult.resident_inactive()

        service_request.status = "Pending"

        persisted_request = self.service_request_repository.save(
            service_request
        )

        return ServiceRequestSubmissionResult.successful(
            persisted_request
        )