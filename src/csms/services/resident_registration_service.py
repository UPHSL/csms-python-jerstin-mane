from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_registration_result import ResidentRegistrationResult
from csms.services.resident_validator import ResidentValidator


class ResidentRegistrationService:
    def __init__(
        self,
        validator: ResidentValidator,
        repository: ResidentRepository,
    ) -> None:
        self.validator = validator
        self.repository = repository

    def register_resident(
        self,
        resident: Resident,
    ) -> ResidentRegistrationResult:
        errors = self.validator.validate(resident)

        if errors:
            return ResidentRegistrationResult.failed(errors)

        persisted_resident = self.repository.save(resident)

        return ResidentRegistrationResult.successful(
            persisted_resident
        )