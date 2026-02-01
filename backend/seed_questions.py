from database import SessionLocal
from models import Question
import json

SEED_QUESTIONS = [
    {
        "prompt": "What is the capital of France?",
        "golden_label": json.dumps({"answer": "Paris", "category": "geography"})
    },
    {
        "prompt": "Write a function that returns the factorial of a number n.",
        "golden_label": json.dumps({"category": "coding", "concept": "recursion or iteration"})
    },
    {
        "prompt": "What year did World War II end?",
        "golden_label": json.dumps({"answer": "1945", "category": "history"})
    },
    {
        "prompt": "Explain the difference between TCP and UDP protocols.",
        "golden_label": json.dumps({"category": "networking", "key_points": ["reliability", "connection", "speed"]})
    },
    {
        "prompt": "What is the time complexity of binary search?",
        "golden_label": json.dumps({"answer": "O(log n)", "category": "algorithms"})
    },
    {
        "prompt": "Name three principles of object-oriented programming.",
        "golden_label": json.dumps({"answer": ["encapsulation", "inheritance", "polymorphism"], "category": "programming"})
    },
    {
        "prompt": "What does REST stand for in web APIs?",
        "golden_label": json.dumps({"answer": "Representational State Transfer", "category": "web-development"})
    },
    {
        "prompt": "Write a SQL query to find all users who registered in the last 7 days.",
        "golden_label": json.dumps({"category": "database", "concept": "date filtering"})
    }
]

def seed_questions():
    """Seed the database with initial questions"""
    db = SessionLocal()
    try:
        existing_count = db.query(Question).count()
        if existing_count > 0:
            print(f"Questions already seeded ({existing_count} questions found)")
            return
        for q_data in SEED_QUESTIONS:
            question = Question(
                prompt=q_data["prompt"],
                golden_label=q_data["golden_label"]
            )
            db.add(question)
        
        db.commit()
        print(f"Successfully seeded {len(SEED_QUESTIONS)} questions!")
    except Exception as e:
        print(f"Error seeding questions: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_questions()
