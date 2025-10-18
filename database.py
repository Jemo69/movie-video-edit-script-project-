import os
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from dotenv import load_dotenv
from typing import Type, Optional

load_dotenv()

# Global variables for the engine and session
engine: Optional[Engine] = None
SessionLocal: Optional[Type[Session]] = None
Base = declarative_base()

def init_db():
    """
    Initialize the database engine and session.
    This function is designed to be called once at application startup.
    """
    global engine, SessionLocal

    # Proceed only if the engine has not been initialized
    if engine is not None:
        return

    turso_url = os.getenv("TURSO_DATABASE_URL")
    turso_token = os.getenv("TURSO_TOKEN")

    if not turso_url:
        raise ValueError("TURSO_DATABASE_URL environment variable not set.")

    # Handle both local file and remote libsql URLs
    if turso_url.startswith("file:"):
        db_url = f"sqlite:///{turso_url.split('file:')[1]}"
        connect_args = {}
    else:
        db_url = f"sqlite+libsql://{turso_url.replace('libsql://', '')}?secure=true"
        connect_args = {"auth_token": turso_token}

    engine = create_engine(db_url, connect_args=connect_args, echo=False)

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    Base.metadata.create_all(bind=engine)

def get_session() -> Session:
    """
    Returns a new database session.
    Ensures that init_db has been called.
    """
    if SessionLocal is None:
        raise RuntimeError("Database not initialized. Please call init_db() first.")
    return SessionLocal()