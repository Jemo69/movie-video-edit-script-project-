import os
from tortoise import Tortoise
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Get the database URL from the environment variables
db_url = os.getenv("NEON_DATABASE_URL")
if db_url:
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgres://", 1)
    # Tortoise-ORM uses asyncpg which expects 'ssl' instead of 'sslmode'
    if 'sslmode=require' in db_url:
        db_url = db_url.replace('sslmode=require', 'ssl=require')
    # channel_binding is not a valid asyncpg parameter, so we remove it.
    if '&channel_binding=require' in db_url:
        db_url = db_url.replace('&channel_binding=require', '')

DATABASE_URL = db_url

# Define the Tortoise-ORM configuration.
# This configuration is used by both the application to connect to the database
# and by the Aerich migration tool to manage schema changes.
TORTOISE_ORM = {
    "connections": {
        # The 'default' connection is used by the application models.
        "default": DATABASE_URL
    },
    "apps": {
        "models": {
            # This lists the modules where Tortoise-ORM should look for models.
            # "models" is for our application's models (User, Video).
            # "aerich.models" is required for the Aerich migration tool.
            "models": ["models", "aerich.models"],
            # This specifies that the models in this app use the 'default' connection.
            "default_connection": "default",
        }
    },
}

async def init_db():
    """
    Initializes the database connection using Tortoise-ORM.

    This function connects to the database and generates the database schemas
    based on the models defined in the application. It should be called once
    at the application startup.
    """
    if not DATABASE_URL:
        raise ValueError("NEON_DATABASE_URL environment variable not set or empty. Please check your .env file.")

    # Initialize Tortoise-ORM with a configuration that excludes aerich.models,
    # which is only needed for the migration tool.
    import copy
    app_config = copy.deepcopy(TORTOISE_ORM)
    app_config["apps"]["models"]["models"] = ["models"]
    await Tortoise.init(config=app_config)

    # Generate the database schemas.
    # This creates tables for the models if they don't exist.
    # In a production environment with migrations, you might want to handle this differently.
    await Tortoise.generate_schemas()
