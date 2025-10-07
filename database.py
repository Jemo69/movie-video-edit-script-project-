
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

TURSO_DATABASE_URL = os.getenv("TURSO_DATABASE_URL").replace("libsql://", "")
TURSO_TOKEN = os.getenv("TURSO_TOKEN")

# SQLAlchemy engine for Turso
engine = create_engine(
    f"sqlite+libsql://{TURSO_DATABASE_URL}?secure=true",
    connect_args={"auth_token": TURSO_TOKEN},
    echo=True
)

# SQLAlchemy sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy declarative base
Base = declarative_base()

def init_db():
    Base.metadata.create_all(bind=engine)
