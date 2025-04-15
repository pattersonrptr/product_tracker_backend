from app.fixtures import get_fixtures
from app.database import SessionLocal
from app.models import (  # User,
    SourceWebsite,
    Product,
    PriceHistory,
    SearchConfig,
)


def load_fixtures():
    db = SessionLocal()
    data = get_fixtures()

    try:
        # db.bulk_insert_mappings(User, data['users'])
        db.bulk_insert_mappings(SourceWebsite, data["source_websites"])
        db.bulk_insert_mappings(Product, data["products"])
        db.bulk_insert_mappings(PriceHistory, data["price_history"])
        db.bulk_insert_mappings(SearchConfig, data["search_configs"])

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()
