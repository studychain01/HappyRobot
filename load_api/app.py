import json, os, threading
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

API_KEY = os.getenv("LOADS_API_KEY", "mysecret")
DATA_PATH = os.getenv("LOADS_DATA_PATH", "loads.json")
CONVERSATIONS_PATH = os.getenv("CONVERSATIONS_DATA_PATH", "conversations.json")

_loads_write_lock = threading.Lock()
_conversations_write_lock = threading.Lock()

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

def read_conversations():
    try:
        with open(CONVERSATIONS_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def write_conversations(conversations_list):
    with _conversations_write_lock:
        with open(CONVERSATIONS_PATH, "w") as f:
            json.dump(conversations_list, f, indent=2)

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

class ConversationData(BaseModel):
    conversation_id: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    mc_number: Optional[str] = None
    conversation_summary: str
    load_requirements: Optional[str] = None
    equipment_needed: Optional[str] = None
    pickup_location: Optional[str] = None
    delivery_location: Optional[str] = None
    pickup_date: Optional[str] = None
    delivery_date: Optional[str] = None
    rate_discussed: Optional[int] = None
    customer_priority: Optional[str] = None  # high, medium, low
    follow_up_needed: Optional[bool] = False
    follow_up_date: Optional[str] = None
    agent_notes: Optional[str] = None
    timestamp: Optional[str] = None

class WebhookPayload(BaseModel):
    # Core data that the webhook might send
    transcript: Optional[str] = None
    classification: Optional[str] = None
    extracted_information: Optional[Dict[str, Any]] = None
    
    # Call/conversation metadata
    call_id: Optional[str] = None
    call_type: Optional[str] = None  # Inbound, Outbound
    call_duration: Optional[int] = None
    call_timestamp: Optional[str] = None
    
    # Customer information (might be extracted)
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    customer_company: Optional[str] = None
    mc_number: Optional[str] = None
    
    # Load/shipping related extracted data
    pickup_location: Optional[str] = None
    delivery_location: Optional[str] = None
    pickup_date: Optional[str] = None
    delivery_date: Optional[str] = None
    equipment_type: Optional[str] = None
    load_weight: Optional[str] = None
    commodity_type: Optional[str] = None
    rate_mentioned: Optional[str] = None
    miles: Optional[int] = None
    load_classification: Optional[str] = None  # "successful" or "not successful"
    
    # AI analysis results
    sentiment: Optional[str] = None
    intent: Optional[str] = None
    priority_level: Optional[str] = None
    follow_up_required: Optional[bool] = None
    follow_up_reason: Optional[str] = None
    
    # Any additional variables the system might send
    additional_data: Optional[Dict[str, Any]] = None

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

@app.post("/conversations")
def create_conversation(conversation: ConversationData, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)
    conversations = read_conversations()
    
    # Check if conversation_id already exists
    for c in conversations:
        if c["conversation_id"] == conversation.conversation_id:
            raise HTTPException(status_code=400, detail="Conversation ID already exists")
    
    # Add timestamp if not provided
    new_conversation = conversation.model_dump()
    if not new_conversation.get("timestamp"):
        new_conversation["timestamp"] = datetime.now().isoformat()
    
    conversations.append(new_conversation)
    write_conversations(conversations)
    
    return {"status": "created", "conversation_id": conversation.conversation_id}

@app.get("/conversations")
def get_conversations(
    customer_name: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    follow_up_needed: Optional[bool] = Query(None),
    x_api_key: Optional[str] = Header(None)
):
    require_api_key(x_api_key)
    conversations = read_conversations()
    
    def match(c):
        ok = True
        if customer_name: ok &= customer_name.lower() in (c.get("customer_name", "") or "").lower()
        if priority: ok &= priority.lower() == (c.get("customer_priority", "") or "").lower()
        if follow_up_needed is not None: ok &= c.get("follow_up_needed", False) == follow_up_needed
        return ok
    
    # Sort by timestamp (newest first)
    filtered_conversations = [c for c in conversations if match(c)]
    filtered_conversations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return {"results": filtered_conversations}

@app.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, x_api_key: Optional[str] = Header(None)):
    require_api_key(x_api_key)
    for c in read_conversations():
        if c["conversation_id"] == conversation_id:
            return c
    raise HTTPException(status_code=404, detail="Conversation not found")

@app.post("/webhook/extraction")
def receive_extraction_webhook(payload: WebhookPayload, x_api_key: Optional[str] = Header(None)):
    """
    Webhook endpoint to receive extracted information from AI agents/systems.
    Automatically converts webhook data into conversation records.
    """
    require_api_key(x_api_key)
    
    # Generate conversation ID from call_id or timestamp
    conversation_id = payload.call_id or f"webhook_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create conversation summary from available data
    summary_parts = []
    
    # Use transcript (limit to 300 chars for readability)
    if payload.transcript:
        transcript_summary = payload.transcript[:300]
        if len(payload.transcript) > 300:
            transcript_summary += "..."
        summary_parts.append(transcript_summary)
    
    # Add classification if available
    if payload.classification:
        summary_parts.append(f"[{payload.classification}]")
    
    # Add intent if available
    if payload.intent:
        summary_parts.append(f"Intent: {payload.intent}")
    
    # If no transcript, create summary from other fields (excluding customer name)
    if not payload.transcript:
        if payload.pickup_location and payload.delivery_location:
            summary_parts.append(f"Route: {payload.pickup_location} → {payload.delivery_location}")
        if payload.equipment_type:
            summary_parts.append(f"Equipment: {payload.equipment_type}")
        if payload.rate_mentioned:
            summary_parts.append(f"Rate: {payload.rate_mentioned}")
        if payload.call_type:
            summary_parts.append(f"{payload.call_type} call")
    
    conversation_summary = " | ".join(summary_parts) if summary_parts else "Webhook data received"
    
    # Parse rate if mentioned as string
    rate_discussed = None
    if payload.rate_mentioned:
        try:
            # Extract numbers from rate string (e.g., "$2,500" -> 2500)
            import re
            rate_match = re.search(r'[\d,]+', str(payload.rate_mentioned).replace(',', ''))
            if rate_match:
                rate_discussed = int(rate_match.group())
        except:
            pass
    
    # Build agent notes from AI analysis
    agent_notes_parts = []
    if payload.load_classification:
        agent_notes_parts.append(f"Load Status: {payload.load_classification.title()}")
    if payload.sentiment:
        agent_notes_parts.append(f"Sentiment: {payload.sentiment}")
    if payload.follow_up_reason:
        agent_notes_parts.append(f"Follow-up reason: {payload.follow_up_reason}")
    if payload.call_duration:
        agent_notes_parts.append(f"Call duration: {payload.call_duration}s")
    if payload.extracted_information:
        agent_notes_parts.append(f"Additional extracted data: {payload.extracted_information}")
    if payload.additional_data:
        agent_notes_parts.append(f"Additional webhook data: {payload.additional_data}")
    
    agent_notes = " | ".join(agent_notes_parts) if agent_notes_parts else None
    
    # Create conversation data from webhook payload
    conversation_data = ConversationData(
        conversation_id=conversation_id,
        customer_name=payload.customer_name or payload.customer_company,
        customer_phone=payload.customer_phone,
        customer_email=payload.customer_email,
        mc_number=payload.mc_number,
        conversation_summary=conversation_summary,
        load_requirements=f"{payload.load_weight or ''} {payload.commodity_type or ''}".strip() or None,
        equipment_needed=payload.equipment_type,
        pickup_location=payload.pickup_location,
        delivery_location=payload.delivery_location,
        pickup_date=payload.pickup_date,
        delivery_date=payload.delivery_date,
        rate_discussed=rate_discussed,
        customer_priority=payload.priority_level or "medium",
        follow_up_needed=payload.follow_up_required or False,
        agent_notes=agent_notes,
        timestamp=payload.call_timestamp or datetime.now().isoformat(),
        miles=payload.miles
    )
    
    # Save to conversations
    conversations = read_conversations()
    
    # Check if conversation already exists (update instead of duplicate)
    existing_index = None
    for i, c in enumerate(conversations):
        if c["conversation_id"] == conversation_id:
            existing_index = i
            break
    
    new_conversation = conversation_data.model_dump()
    
    if existing_index is not None:
        # Update existing conversation
        conversations[existing_index] = new_conversation
        status = "updated"
    else:
        # Add new conversation
        conversations.append(new_conversation)
        status = "created"
    
    write_conversations(conversations)
    
    return {
        "status": status,
        "conversation_id": conversation_id,
        "message": "Webhook data successfully processed and converted to conversation record",
        "extracted_fields": {
            "customer_name": payload.customer_name,
            "pickup_location": payload.pickup_location,
            "delivery_location": payload.delivery_location,
            "equipment_type": payload.equipment_type,
            "rate_discussed": rate_discussed,
            "priority": payload.priority_level,
            "follow_up_needed": payload.follow_up_required
        }
    }

@app.get("/webhook/test")
def webhook_test_endpoint():
    """Test endpoint to verify webhook connectivity"""
    return {
        "status": "ok",
        "message": "Webhook endpoint is active",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "POST /webhook/extraction": "Main webhook for receiving extracted call data",
            "GET /webhook/test": "This test endpoint"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
