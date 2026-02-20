# 🚀 Location Safety RAG - Installation & Testing Guide

## ✅ Fixed & Completed

All missing files have been created and the project is now complete:
- ✅ `app/api/schemas.py` - API request/response models
- ✅ `app/rag/embeddings.py` - Sentence-Transformers integration
- ✅ `app/utils/logger.py` - Logging configuration
- ✅ All `__init__.py` files for package imports
- ✅ Pipeline fixed for category/sentiment extraction

---

## 📋 How the System Works

### **POST API**: `/feedback/submit`
Frontend sends user feedback with location:
```json
{
  "question": "How safe is this area after 10 PM?",
  "answer": "Generally safe with good police presence and street lights, though some petty theft reported",
  "location": {
    "lat": 28.6139,
    "long": 77.2090,
    "name": "Delhi - Connaught Place"
  },
  "rating": 4,
  "user_id": "user_123"
}
```

✅ System:
1. Validates all inputs
2. **Stores feedback** in PostgreSQL
3. **Generates embeddings** using Sentence-Transformers
4. Extracts **category** & **sentiment** using Groq AI
5. Returns feedback_id

### **GET API**: `/location/analyze?lat=28.6139&long=77.2090&name=Delhi`

✅ System:
1. Finds all feedback within **5km radius** of location
2. Uses **vector similarity** to find relevant feedback
3. Retrieves **top 15 most similar** feedbacks
4. **Analyzes** using Groq LLM to generate:
   - Safety score (0-10)
   - Trend (improving/stable/declining)
   - Time-based patterns (morning/afternoon/evening/night)
   - Top concerns & positive aspects
   - Recommendations
5. Returns comprehensive safety analysis

---

## 🔧 Installation & Setup

### **Step 1: Install Python Dependencies**
```bash
# Navigate to project folder
cd c:\Users\hp\Documents\Git Projects\eugugma\location_feedback_API

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### **Step 2: Setup PostgreSQL Database**

**Option A: Using Command Line (Windows)**
```powershell
# Check PostgreSQL is installed
psql --version

# Login to PostgreSQL
psql -U postgres

# In PostgreSQL console:
CREATE DATABASE location_safety;
\c location_safety
CREATE EXTENSION IF NOT EXISTS vector;
\q
```

**Option B: Using pgAdmin (GUI)**
1. Open pgAdmin
2. Create new database `location_safety`
3. Connect to database
4. Open Query Editor
5. Run: `CREATE EXTENSION IF NOT EXISTS vector;`

### **Step 3: Verify .env Configuration**

Your `.env` file already has:
- ✅ DATABASE_URL configured for postgres:postgres
- ✅ GROQ_API_KEY set (get your key from https://console.groq.com)
- ✅ All LLM parameters configured
- ✅ Embeddings model configured

**If you need to change the database password**, update:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/location_safety
```

### **Step 4: Initialize Database Tables**

```bash
# Make sure venv is activated
python app/database/init.py
```

Output should be:
```
🔧 Initializing database...
📍 Database URL: postgresql://postgres:postgres@localhost:5432/location_safety
✅ Database initialized successfully!

Tables created:
  - feedback
  - location_profiles
```

---

## 🚀 Running the Application

```bash
# Activate virtual environment
venv\Scripts\activate

# Start the server
uvicorn app.main:app --reload
```

**Expected startup output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     ============================================================
INFO:     🚀 Starting Location Safety RAG Application...
INFO:     ============================================================
INFO:     ✅ Database ready
INFO:     ✅ RAG Pipeline initialized
INFO:     ✅ Application started successfully
INFO:     ============================================================
INFO:     📖 Documentation: http://localhost:8000/docs
INFO:     ============================================================
```

---

## 🧪 Testing the API

### **Method 1: Using Swagger UI (Recommended)**

1. Open: **http://localhost:8000/docs**
2. You'll see all endpoints with Try it Out buttons

### **Method 2: Using test_api.py**

```bash
python test_api.py
```

### **Method 3: Using cURL (PowerShell)**

**Submit Feedback (POST):**
```powershell
$body = @{
    question = "How safe is this area at night?"
    answer = "Very safe with good street lighting and police patrols"
    location = @{
        lat = 28.6139
        long = 77.2090
        name = "Delhi"
    }
    rating = 5
    user_id = "user_001"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/feedback/submit" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

**Analyze Location (GET):**
```powershell
Invoke-WebRequest -Uri "http://localhost:8000/location/analyze?lat=28.6139&long=77.2090&name=Delhi" `
  -Method GET
```

### **Method 4: Using Python Requests**

```python
import requests

# Submit feedback
feedback_data = {
    "question": "How safe is this area at night?",
    "answer": "Very safe with good street lighting and police patrols",
    "location": {
        "lat": 28.6139,
        "long": 77.2090,
        "name": "Delhi"
    },
    "rating": 5,
    "user_id": "user_001"
}

response = requests.post(
    "http://localhost:8000/feedback/submit",
    json=feedback_data
)
print(response.json())

# Analyze location
response = requests.get(
    "http://localhost:8000/location/analyze",
    params={
        "lat": 28.6139,
        "long": 77.2090,
        "name": "Delhi"
    }
)
print(response.json())
```

---

## 🔗 Available Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/feedback/submit` | POST | Submit location feedback |
| `/location/analyze` | GET | Analyze location safety |
| `/health` | GET | Health check |
| `/docs` | GET | Swagger documentation |
| `/redoc` | GET | ReDoc documentation |

---

## 🐛 Troubleshooting

### **Error: "DATABASE_URL not set"**
→ Check `.env` file exists in root directory with DATABASE_URL

### **Error: "GROQ_API_KEY not set"**
→ Your API key is already configured in `.env`, but ensure it's correct

### **Error: "psycopg binary not found"**
→ Run: `pip install psycopg[binary]`

### **Error: "Sentence-Transformers model not found"**
→ Run: `pip install sentence-transformers` (will download model ~500MB on first run)

### **Error: "connection refused" for PostgreSQL**
→ Make sure PostgreSQL service is running:
```powershell
# Windows - Check if PostgreSQL is running
Get-Service postgresql-x64* | Start-Service
```

### **Port 8000 already in use**
→ Use different port:
```bash
uvicorn app.main:app --port 8001 --reload
```

---

## ✨ Example Workflow

1. **Submit Feedback** (POST):
   - User in Delhi submits: "How safe at night?" → "Very safe, good police"
   - Rating: 5/5
   - System stores it with embeddings

2. **Submit More Feedback** (POST):
   - Another user: "Is it crowded?" → "Yes, very crowded, but safe"
   - Rating: 4/5
   - System stores it

3. **Analyze Location** (GET):
   - Request: Get safety analysis for Delhi (28.6139, 77.2090)
   - System retrieves both feedbacks
   - Groq AI analyzes and generates:
     ```
     Safety Score: 4.5/10
     Trend: Stable
     Top Concerns: ["Crowd density", "Petty theft"]
     Positive: ["Good police presence", "Street lighting"]
     Night Safety: Safe
     Recommendations: ["Avoid early morning", "Keep valuables safe"]
     ```

---

## 📚 Project Structure

```
location_feedback_API/
├── app/
│   ├── main.py                 # FastAPI app
│   ├── config.py               # Settings from .env
│   ├── api/
│   │   ├── routes.py           # POST/GET endpoints
│   │   └── schemas.py          # Request/response models ✅ NEW
│   ├── database/
│   │   ├── connection.py       # PostgreSQL setup
│   │   ├── models.py           # SQLAlchemy models
│   │   └── init.py             # DB initialization
│   ├── rag/
│   │   ├── embeddings.py       # Sentence-Transformers ✅ NEW
│   │   ├── retriever.py        # Vector similarity search
│   │   ├── generator.py        # Groq LLM analysis
│   │   └── pipeline.py         # Complete RAG flow
│   └── utils/
│       ├── logger.py           # Logging setup ✅ NEW
│       └── validators.py       # Input validation
├── .env                        # Configuration (already setup)
├── requirements.txt            # Dependencies
└── test_api.py                # API test script
```

---

## 📊 Data Flow Diagram

```
Frontend
   ↓
┌──────────────────────────────┐
│  POST /feedback/submit       │
│  (Q, A, location, rating)    │
└──────────────────────────────┘
   ↓
Database Stores:
  - Question & Answer
  - Location (lat, long)
  - Rating
  - Embeddings
  - Category & Sentiment
   ↓
┌──────────────────────────────┐
│  GET /location/analyze       │
│  (lat, long)                 │
└──────────────────────────────┘
   ↓
Retriever finds similar feedback within 5km
   ↓
Groq LLM analyzes all feedback
   ↓
Returns: Safety Score, Trends, Concerns, Recommendations
```

---

## 🎓 Next Steps

1. ✅ Complete setup guide done
2. 🧪 Start server and test endpoints
3. 📊 Submit test feedback from multiple locations
4. 🔍 Query locations and see AI analysis
5. 🚀 Connect frontend to API
6. 📈 Monitor and improve with more data

Happy testing! 🎉
