from fastapi import FastAPI
from app.routers import ad_router

app = FastAPI()

app.include_router(ad_router.router)
