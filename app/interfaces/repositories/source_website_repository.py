from abc import ABC, abstractmethod
from typing import Optional, List

from app.infrastructure.database.models.source_website_model import SourceWebsite


class SourceWebsiteRepositoryInterface(ABC):
    @abstractmethod
    def create(self, source_website: SourceWebsite) -> SourceWebsite:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, source_website_id: int) -> Optional[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> Optional[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, source_website_id: int, source_website: SourceWebsite
    ) -> Optional[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, source_website_id: int) -> bool:
        raise NotImplementedError
