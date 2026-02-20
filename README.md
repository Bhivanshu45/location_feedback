# Location Safety RAG - API

A **Retrieval Augmented Generation (RAG)** powered location safety analysis system using FastAPI, PostgreSQL, and Groq LLM.

## 🎯 Features

- **📍 Location Feedback Submission**: Users submit Q&A feedback with ratings and location data
- **🧠 RAG Pipeline**: Vector similarity search + LLM-powered analysis
- **🔍 Semantic Search**: Uses HuggingFace embeddings for intelligent retrieval
- **⚡ Groq LLM**: Fast inference with Mixtral-8x7b model
- **📊 Safety Analysis**: Time-based patterns, trends, and recommendations
- **🗄️ PostgreSQL + pgvector**: Efficient vector storage and similarity search

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI |
| Database | PostgreSQL + pgvector |
| Embeddings | Sentence-Transformers (HuggingFace) |
| LLM | Groq (Mixtral-8x7b) |
| RAG Framework | LangChain |
| Validation | Pydantic |

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- Groq API key (free from https://console.groq.com)

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone <your-repo>
cd location_feedback_API

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup PostgreSQL
# Windows: psql -U postgres
# Create database
CREATE DATABASE location_safety;

# Enable pgvector
\c location_safety
CREATE EXTENSION IF NOT EXISTS vector;

# 5. Configure .env
cp .env.example .env
# Edit .env with your credentials and Groq API key
```

## 🚀 Running the Application

```bash
# Activate venv (if not already)
venv\Scripts\activate  # Windows

# Start the server
uvicorn app.main:app --reload

# API will be available at: http://localhost:8000
# Swagger Docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 📡 API Endpoints

### 1. Submit Feedback
**POST** `/feedback/submit`

```json
{
  "question": "How safe is this area after 10 PM?",
  "answer": "Generally safe, good police presence but some petty theft",
  "location": {
    "lat": 28.6139,
    "long": 77.2090,
    "name": "Delhi"
  },
  "rating": 4,
  "timestamp": "2026-02-19T10:30:00Z",
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "success": true,
  "feedback_id": "uuid",
  "message": "Feedback received successfully",
  "processing_status": "completed"
}
```

### 2. Analyze Location
**GET** `/location/analyze?lat=28.6139&long=77.2090&name=Delhi`

**Response:**
```json
{
  "location": {
    "lat": 28.6139,
    "long": 77.2090,
    "name": "Delhi"
  },
  "safety_profile": {
    "score": 7.2,
    "trend": "improving",
    "confidence": 0.85
  },
  "insights": {
    "top_concerns": ["Heavy traffic", "Occasional crime"],
    "positive_aspects": ["Good police presence"],
    "time_patterns": {
      "morning": "Safe",
      "afternoon": "Safe",
      "evening": "Moderate",
      "night": "Caution"
    },
    "recommendations": [...]
  },
  "data_quality": {
    "reports_count": 42,
    "date_range": "Last 90 days",
    "last_updated": "2 hours ago",
    "data_freshness_hours": 2
  }
}
```

### 3. Health Check
**GET** `/health`

## 🔧 Project Structure

```
location_feedback_API/
├── app/
│   ├── api/
│   │   ├── routes.py          # API endpoints
│   │   └── schemas.py         # Pydantic models
│   ├── database/
│   │   ├── models.py          # SQLAlchemy models
│   │   └── connection.py      # DB connection
│   ├── rag/
│   │   ├── embeddings.py      # Embedding generation
│   │   ├── retriever.py       # Vector search
│   │   ├── generator.py       # LLM response
│   │   └── pipeline.py        # RAG orchestration
│   ├── utils/
│   │   └── logger.py          # Logging
│   ├── main.py                # FastAPI app
│   └── config.py              # Configuration
├── .env                       # Environment variables
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔐 Environment Variables

Create a `.env` file with:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/location_safety
GROQ_API_KEY=gsk_your_key_here
LLM_MODEL=mixtral-8x7b-32768
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## 🧪 Testing

```bash
# Test feedback submission
curl -X POST http://localhost:8000/feedback/submit \
  -H "Content-Type: application/json" \
  -d '{...}'

# Test location analysis
curl http://localhost:8000/location/analyze?lat=28.6139&long=77.2090&name=Delhi

# Health check
curl http://localhost:8000/health
```

## 📈 How RAG Works

1. **Ingestion**: User submits feedback with location
2. **Embedding**: Text is converted to vectors using Sentence-Transformers
3. **Storage**: Vectors stored in PostgreSQL with pgvector
4. **Query**: When analyzing location, similar feedback is retrieved
5. **Generation**: Groq LLM synthesizes insights from retrieved data
6. **Response**: Comprehensive safety analysis returned to user

## 🚀 Deployment

Ready to deploy to Railway/Render:

1. Push to GitHub
2. Connect repo to Railway
3. Set environment variables
4. Deploy! ✨

## 📝 License

MIT License

## 👨‍💻 Author

Built for location safety intelligence

---

**Happy analyzing!** 🎉
