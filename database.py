import os
import sys
from tortoise import Tortoise
from dotenv import load_dotenv
from typing import Dict, Any
from urllib.parse import urlparse

load_dotenv()

def get_tortoise_config() -> Dict[str, Any] | None:
    """
    Constructs the Tortoise ORM configuration from a LIBSQL_URL environment variable,
    supporting both local SQLite files and remote libSQL databases.
    """
    db_url = os.getenv("LIBSQL_URL")
    if not db_url:
        return None

    parsed_url = urlparse(db_url)

    if parsed_url.scheme in ("libsql", "https"):
        # For remote libsql connections, we monkey-patch the sqlite3 module
        # so Tortoise ORM uses the libsql client.
        import libsql_client.dbapi2
        sys.modules["sqlite3"] = libsql_client.dbapi2

        auth_token = os.getenv("LIBSQL_AUTH_TOKEN")

        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {
                        "file_path": db_url,
                        "autocommit": True,
                        "auth_token": auth_token,
                    },
                }
            },
            "apps": {
                "models": {
                    "models": ["models", "aerich.models"],
                    "default_connection": "default",
                }
            },
        }
    else:
        # For local SQLite files, we use the standard configuration.
        file_path = parsed_url.netloc + parsed_url.path
        return {
            "connections": {
                "default": {
                    "engine": "tortoise.backends.sqlite",
                    "credentials": {"file_path": file_path},
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
        raise ValueError("LIBSQL_URL environment variable not set or empty. Please check your .env file.")

    await Tortoise.init(config=config)
    await Tortoise.generate_schemas()

TORTOISE_ORM = get_tortoise_config()