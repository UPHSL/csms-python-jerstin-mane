from csms.models.resident import Resident
from csms.services.resident_validator import ResidentValidator


def make_valid_resident(**overrides):
    data = {
        "first_name": "Juan",
        "last_name": "Dela Cruz",
        "address": "Barangay Santo Tomas",
        "contact_number": "09171234567",
        "email": "juan@example.com",
        "status": "Active",
    }

    data.update(overrides)

    return Resident(**data)


def test_valid_resident_information_passes_validation():
    resident = make_valid_resident()
    validator = ResidentValidator()

    assert validator.is_valid(resident)


def test_missing_first_name_fails_validation():
    resident = make_valid_resident(first_name="")
    validator = ResidentValidator()

    errors = validator.validate(resident)

    assert not validator.is_valid(resident)
    assert "first_name" in errors


def test_missing_last_name_fails_validation():
    resident = make_valid_resident(last_name="")
    validator = ResidentValidator()

    errors = validator.validate(resident)

    assert not validator.is_valid(resident)
    assert "last_name" in errors


def test_missing_address_fails_validation():
    resident = make_valid_resident(address="")
    validator = ResidentValidator()

    errors = validator.validate(resident)

    assert not validator.is_valid(resident)
    assert "address" in errors


def test_whitespace_only_required_information_fails_validation():
    resident = make_valid_resident(first_name="   ")
    validator = ResidentValidator()

    errors = validator.validate(resident)

    assert not validator.is_valid(resident)
    assert "first_name" in errors


def test_invalid_contact_number_fails_validation():
    resident = make_valid_resident(
        contact_number="0917ABC4567"
    )
    validator = ResidentValidator()

    errors = validator.validate(resident)

    assert not validator.is_valid(resident)
    assert "contact_number" in errors


def test_invalid_email_fails_validation():
    resident = make_valid_resident(
        email="juan.example.com"
    )
    validator = ResidentValidator()

    errors = validator.validate(resident)

    assert not validator.is_valid(resident)
    assert "email" in errors


def test_supported_resident_statuses_pass_validation():
    active_resident = make_valid_resident(
        status="Active"
    )
    inactive_resident = make_valid_resident(
        status="Inactive"
    )

    validator = ResidentValidator()

    assert validator.is_valid(active_resident)
    assert validator.is_valid(inactive_resident)


def test_unsupported_resident_status_fails_validation():
    resident = make_valid_resident(
        status="Unknown"
    )
    validator = ResidentValidator()

    errors = validator.validate(resident)

    assert not validator.is_valid(resident)
    assert "status" in errors