from csms.models.resident import Resident
from csms.repositories.resident_repository import ResidentRepository


class ResidentQueryService:
    def __init__(self, repository: ResidentRepository) -> None:
        self.repository = repository

    def list_residents(self) -> list[Resident]:
        return self.repository.find_all()

    def search_residents(self, search_term: str | None) -> list[Resident]:
        normalized_search_term = (
            ""
            if search_term is None
            else search_term.strip()
        )

        if not normalized_search_term:
            return self.list_residents()

        return self.repository.search_by_name(
            normalized_search_term
        )
