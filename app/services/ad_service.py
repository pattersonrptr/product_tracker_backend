"""
Business Logic Layer
"""

from app.repositories.ad_repository import AdRepository

class AdService:
    def __init__(self, repository: AdRepository):
        self.repository = repository

    async def create_ad(self, ad_data: dict):
        return self.repository.create(ad_data)

    async def get_all_ads(self):
        return self.repository.get_all()

    async def get_ad_by_id(self, ad_id: int):
        return self.repository.get_by_id(ad_id)

    async def update_ad(self, ad_id: int, ad_data: dict):
        return self.repository.update(ad_id, ad_data)

    async def delete_ad(self, ad_id: int):
        return self.repository.delete(ad_id)

