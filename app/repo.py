import json 
from typing import List, Optional 
from .models import Load 
from .config import LOADS_FILE 

class LoadRepo: 
    def __init__(self, filepath: str = LOADS_FILE):
        with open(filepath, "r") as f: 
            self._data = [Load(**rec) for rec in json.load(f)]
    
    def get(self, load_id: str) -> Optional[Load]:
        return next((x for x in self._data if x.id == load_id), None)
    
    def list(self, origin_state=None, destination_state=None,
            equipment_type=None, min_weight=None, max_weight=None, 
            price_min=None, price_max=None, status="available", 
            limit=50, offset=0) -> List[Load]: 
        items = self._data 
        if origin_state: 
            items = [x for x in items if x.origin.state == origin_state]

        if destination_state: 
            items = [x for x in items if x.destination.state == destination_state]

        if equipment_type: 
            items = [x for x in items if (x.equipment_type or "").lower() == equipment_type.lower()]
        
        if min_weight: 
            items = [x for x in items if (x.weight_lbs or 0) >= min_weight]

        if max_weight: 
            items = [x for x in items if (x.weight_lbs or 0) <= max_weight]

        if price_min:
            items = [x for x in items if (x.price_usd or 0) >= price_min]
        
        if price_max: 
            items = [x for x in items if (x.price_usd or 0) <= price_max]

        if status: 
            items = [x for x in items if x.status == status]

        return items[offset: offset + limit]
        