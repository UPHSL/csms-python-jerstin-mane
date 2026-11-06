from csms.repositories.service_request_repository import ServiceRequestRepository

ALLOWED_STATUSES = {
    "Pending",
    "In Progress",
    "Completed",
    "Cancelled",
}

class ServiceRequestQueryService:
    def __init__(self, repository: ServiceRequestRepository):
        self.repository = repository

    def list_requests(
        self,
        search_term: str | None = None,
        status: str | None = None,
    ):
        normalized_search_term = (
            "" if search_term is None else search_term.strip()
        )

        normalized_status = (
            "" if status is None else status.strip()
        )

        if normalized_status and normalized_status not in ALLOWED_STATUSES:
            raise ValueError(
                f"Unsupported service request status: {normalized_status}"
            )

        return self.repository.find_all(
            search_term=normalized_search_term or None,
            status=normalized_status or None,
        )

    def get_request(self, service_request_id: int):
        return self.repository.find_by_id(service_request_id)
