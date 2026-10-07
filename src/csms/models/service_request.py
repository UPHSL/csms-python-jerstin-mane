class ServiceRequest:
    def __init__(
        self,
        resident_id,
        service_type,
        description,
        date_requested,
        status="Pending",
        id=None,
    ):
        self.id = id
        self.resident_id = resident_id
        self.service_type = service_type
        self.description = description
        self.date_requested = date_requested
        self.status = status
