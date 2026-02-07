from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import os
from dotenv import load_dotenv

load_dotenv()

# Default to /app/data/ which is the Railway volume mount path
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/data/combat.db")

# Safety: ensure SQLite databases use the persistent volume directory
if DATABASE_URL.startswith("sqlite:///") and "/app/data/" not in DATABASE_URL:
    import sys
    print(f"⚠️  WARNING: DATABASE_URL={DATABASE_URL} is NOT using /app/data/ volume!", file=sys.stderr)
    print(f"⚠️  This will cause data loss on redeployment!", file=sys.stderr)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI routes"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize the database - create all tables if they don't exist"""
    import os
    
    # Check if database file exists (for SQLite)
    db_exists = False
    if "sqlite" in DATABASE_URL:
        db_path = DATABASE_URL.replace("sqlite:///", "")
        db_exists = os.path.exists(db_path)
    
    Base.metadata.create_all(bind=engine)
    
    if db_exists:
        print("✅ Database already exists - schema updated if needed")
    else:
        print("✅ Database initialized successfully!")
        # Only seed questions on first initialization
        try:
            from seed_questions import seed_questions
            seed_questions()
            print("✅ Questions seeded successfully!")
        except Exception as e:
            print(f"⚠️  Question seeding skipped: {e}")

if __name__ == "__main__":
    init_database()
