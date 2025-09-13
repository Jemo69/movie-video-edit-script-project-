import asyncio
import asyncpg
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

async def main():
    db_url = os.getenv("NEON_DATABASE_URL")
    if not db_url:
        print("Error: NEON_DATABASE_URL environment variable not set or empty.")
        return

    print("Attempting to connect to the database...")
    
    try:
        parsed_url = urlparse(db_url)
        conn = await asyncpg.connect(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            user=parsed_url.username,
            password=parsed_url.password,
            database=parsed_url.path.lstrip('/'),
            ssl="require"
        )
        print("Connection successful!")
        version = await conn.fetchval('SELECT version()')
        print(f"PostgreSQL version: {version}")
        await conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
