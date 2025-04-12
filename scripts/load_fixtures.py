from app.fixtures import get_fixtures
from app.database import SessionLocal
from app.models.product_models import SourceWebsite, Product, PriceHistory


def main():
    db = SessionLocal()
    data = get_fixtures()
    try:
        db.bulk_insert_mappings(SourceWebsite, data["source_websites"])
        db.bulk_insert_mappings(Product, data["products"])
        db.bulk_insert_mappings(PriceHistory, data["price_history"])
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    main()
