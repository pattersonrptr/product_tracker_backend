from fastapi import FastAPI, Depends, HTTPException, status
from typing import List
from services.database_manager import DatabaseManager
from schemas.schemas import AdCreate, AdResponse

app = FastAPI()

# Dependência
def get_db():
    db = DatabaseManager()
    try:
        yield db
    finally:
        db.engine.dispose()

@app.post("/ads/", response_model=AdResponse, status_code=status.HTTP_201_CREATED)
def create_ad(ad: AdCreate, db: DatabaseManager = Depends(get_db)):
    try:
        new_ad = db.save_ad(url=ad.url, title=ad.title, price=ad.price)
        return new_ad  # Conversão automática via orm_mode
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao criar anúncio: {str(e)}"
        )

@app.get("/ads/", response_model=List[AdResponse])
def read_all_ads(db: DatabaseManager = Depends(get_db)):
    try:
        return db.get_all_ads()  # Lista de objetos Ad convertida automaticamente
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao buscar anúncios: {str(e)}"
        )

@app.get("/ads/{ad_id}", response_model=AdResponse)
async def read_ad(ad_id: int, db: DatabaseManager = Depends(get_db)):
    ad = db.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anúncio não encontrado"
        )
    return ad

@app.delete("/ads/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_ad(ad_id: int, db: DatabaseManager = Depends(get_db)):
    ad = db.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Anúncio não encontrado"
        )
    try:
        db.delete_ad(ad_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao deletar anúncio: {str(e)}"
        )
