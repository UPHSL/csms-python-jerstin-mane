from dataclasses import dataclass, field

from csms.models.resident import Resident


@dataclass
class ResidentRegistrationResult:
    success: bool
    resident: Resident | None = None
    errors: list[str] = field(default_factory=list)

    @classmethod
    def successful(
        cls,
        resident: Resident,
    ) -> "ResidentRegistrationResult":
        return cls(
            success=True,
            resident=resident,
            errors=[],
        )

    @classmethod
    def failed(
        cls,
        errors: list[str],
    ) -> "ResidentRegistrationResult":
        return cls(
            success=False,
            resident=None,
            errors=list(errors),
        )