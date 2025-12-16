import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Build database URL
db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

# Create engine
engine = create_engine(db_url)

# Query users
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM users"))
    users = result.fetchall()
    
    print("\n=== USERS TABLE ===")
    print(f"Total users: {len(users)}\n")
    
    for user in users:
        print(f"ID: {user[0]}")
        print(f"Username: {user[1] if len(user) > 1 else 'N/A'}")
        print(f"Email: {user[2] if len(user) > 2 else 'N/A'}")
        print(f"Created: {user[-1] if len(user) > 0 else 'N/A'}")
        print("-" * 40)
