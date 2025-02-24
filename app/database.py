import os

from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_db_url_from_alembic_ini():
    config = ConfigParser()
    alembic_ini_path = os.path.join(os.path.dirname(__file__), '..', 'alembic.ini')
    config.read(alembic_ini_path)
    return config.get('alembic', 'sqlalchemy.url')

# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Exemplo com SQLite
db_url = get_db_url_from_alembic_ini()

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
engine = create_engine(db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
