import os
import re
from tortoise import Tortoise
from dotenv import load_dotenv

load_dotenv()

async def init_db():
    db_url = os.getenv("NEON_DATABASE_URL")
    # Remove the unsupported parameters from the URL
    db_url = re.sub(r'\?.*', '', db_url)

    await Tortoise.init(
        db_url=db_url,
        modules={"models": ["models"]}
    )
    await Tortoise.generate_schemas()

raw_db_url = os.getenv("NEON_DATABASE_URL")
clean_db_url = re.sub(r'\?.*', '', raw_db_url) if raw_db_url else None

TORTOISE_ORM = {
    "connections": {"default": clean_db_url},
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
