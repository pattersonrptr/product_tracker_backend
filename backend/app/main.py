
from fastapi import FastAPI
from app.api.ads import router as ads_router
from app.config import settings

app = FastAPI()
app.include_router(ads_router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
