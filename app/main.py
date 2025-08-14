from fastapi import FastAPI 
from typing import List, Optional 
from .models import Load 
from .repo import LoadRepo 
from .config import API_KEY 

app = FastAPI(title="Loads API", version="1.0.0")
repo = LoadRepo()

def require_key(x_api_key: Optional[str]):
    if x_api_key != API_KEY: 
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/loads", response_model=List[Load])
def list_loads(
    origin_state: Optional[str] = None, 
    destination_state: Optional[str] = None, 
    equipment_type: Optional[str] = None, 
    min_weight: Optional[int] = Query(None, ge=0),
    max_weight: Optional[int] = Query(None, ge=0), 
    price_min: Optional[float] = Query(None, ge=0),
    price_max: Optional[float] = Query(None, ge=0),
    status: Optional[str] = "available",
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    x_api_key: Optional[str] = Header(None)
):

    require_key(x_api_key)
    return repo.list(origin_state, destination_state, equipment_type, 
                    min_weight, max_weight, price_min, price_max,
                    status, limit, offset)

@app.get("/loads/{load_id}", response_model=Load)
def get_load(load_id: str, x_api_key: Optional[str] = Header(None)):
    require_key(x_api_key)
    load = repo.get(load_id)
    if not load: 
        raise HTTPException(status_code=404, detail="Load not found")
    return load

