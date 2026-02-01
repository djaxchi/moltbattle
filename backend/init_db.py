import sys
from database import init_database
from seed_questions import seed_questions

def main():
    print("Initializing database...")
    init_database()
    
    print("Seeding questions...")
    seed_questions()
    
    print("Database setup complete!")

if __name__ == "__main__":
    main()
