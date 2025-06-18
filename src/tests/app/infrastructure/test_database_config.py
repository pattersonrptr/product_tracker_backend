from unittest.mock import patch, MagicMock

import src.app.infrastructure.database_config as db_config


def test_get_db_url_from_alembic_ini_reads_config(monkeypatch):
    fake_url = "sqlite:///test.db"

    class FakeConfig:
        def read(self, path):
            pass

        def get(self, section, key):
            return fake_url

    monkeypatch.setattr(db_config, "ConfigParser", lambda: FakeConfig())
    url = db_config.get_db_url_from_alembic_ini()
    assert url == fake_url


def test_engine_and_sessionlocal_created():
    assert db_config.engine is not None
    assert db_config.SessionLocal is not None


def test_get_db_yields_and_closes():
    db_mock = MagicMock()
    with patch.object(db_config, "SessionLocal", return_value=db_mock):
        gen = db_config.get_db()
        db = next(gen)
        assert db is db_mock

        try:
            next(gen)
        except StopIteration:
            pass
        db_mock.close.assert_called_once()
