from dataclasses import dataclass, field

from csms.models.resident import Resident


@dataclass
class ResidentUpdateResult:
    status: str
    resident: Resident | None = None
    errors: list[str] = field(default_factory=list)

    @classmethod
    def successful(
        cls,
        resident: Resident,
    ) -> "ResidentUpdateResult":
        return cls(
            status="success",
            resident=resident,
            errors=[],
        )

    @classmethod
    def failed(
        cls,
        errors: list[str],
    ) -> "ResidentUpdateResult":
        return cls(
            status="validation_failed",
            resident=None,
            errors=list(errors),
        )

    @classmethod
    def not_found(cls) -> "ResidentUpdateResult":
        return cls(
            status="not_found",
            resident=None,
            errors=[],
        )
