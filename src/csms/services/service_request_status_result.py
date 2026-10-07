from dataclasses import dataclass

from csms.models.service_request import ServiceRequest


@dataclass
class ServiceRequestStatusResult:
    status: str
    service_request: ServiceRequest | None = None
    errors: list[str] | None = None

    @classmethod
    def successful(cls, service_request: ServiceRequest):
        return cls(
            status="success",
            service_request=service_request,
            errors=[],
        )

    @classmethod
    def not_found(cls):
        return cls(
            status="not_found",
            service_request=None,
            errors=["Service request not found."],
        )

    @classmethod
    def unsupported_status(cls, status: str):
        return cls(
            status="unsupported_status",
            service_request=None,
            errors=[f"Unsupported target status: {status}."],
        )

    @classmethod
    def invalid_transition(cls, current_status: str, target_status: str):
        return cls(
            status="invalid_transition",
            service_request=None,
            errors=[
                f"Invalid status transition: {current_status} to {target_status}."
            ],
        )