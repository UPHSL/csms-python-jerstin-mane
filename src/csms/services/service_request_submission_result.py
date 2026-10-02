from dataclasses import dataclass

from csms.models.service_request import ServiceRequest


@dataclass
class ServiceRequestSubmissionResult:
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
    def validation_failed(cls, errors: list[str]):
        return cls(
            status="validation_failed",
            service_request=None,
            errors=errors,
        )

    @classmethod
    def resident_not_found(cls):
        return cls(
            status="resident_not_found",
            service_request=None,
            errors=["Resident not found."],
        )

    @classmethod
    def resident_inactive(cls):
        return cls(
            status="resident_inactive",
            service_request=None,
            errors=["Resident is inactive."],
        )