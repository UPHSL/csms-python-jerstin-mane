from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from csms.services.service_request_status_result import (
    ServiceRequestStatusResult,
)


class ServiceRequestStatusService:
    ALLOWED_STATUSES = {
        "Pending",
        "In Progress",
        "Completed",
        "Cancelled",
    }

    ALLOWED_TRANSITIONS = {
        "Pending": {
            "In Progress",
            "Cancelled",
        },
        "In Progress": {
            "Completed",
            "Cancelled",
        },
        "Completed": set(),
        "Cancelled": set(),
    }

    def __init__(
        self,
        service_request_repository: ServiceRequestRepository,
    ) -> None:
        self.service_request_repository = service_request_repository

    def update_status(self, service_request_id, target_status):
        service_request = self.service_request_repository.find_by_id(
            service_request_id
        )

        if service_request is None:
            return ServiceRequestStatusResult.not_found()

        if target_status not in self.ALLOWED_STATUSES:
            return ServiceRequestStatusResult.unsupported_status(
                target_status
            )

        current_status = service_request.status

        if target_status not in self.ALLOWED_TRANSITIONS[current_status]:
            return ServiceRequestStatusResult.invalid_transition(
                current_status,
                target_status,
            )

        updated_request = self.service_request_repository.update_status(
            service_request_id,
            target_status,
        )

        return ServiceRequestStatusResult.successful(updated_request)