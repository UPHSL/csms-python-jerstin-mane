"""Web routes for the CSMS user interface."""

from datetime import date

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
from csms.models.service_request import ServiceRequest
from csms.repositories.resident_repository import ResidentRepository
from csms.repositories.service_request_repository import (
    ServiceRequestRepository,
)
from csms.services.request_service import (
    ALLOWED_STATUSES,
    ServiceRequestQueryService,
)
from csms.services.resident_deactivation_service import (
    ResidentDeactivationService,
)
from csms.services.resident_query_service import ResidentQueryService
from csms.services.resident_registration_service import (
    ResidentRegistrationService,
)
from csms.services.resident_update_service import ResidentUpdateService
from csms.services.resident_validator import ResidentValidator
from csms.services.service_request_status_service import (
    ServiceRequestStatusService,
)
from csms.services.service_request_submission_service import (
    ServiceRequestSubmissionService,
)
from csms.services.service_request_validator import (
    ServiceRequestValidator,
)


main_blueprint = Blueprint("main", __name__)


FIELD_ERROR_MESSAGES = {
    "first_name": "First name is required.",
    "last_name": "Last name is required.",
    "address": "Address is required.",
    "contact_number": "Enter a valid 11-digit Philippine mobile number starting with 09.",
    "email": "Enter a valid email address.",
    "status": "The resident status is invalid.",
}

SERVICE_REQUEST_STATUSES = (
    "Pending",
    "In Progress",
    "Completed",
    "Cancelled",
)


def _resident_repository() -> ResidentRepository:
    """Create a resident repository using the configured database."""
    return ResidentRepository(current_app.config["DATABASE_PATH"])


def _service_request_repository() -> ServiceRequestRepository:
    """Create a Service Request repository using the configured database."""
    return ServiceRequestRepository(current_app.config["DATABASE_PATH"])


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


# Resident Management Routes


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


# Service Request Management Routes


@main_blueprint.get("/service-requests")
def service_request_list() -> str:
    """Display, search, and filter Service Requests."""
    search_term = request.args.get("q", "").strip()
    selected_status = request.args.get("status", "").strip()

    service = ServiceRequestQueryService(
        _service_request_repository()
    )

    try:
        service_requests = service.list_requests(
            search_term=search_term,
            status=selected_status,
        )
    except ValueError:
        flash("Please select a valid Service Request status.", "error")
        return redirect(
            url_for(
                "main.service_request_list",
                q=search_term or None,
            )
        )

    return render_template(
        "service_requests/list.html",
        service_requests=service_requests,
        search_term=search_term,
        selected_status=selected_status,
        statuses=SERVICE_REQUEST_STATUSES,
    )


@main_blueprint.route(
    "/service-requests/new",
    methods=["GET", "POST"],
)
def new_service_request() -> str:
    """Display the submission form and submit a new Service Request."""
    form_data = {
        "resident_id": "",
        "service_type": "",
        "description": "",
        "date_requested": "",
    }

    if request.method == "POST":
        form_data = {
            "resident_id": request.form.get("resident_id", "").strip(),
            "service_type": request.form.get("service_type", "").strip(),
            "description": request.form.get("description", "").strip(),
            "date_requested": request.form.get(
                "date_requested",
                "",
            ).strip(),
        }

        try:
            resident_id = int(form_data["resident_id"])
        except ValueError:
            resident_id = form_data["resident_id"]

        try:
            date_requested = date.fromisoformat(
                form_data["date_requested"]
            )
        except ValueError:
            date_requested = form_data["date_requested"]

        service_request = ServiceRequest(
            resident_id=resident_id,
            service_type=form_data["service_type"],
            description=form_data["description"],
            date_requested=date_requested,
        )

        service = ServiceRequestSubmissionService(
            service_request_repository=_service_request_repository(),
            resident_repository=_resident_repository(),
            validator=ServiceRequestValidator(),
        )

        result = service.submit(service_request)

        if result.status == "success":
            flash(
                "Service Request submitted successfully.",
                "success",
            )
            return redirect(url_for("main.service_request_list"))

        errors = result.errors or [
            "Unable to submit the Service Request."
        ]

        if result.status == "resident_inactive":
            errors = [
                "Inactive Residents cannot submit new Service Requests."
            ]

        return render_template(
            "service_requests/new.html",
            form_data=form_data,
            errors=errors,
        )

    return render_template(
        "service_requests/new.html",
        form_data=form_data,
        errors=[],
    )


@main_blueprint.get("/service-requests/<int:service_request_id>")
def view_service_request(service_request_id: int) -> str:
    """Display the details of one persisted Service Request."""
    service = ServiceRequestQueryService(
        _service_request_repository()
    )

    service_request = service.get_request(service_request_id)

    if service_request is None:
        abort(404)

    return render_template(
        "service_requests/detail.html",
        service_request=service_request,
    )


def _change_service_request_status(
    service_request_id: int,
    target_status: str,
    success_message: str,
):
    """Request a controlled status change through the T10 service."""
    service = ServiceRequestStatusService(
        _service_request_repository()
    )

    result = service.update_status(
        service_request_id,
        target_status,
    )

    if result.status == "not_found":
        abort(404)

    if result.status == "success":
        flash(success_message, "success")
    else:
        errors = result.errors or [
            "Unable to update the Service Request status."
        ]
        flash(errors[0], "error")

    return redirect(
        url_for(
            "main.view_service_request",
            service_request_id=service_request_id,
        )
    )


@main_blueprint.post(
    "/service-requests/<int:service_request_id>/process"
)
def process_service_request(service_request_id: int):
    """Start processing a Pending Service Request."""
    return _change_service_request_status(
        service_request_id,
        "In Progress",
        "Service Request is now In Progress.",
    )


@main_blueprint.post(
    "/service-requests/<int:service_request_id>/complete"
)
def complete_service_request(service_request_id: int):
    """Complete an In Progress Service Request."""
    return _change_service_request_status(
        service_request_id,
        "Completed",
        "Service Request completed successfully.",
    )


@main_blueprint.post(
    "/service-requests/<int:service_request_id>/cancel"
)
def cancel_service_request(service_request_id: int):
    """Cancel an eligible Service Request."""
    return _change_service_request_status(
        service_request_id,
        "Cancelled",
        "Service Request cancelled successfully.",
    )
