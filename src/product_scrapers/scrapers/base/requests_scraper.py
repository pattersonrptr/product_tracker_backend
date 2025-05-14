import cloudscraper
import requests
import time
from abc import ABC, abstractmethod

from typing import Optional, Dict, Any


class RequestScraper(ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = cloudscraper.create_scraper()

    @abstractmethod
    def headers(self) -> Dict[str, Any]:
        raise NotImplementedError

    def retry_request(
        self,
        url: str,
        headers: dict = {},
        max_retries: int = 3,
        backoff_factor: float = 2,
    ) -> Optional[requests.Response]:
        for i in range(max_retries + 1):
            try:
                response = self.session.get(url, headers=headers, allow_redirects=True)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                print(f"Erro de conexão na tentativa {i + 1}: {str(e)}")
                if i < max_retries:
                    wait_time = (backoff_factor**i) * 1  # Exponential backoff
                    print(f"Retentando em {wait_time:.2f} segundos...")
                    time.sleep(wait_time)
                else:
                    print("Número máximo de retries atingido.")
                    return None
            except Exception as e:
                # TODO raise an exception instead of printing
                print(f"Erro inesperado na tentativa {i + 1}: {str(e)}")
                return None

        # TODO raise an exception instead of returning None
        return None
