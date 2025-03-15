from unittest.mock import patch, Mock
from importlib import reload
from app.database import get_db_url_from_alembic_ini


def test_get_db_url_from_alembic_ini():
    with patch('app.database.ConfigParser') as mock_parser:
        mock_config = Mock()
        mock_parser.return_value = mock_config
        mock_config.get.return_value = 'postgresql://user:***@db:5432/price_monitor'
        url = get_db_url_from_alembic_ini()
        called_path = mock_config.read.call_args[0][0]

        assert called_path.endswith('alembic.ini'), f"Unexpected path: {called_path}"

        mock_config.get.assert_called_once_with('alembic', 'sqlalchemy.url')
        assert url == 'postgresql://user:***@db:5432/price_monitor'


def test_engine_creation():
    with patch('app.database.get_db_url_from_alembic_ini') as mock_get_url:
        mock_get_url.return_value = 'postgresql://user:***@db:5432/price_monitor'

        from app import database
        reload(database)

        assert str(database.engine.url) == 'postgresql://user:***@db:5432/price_monitor'


def test_session_local_config():
    from app.database import SessionLocal, engine
    assert SessionLocal.kw['autocommit'] is False
    assert SessionLocal.kw['autoflush'] is False
    assert SessionLocal.kw['bind'] is engine


def test_base_declarative():
    from app.database import Base
    from sqlalchemy.orm import declarative_base
    assert isinstance(Base, declarative_base().__class__)
