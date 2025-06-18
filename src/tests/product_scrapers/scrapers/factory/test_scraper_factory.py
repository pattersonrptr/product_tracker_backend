import pytest
from src.product_scrapers.scrapers.factory.scraper_factory import ScraperFactory
from src.product_scrapers.scrapers.olx import OLXScraper
from src.product_scrapers.scrapers.enjoei import EnjoeiScraper
from src.product_scrapers.scrapers.estante_virtual import EstanteVirtualScraper
from src.product_scrapers.scrapers.mercado_livre import MercadoLivreScraper


@pytest.mark.parametrize(
    "name,expected_type",
    [
        ("olx", OLXScraper),
        ("enjoei", EnjoeiScraper),
        ("estante_virtual", EstanteVirtualScraper),
        ("mercado_livre", MercadoLivreScraper),
        ("OLX", OLXScraper),
        ("ENJOEI", EnjoeiScraper),
    ],
)
def test_create_scraper_success(name, expected_type):
    scraper = ScraperFactory.create_scraper(name)
    assert isinstance(scraper, expected_type)


def test_create_scraper_invalid():
    with pytest.raises(ValueError) as exc:
        ScraperFactory.create_scraper("foo")
    assert "Not supported scraper" in str(exc.value)
