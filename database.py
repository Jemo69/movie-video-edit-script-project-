import os
from tortoise import Tortoise
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

def get_tortoise_config():
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        return None

    parsed_url = urlparse(db_url)
    
    credentials = {
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

async def init_db():
    config = get_tortoise_config()
    if not config:
        raise ValueError("NEON_DATABASE_URL environment variable not set or empty. Please check your .env file.")
    
    app_config = config.copy()
    app_config["apps"]["models"]["models"] = ["models"]

    await Tortoise.init(config=app_config)
    await Tortoise.generate_schemas()

TORTOISE_ORM = get_tortoise_config()
