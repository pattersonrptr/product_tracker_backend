import os

from configparser import ConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Ad  # Importe a classe Ad

class DatabaseManager:
    def __init__(self, db_url=None):
        """
        Inicializa a conexão com o banco de dados.
        :param db_url: URL do banco de dados. Se None, usa a URL do alembic.ini.
        """
        if db_url is None:
            db_url = self.get_db_url_from_alembic_ini()
        
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_db_url_from_alembic_ini(self):
        config = ConfigParser()
        alembic_ini_path = os.path.join(os.path.dirname(__file__), '..', 'alembic.ini')
        config.read(alembic_ini_path)
        return config.get('alembic', 'sqlalchemy.url')

    def save_ad(self, url: str, title: str, price: float) -> Ad:
        session = self.Session()
        try:
            new_ad = Ad(url=url, title=title, price=price)
            session.add(new_ad)
            session.commit()
            session.refresh(new_ad)  # Importante para obter o ID gerado
            return new_ad
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_all_ads(self):
        session = self.Session()
        try:
            ads = session.query(Ad).all()
            return ads
        except Exception as e:
            print(f"Erro ao buscar anúncios: {e}")
            return []
        finally:
            session.close()

    def get_ad_by_id(self, ad_id):
        session = self.Session()
        try:
            ad = session.query(Ad).filter(Ad.id == ad_id).first()
            return ad
        except Exception as e:
            print(f"Erro ao buscar anúncio: {e}")
            return None
        finally:
            session.close()

    def delete_ad(self, ad_id):
        session = self.Session()
        try:
            ad = session.query(Ad).filter(Ad.id == ad_id).first()
            if ad:
                session.delete(ad)
                session.commit()
                print("Anúncio removido com sucesso!")
            else:
                print("Anúncio não encontrado.")
        except Exception as e:
            session.rollback()
            print(f"Erro ao remover anúncio: {e}")
        finally:
            session.close()
