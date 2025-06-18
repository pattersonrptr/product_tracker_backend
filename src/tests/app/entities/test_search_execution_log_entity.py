from datetime import datetime, timezone
from src.app.entities.search_execution_log import SearchExecutionLog

def test_search_execution_log_minimal_fields():
    log = SearchExecutionLog(search_config_id=1)
    assert log.search_config_id == 1
    assert isinstance(log.timestamp, datetime)
    assert log.results_count is None
    assert log.status is None
    assert log.id is None

def test_search_execution_log_all_fields():
    now = datetime(2024, 1, 1, tzinfo=timezone.utc)
    log = SearchExecutionLog(
        search_config_id=2,
        timestamp=now,
        results_count=5,
        status="ok",
        id=10
    )
    assert log.search_config_id == 2
    assert log.timestamp == now
    assert log.results_count == 5
    assert log.status == "ok"
    assert log.id == 10
