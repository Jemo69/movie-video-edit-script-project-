
import os
from tortoise import Tortoise
from dotenv import load_dotenv
from urllib.parse import urlparse
from typing import Dict, Any

load_dotenv()

def get_tortoise_config() -> Dict[str, Any]:
    """
    Constructs the Tortoise ORM configuration from a NEON_DATABASE_URL environment variable.
    """
    db_url: str | None = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        return None  # type: ignore

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
            }
        },
        "apps": {
            "models": {
                "models": ["models", "aerich.models"],
                "default_connection": "default",
            }
        },
    }

async def init_db() -> None:
    """
    Initializes the database connection and generates schemas.
    """
    config = get_tortoise_config()
    if not config:
        raise ValueError("NEON_DATABASE_URL environment variable not set or empty. Please check your .env file.")
    
    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()

TORTOISE_ORM = get_tortoise_config()
