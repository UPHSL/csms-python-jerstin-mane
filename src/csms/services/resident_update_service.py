from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_update_result import ResidentUpdateResult
from csms.services.resident_validator import ResidentValidator


class ResidentUpdateService:
    def __init__(
        self,
        validator: ResidentValidator,
        repository: ResidentRepository,
    ) -> None:
        self.validator = validator
        self.repository = repository

    def update_resident(
        self,
        resident_id: int,
        first_name: str,
        last_name: str,
        address: str,
        contact_number: str,
        email: str,
    ) -> ResidentUpdateResult:
        existing_resident = self.repository.find_by_id(resident_id)

        if existing_resident is None:
            return ResidentUpdateResult.not_found()

        candidate = Resident(
            id=existing_resident.id,
            first_name=first_name,
            last_name=last_name,
            address=address,
            contact_number=contact_number,
            email=email,
            status=existing_resident.status,
        )

        errors = self.validator.validate(candidate)

        if errors:
            return ResidentUpdateResult.failed(errors)

        updated_resident = self.repository.update(candidate)

        return ResidentUpdateResult.successful(
            updated_resident
        )