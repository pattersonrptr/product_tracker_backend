from datetime import datetime, timezone
from app.models.product_models import ProductCondition


def get_fixtures():
    return {
        "source_websites": [
            {
                "id": 1,
                "name": "OLX",
                "base_url": "https://www.olx.com.br",
                "is_active": True,
            },
            {
                "id": 2,
                "name": "Enjoei",
                "base_url": "https://www.enjoei.com.br",
                "is_active": True,
            },
            {
                "id": 3,
                "name": "Mercado Livre",
                "base_url": "https://www.mercadolivre.com.br",
                "is_active": False,
            },
        ],
        "products": [
            {
                "id": 1,
                "url": "https://www.olx.com.br/item/iphone-13-128gb",
                "title": "iPhone 13 128GB",
                "description": "iPhone 13 em perfeito estado, 128GB, cor azul",
                "price": 3500.00,
                "source_product_code": "OLX12345",
                "city": "São Paulo",
                "state": "SP",
                "condition": ProductCondition.USED,
                "seller_type": "individual",
                "source": "olx",
                "is_available": True,
                "image_urls": "https://img1.jpg,https://img2.jpg",
                "created_at": datetime(2023, 10, 15, 10, 0, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2023, 10, 15, 10, 0, 0, tzinfo=timezone.utc),
                "source_website_id": 1,
            },
            {
                "id": 2,
                "url": "https://www.enjoei.com.br/camera-sony-a7",
                "title": "Câmera Sony A7 III",
                "description": "Câmera profissional com lente 24-70mm",
                "price": 8500.00,
                "source_product_code": "ENJ67890",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "condition": ProductCondition.NEW,
                "seller_type": "store",
                "source": "enjoei",
                "is_available": True,
                "image_urls": "https://img3.jpg,https://img4.jpg",
                "created_at": datetime(2023, 10, 16, 11, 30, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2023, 10, 16, 11, 30, 0, tzinfo=timezone.utc),
                "source_website_id": 2,
            },
        ],
        "price_history": [
            {
                "id": 1,
                "product_id": 1,
                "price": 3800.00,
                "created_at": datetime(2023, 10, 10, 9, 0, 0, tzinfo=timezone.utc),
            },
            {
                "id": 2,
                "product_id": 1,
                "price": 3700.00,
                "created_at": datetime(2023, 10, 12, 14, 30, 0, tzinfo=timezone.utc),
            },
            {
                "id": 3,
                "product_id": 1,
                "price": 3500.00,
                "created_at": datetime(2023, 10, 15, 10, 0, 0, tzinfo=timezone.utc),
            },
            {
                "id": 4,
                "product_id": 2,
                "price": 9000.00,
                "created_at": datetime(2023, 10, 14, 16, 45, 0, tzinfo=timezone.utc),
            },
            {
                "id": 5,
                "product_id": 2,
                "price": 8500.00,
                "created_at": datetime(2023, 10, 16, 11, 30, 0, tzinfo=timezone.utc),
            },
        ],
    }
