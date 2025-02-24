"""
Application Layer
"""

from app.services.ad_service import AdService

class CreateAd:
    def __init__(self, ad_service: AdService):
        self.ad_service = ad_service

    async def execute(self, ad_data: dict):
        return await self.ad_service.create_ad(ad_data)
