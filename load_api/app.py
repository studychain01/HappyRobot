import json, os, threading
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("LOADS_API_KEY", "mysecret")
DATA_PATH = os.getenv("LOADS_DATA_PATH", "loads.json")

_loads_write_lock = threading.Lock()

app = FastAPI(title="Loads API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def read_loads():
    with open(DATA_PATH, "r") as f:
        return json.load(f)

def write_loads(loads_list):
    with _loads_write_lock:
        with open(DATA_PATH, "w") as f:
            json.dump(loads_list, f, indent=2)

def require_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/loads")
def search_loads(
    origin: Optional[str] = Query(None),
    destination: Optional[str] = Query(None),
    equipment_type: Optional[str] = Query(None),
    pickup_from: Optional[str] = Query(None),   # ISO date
    pickup_to: Optional[str] = Query(None),
    min_rate: Optional[int] = Query(None),
    x_api_key: Optional[str] = Header(None)
):
    require_api_key(x_api_key)
    loads = read_loads()
    def match(l):
        ok = True
        if origin:         ok &= origin.lower() in l["origin"].lower()
        if destination:    ok &= destination.lower() in l["destination"].lower()
        if equipment_type: ok &= equipment_type.lower() == l["equipment_type"].lower()
        if min_rate is not None: ok &= l["loadboard_rate"] >= min_rate
        if pickup_from:
            ok &= datetime.fromisoformat(l["pickup_datetime"].replace("Z","+00:00")) >= datetime.fromisoformat(pickup_from)
        if pickup_to:
            ok &= datetime.fromisoformat(l["pickup_datetime"].replace("Z","+00:00")) <= datetime.fromisoformat(pickup_to)
        return ok
    return {"results": [l for l in loads if match(l)]}

@app.get("/loads/{load_id}")
def get_load(load_id: str, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)
    for l in read_loads():
        if l["load_id"] == load_id:
            return l
    raise HTTPException(status_code=404, detail="Load not found")

class LoadCreate(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: str
    delivery_datetime: str
    equipment_type: str
    loadboard_rate: int
    notes: Optional[str] = None
    weight: Optional[int] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[int] = None
    dimensions: Optional[str] = None

@app.post("/loads")
def create_load(load: LoadCreate, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)
    loads = read_loads()
    
    # Check if load_id already exists
    for l in loads:
        if l["load_id"] == load.load_id:
            raise HTTPException(status_code=400, detail="Load ID already exists")
    
    # Add new load
    new_load = load.model_dump()
    loads.append(new_load)
    write_loads(loads)
    
    return {"status": "created", "load_id": load.load_id}

@app.delete("/loads/{load_id}")
def delete_load(load_id: str, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)
    loads = read_loads()
    
    # Find and remove load
    for i, l in enumerate(loads):
        if l["load_id"] == load_id:
            deleted_load = loads.pop(i)
            write_loads(loads)
            return {"status": "deleted", "load_id": load_id}
    
    raise HTTPException(status_code=404, detail="Load not found")
