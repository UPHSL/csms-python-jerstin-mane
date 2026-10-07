class Resident:
    def __init__(
        self,
        first_name,
        last_name,
        address,
        contact_number,
        email,
        status="Active",
        id=None,
    ):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.contact_number = contact_number
        self.email = email
        self.status = status