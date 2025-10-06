import asyncio
import os
from dotenv import load_dotenv
from tortoise import Tortoise
from database import init_db, get_tortoise_config

load_dotenv()

async def main():
    """
    Tests the database connection and schema generation using the configuration
    from database.py.
    """
    db_url = os.getenv("LIBSQL_URL")
    if not db_url:
        print("Error: LIBSQL_URL environment variable not set or empty.")
        return

    print("Attempting to connect to the database using Tortoise ORM...")
    
    try:
        # Initialize the database connection and generate schemas
        await init_db()
        print("Database connection successful and schemas generated!")

        # Optional: Perform a simple query to further test the connection
        # This assumes you have at least one model defined.
        # from models import User
        # users = await User.all()
        # print(f"Found {len(users)} users.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connections
        await Tortoise.close_connections()
        print("Database connections closed.")

if __name__ == "__main__":
    asyncio.run(main())