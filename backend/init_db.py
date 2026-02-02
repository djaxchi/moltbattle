import sys
import os
from database import init_database, DATABASE_URL
from seed_questions import seed_questions

def main():
    # Extract database file path from DATABASE_URL
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = DATABASE_URL.replace("sqlite:///", "")
        # Handle relative paths (starting with ./)
        if db_path.startswith("./"):
            db_path = db_path[2:]
        
        # Delete existing database if it exists
        if os.path.exists(db_path):
            print(f"Found existing database at {db_path}, deleting...")
            os.remove(db_path)
            print("Existing database deleted.")

    print("Initializing database...")
    init_database()
    
    print("Seeding questions...")
    seed_questions()
    
    print("Database setup complete!")

if __name__ == "__main__":
    main()
