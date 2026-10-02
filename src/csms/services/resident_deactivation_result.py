from dataclasses import dataclass

from csms.models.resident import Resident


@dataclass
class ResidentDeactivationResult:
    status: str
    resident: Resident | None = None

    @classmethod
    def successful(cls, resident: Resident):
        return cls(
            status="success",
            resident=resident,
        )

    @classmethod
    def already_inactive(cls, resident: Resident):
        return cls(
            status="already_inactive",
            resident=resident,
        )

    @classmethod
    def not_found(cls):
        return cls(
            status="not_found",
            resident=None,
        )
