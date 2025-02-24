"""
Business Logic Layer
"""

from app.repositories.ad_repository import AdRepository

class AdService:
    def __init__(self, repository: AdRepository):
        self.repository = repository

    async def create_ad(self, ad_data: dict):
        return self.repository.create_ad(
            ad_data['url'],
            ad_data['title'],
            ad_data['price']
        )
