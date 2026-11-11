from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)


class DashboardService:
    def __init__(
        self,
        resident_repository: ResidentRepository,
        service_request_repository: ServiceRequestRepository,
    ) -> None:
        self.resident_repository = resident_repository
        self.service_request_repository = service_request_repository

    def get_dashboard_summary(self) -> dict:
        """Get the current operational summary of the CSMS."""

        resident_status_counts = (
            self.resident_repository.get_status_counts()
        )

        service_request_status_counts = (
            self.service_request_repository.get_status_counts()
        )

        pending_requests = service_request_status_counts["Pending"]
        in_progress_requests = service_request_status_counts["In Progress"]

        return {
            "total_residents": self.resident_repository.count_all(),
            "active_residents": resident_status_counts["Active"],
            "inactive_residents": resident_status_counts["Inactive"],

            "total_service_requests": (
                self.service_request_repository.count_all()
            ),
            "pending_requests": pending_requests,
            "in_progress_requests": in_progress_requests,
            "completed_requests": service_request_status_counts["Completed"],
            "cancelled_requests": service_request_status_counts["Cancelled"],

            "open_service_requests": (
                pending_requests + in_progress_requests
            ),

            "recent_service_requests": (
                self.service_request_repository.find_recent(limit=5)
            ),
        }
