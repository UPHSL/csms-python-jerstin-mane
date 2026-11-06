
"""Web routes for the CSMS user interface."""

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository
from csms.services.resident_deactivation_service import (
    ResidentDeactivationService,
)
from csms.services.resident_query_service import ResidentQueryService
from csms.services.resident_registration_service import (
    ResidentRegistrationService,
)
from csms.services.resident_update_service import ResidentUpdateService
from csms.services.resident_validator import ResidentValidator


main_blueprint = Blueprint("main", __name__)


FIELD_ERROR_MESSAGES = {
    "first_name": "First name is required.",
    "last_name": "Last name is required.",
    "address": "Address is required.",
    "contact_number": "Enter a valid 11-digit Philippine mobile number starting with 09.",
    "email": "Enter a valid email address.",
    "status": "The resident status is invalid.",
}


def _resident_repository() -> ResidentRepository:
    """Create a resident repository using the configured database."""
    return ResidentRepository(current_app.config["DATABASE_PATH"])


def _friendly_validation_errors(errors: list[str]) -> list[str]:
    """Convert validator field names into readable messages."""
    return [
        FIELD_ERROR_MESSAGES.get(
            field,
            "Please check the information you entered.",
        )
        for field in errors
    ]


@main_blueprint.get("/")
def index() -> str:
    """Display the Sprint 0 welcome page."""
    return render_template(
        "index.html",
        application_name=current_app.config["APP_NAME"],
        application_version=current_app.config["APP_VERSION"],
        current_sprint=current_app.config["CURRENT_SPRINT"],
    )


@main_blueprint.get("/health")
def health():
    """Return a simple application health response."""
    return jsonify(
        {
            "application": current_app.config["APP_NAME"],
            "status": "ok",
            "version": current_app.config["APP_VERSION"],
        }
    )


@main_blueprint.get("/residents")
def resident_list() -> str:
    """Display all residents or search residents by name."""
    search_term = request.args.get("q", "").strip()

    service = ResidentQueryService(_resident_repository())
    residents = service.search_residents(search_term)

    return render_template(
        "residents/list.html",
        residents=residents,
        search_term=search_term,
    )


@main_blueprint.route(
    "/residents/register",
    methods=["GET", "POST"],
)
def register_resident() -> str:
    """Display the registration form and register new residents."""
    if request.method == "POST":
        resident = Resident(
            first_name=request.form.get("first_name", "").strip(),
            last_name=request.form.get("last_name", "").strip(),
            address=request.form.get("address", "").strip(),
            contact_number=request.form.get("contact_number", "").strip(),
            email=request.form.get("email", "").strip(),
        )

        service = ResidentRegistrationService(
            ResidentValidator(),
            _resident_repository(),
        )
        result = service.register_resident(resident)

        if result.success:
            flash("Resident registered successfully.", "success")
            return redirect(url_for("main.resident_list"))

        return render_template(
            "residents/register.html",
            resident=resident,
            errors=_friendly_validation_errors(result.errors),
        )

    resident = Resident(
        first_name="",
        last_name="",
        address="",
        contact_number="",
        email="",
    )

    return render_template(
        "residents/register.html",
        resident=resident,
        errors=[],
    )


@main_blueprint.route(
    "/residents/<int:resident_id>/edit",
    methods=["GET", "POST"],
)
def edit_resident(resident_id: int) -> str:
    """Display the edit form and update an existing resident."""
    repository = _resident_repository()
    existing_resident = repository.find_by_id(resident_id)

    if existing_resident is None:
        abort(404)

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        address = request.form.get("address", "").strip()
        contact_number = request.form.get("contact_number", "").strip()
        email = request.form.get("email", "").strip()

        service = ResidentUpdateService(
            ResidentValidator(),
            repository,
        )

        result = service.update_resident(
            resident_id,
            first_name,
            last_name,
            address,
            contact_number,
            email,
        )

        if result.status == "not_found":
            abort(404)

        if result.status == "success":
            flash("Resident information updated successfully.", "success")
            return redirect(url_for("main.resident_list"))

        submitted_resident = Resident(
            id=existing_resident.id,
            first_name=first_name,
            last_name=last_name,
            address=address,
            contact_number=contact_number,
            email=email,
            status=existing_resident.status,
        )

        return render_template(
            "residents/edit.html",
            resident=submitted_resident,
            errors=_friendly_validation_errors(result.errors),
        )

    return render_template(
        "residents/edit.html",
        resident=existing_resident,
        errors=[],
    )


@main_blueprint.post("/residents/<int:resident_id>/deactivate")
def deactivate_resident(resident_id: int):
    """Deactivate an active resident through a POST request."""
    service = ResidentDeactivationService(_resident_repository())
    result = service.deactivate_resident(resident_id)

    if result.status == "not_found":
        abort(404)

    if result.status == "success":
        flash("Resident deactivated successfully.", "success")
    elif result.status == "already_inactive":
        flash("This resident is already inactive.", "info")

    return redirect(url_for("main.resident_list"))
