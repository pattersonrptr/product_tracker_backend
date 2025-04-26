from product_scrapers.interfaces.scraper_interface import ScraperInterface
from product_scrapers.scrapers.enjoei import EnjoeiScraper
from product_scrapers.scrapers.estante_virtual import EstanteVirtualScraper
from product_scrapers.scrapers.mercado_livre import MercadoLivreScraper
from product_scrapers.scrapers.olx import OLXScraper


_registry = {}


def register_scraper(name):
    def decorator(cls):
        _registry[name] = cls
        return cls

    return decorator


class ScraperFactory:
    @staticmethod
    def create_scraper(name: str) -> ScraperInterface:
        match name.lower():
            case "olx":
                return OLXScraper()
            case "enjoei":
                return EnjoeiScraper()
            case "estante_virtual":
                return EstanteVirtualScraper()
            case "mercado_livre":
                return MercadoLivreScraper()
            case _:
                raise ValueError(f"Scraper '{name}' não suportado.")
