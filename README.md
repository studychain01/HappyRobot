# 🚛 HappyRobot Trucking Platform

A comprehensive trucking management platform that combines load management with customer conversation tracking and classification.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Components](#components)
  - [Dashboard](#dashboard)
  - [Load API](#load-api)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Docker Setup](#docker-setup)
- [Usage Examples](#usage-examples)

## 🎯 Overview

HappyRobot Trucking Platform provides:
- **Load Management**: Create, view, and manage trucking loads
- **Customer Conversations**: Track and classify customer interactions
- **Analytics Dashboard**: Visual insights into load classifications and metrics
- **RESTful API**: Programmatic access to all platform features

## 🏗️ Architecture

```
HappyRobot Platform
├── 📊 Dashboard (Streamlit)    # Web interface for management
├── 🔌 Load API (FastAPI)      # RESTful API backend
└── 📁 Data Storage           # JSON-based data persistence
```

**Components:**
- **Dashboard**: Streamlit-based web interface for viewing loads and conversations
- **Load API**: FastAPI backend providing REST endpoints for data management
- **Data**: JSON files for persistent storage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda

### 1. Clone & Setup
```bash
git clone https://github.com/studychain01/HappyRobot.git
cd HappyRobot
pip install -r dashboard/requirements.txt
pip install -r load_api/requirements.txt
```

### 2. Start the API Server
```bash
cd load_api
python app.py
# API will be available at http://localhost:8000
```

### 3. Start the Dashboard
```bash
cd dashboard
streamlit run app.py
# Dashboard will be available at http://localhost:8501
```

### 4. Access the Platform
- **Dashboard**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs

### 🌐 Live Demo
- **Live Application**: https://happyrobot-2.onrender.com/

## 📊 Components

### Dashboard

**Features:**
- **Load Management**: View, add, and delete trucking loads
- **Equipment Analytics**: Visual breakdown by equipment type
- **Route Analysis**: Average miles by origin location
- **Customer Conversations**: Track agent interactions with customers
- **Load Classification**: Visual metrics of successful vs unsuccessful loads
- **Filtering**: Search by MC number and load status

**Navigation:**
- **Loads Dashboard**: Main load management interface
- **Customer Conversations**: Conversation tracking and metrics

### Load API

**Features:**
- RESTful endpoints for load and conversation management
- API key authentication
- JSON data persistence
- Automatic data validation
- Interactive API documentation (Swagger/OpenAPI)

**Base URL**: `http://localhost:8000`

## 🔌 API Documentation

### Authentication
All endpoints require an API key in the header:
```
x-api-key: mysecret
```

### Load Endpoints

#### GET /loads
Retrieve all loads
```bash
curl -H "x-api-key: mysecret" http://localhost:8000/loads
```

#### POST /loads
Create a new load
```bash
curl -X POST -H "x-api-key: mysecret" -H "Content-Type: application/json" \
  -d '{
    "load_id": "L-2001",
    "origin": "Dallas, TX",
    "destination": "Los Angeles, CA",
    "pickup_datetime": "2025-08-30T10:00:00Z",
    "delivery_datetime": "2025-08-31T16:00:00Z",
    "equipment_type": "Dry Van",
    "loadboard_rate": 2000
  }' http://localhost:8000/loads
```

#### DELETE /loads/{load_id}
Delete a load
```bash
curl -X DELETE -H "x-api-key: mysecret" http://localhost:8000/loads/L-2001
```

### Conversation Endpoints

#### GET /conversations
Retrieve all customer conversations
```bash
curl -H "x-api-key: mysecret" http://localhost:8000/conversations
```

#### POST /conversations
Submit a customer conversation
```bash
curl -X POST -H "x-api-key: mysecret" -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_20250115_001",
    "customer_name": "John Smith Trucking",
    "customer_phone": "+1-555-123-4567",
    "mc_number": "070208",
    "pickup_location": "Los Angeles, California",
    "delivery_location": "San Francisco, California",
    "rate_discussed": 950,
    "agent_notes": "Load Status: Successful"
  }' http://localhost:8000/conversations
```

## 🔧 Environment Variables

### Dashboard Environment
```bash
API_BASE=http://localhost:8000  # API server URL
API_KEY=mysecret               # API authentication key
```

### API Environment
```bash
API_KEY=mysecret              # Authentication key for API access
```

## 🐳 Docker Setup

### Build and Run API
```bash
cd load_api
docker build -t happyrobot-api .
docker run -p 8000:8000 happyrobot-api
```

### Build and Run Dashboard
```bash
cd dashboard
docker build -t happyrobot-dashboard .
docker run -p 8501:8501 -e API_BASE=http://host.docker.internal:8000 happyrobot-dashboard
```

## 🌐 Render Deployment

Deploy as two separate services for best practices:

### API Service (Backend)
1. **Create Web Service** on Render
2. **Settings**:
   - **Root Directory**: `load_api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Port**: 8000
3. **Environment Variables**:
   - `API_KEY=your-secret-key`

### Dashboard Service (Frontend)
1. **Create Web Service** on Render
2. **Settings**:
   - **Root Directory**: `dashboard`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
   - **Port**: 8501
3. **Environment Variables**:
   - `API_BASE=https://your-api-service.onrender.com`
   - `API_KEY=your-secret-key`

### Alternative: Single Service Deployment
If deploying as one service, specify Dockerfile path:
- **Dockerfile Path**: `load_api/Dockerfile` (for API) or `dashboard/Dockerfile` (for dashboard)

## 💡 Usage Examples

### Load Management Workflow
1. **View Loads**: Access dashboard to see current load inventory
2. **Add Load**: Use dashboard form or POST to `/loads` endpoint
3. **Analyze**: Review equipment mix and route analytics
4. **Delete**: Remove completed loads via dashboard or API

### Conversation Tracking Workflow
1. **Agent Interaction**: Agent talks with customer about load requirements
2. **Submit Conversation**: Agent submits conversation data via API
3. **Classification**: Include load classification (successful/unsuccessful) in agent notes
4. **Analytics**: View conversion metrics and classification results in dashboard

### Customer Classification
Agent notes should include load classification:
```
"agent_notes": "Load Status: Successful"    # For successful bookings
"agent_notes": "Load Status: Unsuccessful"  # For failed bookings
```

## 📈 Dashboard Features

### Conversation Metrics
- **Total Conversations**: Count of all customer interactions
- **Customer Classification**: Ratio of successful/total conversations
- **Load Classification Chart**: Visual breakdown of successful vs unsuccessful loads

### Filtering Options
- **MC Number Search**: Find conversations by motor carrier number
- **Load Status Filter**: Filter by Booked/Not Booked/Unknown status

### Load Analytics
- **Equipment Mix**: Bar chart showing distribution by equipment type
- **Route Analysis**: Average miles by origin location (top 10)

## 🔒 Security Notes

- API key authentication required for all endpoints
- Default API key is `mysecret` (change in production)
- No user authentication implemented (suitable for internal tools)

## 🏷️ Data Schema

### Load Object
```json
{
  "load_id": "string",
  "origin": "string",
  "destination": "string", 
  "pickup_datetime": "string (ISO 8601)",
  "delivery_datetime": "string (ISO 8601)",
  "equipment_type": "string",
  "loadboard_rate": "number",
  "notes": "string (optional)",
  "weight": "number (optional)",
  "commodity_type": "string (optional)",
  "num_of_pieces": "number (optional)",
  "miles": "number (optional)",
  "dimensions": "string (optional)"
}
```

### Conversation Object
```json
{
  "conversation_id": "string",
  "customer_name": "string",
  "customer_phone": "string",
  "customer_email": "string (optional)",
  "mc_number": "string",
  "pickup_location": "string",
  "delivery_location": "string", 
  "equipment_needed": "string (optional)",
  "rate_discussed": "number",
  "miles": "number (optional)",
  "agent_notes": "string",
  "timestamp": "string (auto-generated)"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test both dashboard and API functionality
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

---

**HappyRobot Trucking Platform** - Streamlining load management and customer interactions for the trucking industry.
