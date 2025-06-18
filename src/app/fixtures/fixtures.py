from datetime import datetime, timezone, time
from src.app.infrastructure.database.models.product_model import ProductCondition


def get_fixtures():
    return {
        "source_websites": [
            {
                "id": 1,
                "name": "olx",
                "base_url": "https://www.olx.com.br/brasil",
                "is_active": True,
            },
            {
                "id": 2,
                "name": "enjoei",
                "base_url": "https://enjusearch.enjoei.com.br",
                "is_active": True,
            },
            {
                "id": 3,
                "name": "mercado_livre",
                "base_url": "https://lista.mercadolivre.com.br",
                "is_active": True,
            },
            {
                "id": 4,
                "name": "estante_virtual",
                "base_url": "https://www.estantevirtual.com.br",
                "is_active": True,
            },
        ],
        "products": [
            {
                "id": 1,
                "url": "https://www.olx.com.br/item/iphone-13-128gb",
                "title": "iPhone 13 128GB",
                "description": "iPhone 13 em perfeito estado, 128GB, cor azul",
                "source_product_code": "OLX12345",
                "city": "São Paulo",
                "state": "SP",
                "condition": ProductCondition.USED.value,
                "seller_name": "individual",
                "is_available": True,
                "image_urls": "https://img1.jpg,https://img2.jpg",
                "created_at": datetime(2023, 10, 15, 10, 0, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2023, 10, 15, 10, 0, 0, tzinfo=timezone.utc),
                "source_website_id": 1,
                "source_metadata": None,
            },
            {
                "id": 2,
                "url": "https://www.enjoei.com.br/camera-sony-a7",
                "title": "Câmera Sony A7 III",
                "description": "Câmera profissional com lente 24-70mm",
                "source_product_code": "ENJ67890",
                "city": "Rio de Janeiro",
                "state": "RJ",
                "condition": ProductCondition.NEW.value,
                "seller_name": "store",
                "is_available": True,
                "image_urls": "https://img3.jpg,https://img4.jpg",
                "created_at": datetime(2023, 10, 16, 11, 30, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2023, 10, 16, 11, 30, 0, tzinfo=timezone.utc),
                "source_website_id": 2,
                "source_metadata": None,
            },
        ],
        "price_history": [
            {
                "product_id": 1,
                "price": 3800.00,
                "created_at": datetime(2023, 10, 10, 9, 0, 0, tzinfo=timezone.utc),
            },
            {
                "product_id": 1,
                "price": 3700.00,
                "created_at": datetime(2023, 10, 12, 14, 30, 0, tzinfo=timezone.utc),
            },
            {
                "product_id": 1,
                "price": 3500.00,
                "created_at": datetime(2023, 10, 15, 10, 0, 0, tzinfo=timezone.utc),
            },
            {
                "product_id": 2,
                "price": 9000.00,
                "created_at": datetime(2023, 10, 14, 16, 45, 0, tzinfo=timezone.utc),
            },
            {
                "product_id": 2,
                "price": 8500.00,
                "created_at": datetime(2023, 10, 16, 11, 30, 0, tzinfo=timezone.utc),
            },
        ],
        "users": [
            {
                "id": 1,
                "username": "celery_user",
                "email": "celery_user@example.com",
                "hashed_password": "$2b$12$TTn3Ejs8VBS9hHnUHN3bhesd/tOw1jqo5GVZHjm9f.XENVyhLz.QC",
                "is_active": True,
                "created_at": datetime(2023, 10, 10, 9, 0, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2023, 10, 10, 9, 0, 0, tzinfo=timezone.utc),
            },
            {
                "id": 2,
                "username": "admin",
                "email": "user@admin.com",
                "hashed_password": "$2b$12$twjBaSo7cCa9v/tn4V4jBeGHT1QD5g0ZkrIySUTJqjvZa2KT0LSwy",  # admin123
                "is_active": True,
                "created_at": datetime(
                    2025, 5, 18, 2, 4, 29, 767003, tzinfo=timezone.utc
                ),
                "updated_at": datetime(
                    2025, 5, 18, 2, 4, 29, 767037, tzinfo=timezone.utc
                ),
            },
            {
                "id": 3,
                "username": "patterson",
                "email": "pattersonjunior@gmail.com",
                "hashed_password": "$2b$12$f.y/FNygqcLA19f7uTlxye9J2ep4fEVwtpxdCBucJvXl8dY./ZbV2",
                "is_active": True,
                "created_at": datetime(2023, 10, 11, 10, 30, 0, tzinfo=timezone.utc),
                "updated_at": datetime(2023, 10, 11, 10, 30, 0, tzinfo=timezone.utc),
            },
        ],
        "search_configs": [
            {
                "id": 1,
                "search_term": "notebook vaio",
                "is_active": True,
                "frequency_days": 1,
                "preferred_time": time(9, 0),
                "search_metadata": {"condition": "used"},
                "source_website_ids": [1],
                "user_id": 2,
            },
            {
                "id": 2,
                "search_term": "controle gamesir",
                "is_active": True,
                "frequency_days": 1,
                "preferred_time": time(9, 30),
                "search_metadata": {"category": "eletrônicos", "warranty": True},
                "source_website_ids": [2],
                "user_id": 2,
            },
            {
                "id": 3,
                "search_term": "fones de ouvidos qcy com anc",
                "is_active": True,
                "frequency_days": 1,
                "preferred_time": time(10, 0),
                "search_metadata": {"category": "eletrônicos", "warranty": True},
                "source_website_ids": [3],
                "user_id": 2,
            },
            {
                "id": 4,
                "search_term": "python e django",
                "is_active": True,
                "frequency_days": 1,
                "preferred_time": time(10, 30),
                "search_metadata": {"category": "livros", "warranty": True},
                "source_website_ids": [4],
                "user_id": 2,
            },
        ],
    }
