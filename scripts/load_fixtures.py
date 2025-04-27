from app.fixtures.fixtures import get_fixtures
from app.infrastructure.database_config import SessionLocal
from app.infrastructure.database.models.source_website_model import SourceWebsite
from app.infrastructure.database.models.product_model import Product
from app.infrastructure.database.models.price_history_model import PriceHistory
from app.infrastructure.database.models.user_model import User
from app.infrastructure.database.models.search_config_model import SearchConfig
from app.infrastructure.database.models.search_config_source_website_model import (
    search_config_source_website,
)


def load_fixtures():
    db = SessionLocal()
    data = get_fixtures()

    try:
        db.bulk_insert_mappings(SourceWebsite, data["source_websites"])

        db.bulk_insert_mappings(Product, data["products"])

        db.bulk_insert_mappings(PriceHistory, data["price_history"])

        db.bulk_insert_mappings(User, data.get("users", []))

        search_configs_data = []
        for sc in data["search_configs"]:
            sc_copy = sc.copy()
            sc_copy.pop("source_website_ids", None)
            search_configs_data.append(sc_copy)

        db.bulk_insert_mappings(SearchConfig, search_configs_data)

        search_config_source_website_data = []
        for sc in data["search_configs"]:
            search_config_id = sc["id"]
            source_website_ids = sc.get("source_website_ids", [])
            for sw_id in source_website_ids:
                search_config_source_website_data.append(
                    {"search_config_id": search_config_id, "source_website_id": sw_id}
                )

        for data_point in search_config_source_website_data:
            stmt = search_config_source_website.insert().values(data_point)
            db.execute(stmt)

        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    load_fixtures()
    print("Fixtures loaded successfully.")
