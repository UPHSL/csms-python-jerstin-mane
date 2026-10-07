from datetime import date

from csms.models.service_request import ServiceRequest


class ServiceRequestValidator:
    def validate(self, service_request: ServiceRequest):
        errors = []

        if service_request.id is not None:
            errors.append("Service Request ID must be unassigned.")

        if not isinstance(service_request.resident_id, int):
            errors.append("Resident ID must be a valid positive integer.")
        elif service_request.resident_id <= 0:
            errors.append("Resident ID must be a valid positive integer.")

        if not isinstance(service_request.service_type, str):
            errors.append("Service type is required.")
        elif not service_request.service_type.strip():
            errors.append("Service type is required.")

        if not isinstance(service_request.description, str):
            errors.append("Description is required.")
        elif not service_request.description.strip():
            errors.append("Description is required.")

        if not isinstance(service_request.date_requested, date):
            errors.append("Date requested must be a valid date.")

        if service_request.status != "Pending":
            errors.append("New Service Request status must be Pending.")

        return errors