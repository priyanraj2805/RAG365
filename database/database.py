from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from pathlib import Path

# Define Base FIRST
Base = declarative_base()


# Load environment variables from backend location
env_path = Path(__file__).parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

# Set AWS region for boto3
os.environ.setdefault("AWS_DEFAULT_REGION", os.getenv("AWS_REGION", "us-east-1"))

DATABASE_URL = os.getenv("DATABASE_URI")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()