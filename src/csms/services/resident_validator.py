import re

from csms.models.resident import Resident


CONTACT_NUMBER_PATTERN = re.compile(r"^09[0-9]{9}$")

EMAIL_PATTERN = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)

SUPPORTED_STATUSES = {
    "Active",
    "Inactive",
}


class ResidentValidator:
    def validate(self, resident: Resident) -> list[str]:
        errors = []

        if self._is_blank(resident.first_name):
            errors.append("first_name")

        if self._is_blank(resident.last_name):
            errors.append("last_name")

        if self._is_blank(resident.address):
            errors.append("address")

        if not self._is_valid_contact_number(
            resident.contact_number
        ):
            errors.append("contact_number")

        if not self._is_valid_email(resident.email):
            errors.append("email")

        if not self._is_supported_status(resident.status):
            errors.append("status")

        return errors

    def is_valid(self, resident: Resident) -> bool:
        return len(self.validate(resident)) == 0

    @staticmethod
    def _is_blank(value: object) -> bool:
        return (
            not isinstance(value, str)
            or not value.strip()
        )

    @staticmethod
    def _is_valid_contact_number(value: object) -> bool:
        return (
            isinstance(value, str)
            and CONTACT_NUMBER_PATTERN.fullmatch(value)
            is not None
        )

    @staticmethod
    def _is_valid_email(value: object) -> bool:
        return (
            isinstance(value, str)
            and EMAIL_PATTERN.fullmatch(value)
            is not None
        )

    @staticmethod
    def _is_supported_status(value: object) -> bool:
        return (
            isinstance(value, str)
            and value in SUPPORTED_STATUSES
        )