from typing import Optional, List

from src.app.infrastructure.database.models.source_website_model import SourceWebsite
from src.app.interfaces.repositories.source_website_repository import (
    SourceWebsiteRepositoryInterface,
)


class CreateSourceWebsiteUseCase:
    def __init__(self, source_website_repository: SourceWebsiteRepositoryInterface):
        self.source_website_repository = source_website_repository

    def execute(self, source_website: SourceWebsite) -> SourceWebsite:
        existing_website = self.source_website_repository.get_by_name(
            source_website.name
        )
        if existing_website:
            return existing_website
        return self.source_website_repository.create(source_website)


class GetSourceWebsiteByIdUseCase:
    def __init__(self, source_website_repository: SourceWebsiteRepositoryInterface):
        self.source_website_repository = source_website_repository

    def execute(self, source_website_id: int) -> Optional[SourceWebsite]:
        return self.source_website_repository.get_by_id(source_website_id)


class GetSourceWebsiteByNameUseCase:
    def __init__(self, source_website_repository: SourceWebsiteRepositoryInterface):
        self.source_website_repository = source_website_repository

    def execute(self, name: str) -> Optional[SourceWebsite]:
        return self.source_website_repository.get_by_name(name)


class ListSourceWebsitesUseCase:
    def __init__(self, source_website_repository: SourceWebsiteRepositoryInterface):
        self.source_website_repository = source_website_repository

    def execute(self) -> List[SourceWebsite]:
        return self.source_website_repository.get_all()


class UpdateSourceWebsiteUseCase:
    def __init__(self, source_website_repository: SourceWebsiteRepositoryInterface):
        self.source_website_repository = source_website_repository

    def execute(
        self, source_website_id: int, source_website: SourceWebsite
    ) -> Optional[SourceWebsite]:
        return self.source_website_repository.update(source_website_id, source_website)


class DeleteSourceWebsiteUseCase:
    def __init__(self, source_website_repository: SourceWebsiteRepositoryInterface):
        self.source_website_repository = source_website_repository

    def execute(self, source_website_id: int) -> bool:
        return self.source_website_repository.delete(source_website_id)
