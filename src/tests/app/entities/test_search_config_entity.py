from datetime import time
from src.app.entities.search_config import SearchConfig
from src.app.entities.source_website import SourceWebsite


def test_search_config_minimal_fields():
    sc = SearchConfig(search_term="notebook")
    assert sc.search_term == "notebook"
    assert sc.is_active is True
    assert sc.frequency_days == 1
    assert sc.preferred_time == time(0, 0)
    assert sc.search_metadata is None
    assert sc.source_websites is None
    assert sc.user_id is None
    assert sc.id is None


def test_search_config_all_fields():
    sw = SourceWebsite(id=1, name="OLX", base_url="https://olx.com.br")
    sc = SearchConfig(
        search_term="livro",
        is_active=False,
        frequency_days=3,
        preferred_time=time(8, 30),
        search_metadata={"foo": "bar"},
        source_websites=[sw],
        user_id=42,
        id=10,
    )
    assert sc.is_active is False
    assert sc.frequency_days == 3
    assert sc.preferred_time == time(8, 30)
    assert sc.search_metadata == {"foo": "bar"}
    assert sc.source_websites[0].name == "OLX"
    assert sc.user_id == 42
    assert sc.id == 10
