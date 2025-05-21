from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Dict

from src.app.infrastructure.database.models.source_website_model import SourceWebsite
from src.app.entities import source_website as SourceWebsiteEntity


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
    def get_all(
            self,
            limit: int,
            offset: int,
            filter_params: Dict,
            sort_by: str,
            sort_order: str,
    ) -> Tuple[List[SourceWebsiteEntity.SourceWebsite], int]:
        raise NotImplementedError

    @abstractmethod
    def update(
        self, source_website_id: int, source_website: SourceWebsite
    ) -> Optional[SourceWebsite]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, source_website_id: int) -> bool:
        raise NotImplementedError
