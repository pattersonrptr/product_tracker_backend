from fastapi import FastAPI

from src.app.interfaces.controllers import (
    product_controller,
)
from src.app.interfaces.controllers import (
    user_controller,
    source_website_controller,
    price_history_controller,
    search_config_controller,
)

# TODO: verify if this import is necessary
from src.app.infrastructure.database import models  # noqa: F401

app = FastAPI()

app.include_router(product_controller.router)
app.include_router(price_history_controller.router)
app.include_router(source_website_controller.router)
app.include_router(search_config_controller.router)
app.include_router(user_controller.router)
