from src.app.entities.source_website import SourceWebsite


def test_source_website_minimal_fields():
    sw = SourceWebsite(name="OLX", base_url="https://olx.com.br")
    assert sw.name == "OLX"
    assert sw.base_url == "https://olx.com.br"
    assert sw.is_active is True
    assert sw.id is None


def test_source_website_all_fields():
    sw = SourceWebsite(id=2, name="ML", base_url="https://ml.com", is_active=False)
    assert sw.id == 2
    assert sw.name == "ML"
    assert sw.base_url == "https://ml.com"
    assert sw.is_active is False
