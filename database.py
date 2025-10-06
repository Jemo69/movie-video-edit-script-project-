import random
import asyncio
import os
from tortoise import Tortoise
from dotenv import load_dotenv
from tortoise.exceptions import DBConnectionError, OperationalError
from urllib.parse import urlparse
from typing import Dict, Any
from logger import get_logger 

load_dotenv()
logger = get_logger(__name__)

# In your database connection module

def get_tortoise_config() -> Dict[str, Any] | None:
    """
    Constructs the Tortoise ORM configuration from a NEON_DATABASE_URL environment variable,
    including connection pool management settings.
    """
    db_url: str | None = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        return None

    parsed_url = urlparse(db_url)
    
    credentials: Dict[str, Any] = {
        "host": parsed_url.hostname,
        "port": parsed_url.port or 5432,
        "user": parsed_url.username,
        "password": parsed_url.password,
        "database": parsed_url.path.lstrip('/'),
        "ssl": "require"
    }

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": credentials,
                
                # --- START: THE FIX ---
                # These are parameters for the underlying asyncpg connection pool.
                
                # Minimum number of connections to keep in the pool.
                "min_size": 2,
                
                # Maximum number of connections in the pool.
                "max_size": 10,
                
                # **THIS IS THE MOST IMPORTANT SETTING FOR YOUR PROBLEM**
                # Close connections that have been idle in the pool for more than 180 seconds (3 minutes).
                # This ensures we don't try to use a connection that Neon has already closed.
                # Neon's default idle timeout is 5 minutes. This value MUST be lower.
                "max_inactive_connection_lifetime": 180 
                # --- END: THE FIX ---
            }
        },
        "apps": {
            "models": {
                "models": ["models", "aerich.models"],
                "default_connection": "default",
            }
        },
    }

async def init_db(max_retries: int = 5, initial_delay: float = 1.0) -> None:
    """
    Initializes the database connection with retry logic.
    
    Args:
        max_retries: Maximum number of connection attempts
        initial_delay: Initial delay between retries in seconds (will exponential backoff)
    """
    config = get_tortoise_config()
    if not config:
        raise ValueError("NEON_DATABASE_URL environment variable not set or empty. Please check your .env file.")
    
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting database connection (attempt {attempt}/{max_retries})")
            await Tortoise.init(config=config)
            await Tortoise.generate_schemas()
            logger.info("Database connection established successfully")
            return  # Success, exit the function
            
        except (ConnectionResetError, ConnectionError, DBConnectionError, OperationalError) as e:
            logger.warning(f"Database connection failed on attempt {attempt}: {e}")
            
            if attempt == max_retries:
                logger.error("All database connection attempts failed")
                raise  # Re-raise the last exception after all retries
                
            # Calculate next delay with exponential backoff and jitter
            next_delay = delay * (2 ** (attempt - 1))  # Exponential backoff
            jitter = next_delay * 0.25  # Add up to 25% jitter
            actual_delay = next_delay + (jitter * random.random())
            
            logger.info(f"Retrying in {actual_delay:.2f} seconds...")
            await asyncio.sleep(actual_delay)
            
        except Exception as e:
            # For other exceptions, don't retry
            logger.error(f"Unexpected error during database initialization: {e}")
            raise

# You might also want to add retry logic to your connection getter
TORTOISE_ORM = get_tortoise_config()
