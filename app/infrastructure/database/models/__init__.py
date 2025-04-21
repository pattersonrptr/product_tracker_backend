from app.infrastructure.database_config import Base

from . import user_model  # noqa: F401
from . import search_config_model  # noqa: F401
from . import source_website_model  # noqa: F401
from . import search_config_source_website_model  # noqa: F401
from . import search_execution_log_model  # noqa: F401
from . import product_model  # noqa: F401
from . import price_history_model  # noqa: F401

Base.registry.configure()
