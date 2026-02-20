"""
Database initialization script
Run this to setup the PostgreSQL database with all required tables
"""

from sqlalchemy import create_engine, text
from app.config import get_settings
from app.database.models import Base
from app.utils.logger import get_logger

logger = get_logger(__name__)

def init_database():
    """Initialize database with all tables"""
    settings = get_settings()
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL, echo=True)
        
        print("🔧 Initializing database...")
        print(f"📍 Database URL: {settings.DATABASE_URL}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database initialized successfully!")
        print("\nTables created:")
        print("  - feedback")
        print("  - location_profiles")
        
        # Print sample query
        print("\n📝 You can now:")
        print("  1. Submit feedback via POST /feedback/submit")
        print("  2. Analyze locations via GET /location/analyze")
        print("  3. Start the server: uvicorn app.main:app --reload")
        
        engine.dispose()
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    init_database()
