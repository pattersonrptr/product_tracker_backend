from fastapi import FastAPI

from app.interfaces.controllers import (
    product_controller,
    price_history_controller,
    source_website_controller,
    search_config_controller,
    user_controller,
)

app = FastAPI()

app.include_router(product_controller.router)
app.include_router(price_history_controller.router)
app.include_router(source_website_controller.router)
app.include_router(search_config_controller.router)
app.include_router(user_controller.router)
